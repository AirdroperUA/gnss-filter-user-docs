# Runtime Operation

> Board store: [GPS Spoofing Filter](https://airdroper.org/product/gps-spoofing-filter/)

## DR0 vs DR1

- **DR0**: normal operation. GNSS forwarding to FC GPS UART is enabled.
- **DR1**: protection mode. Live GNSS forwarding to FC GPS UART is blocked. If `DR_NOFIX=1` and `NMEA_NOFIX=1`, periodic NMEA NO_FIX beacons are sent instead.

This prevents suspect live GNSS data from reaching FC navigation input while DR1 is active.

## DR1 trigger behavior (current firmware)

- No-fix or low-satellite condition (`sats < 5`) triggers DR1 immediately (after startup guard window).
- Position jump, altitude checks, SNR checks, and EKF checks can also trigger DR1 based on tuning.
- `EKF_TRIPMS=0` means EKF-based DR1 trip is immediate when EKF is unhealthy.

## Startup guard

- `BOOT_DLYMS` creates a startup grace window before DR/EKF trip logic can enter DR1.
- Increase `BOOT_DLYMS` if DR1 appears right after power-up and clears after reset.

## GNSS forwarding diagnostics

- `FCGPS_FWD=1` forces live GNSS forwarding even in DR1 (diagnostic only).
- `FCGPS_FWD=0` is the normal anti-spoof setting.

## Receiver mode

- `GNSS_TYPE=0`: u-blox/UBX mode.
- `GNSS_TYPE=1`: UM980/UM981 NMEA mode.
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
3. Filter exits DR1 and restores DR0 forwarding (or stops NO_FIX beacons if they were enabled).

## DR1 event pulse output

- Pin: `B5`.
- Behavior: high for 3 seconds on each DR0 -> DR1 transition, then low.
- Use case: external logger/beacon/indicator.

## GNSS recovery watchdog

The filter automatically attempts to recover a stuck GNSS receiver when no valid fix is received.

- After **15 s** without fix: hot restart is issued.
- After **45 s** without fix: cold/factory restart is issued.
- Every **60 s** after the cold restart, if still no fix: another cold restart is retried.
- All timers reset as soon as a valid fix is received.

**u-blox**: hot restart uses UBX `CFG-RST` with `navBbrMask=0x0000`; cold restart uses `navBbrMask=0xFFFF`.

**UM980/981**: hot restart sends `RESET\r\n` over the GNSS UART; cold/factory restart sends `FRESET\r\n`.
After `FRESET`, the STM32 waits for the receiver to boot, rescans the active GNSS baud,
and reapplies the full UM980 profile before saving it again.

Recovery status messages are logged to GCS (`INFO` for hot, `WARNING` for cold/retry).

## Operational checks

- If FC constantly shows `No Fix`, verify RC AUX logic is not forcing GPS disable on FC.
- If map shows jumps during spoofing, trust DR state and filter logs over map position.
