# Швидка довідка (польові перевірки)

> Де купити плату: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

Це односторінкова довідка для швидких перевірок, режимів DR та типових дій. Для детальних пояснень див. [Огляд пристрою](#device-overview).

## 1) Підсумок UART

Див. [Схема підключення](#wiring) для повних діаграм.

- GNSS і STM32: `A2/A3`
- FC MAVLink і STM32: `A9/A10` (MAVLink2 @ 115200)
- FC GPS і STM32: `A11/A12` на F401 або `C6/C7` на H743 UART-збірці (зазвичай 460800)
- H743 DroneCAN: GNSS `A2/A3`, OpenIPC camera `PA10` RX / `PA9` TX, CAN
  transceiver `PB8/PB9`; USB-C лишається на `A11/A12`

H743 DroneCAN-прошивка не має фізичних FC MAVLink або FC GPS UART. ArduPilot
має бачити native DroneCAN GPS (`GPS1_TYPE=9`), camera MAVLink2 на S1/index
`0`, а MAVLink2 фільтра та зворотну FC telemetry — на S2/index `1`.

## 2) Режим приймача (`GNSS_TYPE`)

- `GNSS_TYPE=0`: режим u-blox/UBX.
- `GNSS_TYPE=1`: режим UM980/UM981/UM982 NMEA. Потребує одноразового налаштування — див. [Конфігурація приймача](#receiver-config).
- `GNSS_TYPE=2`: режим Septentrio Mosaic X5. H743 DroneCAN може використовувати SBF; UART-збірки використовують NMEA. Потребує одноразового налаштування — див. [Конфігурація приймача](#receiver-config).
- `FCGPS_UART=1`: FC GPS UART-піни активні (F401 `A11/A12`, H743 UART `C6/C7`; нормальна робота, за замовчуванням).
- `FCGPS_UART=0`: FC GPS UART-піни переведені у вхідний режим. Не використовуйте під час польоту.
- У H743 DroneCAN `v0.1.4+` tuning відкривається в Mission Planner:
  `SETUP -> Optional Hardware -> DroneCAN/UAVCAN -> node 42 -> Params`.
- У H743 DroneCAN `v0.1.5+` tuning також доступний напряму через USB-C:
  Mission Planner -> H743 COM port -> `115200`.
- У H743 DroneCAN `v0.2.0+` MAVLink parameters також доступні через
  налаштований virtual port S2/index `1`.
- Для `GNSS_TYPE=1` або `GNSS_TYPE=2` використовуйте лише один фізичний NMEA-потік:
  - потік приймача -> STM32 `A2/A3`
  - UART-збірки пересилають цей потік на FC GPS UART; H743 DroneCAN публікує
    розібраний fix як native `Fix2/Auxiliary`
- Після зміни `GNSS_TYPE` перезавантажте STM32 (`NRST` або повне вимкнення/увімкнення).
- Для кастомного u-blox без автоконфігу:
  - задайте `UBX_BAUD` як baud приймача (`0` означає автоконфіг ON),
  - перезавантажте STM32 для застосування.
- Для gateway / dual-F9P модулів на кшталт Quadro GPS, UNA3 та UNA4-SFE:
  - використовуйте `GNSS_TYPE=0`,
  - задавайте точний `UBX_BAUD`,
  - не використовуйте autobaud фільтра.

## 3) Режими DR

- **DR0**: штатний режим — GPS-дані передаються на контролер польоту.
- **DR1**: захисний режим — GPS заблоковано, FC використовує dead-reckoning.
- **B5**: високий імпульс (~3 с) на кожен перехід DR0 -> DR1 (підключіть LED або зумер).

Див. [Огляд пристрою](#device-overview) для повного пояснення.

## 4) Швидка діагностика

**FC показує "No GPS config data":**

1. Перевірте протокол і baud GPS UART на FC — див. [Схема підключення](#wiring)
2. Перевірте перехресне TX/RX підключення `A11/A12` на F401 або `C6/C7` на H743 UART-збірці
3. Перевірте спільну землю

**H743 DroneCAN GPS не з'являється:**

1. Перевірте CAN bitrate `1000000` і `GPS1_TYPE=9`
2. Перевірте `PB9 -> TXD`, `PB8 -> RXD`, `CANH/CANL/GND`
3. Перевірте termination тільки на фізичних кінцях CAN-шини

**H743 camera або filter MAVLink відсутній:**

1. Встановіть `CAN_Dx_UC_SER_EN=1` на активному CAN driver
2. Налаштуйте S1: node `42` / index `0` / baud `115` / protocol `2`
3. Налаштуйте S2: node `42` / index `1` / baud `115` / protocol `2`
4. Перевірте camera TX -> `PA10`, `PA9` -> camera RX, 3.3 V logic і common ground

**DR1 не вимикається:**

1. Перевірте no-fix / низьку кількість супутників
2. Перевірте пороги захистів — див. [Тюнінг](#tuning) для параметрів `ARM_*`, `SP_*`, `ALT_*`, `SNR_*`
3. Збільшіть `BOOT_DLYMS`, якщо хибний DR1 з'являється одразу після старту

**FC постійно показує "No Fix":**

- Перевірте, чи AUX-логіка RC не примусово вимикає GPS у налаштуваннях FC
- Див. [Діагностика підключення](#wiring-debug) для покрокового усунення несправностей

## 5) Схема запису параметрів у Mission Planner

1. `Config/Tuning` -> `Full Parameter List`.
2. Виберіть STM32 (`SYSID 42`).
3. Натисніть `Refresh Params`.
4. Змініть значення — див. [Тюнінг](#tuning) для опису параметрів
5. Натисніть `Write Params`
6. Натисніть `Refresh Params` для перевірки

Необов'язково, але рекомендовано: спочатку встановіть
[AirDroper Mission Planner Mod](https://gps.airdroper.org/download/mission-planner-mod),
щоб Mission Planner показував описи, діапазони, одиниці та підписи варіантів,
а не лише сирі назви параметрів.

## 6) Правила запису параметрів

- Читання і запис параметрів виконуються у Mission Planner (Full Parameter List).
- Якщо значення не записалося з першого разу, натисніть `Write Params` повторно. 1-2 спроби — норма; 3+ вказує на перевантажений MAVLink-лінк.
- Після запису можливе коротке відновлення телеметрії до 30-45 секунд.
- Для `GNSS_TYPE` і `UBX_BAUD` потрібен reboot STM32.
- Для більшості інших параметрів reboot не потрібен.

## 7) Типові тригери DR1

| Тригер | Параметри | Поведінка |
|--------|-----------|-----------|
| No-fix / мало супутників | — | No-fix: 3 різні епохи за >=600 мс. Low sats: rolling ~3 с peak і 3 low епохи з інтервалом >=200 мс |
| Стрибок позиції | `SP_ABS_M`, `SP_JMP_MPS` | Різкий великий стрибок координат |
| Аномалія SNR | `SNR_EN`, `SNR_HOLDMS` | Аномальний розподіл рівня сигналів |
| Receiver spoof verdict | — | `SEC-SIG`, лише H743 з підтримуваним u-blox |
| Розходження vertical rate баро та GNSS | — | Свіже FC barometer проти GNSS vertical velocity, лише DroneCAN build |
| Аномалія висоти | `ALT_*` | Великий стрибок або аномальна швидкість висоти |
| Невалідний EKF | `EKF_TRIPMS` | FC повідомляє проблему навігації |
| Південна півкуля | — | Latitude <0°: миттєвий DR1 і hard block |
| Гео-огорожа | `FENCE_RAD` | Позиція поза радіусом до 2000 км від першого fix |
| Розворот курсу | — | 3 reversed епохи: gaps <=2,5 с, усі за 5 с; потім 1,5 с score hold |
| Аномалія часу GPS | — | Різниця понад 2 с між GPS та internal clock |
| Стрибок clock bias | — | u-blox або Mosaic SBF |
| Velocity-position mismatch | — | Швидкість не відповідає зміні позиції |

## 7b) Оцінка достовірності спуфінгу (v1.5.5+)

Фільтр обчислює `DR_CONF` (0–100) з до 10 сигналів. Бал видно в Mission
Planner та event logs. Недоступні рядки не входять до зваженого знаменника.

| Сигнал | Вага | Примітка про доступність |
|--------|------|--------------------------|
| Vertical rate баро проти GNSS | 20 | DroneCAN build + свіже FC barometer/GNSS velocity |
| SNR span | 20 | Усі підтримувані режими зі свіжим SNR/C/N0 |
| Receiver spoof verdict | 25 | Лише H743 + підтримуваний u-blox `SEC-SIG` |
| Pseudorange residual | 15 | Лише u-blox `NAV-SAT` |
| SNR temporal correlation | 12 | u-blox, partial NMEA, Mosaic SBF |
| Розворот курсу | 12 | Усі підтримувані режими |
| GDOP jump | 8 | Лише u-blox `NAV-DOP` |
| GPS time sanity | 12 | Усі підтримувані режими |
| Velocity-position consistency | 10 | Усі; partial на passive NMEA |
| Clock bias jump | 11 | u-blox і Mosaic SBF |

## 8) Частота логів у Mission Planner

- У вкладці Mission Planner `Messages` статус-логи STM32-фільтра зазвичай з’являються приблизно кожні **10 секунд**.
- Зазвичай поруч ідуть дві строки:
  - `data=... fix=... nav=... SATS=... SNR=...`
  - `ARM=... DR=... BLEND=... LAT=... LONG=...`

H743 DroneCAN `v0.2.0+` передає ці повідомлення через S2/index `1`. S1 та S2
лишаються активними в DR1, навіть коли GPS `Fix2/Auxiliary` заблоковано.

Див. [Робота](#operation) для пояснення цих повідомлень.

## 9) Повідомлення про паливо і що з ними робити

Оцінка витрати палива — це H743 DroneCAN `v0.5.28+`. Це оцінка за моделлю
гвинта, і на літаку без датчика рівня палива вона є єдиним покажчиком палива —
тож кожне повідомлення нижче варто прочитати, а не відмахнутися від нього.

| Повідомлення | Що це означає | Що робити |
|--------------|---------------|-----------|
| `RPM sensor lost - fuel charged at max burn` | Показань обертів немає; витрата нараховується за НОМІНАЛЬНОЮ потужністю. Свідоме значне завищення. | Сідайте за годинником, а не за покажчиком. Перевірте проводку датчика. |
| `Fuel held up by throttle - check RPM_SCALING` | Газ показує більшу потужність, ніж випливає з обертів, тому оцінку підпирає «підлога». Звична причина — хибна кількість імпульсів на оберт. | **Звірте `RPM1_SCALING` з ручним тахометром, перш ніж летіти знову.** |
| `Main loop stalled - fuel charged at max burn` | Пауза планувальника понад 10 с була нарахована за номіналом, а не відкинута. | Занотуйте. Повторювані випадки варто повідомити. |
| `Reset in flight - fuel total kept: N g` | Плата перезавантажилась, і підсумок відновлено з резервної пам'яті. | Нічого. Механізм працює як задумано. |
| `Fuel total LOST - write FUEL_CAPG to restart it` | При будь-якому boot, включно зі звичайним вмиканням, не було надійного V2 backup record або H743 tune journal не мав valid record. ICE Status припиняється, тому EFI backend FC стає stale/unhealthy; warning ladder мовчить. Повторюється кожні 60 с. | Сідайте або лишайтеся на землі, перевірте fuel configuration, дочекайтеся fresh stopped-engine quorum (disarmed + valid zero RPM + closed throttle), тоді повторно запишіть `FUEL_CAPG` для фактичного палива, навіть якщо його числове значення не змінилося. Змінене значення відновить EFI лише після `Tune saved`; disarmed alone відхиляється. |
| `Fuel total kept: N g - re-set FUEL_CAPG if refuelled` | Запис пережив те, що виглядало як вимкнення живлення. | Якщо ви заправлялись — запишіть `FUEL_CAPG`. Якщо ні — ігноруйте. |
| `FUEL_CAPG blocked: engine not confirmed stopped` | Один або кілька stopped-engine inputs відсутні, stale чи суперечливі; disarmed alone не доводить, що поршневий двигун зупинився. | Зупиніть двигун і тримайте FC telemetry підключеною, доки disarmed, valid zero RPM і closed throttle не стануть fresh, тоді запишіть знову. |
| `FUEL_CAPG blocked: wait for FUEL_DENS save` | Фактична зміна густини ще чекає verified persistence tune journal. Fuel лишається TOTAL LOST. | Не повторюйте запис місткості без кінця. Дочекайтеся `Tune saved`; після `Tune save failed` стан лишається blocked. Після успіху запишіть `FUEL_CAPG` за fresh stopped-engine quorum. |
| `FUEL_DENS blocked: engine not confirmed stopped` | Зміна густини використовує той самий stopped-engine safety gate. | Отримайте той самий fresh quorum disarmed + zero RPM + closed throttle, тоді запишіть знову. |
| `FUEL_CAPG written - fuel total zeroed` | Підтвердження, що запис прийнято й running counter обнулено. Це не доводить durability зміненої місткості. | Якщо числове значення змінилося, лишайтеся на землі до `Tune saved`; `Tune save failed` означає, що EFI далі мовчить. |
| `FUEL est NN% usable left` | Драбина попереджень: 30% корисного — WARNING, 10% — CRITICAL. | Корисне — це `FUEL_CAPG` мінус 20% резерву, а не весь бак. |

**Запис `FUEL_CAPG` — єдине, що обнуляє накопичений підсумок.** Робіть це після
кожної заправки та після звичайного вмикання, яке повідомляє TOTAL LOST, навіть
якщо число не змінилося. Запис приймається лише коли disarmed, valid zero RPM і
closed throttle усі fresh. Змінене значення лишається TOTAL LOST і EFI-silent,
доки asynchronous save tune journal не завершиться успішно.

Будь-яка спроба factory reset позначає fuel total як LOST до початку flash work;
навіть failed attempt може консервативно лишити його таким. Після цього перевірте
всі settings fuel model і повторіть stopped-engine процедуру `FUEL_CAPG`.

Фактична зміна `FUEL_DENS` також позначає TOTAL LOST до застосування нової
густини й скасовує старий pending capacity commit. До успішного verified save
density запис `FUEL_CAPG` blocked; save failure лишається blocked/LOST. Після
`Tune saved` EFI все ще мовчить, доки ви не запишете `FUEL_CAPG` за тим самим
fresh quorum, щоб установити новий zero.

Облік палива триває крізь втрату телеметрії FC і блок через невідому/непідтримувану
версію FC. Кожен boot установлює latch «двигун міг працювати»; відсутні RPM
нараховуються за номінальною потужністю, доки одночасно fresh disarmed state,
нульові RPM і закритий газ не підтвердять зупинку. Тиша лінку й запис
`FUEL_CAPG` не очищають latch.

Див. [Налаштування](06_tuning.md) для моделі, процедури калібрування і двох
випадків, які все ще можуть занизити оцінку.
