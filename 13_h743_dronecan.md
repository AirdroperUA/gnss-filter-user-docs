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
- compile-time defaults instead of Mission Planner MAVLink parameters

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

The Windows **AirDroper GNSS Filter** app version `2026.06.23.5` or newer can
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

2. Open **AirDroper GNSS Filter** app version `2026.06.23.5` or newer.
3. Set **Board target** to **H743 WeAct DroneCAN**.
4. Set **Update transport** to **ST-Link (SWD)** when updating through SWD.
5. Enter the license key.
6. Click **Activate** for a new board, or **Update** for an already activated
   H743 DroneCAN board.

The app reads the H743 UID at `0x1FF1E800`, requests `target=h743_dronecan`
from the server, flashes app `0x08020000`, metadata `0x081E0000`,
bootloader `0x08000000`, and then applies H743 RDP Level 1 with `RDP=0xBB`.
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

| Region | Address |
|--------|---------|
| Bootloader | `0x08000000` |
| App | `0x08020000` |
| Metadata | `0x081E0000` |

Do not flash H743 app or metadata images at F401 addresses.

## 6) Flight controller setup

Configure the ArduPilot CAN port connected to the H743 transceiver:

| Parameter | CAN1 example | CAN2 example |
|-----------|--------------|--------------|
| CAN driver enable | `CAN_P1_DRIVER = 1` | `CAN_P2_DRIVER = 1` |
| DroneCAN protocol | `CAN_D1_PROTOCOL = 1` | `CAN_D2_PROTOCOL = 1` |
| CAN bitrate | `CAN_P1_BITRATE = 1000000` | `CAN_P2_BITRATE = 1000000` |
| GPS type | `GPS1_TYPE = 9` | `GPS2_TYPE = 9` if using GPS2 |

Reboot the flight controller after changing CAN driver parameters.

The H743 firmware uses static DroneCAN node ID `42` and CAN bitrate `1 Mbps`.
It publishes native DroneCAN GPS messages:

- `uavcan.protocol.NodeStatus`
- `uavcan.protocol.GetNodeInfo` response
- `uavcan.equipment.gnss.Fix2`
- `uavcan.equipment.gnss.Auxiliary`

It does not tunnel raw NMEA, UBX, or MAVLink over CAN in v1.

## 7) Display behavior

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

Exact ArduPilot flight-mode names such as Loiter, Auto, Guided, or RTL are
not part of the standard DroneCAN GPS/status messages used by this firmware.
The screen shows DroneCAN node mode plus ArduPilot vehicle-state bits instead.

By default `FILTER_DRONECAN_FC_NODE_ID=0`, so the display identifies the FC
from arm, safety, or NotifyState broadcasts and ignores arbitrary NodeStatus
frames from other DroneCAN peripherals. On a busy multi-node bus, set
`FILTER_DRONECAN_FC_NODE_ID` at build time to lock the display to one FC node.

## 8) DR0 and DR1 behavior on DroneCAN

The spoofing/guard logic is the same GNSS-side protection logic as the UART
firmware, but the output transport is different.

In DR0:

- the firmware publishes DroneCAN `Fix2` on each fresh GNSS update, capped at
  10 Hz
- it publishes `Auxiliary` at 1 Hz
- `NodeStatus` stays online

In DR1 or any blocked state:

- `Fix2` and `Auxiliary` are suppressed
- the flight controller stops receiving fresh GPS from this node
- `NodeStatus` continues at 1 Hz with warning health and vendor status bits
- the screen shows `FILTER NO OK`, a compact `WHY` reason, and `PUB BLK DR1`

H743 DroneCAN v1 disables MAVLink-dependent behavior:

- no Mission Planner MAVLink parameters
- no EKF-status trip
- no barometer altitude comparison
- no MAVLink `STATUSTEXT` or `NAMED_VALUE` logging from the filter
- no `FCGPS_FWD` raw UART bypass

GNSS-only guards remain active: no-fix, low satellites, position jumps,
altitude rate/jump, SNR, hemisphere, geofence, heading reversal, GPS time
sanity, velocity-position consistency, and receiver clock jump when available.

## 9) Bring-up checklist

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

## 10) Troubleshooting

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
- Confirm the GNSS receiver has a valid fix; the screen should show `GPS FIX`.
- Confirm the screen shows `PUB ON DR0`, not `PUB BLK DR1`.
- Confirm `WHY` is not `GNSSCFG`, `GPS`, `SOUTH`, `FENCE`, `NOFIX`, `SATS`,
  `JUMP`, or another DR1 cause label.

### Screen does not show FC arm or safety state

- Confirm the FC is on the same CAN bus and DroneCAN is running.
- If the bus has many nodes, rebuild with `FILTER_DRONECAN_FC_NODE_ID=<fc id>`.
- Some FC status rows depend on ArduPilot broadcasts. GPS publishing does not
  require those rows to be present.

### Screen turns off after boot

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

## 11) What H743 v1 intentionally does not do

- no full MAVLink replacement over CAN
- no runtime tuning over DroneCAN
- no DroneCAN firmware update protocol
- no raw GNSS tunnel over CAN
- no exact ArduPilot flight-mode names on the screen
- no direct connection from H743 FDCAN pins to the flight controller without a
  CAN transceiver

For normal F401 UART operation, use the rest of the user documentation. For
H743 DroneCAN, this page is the source of truth.
