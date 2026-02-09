# Device Overview

This document describes how the STM32 filter operates between the GNSS receiver and the flight controller (FC).

## Terminology (quick glossary)

- **DR (dead-reckoning)**: estimating position from IMU/airspeed when GNSS is unreliable. It works for short periods but drifts over time.
- **DR0**: normal mode. GNSS is forwarded to the FC GPS UART.
- **DR1**: protection mode. GNSS forwarding is blocked, so the FC relies on inertial estimates only.
- **FC**: flight controller (ArduPilot).
- **GNSS**: satellite navigation receiver (u-blox).
- **GPS**: satellite positioning system. In this document, “GPS” refers to the GNSS receiver input and the FC GPS UART.
- **UART**: a simple serial port (TX/RX) used to connect modules.
- **MAVLink**: telemetry/control protocol between STM32 and FC.
- **MAV**: shorthand for MAVLink telemetry.
- **GCS**: ground control station (Mission Planner, QGroundControl).
- **UBX**: u-blox binary GNSS protocol.
- **EKF**: Extended Kalman Filter inside the FC.

## Compatibility and Safety

- Requires **ArduPilot 4.6.1 or later**.
- GNSS input must be **UBX (u-blox)**. Other protocols are not supported.
- First flights should be on a low-cost, easy-to-recover airframe (for example, a 10-inch FPV quad with ArduPilot or a small fixed wing such as Reptile Dragon V2). Validate behavior before installing on an expensive UAV.

## 1) Purpose

The filter sits between GNSS and the FC and performs three core tasks:

1. **Parses GNSS UBX** and evaluates signal quality and anomalies.
2. **Controls DR state (DR0/DR1)** by enabling or blocking GNSS forwarding to the FC GPS UART.
3. **Controls GNSS forwarding** to the FC GPS UART (blocked during DR1).

## 2) Data paths

There are three UART links:

- GNSS and STM32: UBX input for quality checks.
- FC MAVLink and STM32: status, commands, and tuning.
- FC GPS and STM32: raw UBX forwarding to the FC GPS UART.

In DR0, GNSS data is forwarded to the FC GPS UART.

In DR1, GNSS forwarding is blocked to avoid passing suspect data to the FC.

## 3) DR0 and DR1

### DR0 (normal mode)

- GNSS is forwarded to the FC GPS UART.
- DR guards monitor GNSS quality.

### DR1 (protection mode)

- UBX forwarding to the FC GPS UART is blocked.
- `B5` pulses high for ~3 seconds on entry.

## 4) What can trigger DR1 (examples)

### Example A: position jump

- A sudden jump of hundreds or thousands of kilometers.
- Guard exceeds `SP_ABS_M` or `SP_JMP_MPS`.
- DR1 is entered.

### Example B: SNR anomaly (nearby jammer/spoofer)

- Satellite count is high, but the SNR spread is abnormally narrow.
- Spread holds longer than `SNR_HOLDMS`.
- With `SNR_EN=1`, DR1 is entered.

### Example C: altitude anomaly

- Large single-step altitude jump or excessive altitude rate.
- Large GNSS-versus-baro separation held over time.
- Altitude guards trigger DR1.

## 5) Returning from DR1 (rejoin)

The filter returns to DR0 only after:

- minimum GNSS quality is met (`RJ_MIN_SATS`, `RJ_MAX_HD`),
- the stable window is satisfied (`RJ_STAB_MS`),
- the lockout window has finished (`DR_LOCK_MS`),
- optional EKF conditions are satisfied if enabled.

If conditions pass, an optional blend (`BLEND_MS`) runs, then DR0 is restored.

## 6) Example flow

1. Flight is normal: DR0.
2. Spoofing or interference starts.
3. The filter enters DR1 and blocks GNSS forwarding.
4. Signal returns to normal.
5. After stable checks, the filter rejoins DR0.

## 7) What you can tune live

Via `tools/tune_cli.py` you can change thresholds without reflashing:

- Rejoin gates and timing (`RJ_*`, `BLEND_MS`, `DR_LOCK_MS`).
- Spoof and altitude guards (`SP_*`, `ALT_*`).
- SNR guard (`SNR_*`).
- DR behavior (`DR_NOFIX`, `RJ_REQEKF`, etc.).

This allows adapting behavior for different regions or flight profiles.

## 8) Key operational notes

- The GCS map may show GNSS jumps during spoofing. Use DR status and filter logs as the primary source of truth.
- Conservative rejoin is safer than fast rejoin in hostile GNSS environments.
- Save a baseline parameter profile before field changes.
