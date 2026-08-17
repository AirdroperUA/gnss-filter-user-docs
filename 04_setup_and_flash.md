# Setup Manual

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

> **Provisioning identity gate:** before Activate, Update, or Recover can read
> UID/option bytes or erase/write flash, inspect the physical PCB and MCU
> marking. Enter `F401CC BLACKPILL` for the 256 KiB BlackPill target or
> `WEACT H743VI` for the 2 MiB WeAct target exactly as prompted. The tool asks
> again after every physical reconnect or SWD/DFU transport change, and
> `--yes` cannot bypass this check. An explicit 128 KiB F401 or 1 MiB H743
> identity is rejected because the production layout does not fit.

## 1) Prerequisites

- STM32F401 filter board is installed and preflashed, or a WeAct H743 board is
  flashed with the matching standalone/H743 DroneCAN development firmware.
- The board should be running the firmware family that matches the wiring mode.
- FC firmware is ArduPilot 4.6.1 or later and must answer the filter's
  `AUTOPILOT_VERSION` request. Firmware v0.5.30 suppresses GNSS immediately
  while that identity is unknown or unsupported.
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
For `GNSS_TYPE=1` or UART-build `GNSS_TYPE=2`, the STM32 expects one physical NMEA receiver stream only:

- UM980 `COM1` -> STM32 `A2/A3`
- STM32 parses spoofing/SNR from that stream
- STM32 forwards that same stream to the FC GPS UART (`A11/A12` on F401,
  `C6/C7` on H743 UART builds)

## 3) H743 DroneCAN GPS mode

Use this section only with the `weact_mini_h743vitx_dronecan` or
`weact_mini_h743vitx_dronecan_usb` firmware. This mode publishes native
DroneCAN GNSS messages and uses two DroneCAN MAVLink2 virtual serial ports. It
does not use physical FC MAVLink or FC GPS UARTs. The complete board-specific
procedure is in the
[H743 DroneCAN Guide](13_h743_dronecan.md).

Firmware defaults:

- DroneCAN node ID: `42`
- FC DroneCAN node filter: `0` (bind only after two valid Targetted transfers
  addressed to this node from the same source; the lease expires after three
  seconds without another valid transfer). Set
  `FILTER_DRONECAN_FC_NODE_ID` at build time if the bus has multiple nodes and
  you want the onboard screen locked to one FC node.
- CAN bitrate: `1 Mbps`
- OpenIPC camera UART: camera TX -> H743 `PA10` RX, H743 `PA9` TX -> camera RX,
  3.3 V logic, common ground, `115200` baud
- Published messages: `uavcan.protocol.NodeStatus`,
  `uavcan.protocol.GetNodeInfo`, `uavcan.equipment.gnss.Fix2`,
  `uavcan.equipment.gnss.Auxiliary`, and `uavcan.tunnel.Targetted`
- Onboard screen: filter OK/warn/no-OK with a `WHY` reason line, GNSS publish
  state, CAN counters, FC DroneCAN node health/mode, arm/safety state, and an
  ArduPilot vehicle-state row from `ardupilot.indication.NotifyState` when that
  broadcast is present

Flight controller parameters for the CAN port used by the H743 node:

- `CAN_P1_DRIVER = 1` for CAN1, or `CAN_P2_DRIVER = 2` for CAN2
- `CAN_D1_PROTOCOL = 1` for CAN1, or `CAN_D2_PROTOCOL = 1` for CAN2
- `CAN_P1_BITRATE = 1000000` or `CAN_P2_BITRATE = 1000000`
- `GPS1_TYPE = 9` for DroneCAN GPS
- `GPS_AUTO_CONFIG = 1` for the default serial-only GPS auto-config mode
- optional: `GPS1_CAN_OVRIDE = 42` if the bus has more than one DroneCAN
  GPS-like node

The `CAN_Px_DRIVER` value selects a virtual driver. These examples deliberately
map physical CAN1 to driver 1 and physical CAN2 to driver 2; use the `CAN_Dn_*`
parameters matching the driver number you assign. Reboot the flight controller
after changing CAN driver parameters. If the H743
node is at a physical end of the CAN bus, enable the CAN module's 120 ohm
termination; otherwise leave it off.

Flash the USB-C ROM DFU build from a development machine:

```powershell
pio run -e weact_mini_h743vitx_dronecan_usb -t upload
```

To enter DFU: hold `BOOT0`, reset or power-cycle the WeAct H743, then connect
USB-C.

The H743 phase-B environment is a **build-only production template** linked at
`0x08020000` behind the secure bootloader:

```powershell
pio run -e weact_mini_h743vitx_dronecan_phaseb_app_usb
```

Direct `-t upload` is intentionally refused for phase-B environments because a
template is not UID-bound and has no matching signed metadata. Use the
AirDroper provisioning app for a licensed ST-Link or USB-C ROM DFU update.
Production H743 DroneCAN boards use the signed H743 bootloader layout:
bootloader at `0x08000000`, app at `0x08020000`, metadata at `0x081E0000`.
Desktop app `2026.08.02.1+` can update already activated H743 boards over USB-C
ROM DFU. It reads the RDP option byte first, then always mass-erases and writes
the complete validated app + metadata + bootloader bundle, even when the board
starts readable at RDP0. RDP1 boards additionally require UID-short confirmation,
verified RDP0 after unlock, and a physical UID re-read before writing. The app
reports success only after a separate option-byte read verifies final RDP1; an
unreadable/unparseable RDP value or failed lock check stops the update.

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

After the first H743 DroneCAN `v0.5.30+` promotion, the update service
permanently refuses to promote or deliver any pre-`v0.5.30` H743 firmware.
Older fuel readers cannot safely preserve the new lost/known fuel provenance,
so this global boundary also applies to owner-authorized rollback. Use a
forward-versioned recovery build instead.

## 4) H743 DroneCAN MAVLink2 virtual ports

Enable DroneCAN serial transport on the flight controller and map two separate
ports to H743 node `42`:

| Function | Node/index | ArduPilot CAN1 parameters |
|----------|------------|----------------------------|
| Enable transport | - | `CAN_D1_UC_SER_EN = 1` |
| OpenIPC camera, bidirectional | node `42`, index `0` | `CAN_D1_UC_S1_NOD = 42`, `CAN_D1_UC_S1_IDX = 0`, `CAN_D1_UC_S1_BD = 115`, `CAN_D1_UC_S1_PRO = 2` |
| H743 filter MAVLink + FC telemetry | node `42`, index `1` | `CAN_D1_UC_S2_NOD = 42`, `CAN_D1_UC_S2_IDX = 1`, `CAN_D1_UC_S2_BD = 115`, `CAN_D1_UC_S2_PRO = 2` |

For virtual CAN driver 2, use the matching `CAN_D2_UC_*` parameters instead.
Both
ports use MAVLink2 at 115200 baud, but their bytes remain separate. Native GPS
continues as DroneCAN `Fix2/Auxiliary`; raw NMEA/UBX/SBF and the FC GPS UART are
not part of either virtual port.

If UART traffic during boot prevents the OpenIPC camera from starting, set
`MAV_TELEM_DELAY = 5` (older ArduPilot versions may use `TELEM_DELAY`). Power
the camera from an appropriate camera/LTE supply; `PA9/PA10` and optional HD-15
pins 13/14 are 3.3 V UART signals, not camera power.

Keep FC MAVLink stream rates modest. A continuous full-duplex 115200 stream is
expensive on classic CAN. A red H743 `MAV` row or nonzero `ERR` row indicates
loss/overload and means stream rates should be reduced; yellow `MAV` means old
queued data expired after a stalled link.

## 5) Filter control expectations

- Filter IDs: `SYSID=42`, `COMPID=191`.
- DR1 protection normally blocks live forwarding from GNSS input to FC GPS UART. The FC receives silence during DR1 unless the diagnostic raw-forward override is enabled.
- In H743 DroneCAN mode, DR1 protection suppresses DroneCAN `Fix2/Auxiliary`
  instead of silencing a GPS UART. `NodeStatus` remains online and reports
  warning health for spoof/fault DR1 reasons or an enabled I2C sensor that is
  missing/stale after its five-second startup grace. Ordinary no-fix, low
  satellites, boot guard, or GNSS reconfiguration output suppression alone
  keeps DroneCAN node health `OK`.
- In H743 DroneCAN mode, the onboard display shows standard DroneCAN node mode
  and ArduPilot `NotifyState` vehicle-state bits. It still does not show exact
  flight-mode names such as Loiter or Auto; the MAVLink tunnel does not change
  the current display UI.
- In H743 DroneCAN mode, the camera tunnel and filter-owned MAVLink remain
  active during DR1. Only GPS `Fix2/Auxiliary` publishing is suppressed.
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
- Before tuning UART builds, install [AirDroper Mission Planner Mod](https://gps.airdroper.org/download/mission-planner-mod) so Mission Planner shows STM32 parameter descriptions, ranges, units, and option labels instead of raw names only.
- Reboot is not required after every parameter write.
- On a busy MAVLink link, `Write Params` may need 1-2 attempts. More than 2 attempts indicates high telemetry load.

Receiver mode selection on STM32:

- `GNSS_TYPE=0`: u-blox/UBX mode.
- `GNSS_TYPE=1`: UM980/UM981/UM982 NMEA mode.
- `GNSS_TYPE=2`: Septentrio Mosaic X5 mode. H743 DroneCAN `v0.1.9+` can use SBF; UART builds use NMEA.
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
node ID `42`, then confirm ArduPilot reports a DroneCAN GPS instance, camera
MAVLink reaches the FC through index `0`, and filter system ID `42` reaches the
FC through index `1`.

## 7) Required commissioning step (before flight tuning)

Before normal operation, validate FC GPS path end-to-end once:

1. Connect to filter (`SYSID=42`) and set `FCGPS_FWD=1`.
2. Wait for healthy GNSS in logs (`fix` and `nav` stay low, satellites are present, no repeated no-fix condition).
3. Confirm FC receives GNSS data. This raw-forward mode forces the FC GPS UART on and bypasses DR1, the boot north gate, and the hemisphere fence, so it can validate the UART path even under spoofed/south bench conditions.
4. Set `FCGPS_FWD=0` for operational anti-spoof mode.

`FCGPS_FWD=1` is diagnostic only. Do not fly with it enabled.

This commissioning step does not apply to H743 DroneCAN mode because that
firmware has no raw GPS UART bypass.

## 8) Bench-testing DR1 recovery (no vehicle, no airspeed)

Leaving DR1 requires at least one **independent witness**: a non-GNSS observation
that actually carried information. All three sources need the airframe to be
doing something:

| Row | Becomes an independent witness when |
|-----|-------------------------------------|
| Barometric vertical rate | a real climb or descent of at least 3 m/s |
| Ground speed vs airspeed | a live pitot reading at or above 12 m/s |
| GNSS course vs FC yaw | the airframe genuinely turns |

A board on a desk supplies none of them, so the **airborne quorum** correctly
refuses to clear on a stationary bench. H743 DroneCAN v0.5.30 has a separate,
strictly parked/disarmed ground-release path for that case. It does not use the
generic three-row pass count. In addition to the existing disarmed, FC-motion,
position-agreement, receiver-verdict, dwell, and budget gates, it requires:

- zero contradicting evidence rows;
- the GNSS-time row positively PASS;
- a fresh, finite, non-negative receiver speed at or below 4 m/s;
- that speed to belong to the current location epoch, with no more than
  1500 ms age/skew. For passive NMEA this is the RMC speed paired with the
  GGA/RMC fix epoch.

Optional evidence such as GSV/SNR may veto the release when it reports FAIL,
but it is not required to exist. The deployed UM980 GGA/RMC/AGRICA profile can
therefore complete a stationary ground release with `SNR=NA`. In the recovery
line, `EVM` means named ground evidence is missing, `EVF` means a contradiction,
and a rising `gnd=` counter means the parked release is progressing. The
`ev...W...` fields continue to describe only the airborne quorum.

To exercise the **airborne** recovery path you still have three options.

**Drive it.** A car with the receiver on the roof and the FC powered gives GNSS
speed above 6 m/s and real course changes, so the course-vs-yaw row supplies the
witness. This is the only option that tests the real code path end to end, and it
is what should be done before a first flight.

**Power-cycle.** Fastest way to get a bench unit back to DR0 without waiting
for the parked dwell. It tests nothing about recovery.

**Build a bench image with the operator waiver compiled in.** The waiver is
`MAV_CMD_USER_1` with `param1 = 20437`, addressed to system 42; it waives *only*
the independent-witness requirement, leaving the pass count, the
zero-contradiction rule and the full hold window in force.

It is compiled **out** of every flight build and is deliberately absent from
`platformio.ini`, so no environment can produce it by accident - `MAV_CMD_USER_1`
has no cryptographic authentication, so any node on the telemetry link could send
it. Build it explicitly and only for the bench:

```powershell
$env:PLATFORMIO_BUILD_FLAGS="-DFILTER_REMOTE_OPERATOR_WAIVER_ENABLE=1"
pio run -e weact_mini_h743vitx_dronecan -t upload
Remove-Item Env:\PLATFORMIO_BUILD_FLAGS
```

The resulting image is about 4 kB larger than the flight build. **Never fly it**,
and reflash a normal build before the aircraft goes anywhere.

If instead you want a guaranteed time-bounded exit from DR1 in flight regardless
of evidence, that is what the `DR1_MAXMS` parameter is for. It ships at 0
(infinite latch) on purpose: a timeout hands the aircraft back to a possibly
still-active spoofer on a clock rather than on evidence, so releasing on a timer
is the less safe failure and staying in dead reckoning is the safer one. Set it
knowingly.

## 9) Build-state note

Normal operation uses the normal board firmware already installed by the supplier or service process.
