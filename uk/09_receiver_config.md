# Конфігурація GNSS-приймача

Встановіть `GNSS_TYPE` у Mission Planner відповідно до вашого приймача, потім перезавантажте STM32.

| `GNSS_TYPE` | Сімейство приймачів | ArduPilot `GPS1_TYPE` |
|---|---|---|
| `0` | u-blox M8 / M9 / M10 | `1` (AUTO) або `2` (u-blox) |
| `1` | Unicore UM980 / UM981 | `24` (UnicoreNMEA) |

---

## UM980 / UM981

**Ручна попередня конфігурація не потрібна.** При `GNSS_TYPE=1` STM32 автоматично
надсилає повний профіль конфігурації до UM980 через COM1 при кожному завантаженні —
так само, як він автоматично конфігурує u-blox приймачі. Режим роботи приймача,
налаштування anti-jam та всі вихідні повідомлення застосовуються і зберігаються
в енергонезалежній пам'яті UM980.

### Налаштування фільтра STM32 для UM980

| Параметр | Значення | Примітки |
|---|---|---|
| `GNSS_TYPE` | `1` | Вибирає шлях UM980/UM981, перезавантаження для застосування |
| `UM980_HIGHDYN` | `0` | Стандартний режим UAV (за замовчуванням) |
| `UM980_HIGHDYN` | `1` | Режим UAV з високою динамікою — для агресивних платформ |
| `UBX_BAUD` | `0` | Залишити за замовчуванням (не використовується для UM980) |

Після зміни `UM980_HIGHDYN` перезавантажте STM32, щоб нова команда
`MODE ROVER UAV [HIGHDYN]` була надіслана до приймача.

### Налаштування ArduPilot FC для UM980

| Параметр | Значення |
|---|---|
| `GPS1_TYPE` | `24` (UnicoreNMEA) |
| `SERIAL3_BAUD` (серійний порт GPS1) | `460` |

### Що застосовує авто-конфігурація

Наступний профіль надсилається до UM980 при кожному завантаженні:

```text
UNLOG COM1

MODE ROVER UAV          (або MODE ROVER UAV HIGHDYN якщо UM980_HIGHDYN=1)
CONFIG ANTIJAM FORCE
CONFIG MMP ENABLE
CONFIG PVTALG MULTI
CONFIG SMOOTH PSRVEL ENABLE
MASK 5
CONFIG NMEA0183 V410

AGRICA COM1 1
GNGGA COM1 1
GPGGA COM1 1
GPRMC COM1 1
GPGSA COM1 1
GPGSV COM1 1
GPGBS COM1 1
GPGST COM1 1
PVTSLNB COM1 1
OBSVMCMPB COM1 0.1
SATSINFOB COM1 1
BESTSATB COM1 1
STADOPB COM1 1
JAMSTATUSB COM1 1
FREQJAMSTATUSB COM1 1
HWSTATUSB COM1 1
AGCB COM1 1
RTKSTATUSB COM1 1
RTCMSTATUSB COM1 ONCHANGED

SAVECONFIG
```

### Примітки

- `GPGGA`, `GPRMC`, `PVTSLNB` та `AGRICA` налаштовані на **1 Гц**.
  Значення 0.1 Гц призводить до того, що ArduPilot час від часу показує
  "GPS 1: not healthy", оскільки watchdog таймаут стану GPS перевищується
  між 10-секундними оновленнями.
- `GNGGA` також увімкнений на 1 Гц, щоб фільтр бачив кількість супутників по всіх
  сузір'ях, а `GPGGA` залишається увімкненим для сумісності з FC.
- `GPGSV` використовується лише для SNR-даних. Low-sat guard у фільтрі бере
  кількість супутників у рішенні з `GGA`, а не кількість видимих супутників з `GSV`.
- `COM2` не потрібен для фільтра. Залиште невикористаним або використовуйте для діагностики.
- Авто-конфігурація **не змінює** швидкість передачі COM1. STM32 визначає
  поточну швидкість приймача через autobaud; ця швидкість зберігається через `SAVECONFIG`.
  Заводська швидкість UM980 — 460800, тому для нового приймача жодних дій не потрібно.

---

## u-blox M8 / M9 / M10

STM32-фільтр автоматично конфігурує u-blox приймачі через протокол UBX при запуску.
Ручна конфігурація приймача не потрібна.

### Стандартний профіль авто-конфігурації (рекомендовано, `UBX_BAUD = 0`)

За можливості залиште u-blox на заводських налаштуваннях. Під час boot фільтр
сканує поширені baud rate і багаторазово надсилає таку портову команду, доки
приймач не перейде на `460800`:

```text
UBX-CFG-PRT    UART1 460800 8N1 in=UBX out=UBX
```

Після того як фільтр перемкнув власний UART на `460800`, він застосовує такий
ACK-перевірений профіль:

```text
UBX-CFG-MSG    NMEA-GGA  off
UBX-CFG-MSG    NMEA-GLL  off
UBX-CFG-MSG    NMEA-GSA  off
UBX-CFG-MSG    NMEA-GSV  off
UBX-CFG-MSG    NMEA-RMC  off
UBX-CFG-MSG    NMEA-VTG  off
UBX-CFG-MSG    NMEA-ZDA  off

UBX-CFG-RATE   measRate=100ms navRate=1 timeRef=GPS
UBX-CFG-MSG    NAV-PVT     rate=1
UBX-CFG-MSG    NAV-POSLLH  rate=1
UBX-CFG-MSG    NAV-STATUS  rate=2
UBX-CFG-MSG    NAV-VELNED  rate=2
UBX-CFG-MSG    NAV-DOP     rate=2
UBX-CFG-MSG    NAV-SOL     rate=2
UBX-CFG-MSG    NAV-SAT     rate=2

UBX-CFG-TMODE3 mode=disabled
UBX-CFG-CFG    save current configuration to BBR/Flash
```

Нічого робити з боку приймача не потрібно.

### Примітки до стандартного авто-конфігу

- `NAV-PVT` і `NAV-POSLLH` працюють на 10 Гц. `NAV-STATUS`, `NAV-VELNED`, `NAV-DOP`,
  `NAV-SOL` і `NAV-SAT` працюють на 5 Гц.
- `UBX-CFG-PRT` надсилається під час autobaud-сканування; решта профілю проходить
  ACK-перевірку вже після переходу лінка на `460800`.
- Цей шлях робить UART приймача UBX-only. На FC залишайте тип GPS `AUTO` або
  `u-blox`, а не NMEA.

### Ручний режим baud (`UBX_BAUD` встановлено)

Використовуйте якщо u-blox повинен залишатися на фіксованій швидкості
(наприклад, інший пристрій підключений до того ж порту).

1. Попередньо налаштуйте u-blox в u-center з бажаною швидкістю передачі.
2. Увімкніть UBX-вивід і вимкніть NMEA на UART, підключеному до фільтра.
3. Увімкніть **NAV-PVT** мінімум на 10 Гц. NAV-DOP та NAV-SAT на 5 Гц рекомендовано.
4. Встановіть `UBX_BAUD` у Mission Planner та перезавантажте.

Під час boot фільтр у цьому режимі робить лише best-effort volatile запит на:

```text
UBX-CFG-RATE   measRate=100ms navRate=1 timeRef=GPS
UBX-CFG-MSG    NAV-PVT  rate=1
UBX-CFG-MSG    NAV-DOP  rate=2
UBX-CFG-MSG    NAV-SAT  rate=2
```

У ручному режимі він **не** змінює baud UART1, **не** вимикає NMEA і **не**
зберігає конфігурацію в BBR/Flash.

### Налаштування фільтра STM32 для u-blox

| Параметр | Значення |
|---|---|
| `GNSS_TYPE` | `0` |
| `UBX_BAUD` | `0` для авто, або точний baud (наприклад, `460800`) для ручного режиму |

### Налаштування ArduPilot FC для u-blox

| Параметр | Значення |
|---|---|
| `GPS1_TYPE` | `1` (AUTO) або `2` (u-blox binary) |
| `SERIAL3_BAUD` (серійний порт GPS1) | `460` |

Фільтр пересилає сирий UBX binary потік на GPS порт FC —
встановіть тип GPS на u-blox або AUTO, не NMEA.
