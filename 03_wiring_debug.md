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
- `tune_cli.py` cannot list/get params.
- No filter status text in GCS.

Checks:
1. **UART pins**: STM32 `A9/A10` to FC telemetry UART with TX/RX crossed.
2. **Protocol**: FC telemetry port set to MAVLink2 at 115200.
3. **Target IDs**: filter defaults are `SYSID=42`, `COMPID=191`.
4. **Port lock**: do not use Mission Planner and `tune_cli.py` on the same COM port at the same time.

Quick verification:
- Run `py -3 .\tools\tune_cli.py --port COM12 --baud 115200 list`.

## 4) Common mistakes

- TX/RX not crossed.
- GNSS UART and FC GPS UART mixed up.
- Missing common ground.
- `GNSS_TYPE` changed but STM32 not rebooted.
- `UBX_BAUD` changed but STM32 not rebooted.
- Testing DR recovery during startup while `BOOT_DLYMS` still active.

## 5) `tune_cli.py` runtime issues (Windows)

If `tune_cli.py` opens/closes instantly or reports import errors:

1. Use explicit interpreter:
   - `py -3 .\tools\tune_cli.py --port COM12 --baud 115200 list`
2. Install missing modules:
   - `py -3 -m ensurepip --upgrade`
   - `py -3 -m pip install pymavlink pyserial`

If `get` shows `No reply` right after `set`:

- Check whether `set` already printed `PARAM=value` (write may already be successful).
- Wait up to 30-45 seconds, then retry `get`.
- Retry `get` 2-3 times if needed.
- Reboot STM32 (`NRST` or power cycle) after parameter updates before flight use.
