# Wiring Guide (STM32F401 BlackPill)

This firmware expects **three UART links** on STM32:

1. GNSS and STM32 (bidirectional receiver link for filter parsing)
2. FC MAVLink and STM32 (bidirectional control/status/tuning)
3. FC GPS and STM32 (bidirectional raw GNSS forwarding to FC GPS UART)

## Pin map (current firmware)

| Function | STM32 Pin | Connect to |
|---|---|---|
| GNSS RX | `A3` | GNSS TX |
| GNSS TX | `A2` | GNSS RX |
| FC MAV RX | `A10` | FC MAV TX (telemetry port) |
| FC MAV TX | `A9` | FC MAV RX (telemetry port) |
| FC GPS RX | `A12` | FC GPS TX (FC GPS UART) |
| FC GPS TX | `A11` | FC GPS RX (FC GPS UART) |
| DR1 event output | `B5` | Optional external logic input |

## Signal direction (TX -> RX)

- GNSS **TX** -> STM32 `A3`.
- GNSS **RX** <- STM32 `A2`.
- FC MAV **TX** -> STM32 `A10`.
- FC MAV **RX** <- STM32 `A9`.
- FC GPS **TX** -> STM32 `A12`.
- FC GPS **RX** <- STM32 `A11`.

## Diagrams

![Wiring diagram](diagrams/GNSS-TX-A3.png)

![Wiring OK example](diagrams/wiring_ok_example.png)

## Board photos (reference)

These are two common BlackPill STM32F401 variants. Pin labels and functions are the same.

![BlackPill variant A](diagrams/blackpill_variant_a.jpeg)

![BlackPill variant B](diagrams/blackpill_variant_b.jpg)

If GNSS or MAVLink does not work after wiring, see `03_wiring_debug.md`.

Also connect:

- `GND` (STM32) to GNSS GND and FC GND (common ground is required).
- Power rails according to your hardware design (do not power GNSS/FC from UART pins).

## Important notes

- UART wiring must be crossed (`TX -> RX`, `RX -> TX`).
- `A11/A12` are USB D-/D+ pins on BlackPill; in this project they are repurposed as UART.
- Runtime GNSS TX/RX swap is not supported on STM32F401 in this firmware; fix wiring physically if reversed.
- Receiver protocol mode is selected by `GNSS_TYPE`:
  - `0`: u-blox/UBX
  - `1`: UM980/UM981 NMEA
- u-blox autoconfig behavior is controlled by `UBX_BAUD`:
  - `UBX_BAUD=0`: autoconfig enabled (default).
  - `UBX_BAUD>0`: autoconfig disabled, use this manual baud (reboot required).

## DR1 event pulse (`B5`)

- On each DR0 -> DR1 transition, firmware drives `B5` high for 3 seconds, then low.
- Verify polarity with your external circuit during first power-up.
