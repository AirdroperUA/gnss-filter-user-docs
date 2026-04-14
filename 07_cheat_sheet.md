# Cheat Sheet (Field Quick Reference)

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

This is a one-page quick reference for setup checks, DR meaning, and common actions. For detailed explanations, see the [Device Overview](#device-overview).

## 1) UART Summary

See the [Wiring Guide](#wiring) for full diagrams.

- GNSS and STM32: `A2/A3`
- FC MAVLink and STM32: `A9/A10` (MAVLink2 @ 115200)
- FC GPS and STM32: `A11/A12` (typically 460800)

## 2) Receiver Mode (`GNSS_TYPE`)

- `GNSS_TYPE=0`: u-blox/UBX mode.
- `GNSS_TYPE=1`: UM980/UM981/UM982 NMEA mode. Requires one-time setup — see [Receiver Config](#receiver-config).
- `FCGPS_UART=1`: A11/A12 active as FC GPS UART (normal operation, default).
- `FCGPS_UART=0`: A11/A12 released into input mode. Do not use during flight.
- After changing `GNSS_TYPE`, reboot STM32 (`NRST` or power cycle).

<details>
<summary><strong>Advanced: Custom baud and gateway modules</strong></summary>

- For custom u-blox that should not be auto-configured:
  - set `UBX_BAUD` to receiver baud (`0` means autoconfig ON),
  - reboot STM32 to apply.
- For gateway / dual-F9P modules such as Quadro GPS, UNA3, and UNA4-SFE:
  - use `GNSS_TYPE=0`,
  - set the exact `UBX_BAUD`,
  - do not use filter autobaud.

</details>

## 3) DR Modes

- **DR0**: normal mode — GPS data flows to your flight controller.
- **DR1**: protection mode — GPS blocked, FC uses dead-reckoning.
- **B5 pin**: outputs a high pulse (~3 s) on each DR0→DR1 transition (connect an LED or buzzer).

See the [Device Overview](#device-overview) for a full explanation.

## 4) Quick Diagnostics

**FC shows "No GPS config data":**

1. Check FC GPS UART protocol and baud — see [Wiring Guide](#wiring)
2. Check `A11/A12` TX/RX crossing
3. Confirm common ground

**DR1 stays active:**

1. Check no-fix / low-satellite state
2. Review guard thresholds — see [Tuning](#tuning) for `ARM_*`, `SP_*`, `ALT_*`, `SNR_*` parameters
3. Increase `BOOT_DLYMS` if false DR1 appears right after boot

**FC constantly shows "No Fix":**

- Verify RC AUX logic is not forcing GPS disable in FC settings
- See [Wiring Debug](#wiring-debug) for step-by-step troubleshooting

## 5) Mission Planner Parameter Write Flow

1. Open [Mission Planner](https://ardupilot.org/planner/) → `Config/Tuning` → `Full Parameter List`
2. Select STM32 target (`SYSID 42` in the dropdown)
3. Click `Refresh Params`
4. Edit values — see [Tuning](#tuning) for parameter descriptions
5. Click `Write Params`
6. Click `Refresh Params` to confirm

## 6) Parameter Write Rules

- If write does not apply on first click, repeat `Write Params`. 1-2 attempts are normal; 3+ suggests a very busy MAVLink link.
- Allow up to 30-45 seconds for telemetry link recovery after writes.
- Reboot is required for `GNSS_TYPE` and `UBX_BAUD`.
- Reboot is not required for most other parameters.

## 7) Typical DR1 Triggers

| Trigger | Parameters | Description |
|---------|-----------|-------------|
| No fix / low satellites | — | Triggers if satellite count < 5 |
| Position jump | `SP_ABS_M`, `SP_JMP_MPS` | Sudden large location step |
| SNR anomaly | `SNR_EN`, `SNR_HOLDMS` | Abnormal signal strength pattern |
| Altitude anomaly | `ALT_*` | Large altitude jump or GPS/baro mismatch |
| EKF unhealthy | `EKF_TRIPMS` | Flight controller reports nav problems |
| South-hemisphere jump | — | Latitude goes below 0° — instant DR1 + hard block |
| Geo-fence | `FENCE_RAD` | Position outside radius (up to 2000 km) from first fix (v1.5.5+) |
| Heading reversal | — | 150°+ heading flip while moving >5 m/s (v1.5.5+) |
| GPS time anomaly | — | >2 s drift between GPS and internal clock (v1.5.5+) |
| Clock bias jump | — | Sudden receiver clock jump, u-blox only (v1.5.5+) |
| Velocity-position mismatch | — | Velocity doesn't match position change (v1.5.5+) |

See [Tuning](#tuning) to adjust these thresholds.

## 7b) Spoofing Confidence Score (v1.5.5+)

The filter computes `DR_CONF` (0–100) combining 8 detection signals. Visible in Mission Planner named-value telemetry and in event logs. Higher = more evidence of spoofing. u-blox receivers use all 8 signals; UM980 uses the subset available via NMEA.

## 8) Status Log Messages

In Mission Planner `Messages`, filter status appears about every **10 seconds** (configurable via `LOG_MS`):

```
ARM=... DR=... BLEND=... LAT=... LONG=...
data=... fix=... nav=... SATS=... SNR=...
```

See [Operation](#operation) for how to interpret these messages.
