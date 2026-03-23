# Cheat Sheet (Field Quick Reference)

> Board store: [GPS Spoofing Filter](https://airdroper.org/product/gps-spoofing-filter/)

This is a one-page quick reference for setup checks, DR meaning, and common actions.

## 1) UART Summary

- GNSS and STM32: `A2/A3`
- FC MAVLink and STM32: `A9/A10` (MAVLink2 @ 115200)
- FC GPS and STM32: `A11/A12` (typically 460800)

## 2) Receiver Mode (`GNSS_TYPE`)

- `GNSS_TYPE=0`: u-blox/UBX mode.
- `GNSS_TYPE=1`: UM980/UM981 NMEA mode.
- `FCGPS_UART=1`: A11/A12 active as FC GPS UART (normal operation, default).
- `FCGPS_UART=0`: A11/A12 released into input mode. Do not use during flight.
- For `GNSS_TYPE=1`, use one physical UM980 stream only:
  - `COM1` -> STM32 `A2/A3`
  - STM32 forwards that same stream to FC GPS UART
- After changing `GNSS_TYPE`, reboot STM32 (`NRST` or power cycle).
- For custom u-blox that should not be auto-configured:
  - set `UBX_BAUD` to receiver baud (`0` means autoconfig ON),
  - reboot STM32 to apply.
- For gateway / dual-F9P modules such as Quadro GPS, UNA3, and UNA4-SFE:
  - use `GNSS_TYPE=0`,
  - set the exact `UBX_BAUD`,
  - do not use filter autobaud.

## 3) DR Modes

- **DR0**: normal mode, forwarding enabled.
- **DR1**: protection mode, live forwarding blocked. With `DR_NOFIX=1` and `NMEA_NOFIX=1`, the FC GPS UART sees periodic NMEA NO_FIX beacons instead.
- **B5**: high pulse (~3 s) on each DR0 -> DR1 transition.

## 4) Quick Diagnostics

If FC shows **No GPS config data**:

- Check FC GPS UART protocol and baud.
- Check `A11/A12` TX/RX crossing.
- Confirm common ground.

If DR1 stays active:

- Check no-fix / low-satellite state.
- Check guard thresholds (`ARM_*`, `SP_*`, `ALT_*`, `SNR_*`).
- Increase `BOOT_DLYMS` if false DR1 appears right after boot.

If FC constantly shows **No Fix**:

- Verify RC AUX logic is not forcing GPS disable in FC settings.

## 5) Mission Planner Parameter Write Flow

1. `Config/Tuning` -> `Full Parameter List`.
2. Select STM32 target (`SYSID 42`).
3. Click `Refresh Params`.
4. Edit values.
5. Click `Write Params`.
6. Click `Refresh Params` to confirm.

## 6) Parameter Write Rules

- Parameter read/write is done in Mission Planner Full Parameter List.
- If write does not apply on first click, repeat `Write Params`. 1-2 attempts are normal; 3+ suggests a very busy MAVLink link.
- Allow up to 30-45 seconds for telemetry link recovery after writes.
- Reboot is required for `GNSS_TYPE` and `UBX_BAUD`.
- Reboot is not required for most other parameters.

## 7) Typical DR1 Triggers

- no-fix / low satellites (`sats < 5`),
- position jump (`SP_ABS_M`, `SP_JMP_MPS`),
- SNR anomaly (`SNR_*` when enabled),
- altitude anomaly (`ALT_*`),
- EKF unhealthy (`EKF_TRIPMS`).

## 8) Mission Planner Log Timing

- In Mission Planner `Messages`, STM32 filter status logs normally show up about every **10 seconds** by default.
- Usually two lines appear together:
  - `ARM=... DR=... BLEND=... LAT=... LONG=...`
  - `data=... fix=... nav=... SATS=... SNR=...`
