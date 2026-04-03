# Device Overview

> Board store: [GPS Spoofing Filter](https://airdroper.org/product/gps-spoofing-filter/)

This document describes how the STM32 filter operates between the GNSS receiver and the flight controller (FC).

## Key terms

- **DR0** (normal mode): GPS data flows through to your flight controller — everything works normally.
- **DR1** (protection mode): GPS data is blocked — the flight controller switches to dead-reckoning (navigating by compass, airspeed, and inertial sensors) until clean GPS returns.
- **FC**: flight controller (the autopilot board in your drone, running ArduPilot).
- **GNSS**: the GPS module/receiver connected to the filter (u-blox or UM980/UM981).

<details>
<summary><strong>Full glossary (advanced)</strong></summary>

- **UART**: serial interface with TX/RX wires — how the filter talks to other devices.
- **MAVLink**: telemetry protocol between the filter and flight controller.
- **GCS**: ground control station (Mission Planner, QGroundControl).
- **UBX**: u-blox binary GPS protocol.
- **NMEA**: text GPS protocol used by many receivers.
- **EKF**: Extended Kalman Filter — the flight controller's internal navigation estimator.
- **Dead-reckoning**: estimating position from IMU, heading, and speed when GPS is unavailable. Keeps navigation going but accumulates drift over time.

</details>

## Compatibility

- Requires **ArduPilot 4.6.1 or later**.
- Supported GPS receivers:
  - **u-blox** (M8, M9, M10, F9, F10) — set `GNSS_TYPE=0`
  - **UM980 / UM981** — set `GNSS_TYPE=1`
- **Important:** Test on a low-cost, easy-to-recover drone first (e.g., a small FPV quad or fixed wing). Validate behavior before installing on an expensive aircraft.

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

## 3) How data flows

In normal mode (DR0), GPS data passes through the filter to your flight controller. When spoofing is detected (DR1), the filter blocks GPS data — your flight controller sees no GPS and switches to dead-reckoning automatically.

<details>
<summary><strong>Technical: Pin assignments and baud rates</strong></summary>

| Link | STM32 pins | Baud | Purpose |
|------|-----------|------|---------|
| GNSS ↔ STM32 | A2 (TX) / A3 (RX) | 460800 | Receiver input for quality checks |
| FC MAVLink ↔ STM32 | A9 (TX) / A10 (RX) | 115200 | Status, commands, tuning |
| FC GPS ← STM32 | A11 (TX) / A12 (RX) | 460800 | GPS forwarding to FC |

For UM980/UM981, one physical receiver connection is enough — the filter reads the GPS stream and mirrors it to the flight controller.

</details>

## 4) DR0 and DR1

### DR0 (normal mode)

- GNSS forwarding enabled.
- Guards monitor quality continuously.

### DR1 (protection mode)

- Live GNSS forwarding disabled.
- FC GPS UART receives silence (no GNSS data forwarded).
- `B5` outputs a high pulse for about 3 seconds on each DR0 -> DR1 transition.

## 5) What can trigger DR1 (examples)

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

## 6) Returning from DR1 (rejoin)

The filter returns to DR0 only after configured quality and timing gates are satisfied:

- quality (`RJ_MIN_SATS`, `RJ_MAX_HD`),
- stability window (`RJ_STAB_MS`),
- DR1 lock window (`DR_LOCK_MS`),
- optional EKF gate (`RJ_REQEKF`, `EKF_OKRJMS`).

If conditions pass, optional blend (`BLEND_MS`) runs, then DR0 is restored.

## 7) Key operational notes

- `FCGPS_FWD=1` is for diagnostics only and bypasses DR1 blocking.
- `BOOT_DLYMS` delays DR triggers right after power-up to reduce startup false trips.
- GCS map can show GNSS jumps during spoofing; use DR state and filter logs as primary truth.
- Save a baseline parameter profile before changing field settings.

## 8) Which GPS receiver to choose?

Both u-blox and UM980/UM981 work well. For areas with heavy jamming or spoofing, **UM980/UM981 tends to perform better** — it has stronger satellite lock, faster recovery after interference, and simpler setup (no auto-configuration needed).

**u-blox** is still a great choice and is auto-configured by the filter at boot — just plug it in.

We recommend testing with your specific setup and region to see which works best for you.
