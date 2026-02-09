# Setup Manual

## 1) Prerequisites

- STM32F401 filter board is installed and **preflashed** (no user flashing required).
- FC firmware is **ArduPilot 4.6.1 or later** and GPS input is **UBX (u-blox)**.
- The airframe **already has a working GPS** for initial calibration:
  - accelerometer calibrated
  - compass calibrated
  - otherwise **EKF flags trip** can persist and the FC may never return to DR0
- Flight controller configured with:
  - one telemetry UART for MAVLink2
  - one GPS UART for UBX

## 2) Flight Controller Serial Setup (ArduPilot)

Use two FC serial ports:

1. **MAVLink port (to STM32 `A9/A10`)**
   - `SERIALx_PROTOCOL = 2` (MAVLink2)
   - `SERIALx_BAUD = 115` (115200)
2. **GPS UART (to STM32 `A11/A12`)**
   - `SERIALy_PROTOCOL = 5` (GPS)
   - `SERIALy_BAUD = 460` (460800)

GPS type should be u-blox on FC side.

Set the following ArduPilot GPS params:

- `GPS_AUTO_SWITCH = 0`
- `GPS1_TYPE = 2` (u-blox)
- `GPS_AUTO_CONFIG = 0`

## 3) Filter Control Expectations

- Filter `SYSID` is `42`, `COMPID` is onboard computer (`191`).
- The filter disables GNSS delivery to the FC by blocking GNSS forwarding to the FC GPS UART.
- During DR1, raw UBX forwarding to the FC GPS UART is blocked.

## 4) First Boot Checks

In GCS messages, confirm you see filter status text such as:

- boot message from filter
- GNSS NAV counters increasing
- no firmware-version warning from filter

If FC says **"No GPS config data"**:

- verify FC GPS serial protocol/baud,
- verify UART cross wiring on `A11/A12`,
- verify common ground.
