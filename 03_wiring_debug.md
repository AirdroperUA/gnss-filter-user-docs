# Wiring Debug Guide

Use this guide when GNSS is not detected, DR1 stays active, or MAVLink tuning does not work.

## 1) GNSS path (STM32 <-> GNSS)

Symptoms:
- `GNS nav=0` persists and `age` keeps increasing.
- `s` may be non-zero but fix is still invalid.
- DR1 stays active because no-fix/low-sat guard trips.

Checks:
1. **Power**: GNSS module has stable power and shared ground with STM32/FC.
2. **UART pins**: GNSS TX -> STM32 `A3`; GNSS RX -> STM32 `A2`.
3. **Receiver mode**:
   - u-blox receiver: set `GNSS_TYPE=0`.
   - UM980/UM981 NMEA receiver: set `GNSS_TYPE=1`.
4. **u-blox custom firmware case**:
   - If your u-blox unit does not accept filter autoconfig, set `UBX_BAUD` to your receiver baud.
   - `UBX_BAUD=0` keeps autoconfig enabled (default).
5. **Reboot after mode/baud change**: `GNSS_TYPE` and `UBX_BAUD` are applied only after STM32 reboot.
6. **Sky/test conditions**: for live GNSS checks, test with clear sky view.

Quick verification:
- In logs, `GNS nav` should increase and `age` should stay low.
- If `age` grows for a long time, the filter is not receiving valid fixes.

## 2) FC GPS path (STM32 <-> FC GPS UART)

Symptoms:
- FC shows **No GPS** or **No GPS config data** while filter sees GNSS traffic.

Checks:
1. **UART pins**: STM32 `A11/A12` to FC GPS UART with TX/RX crossed.
2. **FC serial protocol/baud**:
   - Typical u-blox setup: GPS protocol + 460800 baud.
   - For UM980/UM981 workflows, FC GPS protocol must match your receiver output.
3. **DR state**: in DR1, forwarding is blocked by design.
4. **Diagnostic override**: set `FCGPS_FWD=1` temporarily to validate FC GPS path, then return to `0`.
5. **RC AUX GPS disable**: if FC/RC uses GPS-disable AUX logic, make sure that switch is not active.

Quick verification:
- With healthy GNSS and `FCGPS_FWD=1`, FC should show satellites/fix.
- Return `FCGPS_FWD=0` for normal anti-spoof operation.

## 3) MAVLink path (STM32 <-> FC telemetry)

Symptoms:
- Mission Planner cannot read/write STM32 params.
- No filter status text in GCS.

Checks:
1. **UART pins**: STM32 `A9/A10` to FC telemetry UART with TX/RX crossed.
2. **Protocol**: FC telemetry port set to MAVLink2 at 115200.
3. **Target IDs**: filter defaults are `SYSID=42`, `COMPID=191`.
4. **Single-owner COM port**: close other serial tools when using Mission Planner.

Quick verification:
- In Mission Planner:
  1. `Config/Tuning` -> `Full Parameter List`
  2. select STM32 (`SYSID 42`)
  3. click `Refresh Params` and verify values populate.

## 4) Common mistakes

- TX/RX not crossed.
- GNSS UART and FC GPS UART mixed up.
- Missing common ground.
- `GNSS_TYPE` changed but STM32 not rebooted.
- `UBX_BAUD` changed but STM32 not rebooted.
- Testing DR recovery during startup while `BOOT_DLYMS` still active.

## 5) Mission Planner parameter write issues

If parameter write/read is unstable:

1. Open only one GCS instance on the COM port.
2. In `Full Parameter List`, click `Refresh Params` before editing.
3. Edit value, click `Write Params`, then `Refresh Params` again.
4. If value did not persist, click `Write Params` again.
5. If link drops temporarily, wait up to 30-45 seconds and refresh again.
6. Reboot STM32 only when changing `GNSS_TYPE` or `UBX_BAUD`, or if value still does not apply.
