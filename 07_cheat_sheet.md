# Cheat Sheet (Field Quick Reference)



This is a one-page quick reference for setup checks, DR state meaning, and common actions.



## 1) UART Summary



- GNSS and STM32: `A2/A3` (UBX @ 460800)

- FC MAVLink and STM32: `A9/A10` (MAVLink2 @ 115200)

- FC GPS and STM32: `A11/A12` (UBX @ 460800)



## 2) DR Modes



- **DR0**: normal mode. GNSS is forwarded to the FC GPS UART.

- **DR1**: protection mode. GNSS forwarding to the FC GPS UART is blocked.

- **B5**: pulses high for ~3 s on each DR0 to DR1 transition.



## 3) Quick Diagnostics



If FC shows **"No GPS config data"**:



- Check FC GPS UART protocol/baud.

- Check `A11/A12` wiring (cross TX/RX).

- Confirm common ground.



If you see **GNSS jumps on the GCS map**:



- This can be GNSS spoofing shown by the GCS, not the FC EKF position.

- Use the DR state and filter logs as the primary reference.



If **DR1 remains active**:



- Check guard arming thresholds (`ARM_*`) and GNSS quality.

- Check SNR guard settings (`SNR_*`) if enabled.



## 4) tune_cli Commands



List params:



```bash

python tools/tune_cli.py --port COM12 --baud 115200 list

```



Read one param:



```bash

python tools/tune_cli.py --port COM12 --baud 115200 get BLEND_MS

```



Set one param:



```bash

python tools/tune_cli.py --port COM12 --baud 115200 set RJ_BASE_M 180

```



Export profile:



```bash

python tools/tune_cli.py --port COM12 --baud 115200 export tune_baseline.json

```



Import profile:



```bash

python tools/tune_cli.py --port COM12 --baud 115200 import tune_baseline.json

```



## 5) Common DR1 Trigger Examples



- Position jump: large step > `SP_ABS_M` or speed > `SP_JMP_MPS`.

- SNR spread: if `SNR_EN=1` and spread is too narrow for > `SNR_HOLDMS`.

- Altitude: large jump (`ALT_JMP_M`) or excessive rate (`ALT_RMPS`).



## 6) Recovery (Phase-B Updates)



Flash order:



1) bootloader at `0x08000000`

2) app at `0x08008000`

3) boot_meta at `0x08007C00`



See `08_recovery.md` for full steps.

