# Wiring Debug Guide

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

Use this guide when GNSS is not detected, DR1 stays active, or MAVLink tuning does not work.

For WeAct H743 DroneCAN, there is no FC GPS UART and no FC MAVLink UART. GNSS
debugging still starts at `A2/A3`, but FC-side debugging moves to CAN wiring,
CAN bitrate, ArduPilot DroneCAN setup, and the onboard screen. See the full
[H743 DroneCAN Guide](13_h743_dronecan.md).

## 1) GNSS path (STM32 <-> GNSS)

Symptoms:
- `data=... fix=9999ms nav=9999ms ...` persists, or `fix` / `nav` keeps growing.
- Satellites may be present, but fix is still invalid.
- DR1 stays active because no-fix/low-sat guard trips.

Checks:
1. **Power**: GNSS module has stable power and shared ground with STM32/FC.
2. **UART pins**: GNSS TX -> STM32 `A3`; GNSS RX -> STM32 `A2`.
3. **Receiver mode**:
   - u-blox receiver: set `GNSS_TYPE=0`.
   - UM980/UM981/UM982 NMEA receiver: set `GNSS_TYPE=1`.
   - Septentrio Mosaic X5 NMEA receiver: set `GNSS_TYPE=2`.
   - In UM980/UM981/UM982 or Mosaic mode, use one physical receiver stream only -> STM32 `A2/A3`.
     The filter reads spoofing/SNR data from that stream and forwards the same stream to the FC GPS UART.
4. **u-blox custom firmware case**:
   - If your u-blox unit does not accept filter autoconfig, set `UBX_BAUD` to your receiver baud.
   - `UBX_BAUD=0` keeps autoconfig enabled (default).
   - If `UBX_BAUD>0`, the filter skips the full UBX autoconfig path. It still makes a best-effort request for `NAV-SAT`, but `SNR=NA` is still possible if the receiver ignores that request.
   - This same manual-baud rule applies to gateway modules with an intermediary MCU (for example Quadro GPS, UNA3, UNA4-SFE, or similar dual-F9P products). Set `UBX_BAUD` to the exact output baud; do not rely on filter autobaud.
5. **Reboot after mode/baud change**: `GNSS_TYPE` and `UBX_BAUD` are applied only after STM32 reboot.
6. **Sky/test conditions**: for live GNSS checks, test with clear sky view.

Quick verification:
- In logs, `fix` and `nav` should stay low and `SATS` should reflect the real receiver state.
- If `nav` grows for a long time, the filter is not receiving valid GNSS nav data.
- If `fix` grows for a long time, the filter is not receiving valid position fixes.

## 2) FC GPS path (STM32 <-> FC GPS UART)

Skip this section for H743 DroneCAN firmware. That build publishes GPS over
DroneCAN and does not drive an FC GPS UART. For H743 standalone UART builds,
use `C6/C7` instead of F401 `A11/A12`.

Symptoms:
- FC shows **No GPS** or **No GPS config data** while filter sees GNSS traffic.

Checks:
1. **UART pins**: STM32 `A11/A12` on F401, or `C6/C7` on H743 UART builds, to FC GPS UART with TX/RX crossed.
2. **FC serial protocol/baud**:
   - Typical u-blox setup: GPS protocol + 460800 baud.
   - For UM980/UM981/UM982 or Mosaic workflows, FC GPS protocol must match your receiver output.
   - If UM980 is configured as a single mixed `COM1` stream, the FC must match that same forwarded stream.
3. **DR state**: in DR1, live forwarding is blocked by design. The FC GPS UART receives silence.
4. **Diagnostic override**: set `FCGPS_FWD=1` temporarily to validate FC GPS path, then return to `0`. This raw-forwarding override forces the FC GPS UART on and bypasses DR1, the boot north gate, and the hemisphere fence for bench validation only.
5. **RC AUX GPS disable**: if FC/RC uses GPS-disable AUX logic, make sure that switch is not active.

Quick verification:
- With `FCGPS_FWD=1` and a live GNSS stream, FC should show incoming GPS data even if the filter has not accepted the fix yet.
- Return `FCGPS_FWD=0` for normal anti-spoof operation.

## 3) MAVLink path (STM32 <-> FC telemetry)

Skip this section for H743 DroneCAN firmware. That build has no FC MAVLink
serial link and no Mission Planner MAVLink parameter interface in v1.

Symptoms:
- Mission Planner cannot reliably read/write STM32 params.
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
- If the STM32 parameters appear as raw names only, install [AirDroper Mission Planner Params](https://gps.airdroper.org/download/mission-planner-mod) before troubleshooting tuning values.

## 4) Common mistakes

- TX/RX not crossed.
- GNSS UART and FC GPS UART mixed up.
- Missing common ground.
- `GNSS_TYPE` changed but STM32 not rebooted.
- `UBX_BAUD` changed but STM32 not rebooted.
- Testing DR recovery during startup while `BOOT_DLYMS` still active.

## 4b) H743 DroneCAN path

Symptoms:
- DroneCAN node does not appear.
- ArduPilot does not receive DroneCAN GPS.
- The H743 screen shows `PUB BLK`, `WHY GPS`, `WHY DR1`, or `WHY CAN ERR`.

Checks:
1. **CAN transceiver required**: H743 `PB8/PB9` are logic-level FDCAN pins.
   They must go through a 3.3 V CAN transceiver such as SN65HVD230.
2. **CAN pin crossing to transceiver**: `PB9 -> TXD`, `PB8 <- RXD`.
3. **Bus wiring**: transceiver `CANH/CANL/GND` to the FC CAN port, with common
   ground.
4. **Bitrate**: H743 firmware uses `1 Mbps`; FC CAN port must match.
5. **ArduPilot parameters**: enable the correct CAN driver, set DroneCAN
   protocol, and set the GPS instance type to `9`.
6. **Termination**: enable the module's 120 ohm terminator only if the H743
   node is at a physical bus end.
7. **USB-C pins**: leave `PA11/PA12` unused by external wiring. They belong to
   USB-C on H743.

Quick verification:
- The screen should show `GNSS FILTER` and eventually `PUB ON DR0`.
- DroneCAN/SLCAN tooling should show node ID `42`.
- During DR1, `Fix2/Auxiliary` stop but `NodeStatus` remains online.

## 5) Mission Planner parameter write issues

If parameter write/read is unstable:

1. Open only one GCS instance on the COM port.
2. Install [AirDroper Mission Planner Params](https://gps.airdroper.org/download/mission-planner-mod) if descriptions, ranges, units, or option labels are missing.
3. In `Full Parameter List`, click `Refresh Params` before editing.
4. Edit value, click `Write Params`, then `Refresh Params` again.
5. If value did not persist, click `Write Params` again.
6. On a busy telemetry link, 2-5 write attempts can be normal before the value sticks.
7. If link drops temporarily, wait up to 30-45 seconds and refresh again.
8. Reboot STM32 only when changing `GNSS_TYPE` or `UBX_BAUD`, or if value still does not apply.
