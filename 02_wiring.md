# Wiring Guide (STM32F401 BlackPill / WeAct H743)

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

The UART firmware uses three UART links on supported STM32 boards:

1. GNSS <-> STM32 (receiver parsing)
2. FC MAVLink <-> STM32 (control/status/tuning)
3. FC GPS <-> STM32 (raw GNSS forwarding to FC GPS UART)

The separate H743 DroneCAN firmware uses GNSS UART input plus one CAN
transceiver instead of the two flight-controller serial links.

For a complete H743 bring-up sequence, including USB-C ROM DFU flashing,
ArduPilot CAN parameters, screen behavior, and validation, see the
[H743 DroneCAN Guide](13_h743_dronecan.md).

Video tutorial: [General Wiring Overview](12_video_tutorials.md#wiring).

BlackPill silk labels are `A2`, `A3`, `A9`, `A10`, `A11`, `A12`, `B5`.
WeAct H743 standalone builds use `A2`, `A3`, `A9`, `A10`, `C6`, `C7`, `B5`.
On WeAct H743, leave `A11/A12` unused by external wiring because they belong
to the board USB-C connector.

## RX/TX rule (read first)

Always cross UART lines:

- `TX -> RX`
- `RX -> TX`

Never wire `TX -> TX` or `RX -> RX`.

## STM32F401 pin map (from STM32 point of view)

Use this rule only:
- If STM32 pin is **RX**, connect it to external **TX**.
- If STM32 pin is **TX**, connect it to external **RX**.

| STM32 pin | STM32 direction | Connect this pin to |
|---|---|---|
| `A3` | **RX** (GNSS UART in) | GNSS module **TX** |
| `A2` | **TX** (GNSS UART out) | GNSS module **RX** |
| `A10` | **RX** (FC MAVLink in) | FC telemetry port **TX** |
| `A9` | **TX** (FC MAVLink out) | FC telemetry port **RX** |
| `A12` | **RX** (FC GPS in) | FC GPS port **TX** |
| `A11` | **TX** (FC GPS out) | FC GPS port **RX** |
| `B5` | GPIO output pulse | Optional external logic input |

## WeAct Studio H743 pin map (standalone target)

Use this only with the `weact_mini_h743vitx` or `weact_mini_h743vitx_usb`
firmware build. This standalone UART H743 target is separate from the secure
H743 DroneCAN production build.

| STM32 pin | STM32 direction | Connect this pin to |
|---|---|---|
| `A3` | **RX** (GNSS UART in) | GNSS module **TX** |
| `A2` | **TX** (GNSS UART out) | GNSS module **RX** |
| `A10` | **RX** (FC MAVLink in) | FC telemetry port **TX** |
| `A9` | **TX** (FC MAVLink out) | FC telemetry port **RX** |
| `C7` | **RX** (FC GPS in) | FC GPS port **TX** |
| `C6` | **TX** (FC GPS out) | FC GPS port **RX** |
| `B5` | GPIO output pulse | Optional external logic input |

## WeAct Studio H743 DroneCAN pin map

Use this only with the `weact_mini_h743vitx_dronecan` or
`weact_mini_h743vitx_dronecan_usb` firmware build and a 3.3 V CAN transceiver
module such as SN65HVD230. This build does not use the FC MAVLink UART or FC GPS
UART.

| STM32 / module pin | Direction | Connect this pin to |
|---|---|---|
| STM32 `A3` | **RX** (GNSS UART in) | GNSS module **TX** |
| STM32 `A2` | **TX** (GNSS UART out) | GNSS module **RX** |
| STM32 `PB9` | **FDCAN1_TX** | CAN module `TXD` |
| STM32 `PB8` | **FDCAN1_RX** | CAN module `RXD` |
| STM32 `3V3` | Power | CAN module `VCC` |
| STM32 `GND` | Ground | CAN module `GND` |
| CAN module `CANH` | Bus high | Flight controller CAN `CANH` |
| CAN module `CANL` | Bus low | Flight controller CAN `CANL` |
| CAN module `GND` | Bus ground | Flight controller CAN `GND` |

The WeAct onboard 0.96 inch ST7735 screen is used by the H743 DroneCAN build;
do not wire anything external to its pins. The firmware reserves `PE12`
(SPI4 SCK), `PE14` (SPI4 MOSI), `PE11` (CS), `PE13` (DC), `PF0` (reset), and
`PE10` (backlight). These pins do not intersect with USB-C `PA11/PA12`, CAN
`PB8/PB9`, GNSS `PA2/PA3`, LED `PE3`, or DR1 `PB5`; compile-time checks enforce
that mapping.

Use the module's 120 ohm termination only when the H743 node is at a physical
end of the CAN bus. Leave `A11/A12` unused by external wiring; those pins are
reserved for the H743 USB-C connector and the firmware has compile-time checks
to keep CAN, GNSS, LED, DR1, and the onboard screen off them.

For a single external connector on the H743 DroneCAN box, use the documented
HD-15 D-sub box pinout in the [H743 DroneCAN Guide](13_h743_dronecan.md#optional-hd-15-d-sub-box-connector).
That pinout exposes user-facing FC CAN, box power input, GNSS UART/power, and
optional DR1 status pins; raw H743 `PB8/PB9` stay inside the box between the
MCU and CAN transceiver.

## Wire-by-wire checklist

- [ ] STM32 `A3` (**RX**) -> GNSS `TX`
- [ ] STM32 `A2` (**TX**) -> GNSS `RX`
- [ ] STM32 `A10` (**RX**) -> FC MAV `TX`
- [ ] STM32 `A9` (**TX**) -> FC MAV `RX`
- [ ] STM32 FC GPS **RX** -> FC GPS `TX` (`A12` on F401, `C7` on H743)
- [ ] STM32 FC GPS **TX** -> FC GPS `RX` (`A11` on F401, `C6` on H743)
- [ ] STM32 `GND` -> GNSS `GND`
- [ ] STM32 `GND` -> FC `GND`

For H743 DroneCAN firmware, replace the FC MAVLink and FC GPS serial wiring
above with:

- [ ] STM32 `PB9` -> CAN transceiver `TXD`
- [ ] STM32 `PB8` -> CAN transceiver `RXD`
- [ ] STM32 `3V3` -> CAN transceiver `VCC`
- [ ] STM32 `GND` -> CAN transceiver `GND`
- [ ] CAN transceiver `CANH/CANL/GND` -> flight controller CAN port

## Common wiring mistakes

- Wrong: GNSS `TX -> A2` (TX to TX). Correct: GNSS `TX -> A3`.
- Wrong: FC MAV `TX -> A9` (TX to TX). Correct: FC MAV `TX -> A10`.
- Wrong on F401: FC GPS `TX -> A11` (TX to TX). Correct: FC GPS `TX -> A12`.
- Wrong on H743: FC GPS `TX -> C6` (TX to TX). Correct: FC GPS `TX -> C7`.
- Missing shared ground between STM32, GNSS, and FC.

## Diagrams

![Wiring diagram](diagrams/GNSS-TX-A3.png)

![Wiring OK example](diagrams/wiring_ok_example.png)

## Board photos (reference)

The recommended board is the WeAct Studio BlackPill STM32F401CC V2.0 (black PCB).

![BlackPill STM32F401CC](diagrams/blackpill_variant_a.jpeg)

If GNSS or MAVLink does not work after wiring, see `03_wiring_debug.md`.

## Important notes

- `A11/A12` are USB D-/D+ pins on BlackPill; in this project they are **permanently repurposed as USART6** for the flight-controller GPS UART. The board has **no functional USB path** — the bootloader does not enumerate as a USB device and the application disables USB OTG_FS at every boot.
- **DO NOT plug any cable into the BlackPill's USB-C connector at any time.** Even just connecting a USB power cable applies host signaling to D-/D+ — the same physical wires as `A11/A12` — and that fights the USART6 line driver. The flight controller will report "GPS: No GPS" and EKF3 will refuse to align even though the filter logs show a healthy fix being forwarded. Power must come from the FC GPS-port +5V/+3V3 pin, or from the SWD header during initial flashing — never from a USB cable.
- On WeAct H743, USB-C is allowed. The H743 firmware reserves `A11/A12` for USB OTG FS CDC/DFU and does not assign them to GNSS, MAVLink, FC GPS, LED, or DR1 event output.
- On WeAct H743 DroneCAN firmware, USB-C is allowed and remains on `A11/A12`; CAN uses only `PB8/PB9`.
- On WeAct H743, the FC GPS UART uses `C6/C7`; those pins are also routed to the board's DCMI camera connector, so do not use the camera connector at the same time.
- To release the FC GPS UART pins (e.g. for diagnostics), set `FCGPS_UART=0` in Mission Planner. That disables the FC GPS UART and puts the board-specific pins into input mode. Set `FCGPS_UART=1` to restore normal FC GPS UART operation. `FCGPS_FWD=1` overrides this and forces the FC GPS UART on for bench validation.
- Runtime GNSS TX/RX swap is not supported in these firmware builds; fix wiring physically if reversed.
- Receiver protocol mode is selected by `GNSS_TYPE`:
  - `0`: u-blox/UBX
  - `1`: UM980/UM981/UM982 NMEA
  - `2`: Septentrio Mosaic X5 NMEA
- For `GNSS_TYPE=1` or `GNSS_TYPE=2`, the filter expects one physical receiver link only:
  - receiver serial output (`COM1`, `COM2`, or selected Mosaic stream) -> STM32 `A2/A3`
  - the STM32 reads spoofing/SNR data from that same stream
  - the STM32 forwards that same stream to the FC GPS UART (`A11/A12` on F401, `C6/C7` on H743)
- u-blox autoconfig behavior is controlled by `UBX_BAUD`:
  - `UBX_BAUD=0`: autoconfig enabled (default)
  - `UBX_BAUD>0`: autoconfig disabled, manual baud is used (reboot required)
- Power rails must follow your hardware design. Do not power GNSS/FC from UART pins.

## DR1 event pulse (`B5`)

- On each DR0 -> DR1 transition, firmware drives `B5` high for 3 seconds, then low.
- Verify polarity with your external circuit during first power-up.
