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

## 5) Mission Planner Parameter Write Flow

1. `Config/Tuning` -> `Full Parameter List`.
2. Select STM32 target (`SYSID 42`).
3. Click `Refresh Params`.
4. Edit values.
5. Click `Write Params`.
6. Click `Refresh Params` to confirm.

## 6) Parameter Write Rules

- Parameter read/write is done in Mission Planner Full Parameter List.
- If write does not apply on first click, repeat `Write Params`.
- Allow up to 30-45 seconds for telemetry link recovery after writes.
- Reboot is required for `GNSS_TYPE` and `UBX_BAUD`.
- Reboot is not required for most other parameters.

## 7) Typical DR1 Triggers

- no-fix / low satellites (`sats < 5`),
- position jump (`SP_ABS_M`, `SP_JMP_MPS`),
- SNR anomaly (`SNR_*` when enabled),
- altitude anomaly (`ALT_*`),
- EKF unhealthy (`EKF_TRIPMS`).
