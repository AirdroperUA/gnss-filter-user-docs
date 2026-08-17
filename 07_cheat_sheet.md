# Cheat Sheet (Field Quick Reference)

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

This is a one-page quick reference for setup checks, DR meaning, and common actions. For detailed explanations, see the [Device Overview](#device-overview).

## 1) UART Summary

See the [Wiring Guide](#wiring) for full diagrams.

- GNSS and STM32: `A2/A3`
- FC MAVLink and STM32: `A9/A10` (MAVLink2 @ 115200)
- FC GPS and STM32: `A11/A12` on F401 or `C6/C7` on H743 UART builds (typically 460800)
- H743 DroneCAN: GNSS `A2/A3`, OpenIPC camera `PA10` RX / `PA9` TX, CAN
  transceiver `PB8/PB9`; USB-C remains on `A11/A12`

The H743 DroneCAN firmware has no physical FC MAVLink or FC GPS UART.
ArduPilot should see native DroneCAN GPS (`GPS1_TYPE=9`), camera MAVLink2 on
S1/index `0`, and the filter's MAVLink2 plus returning FC telemetry on S2/index
`1`. Use [H743 DroneCAN Guide](13_h743_dronecan.md) for the complete setup path.

## 2) Receiver Mode (`GNSS_TYPE`)

- `GNSS_TYPE=0`: u-blox/UBX mode.
- `GNSS_TYPE=1`: UM980/UM981/UM982 NMEA mode. Requires one-time setup — see [Receiver Config](#receiver-config).
- `GNSS_TYPE=2`: Septentrio Mosaic X5 mode. H743 DroneCAN `v0.1.9+` can use SBF; UART builds use NMEA. Requires one-time setup — see [Receiver Config](#receiver-config).
- `FCGPS_UART=1`: FC GPS UART pins active (F401 `A11/A12`, H743 UART `C6/C7`; normal operation, default).
- `FCGPS_UART=0`: FC GPS UART pins released into input mode. Do not use during flight.
- H743 DroneCAN `v0.1.4+` tuning is in Mission Planner
  `SETUP -> Optional Hardware -> DroneCAN/UAVCAN -> node 42 -> Params`.
- H743 DroneCAN `v0.1.5+` can also be tuned directly over USB-C by connecting
  Mission Planner to the H743 COM port at `115200`.
- H743 DroneCAN `v0.2.0+` also supports MAVLink parameter access through the
  configured S2/index `1` virtual port.
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

**H743 camera or filter MAVLink is missing:**

1. Set `CAN_Dx_UC_SER_EN=1` on the active CAN driver
2. Configure S1 as node `42` / index `0` / baud `115` / protocol `2`
3. Configure S2 as node `42` / index `1` / baud `115` / protocol `2`
4. Check camera TX -> `PA10`, `PA9` -> camera RX, 3.3 V logic, and common ground

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
[AirDroper Mission Planner Mod](https://gps.airdroper.org/download/mission-planner-mod)
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
| No fix / low satellites | — | No-fix: 3 distinct epochs spanning >=600 ms. Low sats: rolling ~3 s peak plus 3 low epochs >=200 ms apart |
| Position jump | `SP_ABS_M`, `SP_JMP_MPS` | Sudden large location step |
| SNR anomaly | `SNR_EN`, `SNR_HOLDMS` | Abnormal signal strength pattern |
| Receiver spoof verdict | — | `SEC-SIG`, H743 with supported u-blox only |
| Barometric vertical-rate divergence | — | Fresh FC barometer vs GNSS vertical velocity, DroneCAN builds only |
| Altitude anomaly | `ALT_*` | Large GNSS altitude jump/rate; absolute GPS/baro separation is disabled |
| EKF unhealthy | `EKF_TRIPMS` | Flight controller reports nav problems |
| South-hemisphere jump | — | Latitude goes below 0° — instant DR1 + hard block |
| Geo-fence | `FENCE_RAD` | Position outside radius (up to 2000 km) from first fix (v1.5.5+) |
| Heading reversal | — | 3 reversed epochs: gaps <=2.5 s, all within 5 s; then 1.5 s score hold |
| GPS time anomaly | — | >2 s drift between GPS and internal clock (v1.5.5+) |
| Clock bias jump | — | Sudden receiver clock jump, u-blox only (v1.5.5+) |
| Velocity-position mismatch | — | Velocity doesn't match position change (v1.5.5+) |

See [Tuning](#tuning) to adjust these thresholds.

## 7b) Spoofing Confidence Score (v1.5.5+)

The filter computes `DR_CONF` (0–100) from up to 10 detection signals. Visible
in Mission Planner named-value telemetry and event logs. Unavailable rows are
excluded from the weighted denominator.

| Signal | Weight | Availability note |
|--------|--------|-------------------|
| Barometer-vs-GNSS vertical rate | 20 | DroneCAN build + fresh FC barometer/GNSS velocity |
| SNR span | 20 | All supported receiver modes with fresh C/N0/SNR |
| Receiver spoof verdict | 25 | H743 + supported u-blox `SEC-SIG` only |
| Pseudorange residual | 15 | u-blox `NAV-SAT` only |
| SNR temporal correlation | 12 | u-blox, partial NMEA, Mosaic SBF |
| Heading reversal | 12 | All supported receiver modes |
| GDOP jump | 8 | u-blox `NAV-DOP` only |
| GPS time sanity | 12 | All supported receiver modes |
| Velocity-position consistency | 10 | All; partial on passive NMEA |
| Clock bias jump | 11 | u-blox and Mosaic SBF |

## 8) Status Log Messages

In Mission Planner `Messages`, filter status appears about every **10 seconds** (configurable via `LOG_MS`):

```
data=... fix=... nav=... SATS=... SNR=...
ARM=... DR=... BLEND=... LAT=... LONG=...
```

H743 DroneCAN `v0.2.0+` carries these messages on S2/index `1`. Both S1 and S2
remain active in DR1 even while `Fix2/Auxiliary` GPS publishing is blocked.

See [Operation](#operation) for how to interpret these messages.

## 9) Fuel messages and what to do about them

Fuel estimation is H743 DroneCAN `v0.5.28+`. It is an estimate from a propeller
model, and on an airframe with no fuel-level sensor it is the only fuel
indication there is - so every message below is worth reading rather than
dismissing.

| Message | Meaning | Do this |
|---------|---------|---------|
| `RPM sensor lost - fuel charged at max burn` | The RPM reading is gone; the burn is now charged at the engine's RATED power. Deliberately a large over-report. | Land on the clock, not on the gauge. Check the pickup wiring. |
| `Fuel held up by throttle - check RPM_SCALING` | The throttle says more power than the RPM implies, so a floor is propping the estimate up. The usual cause is the wrong pulses-per-revolution. | **Check `RPM1_SCALING` against a hand tachometer before flying again.** |
| `Main loop stalled - fuel charged at max burn` | A scheduling gap over 10 s was billed at rated power rather than dropped. | Note it. Repeated occurrences are worth reporting. |
| `Reset in flight - fuel total kept: N g` | The board rebooted and the running total was recovered from backup SRAM. | Nothing. This is the mechanism working. |
| `Fuel total LOST - write FUEL_CAPG to restart it` | Any boot, including a normal power-on, had no trustworthy V2 backup record, or the H743 tune journal had no valid record. ICE Status stops, so the FC's EFI backend ages stale/unhealthy; the warning ladder is muted. Repeats every 60 s. | Land or remain on the ground, verify the fuel configuration, wait for fresh stopped-engine quorum (disarmed + valid zero RPM + closed throttle), then rewrite `FUEL_CAPG` for the fuel actually aboard even if its numerical value is unchanged. A changed value resumes EFI only after `Tune saved`; disarmed alone is rejected. |
| `Fuel total kept: N g - re-set FUEL_CAPG if refuelled` | The record survived something that looked like a power cycle. | If you refuelled, write `FUEL_CAPG`. If not, ignore. |
| `FUEL_CAPG blocked: engine not confirmed stopped` | One or more stopped-engine inputs is missing, stale, or contradictory; disarmed alone cannot prove a piston engine stopped. | Stop the engine and keep FC telemetry connected until disarmed, valid zero RPM, and closed throttle are all fresh, then write again. |
| `FUEL_CAPG blocked: wait for FUEL_DENS save` | A real density change is still awaiting verified tune-journal persistence. Fuel remains TOTAL LOST. | Do not keep retrying capacity. Wait for `Tune saved`; `Tune save failed` remains blocked. After success, write `FUEL_CAPG` under fresh stopped-engine quorum. |
| `FUEL_DENS blocked: engine not confirmed stopped` | Density edits use the same stopped-engine safety gate. | Obtain the same fresh disarmed + zero-RPM + closed-throttle quorum, then write again. |
| `FUEL_CAPG written - fuel total zeroed` | Confirmation that the write was accepted and the running counter was reset. It is not proof that a changed capacity is durable. | If the numerical value changed, remain on the ground until `Tune saved`; `Tune save failed` means EFI remains silent. |
| `FUEL est NN% usable left` | Warning ladder: 30% of usable is WARNING, 10% is CRITICAL. | Usable is `FUEL_CAPG` minus a 20% reserve, not the whole tank. |

**Writing `FUEL_CAPG` is the only thing that zeroes the running total.** Write
it after every refuel and after any normal power-on that reports TOTAL LOST,
even when the number has not changed. It is accepted only when disarmed, valid
zero RPM, and closed throttle are all fresh. A changed value remains TOTAL LOST
and EFI-silent until its asynchronous tune-journal save succeeds.

Any factory-reset attempt marks the fuel total LOST before flash work begins;
even a failed attempt may conservatively leave it there. Verify all fuel-model
settings and repeat the stopped-engine `FUEL_CAPG` procedure afterward.

An actual `FUEL_DENS` change also marks TOTAL LOST before applying the new
density and cancels any older pending capacity commit. Until verified density
save succeeds, `FUEL_CAPG` is blocked; save failure stays blocked/LOST. After
`Tune saved`, EFI is still silent until you write `FUEL_CAPG` under the same
fresh quorum to establish a new zero.

Fuel accounting continues through FC telemetry loss and an unknown/unsupported
FC-version block. Every boot sets the engine-may-be-running latch; missing RPM
is charged at rated power until fresh disarmed state, zero RPM, and closed
throttle all confirm a stop. Link silence and a `FUEL_CAPG` write cannot clear
it.

See [Tuning](06_tuning.md) for the model, the calibration procedure, and the
two cases that can still under-report.
