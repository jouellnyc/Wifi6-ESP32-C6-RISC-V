# Wifi6-ESP32-C6-RISC-V

# ESP32-C6 MicroPython WiFi 6 Development Guide

A comprehensive guide for working with the ESP32-C6 development board running bleeding-edge MicroPython, showcasing WiFi 6 capabilities and RISC-V features.

## Hardware Setup

- **Board**: ESP32-C6 Development Board (RISC-V)
- **Firmware**: MicroPython v1.26.0-preview.489.gc9b52b2b7 (bleeding edge)
- **Architecture**: Dual-core RISC-V (high-performance + low-power cores)
- **Key Features**: WiFi 6 (802.11ax), Bluetooth 5.0 LE, IEEE 802.15.4 support

## Working Features

### ✅ WiFi 6 Connectivity

Basic WiFi connection works with enhanced performance:

```python
import network

# Standard connection - WiFi 6 benefits automatic
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('your_ssid', 'your_password')

# Check connection status
print("IP Config:", wlan.ifconfig())
print("RSSI:", wlan.status('rssi'))  # Enhanced signal handling
```

**Example Output:**
```
Connected to Wifi
('192.168.0.219', '255.255.255.0', '192.168.0.197', '192.168.0.193')
RSSI: -60
```

### ✅ Advanced WiFi Configuration

Several advanced configuration options are available:

```python
# Explore available WiFi parameters
wlan = network.WLAN(network.STA_IF)

# Working configuration parameters
print("Channel:", wlan.config('channel'))           # Current WiFi channel
print("ESSID:", wlan.config('essid'))              # Network name
print("DHCP Hostname:", wlan.config('dhcp_hostname'))  # Device hostname
print("Reconnects:", wlan.config('reconnects'))     # Auto-reconnect setting
print("TX Power:", wlan.config('txpower'))         # Transmission power (dBm)
print("Power Management:", wlan.config('pm'))       # Power saving mode
print("Protocol:", wlan.config('protocol'))        # WiFi protocol (71 = WiFi 6!)
```

**Example Output:**
```
channel: 3
essid: MY_SSID
dhcp_hostname: mpy-esp32c6
reconnects: -1
txpower: 20.0
pm: 1
protocol: 71
```

### ✅ TX Power Control

Adjust transmission power for range vs. power consumption:

```python
# Set TX power (0.0 to 20.0 dBm)
wlan.config(txpower=15.0)  # Reduce power for battery savings
print("New TX Power:", wlan.config('txpower'))

# Power management modes
wlan.config(pm=0)  # Disable power saving for maximum performance
wlan.config(pm=1)  # Enable power saving
```

### ✅ Enhanced Hardware Access

Improved GPIO and peripheral access:

```python
import machine

# Enhanced ADC with better performance
adc = machine.ADC(machine.Pin(0))
adc.atten(machine.ADC.ATTN_11DB)  # Full voltage range
reading = adc.read()
print("ADC Reading:", reading)

# Improved power management
machine.lightsleep(5000)  # More efficient sleep modes
```

### ✅ Bluetooth 5.0 LE

Basic BLE functionality available:

```python
import bluetooth
from micropython import const

# Initialize BLE 5.0
ble = bluetooth.BLE()
ble.active(True)

# Basic advertising
ble.gap_advertise(100, b'\x02\x01\x06\x04\x09ESP32')
```

## Protocol Analysis

The `protocol: 71` value suggests WiFi 6 (802.11ax) negotiation is active. This is significantly higher than older ESP32 variants, indicating enhanced WiFi capabilities.

## Power Management Features

The ESP32-C6's dual RISC-V architecture provides:
- Better power efficiency during sleep modes
- Enhanced wake-up capabilities
- Flexible power management options

```python
import machine
import esp32

# Enhanced sleep modes
machine.lightsleep(1000)  # Optimized for C6 architecture

# Wake-on-external-pin (if supported)
try:
    esp32.wake_on_ext0(machine.Pin(0), 1)
except:
    pass
```

## Debugging and Exploration

### Check Available Modules
```python
help('modules')  # List all compiled modules
```

### Explore ESP32-specific Features
```python
import esp32
print(dir(esp32))  # Show available ESP32 functions

import machine
print(dir(machine))  # Show available machine functions
```

### WiFi Parameter Discovery
```python
# Test all possible WiFi config parameters
test_params = ['channel', 'essid', 'hidden', 'authmode', 'password', 
               'dhcp_hostname', 'reconnects', 'txpower', 'max_tx_power',
               'pm', 'bandwidth', 'protocol']

for param in test_params:
    try:
        val = wlan.config(param)
        print(f"{param}: {val}")
    except ValueError:
        pass  # Parameter not supported
    except Exception as e:
        print(f"{param}: Error - {e}")
```

## Limitations & Work in Progress

### ❌ Not Yet Working
- `max_tx_power` parameter (use `txpower` instead)
- Some AP-specific configurations require AP mode
- IEEE 802.15.4/Thread support (may require custom builds)
- Extended BLE 5.0 advertising features

### 🔬 Experimental
- Matter/Thread protocol support
- Advanced WiFi 6 features (OFDMA, MU-MIMO)
- Enhanced mesh networking capabilities

## Development Tips

1. **Use bleeding-edge builds** for latest features
2. **Check parameter names** - they may differ from older ESP32 variants  
3. **Explore available options** using `dir()` and config exploration
4. **Monitor power consumption** - the C6 has much better power management
5. **Test WiFi 6 benefits** in congested environments

## Future Possibilities

The ESP32-C6 hardware supports several cutting-edge features that may become available in future MicroPython builds:

- **Thread/Matter** protocol support for smart home applications
- **Enhanced mesh networking** with WiFi 6 improvements
- **Advanced BLE 5.0** features like extended advertising
- **IEEE 802.15.4** integration for Zigbee compatibility

## Contributing

Found new working features or improvements? PRs welcome! This is an active area of development in the MicroPython ecosystem.

---

**Hardware**: ESP32-C6 RISC-V WiFi 6 Development Board  
**Firmware**: MicroPython v1.26.0-preview.489.gc9b52b2b7  
**Last Updated**: August 2025
