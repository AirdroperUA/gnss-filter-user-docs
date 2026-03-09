# Runtime Operation

## DR0 vs DR1

- **DR0**: normal operation. GNSS forwarding to FC GPS UART is enabled.
- **DR1**: protection mode. GNSS forwarding to FC GPS UART is blocked.

This prevents suspect GNSS data from reaching FC navigation input while DR1 is active.

## DR1 trigger behavior (current firmware)

- No-fix or low-satellite condition (`sats < 5`) triggers DR1 immediately (after startup guard window).
- Position jump, altitude checks, SNR checks, and EKF checks can also trigger DR1 based on tuning.
- `EKF_TRIPMS=0` means EKF-based DR1 trip is immediate when EKF is unhealthy.

## Startup guard

- `BOOT_DLYMS` creates a startup grace window before DR/EKF trip logic can enter DR1.
- Increase `BOOT_DLYMS` if DR1 appears right after power-up and clears after reset.

## GNSS forwarding diagnostics

- `FCGPS_FWD=1` forces forwarding even in DR1 (diagnostic only).
- `FCGPS_FWD=0` is the normal anti-spoof setting.
- Log field `d=<fcgps_drop>/<gnss_drop>` reports non-blocking UART write drops.

## Receiver mode

- `GNSS_TYPE=0`: u-blox/UBX mode.
- `GNSS_TYPE=1`: UM980/UM981 NMEA mode.
- `GNSS_TYPE` changes require STM32 reboot.

## Log example (GCS)

The following screenshot shows expected status-text format in GCS messages.

![Example log output](diagrams/log_example.png)

## Rejoin sequence

When rejoin conditions are satisfied:

1. Rejoin stability timer runs.
2. Optional blend phase runs for `BLEND_MS`.
3. Filter exits DR1 and restores DR0 forwarding.

## DR1 event pulse output

- Pin: `B5`.
- Behavior: high for 3 seconds on each DR0 -> DR1 transition, then low.
- Use case: external logger/beacon/indicator.

## Operational checks

- If FC constantly shows `No Fix`, verify RC AUX logic is not forcing GPS disable on FC.
- If map shows jumps during spoofing, trust DR state and filter logs over map position.
