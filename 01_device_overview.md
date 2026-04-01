# Device Overview

> Board store: [GPS Spoofing Filter](https://airdroper.org/product/gps-spoofing-filter/)

This document describes how the STM32 filter operates between the GNSS receiver and the flight controller (FC).

## Terminology (quick glossary)

- **DR (dead-reckoning)**: estimating aircraft position from inertial data (IMU), heading, and speed when GNSS is not trusted. It keeps navigation continuity but accumulates drift over time.
- **DR0**: normal mode. GNSS data is forwarded to the FC GPS UART.
- **DR1**: protection mode. Live GNSS forwarding is blocked — the FC GPS UART receives silence so suspect GNSS data does not reach the FC.
- **FC**: flight controller (ArduPilot).
- **GNSS**: global navigation satellite receiver (for example u-blox M8/M9/M10/F9/F10-class receivers or UM980/UM981-class receivers).
- **GPS**: in this documentation, the GNSS input path and FC GPS UART path.
- **UART**: serial interface with TX/RX lines.
- **MAVLink**: telemetry/control protocol between STM32 and FC.
- **GCS**: ground control station (Mission Planner, QGroundControl).
- **UBX**: u-blox binary GNSS protocol.
- **NMEA**: text GNSS protocol used by many receivers.
- **EKF**: Extended Kalman Filter inside the FC.

## Compatibility and safety

- Requires **ArduPilot 4.6.1 or later**.
- Receiver mode is selected by `GNSS_TYPE`:
  - `GNSS_TYPE=0`: u-blox/UBX mode.
  - `GNSS_TYPE=1`: UM980/UM981 NMEA mode.
- In `GNSS_TYPE=1`, the filter expects one physical UM980 receiver stream:
  - `COM1` -> STM32 `A2/A3`
  - the STM32 reads spoofing/SNR data from that stream
  - the STM32 forwards that same stream to the FC GPS UART
- `GNSS_TYPE` is saved immediately but applied only after STM32 reboot.
- First flights should be on a low-cost, easy-to-recover airframe (for example, a 10-inch FPV quad with ArduPilot or a small fixed wing such as Reptile Dragon V2). Validate behavior before installing on an expensive UAV.

## 1) Purpose

The filter sits between GNSS and FC and performs three core tasks:

1. Parses GNSS data and evaluates quality/anomalies.
2. Controls DR state (DR0/DR1) from guard logic.
3. Controls GNSS forwarding to FC GPS UART (blocked in DR1).

## 2) System architecture

```
┌──────────────┐                ┌───────────────────┐                ┌──────────────┐
│              │   UART 460800  │                   │  MAVLink 115200│              │
│  GNSS        │───────────────►│   STM32 Filter    │◄──────────────►│  Flight      │
│  Receiver    │   A2/A3        │   (BlackPill)     │  A9/A10        │  Controller  │
│              │                │                   │                │              │
│  u-blox or   │                │  ┌─────────────┐  │   UART 460800  │  ArduPilot   │
│  UM980       │                │  │ Guard Logic │  │───────────────►│  GPS input   │
│              │                │  │ DR0 / DR1   │  │  A11/A12       │              │
└──────────────┘                │  └─────────────┘  │                └──────────────┘
                                │                   │
                                │  B5: event pulse  │
                                └───────┬───────────┘
                                        │
                                   (DR0→DR1 pulse)
```

## 3) Data paths

There are three UART links:

| Link | STM32 pins | Baud | Purpose |
|------|-----------|------|---------|
| GNSS ↔ STM32 | A2 (TX) / A3 (RX) | 460800 | Receiver input for quality checks |
| FC MAVLink ↔ STM32 | A9 (TX) / A10 (RX) | 115200 | Status, commands, tuning |
| FC GPS ← STM32 | A11 (TX) / A12 (RX) | 460800 | Raw GNSS forwarding to FC |

For UM980/UM981, one physical receiver UART is enough. The STM32 consumes that single GNSS stream and mirrors it to the FC GPS UART.

**DR0**: GNSS data forwarded to FC GPS UART.
**DR1**: FC GPS UART receives silence — no GNSS data reaches the FC.

## 3) DR0 and DR1

### DR0 (normal mode)

- GNSS forwarding enabled.
- Guards monitor quality continuously.

### DR1 (protection mode)

- Live GNSS forwarding disabled.
- FC GPS UART receives silence (no GNSS data forwarded).
- `B5` outputs a high pulse for about 3 seconds on each DR0 -> DR1 transition.

## 4) What can trigger DR1 (examples)

### Example A: no-fix or low satellites

- GNSS fix becomes invalid, or satellite count drops below 5.
- The filter enters DR1 immediately (outside boot guard delay).

### Example B: position jump

- Sudden large location step or unrealistic implied speed.
- Guard exceeds `SP_ABS_M` or `SP_JMP_MPS`.

### Example C: SNR anomaly (near jammer/spoofer)

- High satellite count with abnormally narrow SNR spread.
- Condition holds longer than `SNR_HOLDMS` with `SNR_EN=1`.

### Example D: altitude anomaly

- Large single-step altitude jump, high altitude rate, or persistent GNSS-vs-baro separation.

### Example E: EKF flags trip

- FC EKF reports unhealthy horizontal state for at least `EKF_TRIPMS`.

## 5) Returning from DR1 (rejoin)

The filter returns to DR0 only after configured quality and timing gates are satisfied:

- quality (`RJ_MIN_SATS`, `RJ_MAX_HD`),
- stability window (`RJ_STAB_MS`),
- DR1 lock window (`DR_LOCK_MS`),
- optional EKF gate (`RJ_REQEKF`, `EKF_OKRJMS`).

If conditions pass, optional blend (`BLEND_MS`) runs, then DR0 is restored.

## 6) Key operational notes

- `FCGPS_FWD=1` is for diagnostics only and bypasses DR1 blocking.
- `BOOT_DLYMS` delays DR triggers right after power-up to reduce startup false trips.
- GCS map can show GNSS jumps during spoofing; use DR state and filter logs as primary truth.
- Save a baseline parameter profile before changing field settings.

## 7) Receiver choice: UM980/UM981 vs u-blox (for this filter use case)

UM980/UM981 can be a better fit than u-blox for long anti-spoof runs in this project, mainly because:

- robust multi-band tracking and generally stronger satellite lock stability in difficult RF environments;
- better behavior after long interference periods in many field setups (faster return to usable fix);
- NMEA-mode operation (`GNSS_TYPE=1`) avoids UBX reconfiguration dependency;
- high satellite availability in open sky improves guard/rejoin confidence.

u-blox is still supported and works well when configured correctly (`GNSS_TYPE=0`).  
Use platform-specific flight testing to confirm which receiver is better for your region and interference profile.
