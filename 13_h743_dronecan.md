# WeAct H743 DroneCAN Guide

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

This page is the complete H743-specific setup path for the WeAct Studio
MiniSTM32H743VITX board with a 3.3 V CAN transceiver such as the SN65HVD230.
Use it when you want the filter to publish GPS to ArduPilot over DroneCAN
instead of using two flight-controller serial ports.

## 1) Supported H743 firmware families

| Firmware environment | Purpose | Upload path |
|----------------------|---------|-------------|
| `weact_mini_h743vitx` | Standalone H743 UART development build | ST-Link |
| `weact_mini_h743vitx_usb` | Same standalone UART build | USB-C ROM DFU |
| `weact_mini_h743vitx_dronecan` | H743 DroneCAN GPS build | ST-Link |
| `weact_mini_h743vitx_dronecan_usb` | Same DroneCAN GPS build | USB-C ROM DFU |
| `weact_mini_h743vitx_dronecan_bootloader` | H743 DroneCAN secure bootloader | ST-Link |
| `weact_mini_h743vitx_dronecan_phaseb_app` | Signed H743 DroneCAN app at `0x08020000` | ST-Link |
| `weact_mini_h743vitx_dronecan_phaseb_app_usb` | Signed H743 DroneCAN app at `0x08020000` | USB-C ROM DFU |

The recommended H743 v1 flight configuration is the DroneCAN family:

- GNSS input on `PA2/PA3`
- CAN to the flight controller on `PB8/PB9` through a CAN transceiver
- USB-C kept on `PA11/PA12` for ROM DFU and bench/debug USB
- no FC MAVLink serial port
- no FC GPS serial port
- tune parameters edited through Mission Planner DroneCAN/UAVCAN node `42`
  Params on firmware `v0.1.4+`, or by connecting Mission Planner directly to
  the H743 USB-C COM port on firmware `v0.1.5+`

The standalone H743 UART build exists for development and compatibility work.
It uses the same idea as the F401 UART build, but its FC GPS UART is `PC6/PC7`
so `PA11/PA12` remain available for USB-C.

## 2) Required hardware

| Item | Notes |
|------|-------|
| WeAct Studio MiniSTM32H743VITX | STM32H743VIT6 board |
| GNSS receiver | u-blox, UM980/UM981/UM982, or Septentrio Mosaic X5 |
| 3.3 V CAN transceiver module | SN65HVD230 is the documented baseline |
| CAN cable to flight controller | CANH, CANL, and GND |
| USB-C cable | For H743 ROM DFU flashing and bench power/debug |
| ST-Link V2 | Optional for development and required for locked production provisioning |

The CAN transceiver is mandatory. The H743 `FDCAN1` pins are logic-level TX/RX
signals; they cannot be connected directly to a flight-controller CAN port.

Use the transceiver module's 120 ohm termination only when the H743 node is at
a physical end of the CAN bus. If the H743 is in the middle of the bus, leave
that termination disabled.

## 3) DroneCAN wiring

| Link | WeAct H743 pin | Module / FC pin | Notes |
|------|----------------|-----------------|-------|
| GNSS TX to STM32 RX | `PA3` | GNSS TX | Cross TX to RX |
| STM32 TX to GNSS RX | `PA2` | GNSS RX | Cross TX to RX |
| CAN TX | `PB9` | Transceiver `TXD` | FDCAN1_TX |
| CAN RX | `PB8` | Transceiver `RXD` | FDCAN1_RX |
| CAN power | `3V3` | Transceiver `VCC` | Use a 3.3 V module |
| Ground | `GND` | Transceiver `GND` and FC CAN GND | Common ground required |
| CAN bus high | Transceiver `CANH` | FC CANH | Twisted pair recommended |
| CAN bus low | Transceiver `CANL` | FC CANL | Twisted pair recommended |
| DR1 event output | `PB5` | Optional LED/logger input | 3 second pulse on DR0 -> DR1 |
| USB-C | `PA11/PA12` internally | USB-C connector | Do not wire these pins externally |

The WeAct onboard ST7735 display is used by the DroneCAN build. The firmware
uses `PE12` SCK, `PE14` MOSI, `PE11` CS, `PE13` DC, `PF0` reset, and `PE10`
backlight. Those display pins do not overlap USB-C, CAN, GNSS, LED, or DR1
event wiring. Compile-time checks enforce the pin contract.

### Optional HD-15 D-sub box connector

If the H743 board, SN65HVD230 CAN transceiver, display, power protection, and
USB-C port are all inside one enclosure, use this as the user-facing 15-pin
"VGA" style connector on the box. The connector exposes only external harness
signals: flight-controller CAN, box power, GNSS UART/power, and optional DR1
status. Raw H743 `PB8/PB9` FDCAN logic stays inside the box between the MCU and
CAN transceiver.

Use a high-density DE-15/HD-15 connector only as a rugged custom harness
connector. It is not a VGA interface. Label it `CAN/GNSS/POWER` and never plug
it into a monitor, PC, or normal VGA cable.

Use this numbering from the mating face of the female panel connector, wide
side up. The solder-cup side is mirrored, so verify the tiny molded pin numbers
on the connector before crimping or soldering.

```text
Female panel connector, mating face

   1   2   3   4   5
    6   7   8   9  10
  11  12  13  14  15
```

Recommended box pinout:

| HD-15 pin | Box connector signal | User connects to | Inside the box | Notes |
|-----------|----------------------|------------------|----------------|-------|
| 1 | `CANH` | Flight controller CANH | SN65HVD230 `CANH` | Twist with pin 2 |
| 2 | `CANL` | Flight controller CANL | SN65HVD230 `CANL` | Twist with pin 1 |
| 3 | `CAN_GND` | Flight controller CAN GND | Box ground | CAN reference ground |
| 4 | `BOX_5V_IN_A` | FC/BEC 5 V output | Box 5 V input | Main power input |
| 5 | `BOX_5V_IN_B` | FC/BEC 5 V output, optional parallel | Same net as pin 4 | Use for lower voltage drop/current sharing |
| 6 | `BOX_GND_A` | FC/BEC ground | Box ground | Main power return |
| 7 | `GNSS_TX_TO_BOX` | GNSS TX | H743 `PA3` RX | Receiver output into filter |
| 8 | `GNSS_RX_FROM_BOX` | GNSS RX | H743 `PA2` TX | Filter output to receiver |
| 9 | `GNSS_VOUT_FUSED` | GNSS VCC/VIN | Fused or switched receiver power output | Output from box, not input |
| 10 | `GNSS_GND` | GNSS GND | Box ground | GNSS power/UART return |
| 11 | `SHIELD` | Cable shield/drain | Shell/chassis or single-point ground | Do not use as current return |
| 12 | `DR1_EVENT` | Optional LED/logger/status input | H743 `PB5` through protection/series resistor | 3.3 V logic pulse, optional |
| 13 | `NC` | No connect | No connect | Reserved for future PPS/time input |
| 14 | `NC` | No connect | No connect | Reserved |
| 15 | `BOX_GND_B` | FC/BEC ground, optional parallel | Box ground | Use with pin 5 for current sharing |

Build rules for this connector:

- Put the CAN transceiver inside the H743 box. The HD-15 connector carries
  only `CANH/CANL/GND` to the flight controller, not raw `PB8/PB9`.
- Keep `CANH/CANL` as a twisted pair all the way to the FC CAN port.
- Power the box from pins 4/6 at minimum. If the receiver or screen current is
  high, also wire pins 5/15 in parallel. Do not rely on CAN ground alone for
  box power return.
- `GNSS_VOUT_FUSED` on pin 9 is an output from the box to the receiver. It
  should come from a fuse, current limiter, or protected switch inside the box.
  Do not back-power the box through pin 9 unless you intentionally design that
  path.
- `GNSS_VOUT_FUSED` must match the receiver. Many GNSS modules accept 5 V on a
  `VCC`/`VIN` pin but use 3.3 V UART logic; raw receivers may require 3.3 V.
  Do not feed 5 V into a raw 3.3 V receiver. Label the selected voltage on the
  enclosure.
- Keep GNSS UART wires separate from the CAN twisted pair. For long runs, use
  a shielded or twisted GNSS cable and keep the 460800 baud noise margin in
  mind.
- All grounds are common inside the box, but keep CAN, box-power, and GNSS
  return conductors separated in the harness until they reach the connector.
- Do not power the H743 through USB-C and the HD-15 `BOX_5V_IN` pins at the
  same time unless the box has proper power ORing/back-feed protection.
- Use 120 ohm CAN termination only when this H743 node is at a physical end of
  the CAN bus. The connector pinout itself does not add termination.

## 4) USB-C flashing

For the unlocked development DroneCAN build:

```powershell
pio run -e weact_mini_h743vitx_dronecan_usb -t upload
```

For the signed secure app build behind the H743 bootloader:

```powershell
pio run -e weact_mini_h743vitx_dronecan_phaseb_app_usb -t upload
```

The secure-app USB environment writes the app slot at `0x08020000`. Use it
only when the H743 bootloader is already installed or when you intentionally
want an app image linked for that address.

To enter STM32 ROM DFU:

1. Hold `BOOT0`.
2. Press reset or power-cycle the WeAct H743.
3. Connect USB-C to the computer.
4. Release `BOOT0` after the board enumerates in DFU mode.

The Windows **AirDroper GNSS Filter** app version `2026.06.23.10` or newer can
update an already activated H743 over USB-C ROM DFU:

1. Set **Board target** to **H743 WeAct DroneCAN**.
2. Set **Update transport** to **USB-C ROM DFU**.
3. Enter the license key.
4. Put the H743 into ROM DFU with `BOOT0` + reset/power-cycle.
5. Click **Update**.

The `.exe` uses two USB-C update paths:

- **Readable/unlocked board:** writes the signed H743 application at
  `0x08020000` and metadata at `0x081E0000`; bootloader and option bytes are
  left unchanged.
- **RDP1-protected production board:** asks the operator to type the expected
  UID-short from the license preflight, removes RDP over USB DFU, requires a
  full power-cycle back into ROM DFU with `BOOT0` held, mass-erases flash,
  writes app + metadata + bootloader, verifies app/metadata readback, then
  restores H743 RDP Level 1.

RDP1 hides the physical UID until after erase, so the protected USB-C path is
intentionally operator-confirmed. If the typed UID-short is wrong or the dialog
is cancelled, the app stops before RDP removal and the board is not changed.

## 5) ST-Link flashing and provisioning

Development ST-Link upload:

```powershell
pio run -e weact_mini_h743vitx_dronecan -t upload
```

Windows app provisioning and updates:

1. Connect ST-Link V2 to the WeAct H743 SWD pins:

   | ST-Link V2 | WeAct H743 |
   |------------|------------|
   | `3V3` | `3V3` |
   | `GND` | `GND` |
   | `SWDIO` | `PA13` / `DIO` |
   | `SWCLK` | `PA14` / `CLK` |

2. Open **AirDroper GNSS Filter** app version `2026.06.23.10` or newer.
3. Set **Board target** to **H743 WeAct DroneCAN**.
4. Set **Update transport** to **ST-Link (SWD)** when updating through SWD.
5. Enter the license key.
6. Click **Activate** for a new board, or **Update** for an already activated
   H743 DroneCAN board.

The app reads the H743 UID at `0x1FF1E800`, requests `target=h743_dronecan`
from the server, flashes app `0x08020000`, metadata `0x081E0000`,
bootloader `0x08000000`, and then applies H743 RDP Level 1 with `RDP=0xBB`.
Version `2026.06.23.10+` writes the H743 application and metadata as separate
flash operations. If CubeProgrammer already erased the board and a repeated
mass erase fails, the app checks blank bootloader/app/metadata sentinels and
continues with write + verify when those slots are already blank.
The app's **Recover Board** button is target-aware. With **Board target** set
to **H743 WeAct DroneCAN**, it uses ST-Link/SWD, removes H743 RDP Level 1 with
the H743 RDP-only path, mass-erases flash, verifies `0x08000000` is blank, and
then tells you to run **Activate** again. Recovery is destructive: it removes
the firmware, license metadata, and saved settings from the connected H743.

If CubeProgrammer reports `DEV_TARGET_HELD_UNDER_RESET`, the H743 reset line is
being held low. Release the board RESET button, remove any suspect ST-Link
`RST/NRST` wire, disconnect the external CAN/GNSS/D-sub harness, power-cycle
the H743, and retry with only `3V3`, `GND`, `SWDIO`, and `SWCLK` connected.
If you do use ST-Link `RST/NRST`, connect it only to the WeAct `NRST/RST` pin.
Do not hold RESET continuously while clicking **Activate**, **Update**, or
**Recover Board**.

If STM32CubeProgrammer GUI connects with **Mode = Normal** and
**Reset mode = Software reset**, use app `2026.06.23.10` or newer. That build
uses the same `mode=NORMAL reset=SWrst` path for H743 before trying
under-reset and hotplug fallbacks.

Close STM32CubeProgrammer GUI before using the AirDroper app. App
`2026.06.23.10+` also checks for running STM32 flashing tools before hardware
access and stops with a clear message if one is still open. If
`STM32_Programmer_CLI.exe` remains after closing the GUI, end it from Windows
Task Manager and retry.

Production-style build:

```powershell
pio run -e weact_mini_h743vitx_dronecan_bootloader
pio run -e weact_mini_h743vitx_dronecan_phaseb_app
```

Target-aware CLI provisioning is still available:

```powershell
python tools/gnss_provision.py activate --target h743_dronecan --license GF-XXXX-XXXX-XXXX --server https://gps.airdroper.org
```

The H743 secure layout is separate from F401:

| Region | Address range | Purpose |
|--------|---------------|---------|
| Bootloader | `0x08000000 - 0x0801FFFF` | Secure bootloader |
| Active app | `0x08020000 - 0x080FFFFF` | Signed H743 DroneCAN firmware |
| Reserved stage | `0x08100000 - 0x081DFFFF` | Reserved for future DroneCAN firmware update |
| Metadata | `0x081E0000 - 0x081FFFFF` | Signed metadata / update state |

Do not flash H743 app or metadata images at F401 addresses.

Firmware update over the standard Mission Planner DroneCAN firmware-update
window is planned but not active in the current H743 firmware. Use the
AirDroper Windows app with **ST-Link (SWD)** or **USB-C ROM DFU** for H743
updates today. When DroneCAN self-update is implemented, already-deployed H743
boards will need one wired update first so the CAN-update-capable bootloader is
installed.

## 6) Flight controller setup

Configure the ArduPilot CAN port connected to the H743 transceiver:

| Parameter | CAN1 example | CAN2 example |
|-----------|--------------|--------------|
| CAN driver enable | `CAN_P1_DRIVER = 1` | `CAN_P2_DRIVER = 1` |
| DroneCAN protocol | `CAN_D1_PROTOCOL = 1` | `CAN_D2_PROTOCOL = 1` |
| CAN bitrate | `CAN_P1_BITRATE = 1000000` | `CAN_P2_BITRATE = 1000000` |
| GPS type | `GPS1_TYPE = 9` | `GPS2_TYPE = 9` if using GPS2 |
| GPS auto-config | `GPS_AUTO_CONFIG = 1` | Same global parameter |
| Optional GPS node lock | `GPS1_CAN_OVRIDE = 42` | `GPS2_CAN_OVRIDE = 42` if using GPS2 |

Reboot the flight controller after changing CAN driver parameters.

The H743 firmware uses static DroneCAN node ID `42` and CAN bitrate `1 Mbps`.
It publishes native DroneCAN GPS messages:

- `uavcan.protocol.NodeStatus`
- `uavcan.protocol.GetNodeInfo` response
- `uavcan.equipment.gnss.Fix2`
- `uavcan.equipment.gnss.Auxiliary`

It does not tunnel raw NMEA, UBX, or MAVLink over CAN in v1.

Because the FC receives native DroneCAN GPS, H743 DroneCAN is not byte-for-byte
GPS packet pass-through. The firmware parses the receiver stream and publishes
the same live fix values in DroneCAN units. It does not generate synthetic GPS
coordinates, blend coordinates, or rewrite raw NMEA/UBX packets; in DR1 it
suppresses `Fix2/Auxiliary` instead of sending altered GPS data.

`GPS_AUTO_CONFIG=1` is ArduPilot's default serial-only GPS auto-config mode and
is the safest setting for this filter. H743 DroneCAN firmware `v0.1.2` and
newer responds to ArduPilot's optional DroneCAN `param.GetSet` queries for
`GPS_TYPE`/`GPS1_TYPE`, so `GPS_AUTO_CONFIG=2` will not block GPS data.

If the CAN bus has more than one DroneCAN GPS-like node, set the matching
`GPSx_CAN_OVRIDE` parameter to `42` so ArduPilot binds that GPS instance to the
filter's static node ID. On a single-GPS bus this is optional.

## 7) Mission Planner Params

H743 DroneCAN firmware `v0.1.4` and newer exposes the spoofing/tuning
parameters through the DroneCAN parameter service. H743 DroneCAN firmware
`v0.1.5` and newer also exposes the same parameters over the H743 USB-C COM
port as a direct MAVLink management link.

The normal Mission Planner full parameter tree connected to the flight
controller will not show these board parameters because the H743 DroneCAN
variant has no FC MAVLink serial link.

### Option A: DroneCAN through the flight controller

Use this while the board is on the aircraft CAN bus:

1. Open Mission Planner.
2. Go to **SETUP -> Optional Hardware -> DroneCAN/UAVCAN**.
3. Select the active CAN driver, usually `MAVLinkCAN1`, and press **Connect**.
4. Wait for node `42` named `org.airdroper.gnss_filter.h743_dronecan`.
5. Press **Menu** on node `42`, then open **Parameters**.
6. Edit the tune row, press **Write Params**, then press **Commit Params**.
7. Reboot the H743 and re-open node `42` Params if you want to confirm the
   value persisted.

### Option B: Direct USB-C to the H743

Use this on the bench when you want the familiar Mission Planner MAVLink
parameter screen without using any flight-controller serial port:

1. Power the H743 normally, not in `BOOT0` ROM DFU mode.
2. Connect the H743 USB-C port to the computer.
3. In Mission Planner, select the new H743 COM port and `115200` baud.
4. Click **Connect**. Mission Planner should see system ID `42`.
5. Open **CONFIG -> Full Parameter Tree** or **Full Parameter List**.
6. Edit the spoofing/tuning values and click **Write Params**.
7. Wait a few seconds for the firmware to save, then reboot/reconnect and
   verify the value if needed.

This USB-C mode is a normal application management port. It is separate from
USB-C ROM DFU flashing: hold `BOOT0` only when updating firmware, and leave
`BOOT0` released when editing parameters.

In the DroneCAN node Params window, the first two rows, `GPS_TYPE` and
`GPS1_TYPE`, are compatibility rows for ArduPilot and are locked to `9`
(`DroneCAN GPS`). Spoofing/tuning rows start after those rows. In the direct
USB-C MAVLink parameter screen, the list starts directly with the
spoofing/tuning rows. The tune names match the F401 firmware, such as
`BOOT_NSATS`, `BOOT_NHDOP`, `RJ_BASE_M`, `SP_JMP_MPS`, `SNR_EN`, `FENCE_RAD`,
and `GNSS_TYPE`.

`UBX_RESET` is a one-shot command, not a saved setting:

- set `UBX_RESET=1` for a u-blox hot start
- set `UBX_RESET=2` for a u-blox cold start
- set `UBX_RESET=3` to clear u-blox config and reinitialize

H743 DroneCAN keeps these MAVLink-dependent F401 settings locked off:

- `RJ_REQEKF = 0`
- `FCGPS_UART = 0`
- `FCGPS_FWD = 0`

The firmware still auto-saves changed values after a short debounce, but
Mission Planner's **Commit Params** button is the explicit save path.

## 8) Display behavior

The onboard screen is enabled in the H743 DroneCAN builds. It shows:

- filter state: `FILTER OK`, `FILTER WARN`, or `FILTER NO OK`
- reason row: `WHY RUN`, `WHY GPS`, `WHY CAN ERR`, `WHY BOOTN`, and compact
  DR1 cause labels such as `WHY NOFIX`, `WHY SATS`, `WHY JUMP`, `WHY FENCE`,
  or `WHY TIME`
- FC DroneCAN node health and generic UAVCAN node mode
- ArduPilot arm/safety state when those broadcasts are present
- ArduPilot `NotifyState` vehicle-state bits as compact labels such as
  `STATE FLY`, `STATE FSRAD`, `STATE FSBAT`, `STATE GPSGL`, or `STATE EKF`
- GNSS fix/satellite row
- publish gate row: `PUB ON DR0` or `PUB BLK DR1`
- compact CAN TX/RX counters such as `CAN 125/91` plus error counters such
  as `ERR 0/0`
- firmware version/build, shortened on the secure app as `H743 PHASEB`

On H743 DroneCAN `v0.1.3` and newer, the screen draws a boot/progress page
immediately after display initialization. During the longer receiver
autobaud/config step it should show `GNSS INIT`; after GNSS startup it changes
to `BOOT GUARD` and then the normal status page takes over.

Exact ArduPilot flight-mode names such as Loiter, Auto, Guided, or RTL are
not part of the standard DroneCAN GPS/status messages used by this firmware.
The screen shows DroneCAN node mode plus ArduPilot vehicle-state bits instead.

By default `FILTER_DRONECAN_FC_NODE_ID=0`, so the display identifies the FC
from arm, safety, or NotifyState broadcasts and ignores arbitrary NodeStatus
frames from other DroneCAN peripherals. On a busy multi-node bus, set
`FILTER_DRONECAN_FC_NODE_ID` at build time to lock the display to one FC node.

## 9) DR0 and DR1 behavior on DroneCAN

The spoofing/guard logic is the same GNSS-side protection logic as the UART
firmware, but the output transport is different.

In DR0:

- the firmware publishes DroneCAN `Fix2` on each fresh GNSS update, capped at
  10 Hz
- it publishes `Auxiliary` at 1 Hz
- `NodeStatus` stays online

In spoof/fault DR1:

- `Fix2` and `Auxiliary` are suppressed
- the flight controller stops receiving fresh GPS from this node
- `NodeStatus` continues at 1 Hz with warning health and vendor status bits
- the screen shows `FILTER NO OK`, a compact `WHY` reason, and `PUB BLK DR1`

No-fix, low satellites, boot guard, or GNSS reconfiguration can also suppress
`Fix2/Auxiliary`, including latched no-fix/low-sat DR1 internally, but those
states keep `NodeStatus` health `OK` and report the output block only through
vendor status bits and the onboard screen. This avoids ArduPilot
`PreArm: DroneCAN: Node 42 unhealthy!` while the GPS is simply not ready yet.

H743 DroneCAN v1 disables flight-controller-serial MAVLink behavior:

- no FC serial Mission Planner parameter path; use node `42` DroneCAN Params
  or direct H743 USB-C MAVLink params instead
- no EKF-status trip
- no barometer altitude comparison
- no FC serial MAVLink `STATUSTEXT` or `NAMED_VALUE` logging from the filter
- no `FCGPS_FWD` raw UART bypass

GNSS-only guards remain active: no-fix, low satellites, position jumps,
altitude rate/jump, SNR, hemisphere, geofence, heading reversal, GPS time
sanity, velocity-position consistency, and receiver clock jump when available.

## 10) Bring-up checklist

1. Flash `weact_mini_h743vitx_dronecan_usb` or `weact_mini_h743vitx_dronecan`.
2. Wire GNSS to `PA2/PA3`.
3. Wire `PB9/PB8` through the CAN transceiver to the FC CAN port.
4. Configure ArduPilot CAN driver, DroneCAN protocol, 1 Mbps bitrate, and
   `GPS1_TYPE=9`.
5. Reboot the flight controller.
6. Confirm the H743 screen lights and shows `GNSS FILTER`.
7. Confirm the DroneCAN node appears as node ID `42` in DroneCAN/SLCAN tooling.
8. Confirm ArduPilot reports a DroneCAN GPS instance.
9. Trigger a bench DR1 condition and confirm `Fix2/Auxiliary` stop while
   `NodeStatus` stays online.
10. Clear the condition and confirm GPS publishing resumes after rejoin.

## 11) Troubleshooting

### Node does not appear on DroneCAN

- Confirm CAN is enabled on the correct FC CAN port.
- Confirm `CAN_Dx_PROTOCOL = 1` and bitrate is `1000000`.
- Confirm `PB9 -> TXD` and `PB8 <- RXD`.
- Confirm transceiver `VCC` is 3.3 V and all grounds are common.
- Confirm CANH/CANL are not swapped.
- Confirm termination exists at both physical ends of the bus and not in the
  middle.

### Node appears but FC does not get GPS

- Confirm `GPS1_TYPE=9` or the matching GPS instance type is set to DroneCAN.
- Confirm `GPS_AUTO_CONFIG=1` on firmware older than H743 DroneCAN `v0.1.2`.
- If there are multiple DroneCAN GPS nodes, set `GPS1_CAN_OVRIDE=42` or the
  matching GPS instance override.
- Confirm the GNSS receiver has a valid fix; the screen should show `GPS FIX`.
- Confirm the screen shows `PUB ON DR0`, not `PUB BLK DR1`.
- Confirm `WHY` is not `GNSSCFG`, `GPS`, `SOUTH`, `FENCE`, `NOFIX`, `SATS`,
  `JUMP`, or another DR1 cause label.

### Screen does not show FC arm or safety state

- Confirm the FC is on the same CAN bus and DroneCAN is running.
- If the bus has many nodes, rebuild with `FILTER_DRONECAN_FC_NODE_ID=<fc id>`.
- Some FC status rows depend on ArduPilot broadcasts. GPS publishing does not
  require those rows to be present.

### Node 42 Params only shows GPS_TYPE/GPS1_TYPE

- Update the H743 DroneCAN firmware to `v0.1.4` or newer.
- Disconnect/reconnect the Mission Planner DroneCAN/UAVCAN page and reopen
  node `42` Params.
- If the value list still looks stale, close and restart Mission Planner.

### USB-C Mission Planner connection does not show params

- Update the H743 DroneCAN firmware to `v0.1.5` or newer.
- Do not hold `BOOT0`; USB-C parameter editing works only in the normal app,
  not in ROM DFU mode.
- Select the H743 USB COM port directly in Mission Planner at `115200`.
- If Mission Planner is already connected to the flight controller telemetry
  link, disconnect that session first, then connect to the H743 USB COM port.

### Screen turns off after boot

- If the board is on H743 DroneCAN firmware `v0.1.0`, the app boots and the
  blue LED blinks every few seconds, but the screen stays black, update to
  H743 DroneCAN `v0.1.1` or newer. `v0.1.1` fixes the WeAct LCD backlight
  polarity (`PE10` is active-low).
- The firmware turns the display backlight off if SPI display writes fail, so
  a bad screen connection cannot keep delaying the flight loop.
- Recheck the onboard display pins, especially `PE12`, `PE14`, `PE11`,
  `PE13`, `PF0`, and `PE10`.
- DroneCAN GPS publishing and guard logic continue without the screen.

### USB-C ROM DFU upload does not start

- Make sure you entered ROM DFU with `BOOT0` held during reset/power-up.
- Try a known data-capable USB-C cable.
- Disconnect ST-Link or other tools that may hold the MCU in reset.
- If the chip is RDP Level 1 locked, raw PlatformIO app-only ROM DFU upload
  cannot update it. Use the desktop app's **USB-C ROM DFU** update path for an
  already activated H743, or use ST-Link/manual recovery when intentionally
  recovering a development board.

## 12) What H743 v1 intentionally does not do

- no full MAVLink replacement over CAN
- no FC-serial F401-style MAVLink parameter tuning path
- no DroneCAN firmware update protocol
- no raw GNSS tunnel over CAN
- no exact ArduPilot flight-mode names on the screen
- no direct connection from H743 FDCAN pins to the flight controller without a
  CAN transceiver

For normal F401 UART operation, use the rest of the user documentation. For
H743 DroneCAN, this page is the source of truth.
