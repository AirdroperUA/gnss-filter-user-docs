# Anti-Spoof Lab Validation (Defensive Only)

This document is focused only on defensive validation of spoofing resilience.

## 1) Scope and Boundaries

- Purpose: verify that the STM32 filter protects FC navigation when GNSS data becomes suspect.
- Allowed use: legal, authorized, isolated lab environments only.
- Not included: attack-enablement instructions (device setup, transmission methods, or procedures to spoof GNSS receivers).

## 2) Video Reference

- Reference video: https://www.youtube.com/watch?v=EFvWup8oCCE
- Treat the video as a demonstration of defensive validation workflow.
- Use it together with this checklist-driven procedure and saved logs.

## 3) Defensive Validation Goals

1. Confirm normal operation in DR0 when GNSS is healthy.
2. Confirm transition to DR1 when spoof-like anomalies appear.
3. Confirm GNSS forwarding is blocked while DR1 is active.
4. Confirm controlled return to DR0 only after stability/rejoin conditions.
5. Confirm no oscillation between DR0 and DR1 under stable inputs.

## 4) Recommended Lab Environment

- RF-isolated test area managed by qualified personnel.
- No radiating tests near live aircraft, real runways, or public operations.
- If your authorized RF lab uses a dedicated SDR source platform, a common hardware set is **HackRF One + PortaPack H2**.
- Full logging enabled:
  - filter status text,
  - FC messages,
  - timestamped test notes for each run.

Note: this document does not include setup or operation steps for HackRF/PortaPack.

## 5) Test Scenarios (Spoofing-Relevant)

Use controlled, authorized anomaly sources and verify expected filter behavior:

1. **Large position discontinuity**
   - Expected: DR1 entry, GNSS forwarding blocked.
2. **Unrealistic implied speed**
   - Expected: DR1 entry and sustained protection state.
3. **Altitude anomaly pattern**
   - Expected: DR1 entry when altitude consistency checks fail.
4. **SNR-pattern anomaly (if enabled in your profile)**
   - Expected: DR1 entry after hold-time logic.
5. **Recovery sequence**
   - Expected: DR0 only after quality/timing gates are satisfied.

## 6) What to Verify in Logs

- DR state changes (`DR=0` -> `DR=1` -> `DR=0`).
- GNSS health trend before and during anomaly windows (`GNS nav`, `age`, satellite count).
- Presence of trigger messages describing why DR1 was entered.
- Rejoin messages when returning to DR0.
- No unexpected FC navigation jumps during DR1.

## 7) Common Validation Failures

- **DR1 never triggers during anomaly**
  - Guard thresholds too permissive or anomaly not strong enough for configured logic.
- **DR1 triggers too often**
  - Overly strict profile, startup instability, or poor baseline GNSS conditions.
- **No clean return to DR0**
  - Rejoin quality/timing conditions not satisfied.
- **Test results are inconsistent**
  - Incomplete environment control, missing logs, or mixed test setups between runs.

## 8) Pass Criteria Before Flight

All must be true:

1. DR1 triggers on spoof-like anomalies in repeated runs.
2. GNSS forwarding remains blocked during DR1.
3. DR0 recovery is stable and repeatable.
4. FC behavior stays controlled (no unsafe navigation jumps).
5. Logs and test records are complete for review.
