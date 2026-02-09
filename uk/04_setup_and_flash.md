# Інструкція з налаштування та прошивки

## 1) Передумови

- Встановлено PlatformIO CLI.
- Підключено STM32F401 BlackPill для прошивки.
- Прошивка FC: **ArduPilot 4.6.1 або новіший**, вхід GPS — **UBX (u-blox)**.
- Перед встановленням фільтра **має бути робочий GPS для первинних калібрувань**:
  - відкалібрований акселерометр

  - відкалібрований компас

  - інакше **EKF flags trip** може залишатись активним і FC не повернеться в DR0

- Польотний контролер налаштовано з:

  - одним телеметрійним UART для MAVLink2

  - одним GPS UART для UBX

## 2) Збірка прошивки

У корені репозиторію:

```bash

platformio run

```

## 3) Прошивка

```bash

platformio run -t upload

```

## 3.1) Необов’язкова збірка Phase-B Secure Boot

Збірка secure-boot образів:

```bash

platformio run -e blackpill_f401cc_phaseb_bootloader

platformio run -e blackpill_f401cc_phaseb_app

```

Адреси прошивки Phase-B:

- bootloader: `0x08000000`

- phase-B app: `0x08008000`

- signed metadata (`tools/updater/sign_phaseb.py`): `0x08007C00`

## 4) Налаштування UART на FC (ArduPilot)

Використайте два UART-порти FC:

1. **MAVLink-порт (до STM32 `A9/A10`)**

   - `SERIALx_PROTOCOL = 2` (MAVLink2)

   - `SERIALx_BAUD = 115` (115200)

2. **GPS UART (до STM32 `A11/A12`)**

   - `SERIALy_PROTOCOL = 5` (GPS)

   - `SERIALy_BAUD = 460` (460800)

Тип GPS на стороні FC має бути u-blox.

Встановіть такі параметри ArduPilot для GPS:

- GPS_AUTO_SWITCH = 0

- GPS1_TYPE = 2 (u-blox)

- GPS_AUTO_CONFIG = 0

## 5) Очікувана поведінка фільтра

- `SYSID` фільтра = `42`, `COMPID` = onboard computer (`191`).

- Фільтр блокує подачу GNSS до FC, **перекриваючи пересилання UBX на GPS UART FC**.

- Під час DR1 пересилання UBX на GPS UART FC вимкнене (якщо не ввімкнено debug override у коді).

## 6) Перевірки після першого запуску

У повідомленнях GCS перевірте, що є:

- boot-повідомлення фільтра

- ростуть лічильники GNSS NAV

- немає попередження про стару прошивку

Якщо FC пише **"No GPS config data"**:

- перевірте протокол/швидкість GPS UART на FC;

- перевірте перехресне підключення `A11/A12` (TX/RX);

- перевірте спільну землю.

