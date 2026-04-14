# Runtime Operation

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

## DR0 vs DR1

- **DR0**: normal operation. GNSS forwarding to FC GPS UART is enabled.
- **DR1**: protection mode. Live GNSS forwarding to FC GPS UART is blocked — the FC receives silence.

This prevents suspect live GNSS data from reaching FC navigation input while DR1 is active.

### State machine

```
                    ┌──────────────────────────────────┐
                    │                                  │
                    ▼                                  │
              ┌──────────┐    guard trip         ┌──────────┐
   boot ────► │   DR0    │ ───────────────────►  │   DR1    │
              │ (normal) │    (position jump,    │ (protect)│
              │          │     no fix, SNR,      │          │
              │ GPS      │     EKF bad, etc.)    │ GPS      │
              │ forwarded│                       │ blocked  │
              └──────────┘  ◄─────────────────── └──────────┘
                    ▲         rejoin conditions:       │
                    │         • RJ_MIN_SATS met        │
                    │         • RJ_MAX_HD met          │
                    │         • RJ_STAB_MS held        │
                    │         • DR_LOCK_MS elapsed     │
                    │         • (optional) EKF OK      │
                    │                                  │
                    └──────────────────────────────────┘
                          rejoin guard (500 ms)
                          prevents immediate re-trip
```

## DR1 trigger behavior (current firmware)

- No-fix or low-satellite condition (`sats < 5`) triggers DR1 immediately (after startup guard window).
- Position jump, altitude checks, SNR checks, and EKF checks can also trigger DR1 based on tuning.
- `EKF_TRIPMS=0` means EKF-based DR1 trip is immediate when EKF is unhealthy.
- South-hemisphere jump: if GPS latitude goes below 0°, DR1 triggers immediately. The filter also hard-blocks any south-hemisphere position from reaching the FC (all drones operate in the northern hemisphere).
- Geo-fence violation (if `FENCE_RAD > 0`): position outside configured radius (up to 2000 km) triggers DR1.
- Heading reversal: 150°+ heading change within 2 seconds while moving > 5 m/s triggers DR1.
- GPS time anomaly: > 2 s drift between GPS time and the filter's internal clock triggers DR1.
- DR1 max duration (`DR1_MAXMS > 0`): automatically exits DR1 after the configured timeout, even if GNSS hasn't recovered. Use for missions that cannot tolerate indefinite GPS blocking.

### Spoofing confidence score

The firmware computes a weighted confidence score (0–100) from up to 8 detection signals. The score is visible in Mission Planner as `DR_CONF` in the named-value telemetry and is recorded in each spoofing event log entry. Higher values indicate more evidence of spoofing. The score adapts to available data — signals that require UBX-specific messages (NAV-SAT, NAV-CLOCK, NAV-DOP) are skipped for UM980/NMEA receivers.

### UBX-only vs universal detection

Most detection signals work with both u-blox and UM980 receivers. The following advanced signals are **u-blox only** because they require UBX binary messages not available in NMEA:

| Signal | Required UBX message |
|--------|---------------------|
| Pseudorange residual stddev | NAV-SAT (prRes field) |
| GDOP sudden change | NAV-DOP (gDOP field) |
| Clock bias jump | NAV-CLOCK (clkB field) |

Velocity-position consistency works with both receivers but is more precise with u-blox (uses NED velocity from NAV-PVT) vs UM980 (derives from RMC speed/course).

## Startup guard

- `BOOT_DLYMS` creates a startup grace window before DR/EKF trip logic can enter DR1.
- Increase `BOOT_DLYMS` if DR1 appears right after power-up and clears after reset.

## Fail-safe behaviors (watchdog, mid-flight reboot, FC link loss)

The filter is designed to survive several failure modes without operator intervention. Understanding what it does in each case helps you read logs and plan recovery.

### Hardware watchdog (IWDG, 15 s)

The STM32 runs an independent hardware watchdog clocked by the internal LSI oscillator (~32 kHz). If the main firmware loop ever stalls for more than **15 seconds** — for example, a pathological parser input, a CPU fault, or a stuck interrupt — the watchdog forcibly resets the MCU. The watchdog counts through CPU faults, so it is the last line of defense against any software deadlock.

Symptoms in logs:
- Unexplained `BOOT t=0ms` log line mid-flight with no user-triggered reset.
- Brief GPS blackout on the FC (typically <15 s depending on what the filter was doing when the deadlock started).

The 15 s window is deliberately chosen to cover the worst-case firmware startup (up to ~11.5 s for a UM980 long-scan autobaud fallback) plus margin. You cannot reduce or disable it from Mission Planner.

### Mid-flight reboot with FC already armed

If the filter resets while the flight controller is already armed (brownout, EMI glitch, watchdog bite during flight), the normal 20-second boot DR guard (`BOOT_DLYMS`) is automatically shortcut to **2 seconds** so GPS forwarding resumes as fast as possible. The filter learns the FC is armed by decoding the `SAFETY_ARMED` flag from the FC's `HEARTBEAT` — the first armed heartbeat after boot collapses the remaining guard.

Behavior:
- Filter resets at T=0.
- Around T≈150 ms it begins listening for MAVLink.
- First FC `HEARTBEAT` with `SAFETY_ARMED=1` arrives shortly after — typically under 1 s.
- Boot DR guard release is rewritten to `fc_armed_first_seen + 2000 ms`.
- Total worst-case blind window: roughly the autobaud time (u-blox ~2.9 s, UM980 short ~2.7 s, UM980 long ~11.5 s) plus the 2 s settle. Typical case on u-blox or UM980 short scan: under 5 s.
- A single `Boot DR guard shortcut: FC armed at boot, release in 2000ms` warning is emitted to GCS on the armed edge.

If the FC is **disarmed** at the moment of reboot (pre-flight bench test), the full `BOOT_DLYMS` window applies — this is intentional, since a cold boot on the bench shouldn't trust a first-second fix.

### FC MAVLink staleness (link loss fail-safe)

The filter tracks a per-field freshness timestamp for `ATTITUDE`, `VFR_HUD`, `ALTITUDE`, and `HEARTBEAT`. If any of these fields stops refreshing for more than **2 seconds**, the filter treats it as positive evidence that the MAVLink link is impaired — not as "no news is good news." Concretely:

- Synthetic position integration freezes (no more IMU-blended coasting) if `ATTITUDE`/`VFR_HUD` are stale.
- Altitude-vs-barometer separation checks are disabled if the FC `ALTITUDE` message is stale — comparing a live GNSS altitude to a frozen baro reading could trip DR1 incorrectly during a climb.
- The rejoin altitude gate skips its baro cross-check when the baro is stale.
- The filter does **not** forcibly exit DR1 when the link drops — dropping protection at the moment the link is in trouble is exactly the wrong response.

Symptoms in logs: no specific message, but a `DR` that sticks across a MAVLink dropout combined with a frozen synth position is expected behavior.

### DR1 maximum latch (`DR1_MAXMS`)

By default, once DR1 latches, the filter stays in DR1 until the normal rejoin gates clear — there is no time-based forced exit. If your mission profile cannot tolerate an open-ended DR1 (e.g. long-range flight where losing GPS for the whole remaining leg is worse than accepting partially-recovered GPS), set `DR1_MAXMS` to a non-zero millisecond value. Once reached, the filter force-exits DR1 and resumes forwarding even if spoof confidence is still high.

Default `DR1_MAXMS=0` leaves this disabled. **Use with caution** — the default is safer for most missions.

## GNSS forwarding diagnostics

- `FCGPS_FWD=1` forces live GNSS forwarding even in DR1 (diagnostic only).
- `FCGPS_FWD=0` is the normal anti-spoof setting.

## Receiver mode

- `GNSS_TYPE=0`: u-blox/UBX mode.
- `GNSS_TYPE=1`: UM980/UM981/UM982 NMEA mode.
- `GNSS_TYPE` changes require STM32 reboot.
- In `GNSS_TYPE=1`, the STM32 expects one physical UM980 receiver stream on `A2/A3` and forwards that same stream to the FC GPS UART.

## Log example (GCS)

The following screenshot shows expected status-text format in GCS messages.

- In Mission Planner `Messages`, these periodic STM32 filter logs normally appear about once every **10 seconds** by default.
- You typically see two back-to-back lines in the same moment:
  - mode/state line: `ARM=... DR=... BLEND=... LAT=... LONG=...`
  - GNSS summary line: `data=... fix=... nav=... SATS=... SNR=...`
- `fix` is the age of the last valid position/altitude fix; `nav` is the age of the last valid GNSS nav-data frame seen by the filter.
- `SNR=NA` means the filter is not currently receiving usable SNR data from the receiver. With u-blox, this usually means `NAV-SAT` is not being output. With UM980/981, it means no `GSV` sentences are arriving.
- If `SNR_EN=1` and `SNR=NA` persists beyond 30 seconds, a `WARNING: SNR_EN=1 but SNR=NA/stale (no fresh GSV/NAV-SAT?)` message is logged. The SNR guard cannot trip while SNR data is absent.

![Example log output](diagrams/log_example.jpg)

## Rejoin sequence

When rejoin conditions are satisfied:

1. Rejoin stability timer runs.
2. Optional blend phase runs for `BLEND_MS`.
3. Filter exits DR1 and restores DR0 forwarding.

## DR1 event pulse output

- Pin: `B5`.
- Behavior: high for 3 seconds on each DR0 -> DR1 transition, then low.
- Use case: external logger/beacon/indicator.

## GNSS recovery watchdog

The filter automatically attempts to recover a stuck GNSS receiver when no valid fix is received.

- After **15 s** without fix: hot restart is issued.
- After **45 s** without fix: cold/factory restart is issued.
- Every **120 s** after the cold restart, if still no fix: another cold restart is retried.
- All timers reset as soon as a valid fix is received.

**u-blox**: hot restart uses UBX `CFG-RST` with `navBbrMask=0x0000`; cold restart uses `navBbrMask=0xFFFF`.

**UM980/981**: hot restart sends `RESET\r\n` over the GNSS UART; cold/factory restart sends `FRESET\r\n`.
After `FRESET`, the STM32 waits for the receiver to boot and rescans the active GNSS baud.

Recovery status messages are logged to GCS (`INFO` for hot, `WARNING` for cold/retry).

## Operational checks

- If FC constantly shows `No Fix`, verify RC AUX logic is not forcing GPS disable on FC.
- If map shows jumps during spoofing, trust DR state and filter logs over map position.
