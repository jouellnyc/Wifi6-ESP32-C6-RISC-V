
# Working Bluetooth Scanner for ESP32-C6 using low-level bluetooth module
# This bypasses aioble and uses the core bluetooth module directly

import asyncio
import bluetooth
from machine import Pin
import time
import struct

class ESP32BLEScanner:
    def __init__(self):
        self.devices_found = {}
        self.ble = bluetooth.BLE()
        self.scan_complete = False

        # ESP32-C6 LED handling
        try:
            self.led = Pin(8, Pin.OUT)  # Common ESP32-C6 LED pin
        except:
            try:
                self.led = Pin(2, Pin.OUT)  # Alternative LED pin
            except:
                self.led = None
                print("Note: No LED pin available")

    def _irq(self, event, data):
        """BLE interrupt handler"""
        # Use numeric constants instead of named constants
        # 5 = IRQ_SCAN_RESULT, 6 = IRQ_SCAN_DONE
        if event == 5:  # IRQ_SCAN_RESULT
            # data: (addr_type, addr, adv_type, rssi, adv_data)
            addr_type, addr, adv_type, rssi, adv_data = data

            # Convert address to string
            mac_addr = ':'.join(['{:02X}'.format(b) for b in addr])

            if mac_addr not in self.devices_found:
                # Parse advertisement data
                name = self._decode_name(adv_data) or "Unknown"
                services = self._decode_services(adv_data)
                manufacturer_data = self._decode_manufacturer(adv_data)

                addr_type_str = "Public" if addr_type == 0 else "Random"

                self.devices_found[mac_addr] = {
                    'name': name,
                    'rssi': rssi,
                    'addr_type': addr_type_str,
                    'connectable': adv_type in (0, 1),  # ADV_IND or ADV_DIRECT_IND
                    'services': services,
                    'manufacturer_data': manufacturer_data,
                    'adv_type': adv_type
                }

                print("*", end="")

                # Show strong signals immediately
                if rssi > -60:
                    print(f"\n  Strong: {name} ({mac_addr}) {rssi}dBm", end="")

        elif event == 6:  # IRQ_SCAN_DONE
            self.scan_complete = True

    def _decode_name(self, adv_data):
        """Decode device name from advertisement data"""
        try:
            i = 0
            while i < len(adv_data):
                length = adv_data[i]
                if length == 0:
                    break

                ad_type = adv_data[i + 1]
                if ad_type == 0x09:  # Complete Local Name
                    return adv_data[i + 2:i + 1 + length].decode('utf-8')
                elif ad_type == 0x08:  # Shortened Local Name
                    return adv_data[i + 2:i + 1 + length].decode('utf-8')

                i += 1 + length
        except:
            pass
        return None

    def _decode_services(self, adv_data):
        """Decode services from advertisement data"""
        services = []
        try:
            i = 0
            while i < len(adv_data):
                length = adv_data[i]
                if length == 0:
                    break

                ad_type = adv_data[i + 1]
                if ad_type in (0x02, 0x03):  # Incomplete/Complete list of 16-bit UUIDs
                    for j in range(i + 2, i + 1 + length, 2):
                        if j + 1 < len(adv_data):
                            uuid = struct.unpack('<H', adv_data[j:j+2])[0]
                            services.append(f"0x{uuid:04X}")
                elif ad_type in (0x06, 0x07):  # Incomplete/Complete list of 128-bit UUIDs
                    for j in range(i + 2, i + 1 + length, 16):
                        if j + 15 < len(adv_data):
                            uuid_bytes = adv_data[j:j+16]
                            # Convert to standard UUID string format
                            uuid_str = '-'.join([
                                uuid_bytes[12:16][::-1].hex(),
                                uuid_bytes[10:12][::-1].hex(),
                                uuid_bytes[8:10][::-1].hex(),
                                uuid_bytes[6:8][::-1].hex(),
                                uuid_bytes[0:6][::-1].hex()
                            ])
                            services.append(uuid_str)

                i += 1 + length
        except:
            pass
        return services

    def _decode_manufacturer(self, adv_data):
        """Decode manufacturer data from advertisement data"""
        try:
            i = 0
            while i < len(adv_data):
                length = adv_data[i]
                if length == 0:
                    break

                ad_type = adv_data[i + 1]
                if ad_type == 0xFF:  # Manufacturer Specific Data
                    return adv_data[i + 2:i + 1 + length]

                i += 1 + length
        except:
            pass
        return None

    async def scan_devices(self, duration_seconds=15):
        """Scan for BLE devices"""
        print(f"Scanning for BLE devices ({duration_seconds} seconds)...")
        print("=" * 50)

        self.devices_found.clear()
        self.scan_complete = False

        if self.led:
            self.led.on()

        try:
            # Activate BLE
            self.ble.active(True)

            # Set up interrupt handler
            self.ble.irq(self._irq)

            print("Scanning", end="")

            # Start scanning
            self.ble.gap_scan(duration_seconds * 1000, 30000, 30000)  # duration, interval, window in microseconds

            # Wait for scan to complete
            start_time = time.ticks_ms()
            while not self.scan_complete:
                if time.ticks_diff(time.ticks_ms(), start_time) > (duration_seconds + 2) * 1000:
                    print("\nScan timeout!")
                    break
                await asyncio.sleep_ms(100)

            print(f"\n\nScan complete! Found {len(self.devices_found)} unique devices")

        except Exception as e:
            print(f"\nScan error: {e}")
            import sys
            sys.print_exception(e)
        finally:
            if self.led:
                self.led.off()
            try:
                self.ble.gap_scan(None)  # Stop scanning
            except:
                pass

        return self.devices_found

    def print_results(self):
        """Print detailed scan results"""
        if not self.devices_found:
            print("No devices found")
            return

        print("\n" + "=" * 60)
        print("DISCOVERED BLE DEVICES")
        print("=" * 60)

        # Sort by signal strength (strongest first)
        sorted_devices = sorted(
            self.devices_found.items(),
            key=lambda x: x[1]['rssi'],
            reverse=True
        )

        for i, (mac, info) in enumerate(sorted_devices, 1):
            # Signal strength indicator
            if info['rssi'] > -50:
                strength = "Excellent"
            elif info['rssi'] > -60:
                strength = "Good"
            elif info['rssi'] > -70:
                strength = "Fair"
            elif info['rssi'] > -80:
                strength = "Weak"
            else:
                strength = "Very Weak"

            print(f"\n{i}. {info['name']}")
            print(f"   MAC Address: {mac}")
            print(f"   Signal: {info['rssi']} dBm ({strength})")
            print(f"   Address Type: {info['addr_type']}")
            print(f"   Connectable: {'Yes' if info['connectable'] else 'No'}")

            # Show services if any
            if info['services']:
                service_list = info['services'][:3]  # First 3
                print(f"   Services: {', '.join(service_list)}")
                if len(info['services']) > 3:
                    print(f"   ... and {len(info['services']) - 3} more services")

            # Show manufacturer data if available
            if info['manufacturer_data']:
                mfg_data = info['manufacturer_data']
                if len(mfg_data) >= 2:
                    company_id = struct.unpack('<H', mfg_data[:2])[0]
                    print(f"   Manufacturer: Company ID 0x{company_id:04X}")
                else:
                    print(f"   Manufacturer: {len(mfg_data)} bytes of data")

    def print_summary(self):
        """Print a quick summary"""
        if not self.devices_found:
            print("No devices found")
            return

        print(f"\nQuick Summary - {len(self.devices_found)} devices:")

        # Sort by signal strength
        sorted_devices = sorted(
            self.devices_found.items(),
            key=lambda x: x[1]['rssi'],
            reverse=True
        )

        for mac, info in sorted_devices:
            strength = "Strong" if info['rssi'] > -60 else "Weak"
            name_display = info['name'] if info['name'] != "Unknown" else "Unnamed"
            print(f"  {name_display} ({mac}) - {info['rssi']}dBm ({strength})")

# Scan functions
async def quick_scan():
    """5-second scan"""
    scanner = ESP32BLEScanner()
    await scanner.scan_devices(5)
    scanner.print_summary()

async def standard_scan():
    """15-second detailed scan"""
    scanner = ESP32BLEScanner()
    await scanner.scan_devices(15)
    scanner.print_results()

async def long_scan():
    """30-second thorough scan"""
    scanner = ESP32BLEScanner()
    await scanner.scan_devices(30)
    scanner.print_results()

async def continuous_scan():
    """Continuous scanning"""
    scanner = ESP32BLEScanner()
    print("Continuous BLE scanning - Press Ctrl+C to stop")

    try:
        while True:
            print(f"\n{'-'*25} New Scan {'-'*25}")
            await scanner.scan_devices(10)
            scanner.print_summary()
            print("\nWaiting 15 seconds...")
            await asyncio.sleep(15)
    except KeyboardInterrupt:
        print("\nStopped continuous scanning")

async def main():
    """Main function"""
    print("ESP32-C6 BLE Scanner (Low-level)")
    print("=" * 35)

    print("\nScan Options:")
    print("1. Quick scan (5 seconds)")
    print("2. Standard scan (15 seconds)")
    print("3. Long scan (30 seconds)")
    print("4. Continuous scanning")

    try:
        choice = input("Choose (1-4): ").strip()

        if choice == "1":
            await quick_scan()
        elif choice == "2":
            await standard_scan()
        elif choice == "3":
            await long_scan()
        elif choice == "4":
            await continuous_scan()
        else:
            print("Running standard scan...")
            await standard_scan()

    except Exception as e:
        print(f"Error: {e}")
        import sys
        sys.print_exception(e)

def run():
    """Run the scanner"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScanner stopped")

if __name__ == "bt_scan_ll":
    run()

