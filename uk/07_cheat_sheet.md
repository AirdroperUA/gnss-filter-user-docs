﻿﻿# Cheat Sheet (швидка довідка для поля)

Це односторінкова довідка для швидких перевірок, DR-станів та типових дій.

## 1) Підсумок UART

- GNSS і STM32: `A2/A3` (UBX @ 460800)

- FC MAVLink і STM32: `A9/A10` (MAVLink2 @ 115200)

- FC GPS і STM32: `A11/A12` (UBX @ 460800)

## 2) Режими DR

- **DR0**: нормальний режим. GNSS пересилається на GPS UART FC.

- **DR1**: захисний режим. Пересилання GNSS на GPS UART FC заблоковано.

- **B5**: імпульс high ~3 с на кожен перехід DR0 → DR1.

## 3) Швидка діагностика

Якщо FC показує **"No GPS config data"**:

- перевірте протокол/baud GPS UART на FC;

- перевірте проводку `A11/A12` (TX/RX перехрещені);

- перевірте спільну землю.

Якщо на карті GCS видно **стрибки GNSS**:

- це може бути спуфінг, показаний GCS, а не позиція EKF.

- орієнтуйтесь на DR-стан і логи моста.

Якщо **DR1 залишається активним**:

- перевірте пороги армінгу (`ARM_*`) і якість GNSS.

- перевірте SNR-настройки (`SNR_*`), якщо увімкнено.

## 4) Команди `tune_cli`

Список параметрів:

```bash

python tools/tune_cli.py --port COM12 --baud 115200 list

```

Читання одного параметра:

```bash

python tools/tune_cli.py --port COM12 --baud 115200 get BLEND_MS

```

Запис одного параметра:

```bash

python tools/tune_cli.py --port COM12 --baud 115200 set RJ_BASE_M 180

```

Експорт профілю:

```bash

python tools/tune_cli.py --port COM12 --baud 115200 export tune_baseline.json

```

Імпорт профілю:

```bash

python tools/tune_cli.py --port COM12 --baud 115200 import tune_baseline.json

```

## 5) Типові приклади тригерів DR1

- Стрибок позиції: великий крок > `SP_ABS_M` або швидкість > `SP_JMP_MPS`.

- SNR розкид: якщо `SNR_EN=1` і розкид занадто вузький довше `SNR_HOLDMS`.

- Висота: великий стрибок (`ALT_JMP_M`) або надмірна швидкість (`ALT_RMPS`).

## 6) Відновлення (Phase-B оновлення)

Порядок прошивки:

1) bootloader на `0x08000000`

2) app на `0x08008000`

3) boot_meta на `0x08007C00`

Див. `08_recovery.md` для повної інструкції.

