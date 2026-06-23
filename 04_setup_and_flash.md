# Setup Manual

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

## 1) Prerequisites

- STM32F401 filter board is installed and preflashed, or a WeAct H743 board is
  flashed with the matching standalone/H743 DroneCAN development firmware.
- The board should be running the firmware family that matches the wiring mode.
- FC firmware is ArduPilot 4.6.1 or later.
- The airframe already has baseline calibration done with a known-good GPS path:
  - accelerometer calibrated,
  - compass calibrated.
  Otherwise, `EKF flags trip` can persist and FC may not return to DR0.
- FC must provide:
  - one telemetry UART for MAVLink2,
  - one GPS UART for GNSS receiver input,
  - or a DroneCAN-capable CAN port for the H743 DroneCAN firmware.

## 2) Flight controller serial setup (ArduPilot)

Use two FC serial ports:

1. **MAVLink port (to STM32 `A9/A10`)**
   - `SERIALx_PROTOCOL = 2` (MAVLink2)
   - `SERIALx_BAUD = 115` (115200)
2. **GPS UART**
   - `SERIALy_PROTOCOL = 5` (GPS)
   - `SERIALy_BAUD = 460` (460800)

For F401, the FC GPS UART connects to STM32 `A11/A12`. For H743 standalone
UART builds, it connects to STM32 `C6/C7`. H743 DroneCAN does not use an FC GPS
UART.

Set ArduPilot GPS parameters for u-blox workflows:

- `GPS_AUTO_SWITCH = 0`
- `GPS1_TYPE = 2` (u-blox)
- `GPS_AUTO_CONFIG = 0`

If you use a different receiver family (for example UM980/UM981/UM982 or Mosaic X5), FC GPS protocol settings must match the receiver output used in your installation.
For `GNSS_TYPE=1` or `GNSS_TYPE=2`, the STM32 expects one physical NMEA receiver stream only:

- UM980 `COM1` -> STM32 `A2/A3`
- STM32 parses spoofing/SNR from that stream
- STM32 forwards that same stream to the FC GPS UART (`A11/A12` on F401,
  `C6/C7` on H743 UART builds)

## 3) H743 DroneCAN GPS mode

Use this section only with the `weact_mini_h743vitx_dronecan` or
`weact_mini_h743vitx_dronecan_usb` firmware. This mode publishes native
DroneCAN GNSS messages and does not use the FC MAVLink or FC GPS serial ports.
The complete board-specific procedure is in the
[H743 DroneCAN Guide](13_h743_dronecan.md).

Firmware defaults:

- DroneCAN node ID: `42`
- FC DroneCAN node filter: `0` (auto-detect/identify the FC from
  arm/safety/NotifyState broadcasts, not from arbitrary NodeStatus frames). Set
  `FILTER_DRONECAN_FC_NODE_ID` at build time if the bus has multiple nodes and
  you want the onboard screen locked to one FC node.
- CAN bitrate: `1 Mbps`
- Published messages: `uavcan.protocol.NodeStatus`,
  `uavcan.protocol.GetNodeInfo`, `uavcan.equipment.gnss.Fix2`,
  `uavcan.equipment.gnss.Auxiliary`
- Onboard screen: filter OK/warn/no-OK with a `WHY` reason line, GNSS publish
  state, CAN counters, FC DroneCAN node health/mode, arm/safety state, and an
  ArduPilot vehicle-state row from `ardupilot.indication.NotifyState` when that
  broadcast is present

Flight controller parameters for the CAN port used by the H743 node:

- `CAN_P1_DRIVER = 1` for CAN1, or `CAN_P2_DRIVER = 1` for CAN2
- `CAN_D1_PROTOCOL = 1` for CAN1, or `CAN_D2_PROTOCOL = 1` for CAN2
- `CAN_P1_BITRATE = 1000000` or `CAN_P2_BITRATE = 1000000`
- `GPS1_TYPE = 9` for DroneCAN GPS
- `GPS_AUTO_CONFIG = 1` for the default serial-only GPS auto-config mode
- optional: `GPS1_CAN_OVRIDE = 42` if the bus has more than one DroneCAN
  GPS-like node

Reboot the flight controller after changing CAN driver parameters. If the H743
node is at a physical end of the CAN bus, enable the CAN module's 120 ohm
termination; otherwise leave it off.

Flash the USB-C ROM DFU build from a development machine:

```powershell
pio run -e weact_mini_h743vitx_dronecan_usb -t upload
```

To enter DFU: hold `BOOT0`, reset or power-cycle the WeAct H743, then connect
USB-C.

The signed H743 secure-app image can also be uploaded over the same USB-C ROM
DFU path. This env sets the DFU write address to the app slot at `0x08020000`,
behind the H743 bootloader:

```powershell
pio run -e weact_mini_h743vitx_dronecan_phaseb_app_usb -t upload
```

This is the board-only USB-C update path for an unlocked WeAct H743. Production
H743 DroneCAN boards can use the signed H743 bootloader layout instead:
bootloader at `0x08000000`, app at `0x08020000`, metadata at `0x081E0000`.
The desktop app can also update already activated H743 boards over USB-C ROM
DFU. Readable/unlocked boards get app+metadata updates only. RDP1-protected
boards require UID-short confirmation, then the app removes RDP over USB DFU,
power-cycles back into ROM DFU with `BOOT0` held, mass-erases, rewrites
app + metadata + bootloader, and restores H743 RDP Level 1.

For licensed H743 DroneCAN provisioning over ST-Link/SWD:

```powershell
python tools/gnss_provision.py activate --target h743_dronecan --license GF-XXXX-XXXX-XXXX --server https://gps.airdroper.org
```

Or use **AirDroper GNSS Filter** app version `2026.06.23.10` or newer:
select **Board target -> H743 WeAct DroneCAN**. For ST-Link activation/update,
set **Update transport -> ST-Link (SWD)**, connect ST-Link V2
`SWDIO -> PA13` and `SWCLK -> PA14`, then click **Activate** or **Update**.
For an already activated H743, set **Update transport -> USB-C ROM DFU**,
enter ROM DFU with `BOOT0` + reset/power-cycle over USB-C, then click
**Update**. If the board is protected, keep `BOOT0` held during the required
power-cycle prompt so it returns to ROM DFU after RDP removal.

## 4) CAN node mode (UCAN serial transport)

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

## 5) Filter control expectations

- Filter IDs: `SYSID=42`, `COMPID=191`.
- DR1 protection normally blocks live forwarding from GNSS input to FC GPS UART. The FC receives silence during DR1 unless the diagnostic raw-forward override is enabled.
- In H743 DroneCAN mode, DR1 protection suppresses DroneCAN `Fix2/Auxiliary`
  instead of silencing a GPS UART. `NodeStatus` remains online and reports
  warning health during the DR1 latch. Ordinary no-fix, boot guard, or GNSS
  reconfiguration output suppression keeps DroneCAN node health `OK`.
- In H743 DroneCAN mode, the onboard display shows standard DroneCAN node mode
  and ArduPilot `NotifyState` vehicle-state bits. It still does not show exact
  flight-mode names such as Loiter or Auto; those require a later custom
  DroneCAN message or MAVLink tunnel.
- H743 DroneCAN `v0.1.4+` params are changed from Mission Planner:
  `SETUP -> Optional Hardware -> DroneCAN/UAVCAN -> node 42 -> Params`, then
  `Write Params` and `Commit Params`.
- H743 DroneCAN `v0.1.5+` can also be tuned directly over USB-C: boot the
  normal app with `BOOT0` released, connect Mission Planner to the H743 COM
  port at `115200`, then use `CONFIG -> Full Parameter Tree/List`.
- UART-build filter params are changed in Mission Planner:
  - `Config/Tuning` -> `Full Parameter List`
  - select STM32 (`SYSID=42`)
  - `Refresh Params` -> edit value -> `Write Params`
- Before tuning UART builds, install [AirDroper Mission Planner Params](https://gps.airdroper.org/download/mission-planner-mod) so Mission Planner shows STM32 parameter descriptions, ranges, units, and option labels instead of raw names only.
- Reboot is not required after every parameter write.
- On a busy MAVLink link, `Write Params` may need 1-2 attempts. More than 2 attempts indicates high telemetry load.

Receiver mode selection on STM32:

- `GNSS_TYPE=0`: u-blox/UBX mode.
- `GNSS_TYPE=1`: UM980/UM981/UM982 NMEA mode.
- `GNSS_TYPE=2`: Septentrio Mosaic X5 NMEA mode.
- `GNSS_TYPE` changes require reboot to apply.
- For u-blox only, `UBX_BAUD` controls autoconfig/manual baud:
  - `UBX_BAUD=0`: autoconfig enabled (default).
  - `UBX_BAUD>0`: autoconfig disabled; filter uses this baud directly.
  - `UBX_BAUD` changes also require reboot to apply.
  - Gateway modules with their own MCU and dual/internal receivers (for example Quadro GPS, UNA3, UNA4-SFE, or similar dual-F9P products) must use `UBX_BAUD>0`; filter autobaud is not possible for that class of module.
- For UM980/UM981/UM982 and Mosaic X5 deployments, configure the receiver stream to match the FC GPS protocol and baud you intend to forward through STM32.

## 6) First boot checks

In GCS messages, confirm:

- filter boot message is present,
- GNSS counters increase,
- no repeated communication faults.

If FC shows **No GPS config data**:

- verify FC GPS UART protocol/baud,
- verify `A11/A12` TX/RX cross wiring,
- verify common ground.

For H743 DroneCAN mode, confirm the node appears in DroneCAN/SLCAN tooling with
node ID `42`, then confirm ArduPilot reports a DroneCAN GPS instance.

## 7) Required commissioning step (before flight tuning)

Before normal operation, validate FC GPS path end-to-end once:

1. Connect to filter (`SYSID=42`) and set `FCGPS_FWD=1`.
2. Wait for healthy GNSS in logs (`fix` and `nav` stay low, satellites are present, no repeated no-fix condition).
3. Confirm FC receives GNSS data. This raw-forward mode forces the FC GPS UART on and bypasses DR1, the boot north gate, and the hemisphere fence, so it can validate the UART path even under spoofed/south bench conditions.
4. Set `FCGPS_FWD=0` for operational anti-spoof mode.

`FCGPS_FWD=1` is diagnostic only. Do not fly with it enabled.

This commissioning step does not apply to H743 DroneCAN mode because that
firmware has no raw GPS UART bypass.

## 8) Build-state note

Normal operation uses the normal board firmware already installed by the supplier or service process.
