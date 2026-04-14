# Setup Manual

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

## 1) Prerequisites

- STM32F401 filter board is installed and preflashed (no user flashing required).
- The board should be running a normal flight build.
- FC firmware is ArduPilot 4.6.1 or later.
- The airframe already has baseline calibration done with a known-good GPS path:
  - accelerometer calibrated,
  - compass calibrated.
  Otherwise, `EKF flags trip` can persist and FC may not return to DR0.
- FC must provide:
  - one telemetry UART for MAVLink2,
  - one GPS UART for GNSS receiver input,
  - or CAN-node transport (if using UCAN integration).

## 2) Flight controller serial setup (ArduPilot)

Use two FC serial ports:

1. **MAVLink port (to STM32 `A9/A10`)**
   - `SERIALx_PROTOCOL = 2` (MAVLink2)
   - `SERIALx_BAUD = 115` (115200)
2. **GPS UART (to STM32 `A11/A12`)**
   - `SERIALy_PROTOCOL = 5` (GPS)
   - `SERIALy_BAUD = 460` (460800)

Set ArduPilot GPS parameters for u-blox workflows:

- `GPS_AUTO_SWITCH = 0`
- `GPS1_TYPE = 2` (u-blox)
- `GPS_AUTO_CONFIG = 0`

If you use a different receiver family (for example UM980/UM981/UM982), FC GPS protocol settings must match the receiver output used in your installation.
For `GNSS_TYPE=1`, the STM32 expects one physical UM980 stream only:

- UM980 `COM1` -> STM32 `A2/A3`
- STM32 parses spoofing/SNR from that stream
- STM32 forwards that same stream to the FC GPS UART on `A11/A12`

## 3) CAN node mode (UCAN transport)

If STM32 is connected through a CAN node, apply these parameters.

CAN node parameters:

- `GPS_AUTO_CONFIG = 0`
- `GPS_SAVE_CFG = 1`
- `GPS_PORT = 2`

Flight controller parameters:

- `GPS1_TYPE = 9`
- `CAN_D1_UC_SER_EN = 1`
- `CAN_D1_UC_S1_BD = 115`
- `CAN_D1_UC_S1_IDX = 1`
- `CAN_D1_UC_S1_NOD = *` (set your actual CAN node ID)
- `CAN_D1_UC_S1_PRO = 2`

## 4) Filter control expectations

- Filter IDs: `SYSID=42`, `COMPID=191`.
- DR1 protection blocks live forwarding from GNSS input to FC GPS UART. The FC receives silence during DR1.
- Filter params are changed in Mission Planner:
  - `Config/Tuning` -> `Full Parameter List`
  - select STM32 (`SYSID=42`)
  - `Refresh Params` -> edit value -> `Write Params`
- Reboot is not required after every parameter write.
- On a busy MAVLink link, `Write Params` may need 1-2 attempts. More than 2 attempts indicate high telemetry load.

Receiver mode selection on STM32:

- `GNSS_TYPE=0`: u-blox/UBX mode.
- `GNSS_TYPE=1`: UM980/UM981/UM982 NMEA mode.
- `GNSS_TYPE` changes require reboot to apply.
- For u-blox only, `UBX_BAUD` controls autoconfig/manual baud:
  - `UBX_BAUD=0`: autoconfig enabled (default).
  - `UBX_BAUD>0`: autoconfig disabled; filter uses this baud directly.
  - `UBX_BAUD` changes also require reboot to apply.
  - Gateway modules with their own MCU and dual/internal receivers (for example Quadro GPS, UNA3, UNA4-SFE, or similar dual-F9P products) must use `UBX_BAUD>0`; filter autobaud is not possible for that class of module.
- For UM980/UM981/UM982 deployments, configure the receiver `COM1` stream to match the FC GPS protocol and baud you intend to forward through STM32.

## 5) First boot checks

In GCS messages, confirm:

- filter boot message is present,
- GNSS counters increase,
- no repeated communication faults.

If FC shows **No GPS config data**:

- verify FC GPS UART protocol/baud,
- verify `A11/A12` TX/RX cross wiring,
- verify common ground.

## 6) Required commissioning step (before flight tuning)

Before normal operation, validate FC GPS path end-to-end once:

1. Connect to filter (`SYSID=42`) and set `FCGPS_FWD=1`.
2. Wait for healthy GNSS in logs (`fix` and `nav` stay low, satellites are present, no repeated no-fix condition).
3. Confirm FC receives GNSS data.
4. Set `FCGPS_FWD=0` for operational anti-spoof mode.

`FCGPS_FWD=1` is diagnostic only.

## 7) Build-state note

Normal operation uses the normal board firmware already installed by the supplier or service process.
