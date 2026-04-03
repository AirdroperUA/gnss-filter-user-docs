# Device Overview

> Board store: [GPS Spoofing Filter](https://airdroper.org/product/gps-spoofing-filter/)

This document describes how the STM32 filter operates between the GNSS receiver and the flight controller (FC). For wiring instructions, see the [Wiring Guide](#wiring). For first-time setup, see [Setup & Flash](#setup-flash).

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
  - **UM980 / UM981** — set `GNSS_TYPE=1` (requires one-time setup, see [Receiver Config](#receiver-config))
- **Important:** Test on a low-cost, easy-to-recover drone first (e.g., a small FPV quad or fixed wing). Validate behavior before installing on an expensive aircraft.

## 1) Purpose

The filter sits between your GPS module and flight controller and performs three core tasks:

1. Monitors GPS data quality and checks for anomalies (spoofing, jamming, signal loss).
2. Decides whether GPS is trustworthy (DR0) or suspect (DR1).
3. Blocks GPS data from reaching the flight controller when DR1 is active.

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

For detailed wiring instructions, see the [Wiring Guide](#wiring).

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

- GPS data forwarded to your flight controller.
- Guards monitor quality continuously in the background.

### DR1 (protection mode)

- GPS data blocked — your flight controller receives silence.
- Pin B5 outputs a 3-second pulse on each DR0→DR1 transition (you can connect an LED or buzzer to it).

See [Operation](#operation) for the full state machine and [Tuning](#tuning) to adjust sensitivity.

## 5) What can trigger DR1 (examples)

### Example A: no-fix or low satellites

- GPS fix becomes invalid, or satellite count drops below 5.
- The filter enters DR1 immediately.

### Example B: position jump

- Sudden large location step or unrealistic implied speed.
- Common during active spoofing attacks.

### Example C: SNR anomaly (near jammer/spoofer)

- High satellite count with abnormally narrow signal strength spread.
- A classic spoofing fingerprint — all satellites appear at similar strength.

### Example D: altitude anomaly

- Large single-step altitude jump, high altitude rate, or persistent GPS-vs-barometer separation.

### Example E: EKF flags trip

- The flight controller's own navigation filter reports unhealthy state.

## 6) Returning from DR1 (rejoin)

The filter returns to DR0 (normal GPS) only after all quality checks pass for a stable period. This prevents false recoveries. See [Tuning](#tuning) for adjustable thresholds (`RJ_MIN_SATS`, `RJ_MAX_HD`, `RJ_STAB_MS`, `DR_LOCK_MS`).

## 7) Key operational notes

- `FCGPS_FWD=1` is for diagnostics only — it bypasses DR1 blocking (see [Cheat Sheet](#cheat-sheet)).
- `BOOT_DLYMS` delays DR triggers right after power-up to reduce startup false trips.
- The GCS map can show GPS jumps during spoofing; use DR state and the [Cloud Dashboard](https://gnss-filter.online/dashboard) as primary truth.
- Save a baseline parameter profile before changing field settings.

## 8) Which GPS receiver to choose?

Both u-blox and UM980/UM981 work well. For areas with heavy jamming or spoofing, **UM980/UM981 tends to perform better** — it has stronger satellite lock, faster recovery after interference, and simpler setup (no auto-configuration needed).

**u-blox** is still a great choice and is auto-configured by the filter at boot — just plug it in.

For UM980 setup instructions, see [Receiver Config](#receiver-config). For general wiring, see the [Wiring Guide](#wiring).
