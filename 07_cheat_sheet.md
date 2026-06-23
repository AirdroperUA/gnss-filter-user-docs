# Cheat Sheet (Field Quick Reference)

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

This is a one-page quick reference for setup checks, DR meaning, and common actions. For detailed explanations, see the [Device Overview](#device-overview).

## 1) UART Summary

See the [Wiring Guide](#wiring) for full diagrams.

- GNSS and STM32: `A2/A3`
- FC MAVLink and STM32: `A9/A10` (MAVLink2 @ 115200)
- FC GPS and STM32: `A11/A12` on F401 or `C6/C7` on H743 UART builds (typically 460800)
- H743 DroneCAN: GNSS `A2/A3`, CAN transceiver `PB8/PB9`, USB-C remains on `A11/A12`

The H743 DroneCAN firmware does not use the FC MAVLink UART or FC GPS UART.
ArduPilot should see a DroneCAN GPS (`GPS1_TYPE=9`) on the configured CAN port.
Use [H743 DroneCAN Guide](13_h743_dronecan.md) for the complete setup path.

## 2) Receiver Mode (`GNSS_TYPE`)

- `GNSS_TYPE=0`: u-blox/UBX mode.
- `GNSS_TYPE=1`: UM980/UM981/UM982 NMEA mode. Requires one-time setup — see [Receiver Config](#receiver-config).
- `GNSS_TYPE=2`: Septentrio Mosaic X5 NMEA mode. Requires one-time setup — see [Receiver Config](#receiver-config).
- `FCGPS_UART=1`: FC GPS UART pins active (F401 `A11/A12`, H743 UART `C6/C7`; normal operation, default).
- `FCGPS_UART=0`: FC GPS UART pins released into input mode. Do not use during flight.
- H743 DroneCAN `v0.1.4+` tuning is in Mission Planner
  `SETUP -> Optional Hardware -> DroneCAN/UAVCAN -> node 42 -> Params`.
- H743 DroneCAN `v0.1.5+` can also be tuned directly over USB-C by connecting
  Mission Planner to the H743 COM port at `115200`.
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
2. Check `A11/A12` TX/RX crossing on F401 or `C6/C7` on H743 UART builds
3. Confirm common ground

**H743 DroneCAN GPS does not appear:**

1. Check CAN bitrate `1000000` and `GPS1_TYPE=9`
2. Check `PB9 -> TXD`, `PB8 -> RXD`, `CANH/CANL/GND`
3. Check termination only at physical CAN bus ends

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

Optional but recommended: install
[AirDroper Mission Planner Params](https://gps.airdroper.org/download/mission-planner-mod)
first so Mission Planner shows descriptions, ranges, units, and option labels
instead of raw parameter names only.

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

The filter computes `DR_CONF` (0–100) combining 8 detection signals. Visible in Mission Planner named-value telemetry and in event logs. Higher = more evidence of spoofing. u-blox receivers use all 8 signals; passive NMEA receivers such as UM980 and Mosaic X5 use the subset available via NMEA.

## 8) Status Log Messages

In Mission Planner `Messages`, filter status appears about every **10 seconds** (configurable via `LOG_MS`):

```
data=... fix=... nav=... SATS=... SNR=...
ARM=... DR=... BLEND=... LAT=... LONG=...
```

See [Operation](#operation) for how to interpret these messages.
