# Wiring Debug Guide

Use this guide when GNSS is not detected, DR1 is always active, or MAVLink tuning does not work.

## 1) GNSS Path (STM32 <-> GNSS)

Symptoms:
- `GNS nav=0` and `s=0` persist in logs.
- `age` grows and `GNS no NAV-PVT` warnings appear.

Checks:
1. **Power**: GNSS module has stable 5V (or its required voltage) and GND.
2. **UART pins**: GNSS TX -> STM32 `A3` (RX). GNSS RX -> STM32 `A2` (TX).
3. **Baud**: GNSS is configured to `460800` UBX. If you changed GNSS baud, update firmware or reconfigure the receiver.
4. **Signal**: test outdoors with clear sky view; indoors may show no satellites.

Quick verification:
- In GCS, look for periodic `GNS nav=...` messages with `s>=5` and `age<1000ms`.

## 2) FC GPS Path (STM32 <-> FC GPS UART)

Symptoms:
- FC shows **GPS: No GPS** even though GNSS is healthy in filter logs.

Checks:
1. **UART pins**: STM32 `A11/A12` connect to FC GPS UART (crossed TX/RX).
2. **FC port protocol**: set FC GPS UART to **UBlox** and `460800` baud.
3. **DR state**: in DR1, GNSS forwarding is blocked by design. Confirm DR0 before testing FC GPS input.

Quick verification:
- In DR0, FC should show satellites and 3D fix once GNSS is stable.

## 3) MAVLink Path (STM32 <-> FC Telemetry)

Symptoms:
- `tune_cli.py` cannot list params.
- No status text appears in GCS.

Checks:
1. **UART pins**: STM32 `A9/A10` connect to FC telemetry UART (crossed TX/RX).
2. **Protocol**: FC telemetry port set to MAVLink2 at `115200`.
3. **SYSID/COMPID**: default is `SYSID=42`, `COMPID=191`.

Quick verification:
- Run: `python tools/tune_cli.py --port COM12 --baud 115200 list`
- You should see filter parameters, including `BLEND_MS`, `RJ_BASE_M`, and `SNR_EN`.

## 4) Common Wiring Mistakes

- TX/RX not crossed (must be TX -> RX, RX -> TX).
- GNSS and FC GPS UART swapped.
- MAVLink UART connected to the GPS UART on the FC.
- No common ground between STM32, GNSS, and FC.

If all checks pass and you still see no GNSS, capture a log screenshot and confirm wiring with a multimeter for continuity.
