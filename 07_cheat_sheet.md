# Cheat Sheet (Field Quick Reference)

This is a one-page quick reference for setup checks, DR meaning, and common actions.

## 1) UART Summary

- GNSS and STM32: `A2/A3`
- FC MAVLink and STM32: `A9/A10` (MAVLink2 @ 115200)
- FC GPS and STM32: `A11/A12` (typically 460800)

## 2) Receiver Mode (`GNSS_TYPE`)

- `GNSS_TYPE=0`: u-blox/UBX mode.
- `GNSS_TYPE=1`: UM980/UM981 NMEA mode.
- After changing `GNSS_TYPE`, reboot STM32 (`NRST` or power cycle).
- For custom u-blox that should not be auto-configured:
  - set `UBX_BAUD` to receiver baud (`0` means autoconfig ON),
  - reboot STM32 to apply.

## 3) DR Modes

- **DR0**: normal mode, forwarding enabled.
- **DR1**: protection mode, forwarding blocked.
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

## 5) `tune_cli.py` Commands

List params:

```bash
py -3 .\tools\tune_cli.py --port COM12 --baud 115200 list
```

Read one param:

```bash
py -3 .\tools\tune_cli.py --port COM12 --baud 115200 get BLEND_MS
```

Set one param:

```bash
py -3 .\tools\tune_cli.py --port COM12 --baud 115200 set RJ_BASE_M 180
```

Commissioning check (one-time):

```bash
py -3 .\tools\tune_cli.py --port COM12 --baud 115200 set FCGPS_FWD 1
```

Return to operational mode:

```bash
py -3 .\tools\tune_cli.py --port COM12 --baud 115200 set FCGPS_FWD 0
```

## 6) Parameter Write Rules

- Mission Planner is read-only for filter params (Read/Refresh only).
- Write filter params only via `tune_cli.py`.
- After `set`, wait up to 30-45 seconds if immediate `get` returns `No reply`.
- After any parameter changes, reboot STM32 before flight.

## 7) Typical DR1 Triggers

- no-fix / low satellites (`sats < 5`),
- position jump (`SP_ABS_M`, `SP_JMP_MPS`),
- SNR anomaly (`SNR_*` when enabled),
- altitude anomaly (`ALT_*`),
- EKF unhealthy (`EKF_TRIPMS`).
