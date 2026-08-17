# WeAct H743 DroneCAN

> Магазин плати: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

Ця сторінка описує окрему H743-версію для WeAct Studio MiniSTM32H743VITX
з 3.3 V CAN-трансивером SN65HVD230. У цій версії GNSS заходить у фільтр по
UART, а production/default build передає GPS і MS4525DO airspeed у польотний
контролер як native DroneCAN messages. У ньому HMC5983 driver compiled out;
compass публікується лише optional direct-flash `*_dronecan_mag` variant. MAVLink2 від OpenIPC camera і самого
фільтра йде через ту саму CAN-шину. Фізичні serial порти FC для MAVLink/GPS не
використовуються.

## Прошивка

Основні середовища:

| PlatformIO env | Призначення | Завантаження |
|----------------|-------------|--------------|
| `weact_mini_h743vitx_dronecan` | H743 DroneCAN GPS build | ST-Link/SWD |
| `weact_mini_h743vitx_dronecan_usb` | Та сама standalone прошивка | USB-C ROM DFU |
| `weact_mini_h743vitx_dronecan_mag` | Optional HMC5983-enabled DroneCAN build | ST-Link/SWD |
| `weact_mini_h743vitx_dronecan_mag_usb` | Той самий optional HMC5983-enabled build | USB-C ROM DFU |
| `weact_mini_h743vitx_dronecan_bootloader` | H743 secure bootloader | ST-Link/SWD |
| `weact_mini_h743vitx_dronecan_phaseb_app` | UID-patchable app template за адресою `0x08020000` | лише provisioner |
| `weact_mini_h743vitx_dronecan_phaseb_app_usb` | ідентичний build-validation template | лише provisioner |

Default direct-flash builds і обидва signed phase-B production templates
мають `FILTER_DRONECAN_HMC5983_ENABLE=0`; node 42 не публікує з них
`MagneticFieldStrength2`. Production/signed phase-B magnetometer variant зараз
немає. Вибирайте `*_dronecan_mag` лише для навмисної direct-flash інсталяції з
фізично встановленим HMC5983.

Значення за замовчуванням:

- DroneCAN node ID: `42`
- CAN bitrate: `1000000`
- CAN pins: `PB9` TX, `PB8` RX
- GNSS UART: `PA2` TX, `PA3` RX
- OpenIPC MAVLink2 UART: `PA10` RX, `PA9` TX, `115200`, 3.3 V logic
- спільна sensor I2C2 шина (`SENSOR_I2C`): `PB10` SCL, `PB11` SDA для default
  MS4525DO; HMC5983 може ділити її лише з `*_dronecan_mag` build
- два bidirectional `uavcan.tunnel.Targetted` порти: index `0` для camera,
  index `1` для MAVLink фільтра та FC telemetry
- USB-C залишається на `PA11/PA12`
- фізичні FC MAVLink serial і FC GPS serial вимкнені
- Parameters можна змінювати через Mission Planner DroneCAN node `42` у
  firmware `v0.1.4+`, або напряму через USB-C COM port H743 у firmware
  `v0.1.5+`

## Підключення всередині бокса

H743 не можна підключати напряму до CAN-порту польотного контролера. Піни
`PB8/PB9` є лише logic-level FDCAN сигналами, тому потрібен CAN-трансивер.

| Зв'язок | WeAct H743 | SN65HVD230 / зовнішній сигнал | Примітка |
|---------|------------|-------------------------------|----------|
| GNSS RX фільтра | `PA3` | GNSS TX | TX приймача у RX STM32 |
| GNSS TX фільтра | `PA2` | GNSS RX | TX STM32 у RX приймача |
| Camera TX до RX фільтра | `PA10` | OpenIPC camera TX | 3.3 V UART, cross TX -> RX |
| TX фільтра до camera RX | `PA9` | OpenIPC camera RX | 3.3 V UART, cross TX -> RX |
| Sensor I2C clock | `PB10` | MS4525DO `SCL`; optional HMC5983 `SCL` лише для `*_dronecan_mag` | I2C2, спільна шина |
| Sensor I2C data | `PB11` | MS4525DO `SDA`; optional HMC5983 `SDA` лише для `*_dronecan_mag` | I2C2, спільна шина |
| Sensor power | `3V3` | Sensor `VCC` | лише для підтверджених 3.3 V parts/modules |
| Sensor ground | `GND` | Sensor `GND` | спільна signal/power ground |
| CAN TX | `PB9` | `TXD` трансивера | FDCAN1_TX |
| CAN RX | `PB8` | `RXD` трансивера | FDCAN1_RX |
| CAN power | `3V3` | `VCC` трансивера | тільки 3.3 V модуль |
| Ground | `GND` | `GND` трансивера і FC CAN GND | спільна земля |
| CAN bus | трансивер | `CANH/CANL/GND` до FC | кручена пара для CANH/CANL |
| DR1 event | `PB5` | опційний LED/logger | 3.3 V pulse |
| USB-C | `PA11/PA12` | роз'єм USB-C на платі | не виводити ці піни в harness |

Camera і H743 повинні мати спільну signal ground. Не подавайте 5 V logic на
`PA9/PA10`. Живіть camera від окремого стабілізованого джерела, розрахованого
на camera/LTE load; ці UART піни не є виходом живлення.

Використовуйте 120 ohm termination на CAN-модулі тільки якщо H743 box стоїть
на фізичному кінці CAN-шини.

<a id="sensor-i2c-connector"></a>

### Окремий роз'єм SENSOR_I2C для airspeed/optional compass

HD-15 нижче вже повністю зайнятий. Не перепризначайте жоден його pin. Для
sensor I2C2 встановіть окремий keyed 4-pin роз'єм із чіткою міткою:

| Pin I2C-роз'єму | Сигнал | Всередині бокса | Sensor harness |
|-----------------|--------|----------------|----------------|
| 1 | `3V3_SENSOR` | захищена 3.3 V rail | VCC обох sensors, лише якщо вони 3.3 V-compatible |
| 2 | `GND` | box ground | GND обох sensors |
| 3 | `I2C2_SCL` | H743 `PB10` | SCL обох sensors |
| 4 | `I2C2_SDA` | H743 `PB11` | SDA обох sensors |

Перевірте numbering зі сторони mating face конкретного connector і key
housing так, щоб його не можна було вставити навпаки. До підключення sensor
перевірте pin 1 мультиметром. Default build використовує цю шину для MS4525DO.
Якщо навмисно використано direct-flash `*_dronecan_mag` build і HMC5983, обидва
sensor підключаються паралельно до однієї I2C-шини; вони не є CAN devices самі по собі.

Потрібен один ефективний комплект pull-ups SCL/SDA до **3.3 V** (типово
2.2-4.7 kohm залежно від capacitance harness). Багато breakout boards уже
мають pull-ups, тому перевірте повністю зібрану схему й не вмикайте паралельно
кілька занадто сильних комплектів. **Ніколи не використовуйте 5 V pull-ups**
на `PB10/PB11`. Тримайте harness коротким, подалі від motor/ESC та LTE power
wiring. I2C не призначений для довгого кабелю через весь апарат.

Default conversion MS4525 відповідає тільки повному TE ordering code
`4525DO-DS3AI001DP`: dual side ports, 3.3 V supply, transfer function A
(10-90% counts), I2C address `0x28`, bidirectional differential range
`-1..+1 psi` і negative pressure polarity, що відповідає ArduPilot pitot
convention у цій збірці. Перевірте **повне маркування/order code** sensor.
`DS5...`, інша address letter, інший pressure range, transfer function B,
absolute/gauge part або невідомий breakout не є drop-in replacement. Для них
треба змінити й заново перевірити firmware build settings voltage, address,
range, transfer function та polarity. На стенді подайте невеликий differential
pressure і переконайтесь, що FC показує зростання додатної airspeed; не
перевіряйте polarity вперше у польоті.

Лише optional direct-flash `*_dronecan_mag` builds вмикають magnetometer
driver. Він очікує HMC5983 за address `0x1E` та identification bytes
`H43`. Багато модулів, проданих як HMC5983, містять HMC5883-compatible або
невідомі clones. Лише відповідь на address scan не доводить тип. Firmware
відхиляє неправильний ID, але clone, що імітує `H43`, все одно може мати інші
gain/noise/temperature характеристики; використовуйте traceable part і
порівняйте його на стенді з відомим compass.

Для цього optional variant жорстко закріпіть HMC5983 і запишіть його axis orientation. Розташуйте його
якнайдалі від motors, magnets, steel fasteners, high-current battery/ESC wires,
switching regulators, CAN transceiver і camera/LTE radio. MS4525 та pitot hoses
тримайте подалі від prop wash, leaks, sharp bends і water traps.

<a id="optional-hd-15-d-sub-box-connector"></a>

## HD-15 D-sub pinout для зовнішнього harness

Якщо H743, CAN-трансивер, дисплей і захист живлення знаходяться всередині
одного бокса, назовні виводьте тільки HD-15 D-sub. Це не VGA-інтерфейс.
Підпишіть роз'єм як `CAN/GNSS/CAMERA/POWER`.

Нумерація показана з боку підключення кабелю до female panel connector:

```text
   1   2   3   4   5
    6   7   8   9  10
  11  12  13  14  15
```

| Pin | Сигнал на боксі | Користувач підключає до | Всередині бокса |
|-----|-----------------|-------------------------|-----------------|
| 1 | `CANH` | FC CANH | SN65HVD230 `CANH` |
| 2 | `CANL` | FC CANL | SN65HVD230 `CANL` |
| 3 | `CAN_GND` | FC CAN GND | box ground |
| 4 | `BOX_5V_IN_A` | FC/BEC 5 V | box 5 V input |
| 5 | `BOX_5V_IN_B` | optional parallel 5 V | same net as pin 4 |
| 6 | `BOX_GND_A` | FC/BEC ground | box ground |
| 7 | `GNSS_TX_TO_BOX` | GNSS TX | H743 `PA3` |
| 8 | `GNSS_RX_FROM_BOX` | GNSS RX | H743 `PA2` |
| 9 | `GNSS_VOUT_FUSED` | GNSS VCC/VIN | protected output from box |
| 10 | `GNSS_GND` | GNSS GND | box ground |
| 11 | `SHIELD` | cable shield/drain | shell/chassis or single-point ground |
| 12 | `DR1_EVENT` | optional LED/logger | H743 `PB5` through protection |
| 13 | `CAM_MAV_TX_FROM_BOX` | OpenIPC camera RX | H743 `PA9` TX |
| 14 | `CAM_MAV_RX_TO_BOX` | OpenIPC camera TX | H743 `PA10` RX |
| 15 | `BOX_GND_B` | optional parallel ground | box ground |

Правила:

- HD-15 не несе raw `PB8/PB9`; CAN-трансивер має бути всередині бокса.
- `CANH/CANL` ведіть крученою парою.
- Живіть box мінімум через pins 4/6; для більшого струму додайте pins 5/15.
- Pin 9 є виходом живлення на GNSS receiver. Не back-power box через pin 9.
- Напруга `GNSS_VOUT_FUSED` має відповідати приймачу: деякі модулі мають 5 V
  `VIN`, але raw receiver може вимагати 3.3 V.
- Перехрестіть camera UART: pin 13/H743 `PA9` TX -> camera RX, camera TX ->
  pin 14/H743 `PA10` RX. Використовуйте 3.3 V logic і common ground.
- Додайте окремий camera signal-ground return до box ground; pins 13/14 самі
  по собі не є повним UART connection. Не використовуйте shield як signal GND.
- Pins 13/14 передають тільки UART data і не живлять camera. Додайте окреме
  належно захищене camera/LTE power, якщо його не спроєктовано в enclosure.
- Не живіть H743 одночасно від USB-C і `BOX_5V_IN`, якщо в box немає ORing або
  захисту від back-feed.

## USB-C ROM DFU

Standalone DroneCAN build:

```powershell
pio run -e weact_mini_h743vitx_dronecan_usb -t upload
```

Збірка secure-app template:

```powershell
pio run -e weact_mini_h743vitx_dronecan_phaseb_app_usb
```

Phase-B environments навмисно відхиляють `-t upload`: template ще містить
непровізіонований UID sentinel і не має відповідних signed metadata.
Використовуйте AirDroper provisioning app для ліцензованого ST-Link/SWD або
USB-C ROM DFU update.

Вхід у ROM DFU:

1. Затисніть `BOOT0`.
2. Натисніть reset або power-cycle H743.
3. Підключіть USB-C до комп'ютера.
4. Відпустіть `BOOT0`, коли плата з'явиться як DFU device.

Windows app `AirDroper GNSS Filter` версії `2026.08.02.1` або новіше може
оновити вже активовану H743 через USB-C ROM DFU:

1. `Board target` -> `H743 WeAct DroneCAN`.
2. `Update transport` -> `USB-C ROM DFU`.
3. Введіть license key.
4. Переведіть H743 у ROM DFU через `BOOT0` + reset/power-cycle.
5. Натисніть `Update`.

USB-C ROM DFU шлях спочатку читає та розбирає фізичний option byte RDP. Якщо
читання невдале, значення не розбирається або це незворотний RDP2, запис не
починається. І readable RDP0, і protected RDP1 плати отримують однаковий
безпечний результат: mass erase, повний попередньо перевірений application за
`0x08020000`, metadata за `0x081E0000`, відповідний bootloader за `0x08000000`
і фінальний RDP1.

Для RDP1 додатково потрібні очікуваний UID-short із license preflight, зняття
RDP, підтвердження RDP0 та фізичне повторне читання exact UID до будь-якого
запису firmware. App/metadata readback перевіряється до bootloader і lock.
Окреме фінальне читання option bytes має підтвердити RDP1; інакше застосунок не
стверджує й не надсилає звіт про успішне оновлення.

RDP1 ховає фізичний UID до erase, тому protected USB-C path починається тільки
після підтвердження UID-short. Якщо UID-short неправильний або діалог
скасовано, app зупиняється до RDP removal і плата не змінюється.

H743 verifier сам не записує option bytes: він відмовляється boot unlocked
production image. Provisioning/update tooling має застосувати й перевірити
`RDP=0xBB`. Production bootloader також відхиляє signed H743 applications,
старіші за anti-rollback floor v0.4.0.

## ST-Link/SWD

Підключення ST-Link V2:

| ST-Link V2 | WeAct H743 |
|------------|------------|
| `3V3` | `3V3` |
| `GND` | `GND` |
| `SWDIO` | `PA13` / `DIO` |
| `SWCLK` | `PA14` / `CLK` |

У Windows app:

1. `Board target` -> `H743 WeAct DroneCAN`.
2. `Update transport` -> `ST-Link (SWD)`.
3. Введіть license key.
4. `Activate` для нової плати або `Update` для вже активованої H743.

Якщо CubeProgrammer вже стер плату і повторний mass erase не вдається, app
`2026.07.23.1+` завантажує та перевіряє, що кожен записуваний region (і
сектори parameter journal) читається повністю порожнім, перш ніж продовжити
write + verify.

**Mass erase і watchdog прошивки (app `2026.07.23.1+`).** Встановлена
прошивка H743 вмикає 15-секундний апаратний watchdog під час boot, і цей
watchdog продовжує рахувати навіть тоді, коли програматор тримає чип
зупиненим. Повний erase flash на H743 триває достатньо довго, щоб watchdog
міг скинути чип посеред erase, що CubeProgrammer повідомляє як
`Mass erase operation failed. Please verify flash protection`, хоча плата
НЕ захищена (RDP читається як `0xAA`). App `2026.07.23.1+` запобігає цьому
автоматично: кожен H743 erase спочатку заморожує watchdog прошивки на час
debug-сесії (запис у регістр `DBGMCU` у тому самому виклику CubeProgrammer).
Якщо erase все одно не вдається, app проводить вас через **BOOT0 power
cycle**:

1. Зніміть живлення з H743.
2. Затисніть кнопку **BOOT0** на платі WeAct.
3. Підключіть живлення, продовжуючи тримати BOOT0.
4. Відпустіть BOOT0 приблизно через одну секунду після подачі живлення.

Із затиснутим BOOT0 під час подачі живлення чип запускає свій вбудований ROM
bootloader замість встановленої прошивки, тому жоден watchdog не працює і
erase завжди отримує чистий чип. Прошивка `v0.4.3` і новіша також сама
заморожує watchdog під будь-яким debugger, тож платам, прошитим нею, усе це
не потрібно.

Примітка щодо NRST wiring: 4-провідне підключення вище є підтримуваним
default. *Коректно* під'єднаний ST-Link `RST` -> WeAct `NRST` теж прийнятний
і навіть допомагає — він дозволяє CubeProgrammer підключатися "under reset",
що зупиняє встановлену прошивку (і її watchdog) до erase. Знімайте цей провід
лише тоді, коли він викликає `DEV_TARGET_HELD_UNDER_RESET` (неправильний pin,
пошкоджений провід або probe, що тримає reset low). Загальна порада для F401
у [10_self_install.md](10_self_install.md) — "під'єднати NRST, коли
підключення не вдається" — застосовується до H743 лише з цим застереженням.

H743 secure layout:

| Region | Address range | Purpose |
|--------|---------------|---------|
| Bootloader | `0x08000000 - 0x0801FFFF` | Secure bootloader |
| Active app | `0x08020000 - 0x080BFFFF` | Signed H743 DroneCAN firmware |
| Bank 1 reserve | `0x080C0000 - 0x080FFFFF` | Growth/guard area |
| Reserved stage | `0x08100000 - 0x0819FFFF` | Reserved for future DroneCAN firmware update |
| Parameter journals | `0x081A0000 - 0x081DFFFF` | Power-fail-safe parameter storage |
| Metadata | `0x081E0000 - 0x081FFFFF` | Signed metadata / update state |

Не прошивайте H743 app або metadata у F401 адреси.

Standard Mission Planner DroneCAN firmware update is planned but not active in
the current H743 firmware. Today use AirDroper Windows app `ST-Link (SWD)` or
`USB-C ROM DFU` for H743 updates. Already-deployed H743 boards will need one
wired update first before future DroneCAN self-update can work.

## ArduPilot setup

Для **ArduPlane 4.6.3 на CAN1** рекомендований стартовий файл —
`presets/arduplane_FC_4.6.3_h743_dronecan_CAN1_core.param` у
[AirDroper Mission Planner Mod](https://gps.airdroper.org/download/mission-planner-mod).
Завантажуйте його у **flight controller (зазвичай SYSID 1), ніколи не у node
42**. На fresh disabled-CAN setup Mission Planner відкриває enable-dependent
parameters поетапно: Load/Write, reboot, reconnect/refresh і знову той самий
file, доки немає popup про missing parameters і всі десять значень точно read
back. Може знадобитися три imports. Core file навмисно зберігає CAN2, camera S1,
airspeed, optional compass, EKF, arming, SR streams і `GPS_AUTO_CONFIG`; виконайте всі
manual safety checks усередині файла. Таблиці нижче лишаються reference для
навмисної конфігурації CAN2 або optional accessories.

Налаштуйте CAN-порт польотного контролера:

| Параметр | CAN1 приклад | CAN2 приклад |
|----------|--------------|--------------|
| Enable CAN driver | `CAN_P1_DRIVER = 1` | `CAN_P2_DRIVER = 2` |
| DroneCAN protocol | `CAN_D1_PROTOCOL = 1` | `CAN_D2_PROTOCOL = 1` |
| Bitrate | `CAN_P1_BITRATE = 1000000` | `CAN_P2_BITRATE = 1000000` |
| GPS type | `GPS1_TYPE = 9` | `GPS1_TYPE = 9` (`GPS2_TYPE` лише для навмисного другого GPS instance) |
| GPS auto-config | `GPS_AUTO_CONFIG = 1` | global parameter |
| Optional GPS node lock | `GPS1_CAN_OVRIDE = 42` | те саме (`GPS2_CAN_OVRIDE` лише для другого GPS instance) |

`CAN_Px_DRIVER` вибирає virtual driver. Таблиця навмисно прив'язує physical
CAN1 до driver 1, а physical CAN2 до driver 2; використовуйте `CAN_Dn_*`, що
відповідають призначеному номеру driver. H743 DroneCAN `v0.2.0+` реалізує два
virtual serial порти. Нижче наведено параметри для driver 1; для driver 2
замініть усі prefixes `CAN_D1_` на `CAN_D2_`:

| Призначення | ArduPilot parameter | Значення |
|-------------|---------------------|----------|
| Enable DroneCAN serial | `CAN_D1_UC_SER_EN` | `1` |
| Camera node | `CAN_D1_UC_S1_NOD` | `42` |
| Camera index | `CAN_D1_UC_S1_IDX` | `0` |
| Camera baud | `CAN_D1_UC_S1_BD` | `115` (115200) |
| Camera protocol | `CAN_D1_UC_S1_PRO` | `2` (MAVLink2) |
| Filter node | `CAN_D1_UC_S2_NOD` | `42` |
| Filter index | `CAN_D1_UC_S2_IDX` | `1` |
| Filter baud | `CAN_D1_UC_S2_BD` | `115` (115200) |
| Filter protocol | `CAN_D1_UC_S2_PRO` | `2` (MAVLink2) |

**Tunnel index `1` (filter) разом із живим `EKF_STATUS_REPORT` на ньому є
ЖОРСТКОЮ ПЕРЕДУМОВОЮ будь-якого GPS output від node `42`.** Це не зручність для
camera, не optional enrichment і не просто logging. Фільтр працює fail-closed
щодо свіжості telemetry польотного контролера: він публікує `Fix2`/`Auxiliary`
лише поки отримує ОБА повідомлення — FC `HEARTBEAT` (не старіше 3000 ms) і FC
`EKF_STATUS_REPORT` у межах його власного freshness window. Якщо бракує
будь-якого з них, фільтр suppress ОДРАЗУ І `Fix2`, І `Auxiliary`, тому FC не
отримує від цього node ЖОДНОГО GPS — не гіршого, не нефільтрованого, а ніякого.
Налаштуйте `CAN_D1_UC_S2_*` навіть якщо вам не потрібні status messages
фільтра, і переконайтесь, що FC справді стрімить `EKF_STATUS_REPORT` на цьому
channel.

**`SYSID_THISMAV = 1` також є жорсткою вимогою.** Фільтр приймає FC safety
telemetry лише від MAVLink system ID `1` і component ID `1`
(`MAV_COMP_ID_AUTOPILOT1`). Обидва значення є compile-time constants у прошивці;
жоден parameter фільтра їх не змінює. За будь-якого іншого `SYSID_THISMAV`
frames FC `HEARTBEAT` і `EKF_STATUS_REPORT` усе одно проходять tunnel і навіть
парсяться, але відкидаються до того, як оновити safety evidence. Результат —
постійний GPS block при повністю робочому CAN tunnel: node `42` присутній,
tunnel byte counters зростають, camera MAVLink2 працює, а GPS не з'являється
ніколи. Default самого ArduPilot вже `1`; ця несправність трапляється на
апаратах, де `SYSID_THISMAV` змінили під multi-vehicle GCS setup.

S1/index `0` є прозорим bidirectional каналом між OpenIPC camera UART і
ArduPilot. S2/index `1` є окремим каналом: він несе MAVLink2, який генерує H743,
і повертає FC telemetry для наявної EKF, arm-state, parameter та
status logic. Окремі serial IDs не дозволяють змішувати camera bytes з MAVLink
самого фільтра.
Значення ArduPilot `_PRO = 2` є serial-protocol setting; стандартний Targetted
DSDL кодує MAVLink2 як on-wire protocol value `1`.

Деякі OpenIPC cameras можуть залишатися у bootloader, якщо під час старту на
RX вже надходять bytes. За потреби встановіть `MAV_TELEM_DELAY = 5`; у старих
ArduPilot цей parameter може називатися `TELEM_DELAY`. Після зміни CAN або
DroneCAN serial parameters перезавантажте FC.

### Stream rates на tunnel channel фільтра

ArduPlane компілює кожну stream group із default `1 Hz` на КОЖНОМУ MAVLink
channel, включно з DroneCAN tunnel channels, тому правильно налаштована
установка зазвичай взагалі не потребує записів `SRn_*`. Додатково фільтр після
binding сам просить у FC `EKF_STATUS_REPORT` на 2 Hz через
`SET_MESSAGE_INTERVAL` і повторює запит, поки field stale.

- **Ніколи не ставте `SRn_EXTRA3` на tunnel channel фільтра у `0`.** `EXTRA3` —
  це stream group, яка несе `EKF_STATUS_REPORT`. Значення `0` на channel
  фільтра прибирає це повідомлення, і фільтр назавжди блокує GPS, хоча все
  інше на tunnel продовжує працювати.
- **`SRn` — це ordinal MAVLink CHANNEL, а не номер `SERIALn`.** За DroneCAN
  tunnels немає жодного `SERIAL8`/`SERIAL9`, і `SR2_` не означає `SERIAL2`. Щоб
  знайти потрібну group, порахуйте кожен `SERIAL0`..`SERIAL7`, у якого
  `SERIALn_PROTOCOL` є MAVLink-варіантом (MAVLink1 або MAVLink2), і врахуйте
  також другий USB port — він займає MAVLink channel навіть на платах, де
  default parameter table показує для нього `None`. Позначте цю кількість як P.
  Тоді camera tunnel — це `SR(P)`, а filter tunnel — `SR(P+1)`: DroneCAN serial
  ports додаються після фізичних MAVLink channels, і port фільтра завжди
  останній.
- **Існують лише `SR0_`..`SR6_`.** Якщо channel фільтра опиняється далі за
  `SR6`, він взагалі не має parameter group і жоден запис `SRn_*` до нього не
  дійде; дістатися можна тільки через `SET_MESSAGE_INTERVAL` із GCS або script.
  Скомпілований default `1 Hz` на цьому channel усе одно діє — саме тому
  стандартна установка працює без жодного редагування `SRn`.
- **Якщо піднімаєте `EXTRA3` для запасу, змінюйте ОДНУ ймовірну group за раз,
  перезавантажуйте FC і перевіряйте, чи зник block.** Не задавайте кілька
  `SRn_EXTRA3` "наосліп", сподіваючись, що одна з них виявиться потрібним
  channel. Parameters `SR*` піднімають цілі ГРУПИ повідомлень, а не окремі
  messages, тому неправильна спроба може saturate telemetry radio на `57600`
  або залити camera UART і CAN bus.

### ArduPilot setup для airspeed і optional compass

Production/default build показує MS4525 як DroneCAN device від node `42`; не
вибирайте local-I2C MS4525 backend польотного контролера. Лише direct-flash
`*_dronecan_mag` build також показує HMC5983.

1. Для потрібного FC airspeed instance встановіть DroneCAN: зазвичай
   `ARSPD_TYPE = 8`. Якщо instance 1 уже зайнятий, використайте відповідний
   `ARSPD2_TYPE`, `ARSPD3_TYPE` тощо.
2. Встановіть відповідний `ARSPDx_USE` згідно з vehicle і control strategy.
   Для Plane вмикайте використання лише після bench check та airspeed
   calibration; перевірте offset, ratio, tube order і pre-arm status за
   актуальною процедурою ArduPilot.
3. **Лише `*_dronecan_mag`:** дозвольте ArduPilot автоматично знайти DroneCAN compass. У Mission Planner
   відкрийте `Setup -> Mandatory Hardware -> Compass`, переконайтесь, що є
   compass від node `42`, позначте/використайте його як external і встановіть
   потрібний priority.
4. **Лише `*_dronecan_mag`:** встановіть або auto-detect orientation HMC5983, потім виконайте повну
   compass calibration уже в остаточно зібраному vehicle. Не копіюйте offsets
   з іншого airframe/sensor. Перевірте напрям усіх axes і motor-current
   interference до використання цього compass для yaw.

ArduPilot автоматично визначає DroneCAN airspeed publisher; для нього не
потрібен virtual serial mapping. Валідний MS4525 sample публікується як
`uavcan.equipment.air_data.RawAirData` до 20 Hz. Лише у `*_dronecan_mag`
build валідний HMC5983 sample
публікується як `uavcan.equipment.ahrs.MagneticFieldStrength2`, sensor ID `0`,
до 25 Hz. Ці messages використовують ті самі node ID і CAN transceiver, що GPS
та обидва MAVLink tunnels.

Це raw sensor transports, а не calibrated airspeed або heading. H743 не вчить
pitot zero/ratio, не компенсує tube order і не застосовує vehicle compass
orientation, hard/soft-iron offsets чи motor-current compensation. Ці
calibrations належать вибраним ArduPilot sensor instances; повторіть їх після
зміни sensor, tubing, mounting, orientation, wiring або nearby power equipment.

Тримайте FC MAVLink stream rates помірними. У classic CAN кожен multi-frame
CAN frame переносить лише сім transport payload bytes, тому camera full duplex,
chatty filter port і 20 Hz airspeed publication можуть наблизити 1 Mbps bus
до saturation; `*_dronecan_mag` build додає 25 Hz compass publication. GPS і NodeStatus мають вищий priority. Червоний `MAV` row або ненульовий `ERR` row
означає loss/overload — зменште stream rates перед польотом.
**Виняток: ніколи не опускайте `EXTRA3` на tunnel channel фільтра нижче його
скомпілованого default `1 Hz` і ніколи не ставте його у `0`.** Ця group несе
`EKF_STATUS_REPORT`, без якого фільтр взагалі не видає GPS, тому таке
"підрізання" перетворює питання bandwidth на повний GPS block. Зменшуйте інші
stream groups і camera channel.
Жовтий `MAV` row
означає, що queued data застаріли після stalled link.
Неповні camera chunks збираються не довше 10 ms, щоб зменшити CAN overhead.
Якщо camera traffic у будь-якому напрямку не просувається 500 ms, bytes, які ще
залишаються у firmware queues, відкидаються замість відтворення після відновлення
link. Frames, вже передані до FDCAN controller, відкликати неможливо.

Прошивка публікує:

- `uavcan.protocol.NodeStatus`
- `uavcan.protocol.GetNodeInfo`
- `uavcan.equipment.gnss.Fix2`
- `uavcan.equipment.gnss.Auxiliary`
- `uavcan.equipment.air_data.RawAirData` для MS4525 differential pressure і
  sensor temperature, до 20 Hz
- `uavcan.equipment.ahrs.MagneticFieldStrength2` для HMC5983 magnetic field,
  sensor ID `0`, до 25 Hz — лише `*_dronecan_mag` builds
- `uavcan.tunnel.Targetted` для двох MAVLink2 virtual serial ports
- `uavcan.equipment.ice.reciprocating.Status` з частотою 1 Гц — оцінка витрати
  палива двигуна (H743 DroneCAN `v0.5.28+`)

MAVLink2 тунелюється, але raw GNSS NMEA, UBX та SBF не тунелюються. GPS
залишається native `Fix2/Auxiliary`, а фізичний FC GPS UART залишається
вимкненим.

### Оцінка витрати палива двигуна (EFI)

Фільтр оцінює витрату палива за обертами двигуна, які польотний контролер і
так йому передає, і публікує результат як
`uavcan.equipment.ice.reciprocating.Status` (тип даних `1120`) з частотою
1 Гц. Це ОЦІНКА за моделлю гвинта, а не вимірювання: у цьому тракті немає ні
витратоміра, ні датчика рівня в баку.

Щоб її прийняти:

| Призначення | Параметр ArduPilot | Значення |
|-------------|--------------------|----------|
| Бекенд EFI | `EFI_TYPE` | варіант DroneCAN для вашої версії ArduPilot |
| Джерело обертів, яке читає фільтр | `RPM1_TYPE` | відповідно до вашого датчика |
| Масштаб обертів | `RPM1_SCALING` | **див. попередження нижче** |

ArduPilot декодує повідомлення в `EFI_STATUS`, що дає індикацію палива в
наземній станції та запис у лог без окремого каналу. Поле спожитого об'єму
монотонне — саме його використовує прив'язка EFI до монітора батареї; датчики,
яких у цього двигуна немає (тиск оливи, температура охолоджувальної рідини
тощо), публікуються як NaN, а не нулем: нуль є вимірюванням, і хибне
вимірювання тривожить.

**`RPM1_SCALING` — єдине налаштування, здатне зробити це небезпечним.** У
фільтра одне джерело обертів, тож ніщо на літаку не може йому заперечити.
Здвоєний CDI дає два імпульси на оберт; налаштуйте один — і кожне показання
зменшиться вдвічі, що вісімкратно занизить член гвинта й саму витрату. Фільтр
підставляє «підлогу» під оцінку за положенням газу й видає
`Fuel held up by throttle - check RPM_SCALING`, коли ця підлога спрацьовує —
**побачивши це повідомлення, звірте масштаб із ручним тахометром, перш ніж
летіти знову.** Перевірте його один раз на відомих обертах холостого ходу під
час введення в експлуатацію.

**На літаку без датчика рівня палива ця оцінка — ЄДИНИЙ покажчик палива в
пілота**, тому вона свідомо зміщена в бік завищення й лишається орієнтовною до
калібрування. Задайте вісім параметрів `PROP_*`/`FUEL_*`/`ENG_PMAXKW` на
ФІЛЬТРІ (вузол `42`, не на польотному контролері), завантажте пресет двигуна,
якщо він відповідає вашій комбінації, і виконайте розділ «Калібрування оцінки
витрати палива» в [06_tuning.md](06_tuning.md). Запис `FUEL_CAPG` обнуляє
накопичений підсумок, тож робіть це після кожної заправки.

Облік палива навмисно не залежить від GNSS output gate. Він триває крізь повну
втрату FC-link і блок невідомої/непідтримуваної FC-version. Кожен boot
починається з установленим консервативним engine-may-be-running latch; тиша
лінку не скидає його, а відсутні RPM нараховуються за номінальною потужністю,
доки одночасно fresh disarmed state, нульові RPM і закритий газ не підтвердять
зупинку. Запис `FUEL_CAPG` приймається лише після того, як ці самі три inputs
стали fresh; сам запис не очищає цей latch.

Якщо при будь-якому boot немає надійного V2 backup record (зокрема при
звичайному вмиканні, warm reset або будь-якому legacy V1 record), total
позначається LOST і фільтр не надсилає **жодного DroneCAN ICE Status**. Missing,
corrupt або іншим чином invalid H743 tune journal також анулює surviving fuel
total, бо provenance settings місткості, густини та моделі, за яких він
накопичувався, невідомий. POR/PDR не доводить заправку чи механічну зупинку
двигуна. EFI backend ArduPilot стає stale/unhealthy замість прийняти хибний
нуль/повний бак. Кожні 60 с фільтр повторює `Fuel total LOST - write FUEL_CAPG
to restart it`. Сідайте або лишайтеся на землі, перевірте всю fuel configuration,
дочекайтеся fresh stopped-engine quorum (disarmed + valid zero RPM + closed
throttle) і повторно запишіть `FUEL_CAPG` для палива на борту, навіть якщо його
числове значення не змінилося. Disarmed alone відхиляється. Якщо числова
місткість змінилася, accepted write обнуляє runtime counter, але лишає TOTAL
LOST і EFI silent, доки asynchronous save tune journal не повідомить `Tune
saved`; `Tune save failed` лишає lockout. Valid V2 restore отримує обмежене
консервативне 25-секундне reset-gap нарахування за номінальною потужністю, а не
точне вимірювання витрати під час reset/startup. Прийнятий запис, що встановлює
новий total, скасовує pending charge старого відновленого total.

`FUEL_DENS` потребує того самого fresh stopped-engine quorum. Фактична зміна
густини позначає total як LOST до runtime assignment, скасовує старий CAPG
commit intent і блокує записи місткості з
`FUEL_CAPG blocked: wait for FUEL_DENS save` до verified save journal. Failure лишається blocked/LOST; `Tune saved`
очищає density latch, але не lost total. Лише після цього наступний
stopped-quorum запис `FUEL_CAPG` встановлює fresh zero.

Factory reset позначає fuel total як LOST у BKPSRAM до початку flash work.
Failed attempt теж може консервативно лишити його LOST. Після будь-якої спроби
перевірте кожен parameter fuel model і виконайте stopped-engine recovery через
`FUEL_CAPG`; після зміненої місткості дочекайтеся `Tune saved`.

**Ніколи не виконуйте Phase-C maintenance при працюючому двигуні.** Підключена
maintenance session може перевищити цей фіксований 25-секундний bound.

Оцінка не потребує додаткового налаштування потоків: оберти, газ і густина
повітря надходять тим самим tunnel-каналом фільтра, який і так обов'язковий
для GPS.

### Septentrio Mosaic X5 SBF input

H743 DroneCAN firmware `v0.1.9+` може парсити native SBF від Mosaic X5 на GNSS
UART, коли `GNSS_TYPE=2`. Налаштуйте Mosaic stream у RxTools/Web UI на
`460800`, 8N1 і SBF output. Увімкніть ці блоки на stream, підключеному до
H743 `PA3/PA2`:

| SBF-блок | Рекомендована частота | Використання firmware |
|----------|------------------------|-----------------------|
| `PVTGeodetic` | 5-10 Гц | fix mode, позиція, MSL/ellipsoid height, velocity, satellites, receiver clock |
| `DOP` | 1-5 Гц | HDOP/VDOP/PDOP/TDOP для DroneCAN і guards |
| `ReceiverTime` | 1 Гц | UTC timestamp у DroneCAN `Fix2` |
| `MeasEpoch` | 1-5 Гц | C/N0/SNR guard і temporal-correlation частина `DR_CONF` |
| `PosCovGeodetic` | 1-5 Гц | position covariance у DroneCAN `Fix2` |
| `VelCovGeodetic` | 1-5 Гц | velocity covariance у DroneCAN `Fix2` |

H743 firmware також приймає Mosaic NMEA у `GNSS_TYPE=2`, але SBF є бажаним
профілем для H743 DroneCAN: він передає velocity, DOP, covariance, receiver
time і C/N0 у binary format без serial GPS driver на flight controller.

Для spoof-confidence scoring Mosaic SBF `MeasEpoch` дає C/N0
temporal-correlation сигнал. Він не вмикає pseudorange-residual signal: цей
score залишається тільки для u-blox, бо залежить від UBX `NAV-SAT` `prRes`.

Оскільки FC отримує native DroneCAN GPS, H743 DroneCAN не є byte-for-byte GPS
packet pass-through. Прошивка парсить receiver stream і публікує ті самі live
fix values у DroneCAN units. Вона не генерує synthetic GPS coordinates, не
blend-ить coordinates і не переписує raw NMEA/UBX/SBF packets; у DR1 вона suppress
`Fix2/Auxiliary` замість того, щоб надсилати altered GPS data.

`GPS_AUTO_CONFIG=1` є default ArduPilot режимом auto-config тільки для serial
GPS і є найбезпечнішим для цього фільтра. H743 DroneCAN firmware `v0.1.2+`
відповідає на optional DroneCAN `param.GetSet` запити ArduPilot для
`GPS_TYPE`/`GPS1_TYPE`, тому `GPS_AUTO_CONFIG=2` не блокує GPS data.

Якщо на CAN bus є більше одного DroneCAN GPS-like node, задайте відповідний
`GPSx_CAN_OVRIDE` на `42`, щоб ArduPilot прив'язав GPS instance до static node
ID фільтра. На single-GPS bus це optional.

## Mission Planner Params

H743 DroneCAN firmware `v0.1.4+` відкриває spoofing/tuning parameters через
DroneCAN parameter service. H743 DroneCAN firmware `v0.1.5+` також відкриває
ті самі parameters через USB-C COM port самої H743 як direct MAVLink
management link.

Коли налаштовано S2/index `1`, MAVLink2 самого H743 доходить до flight
controller, а FC telemetry повертається до фільтра. GCS, підключена через FC,
може вибрати filter system ID `42`, якщо її UI підтримує MAVLink system
selection. DroneCAN node Params лишається найпрямішим способом налаштування на
літальному апараті.

Читання доступне завжди, але кожна mutation fail-closed без свіжого явного
підтвердження **FC disarmed**. Це стосується parameter writes, `UBX_RESET`,
`Commit Params` і factory reset. Тому FC має залишатися powered, підключеним
через DroneCAN і disarmed навіть при direct USB-C parameter UI. DroneCAN
mutation також має надходити від configured або поточного bound FC node.

### Варіант A: DroneCAN через flight controller

Порядок:

1. Відкрийте Mission Planner.
2. `SETUP -> Optional Hardware -> DroneCAN/UAVCAN`.
3. Виберіть активний CAN driver, зазвичай `MAVLinkCAN1`, і натисніть `Connect`.
4. Дочекайтесь node `42` з назвою `org.airdroper.gnss_filter.h743_dronecan`.
5. Натисніть `Menu` на node `42` і відкрийте `Parameters`.
6. Переконайтеся, що FC disarmed, змініть tune value, натисніть `Write Params`,
   потім `Commit Params`.
7. Якщо протягом попередньої хвилини вже була storage operation, зачекайте до
   65 секунд, потім перезавантажте H743 і перевірте persistence.

### Варіант B: direct USB-C до H743

Використовуйте це на столі, якщо хочете звичний Mission Planner MAVLink
parameter screen без жодного FC serial port. FC все одно має бути присутнім у
DroneCAN для fresh disarmed state:

1. Увімкніть H743 у normal app mode, не тримайте `BOOT0`.
2. Підключіть USB-C H743 до комп'ютера.
3. У Mission Planner виберіть новий H743 COM port і `115200` baud.
4. Натисніть `Connect`. Mission Planner має побачити system ID `42`.
5. Відкрийте `CONFIG -> Full Parameter Tree` або `Full Parameter List`.
6. Переконайтеся, що FC disarmed, змініть spoofing/tuning values і натисніть
   `Write Params`.
7. Якщо діє one-minute storage cooldown, зачекайте до 65 секунд, потім
   перезавантажте/reconnect і перевірте persistence.

Цей USB-C режим є normal application management port. Це не ROM DFU flashing:
тримайте `BOOT0` тільки для firmware update, а для редагування parameters
залишайте `BOOT0` відпущеним.

У DroneCAN node Params перші два rows, `GPS_TYPE` і `GPS1_TYPE`, є read-only
compatibility rows зі значенням `9`. Реальні tune rows починаються після них.
У direct USB-C MAVLink parameter screen список починається одразу з tune rows:
`BOOT_NSATS`, `BOOT_NHDOP`, `RJ_BASE_M`, `SP_JMP_MPS`, `SNR_EN`, `FENCE_RAD`,
`GNSS_TYPE` тощо.

Серійний H743 DroneCAN fixed-wing profile використовує:

- `RJ_LOIT_V=0` (вимикає спеціальний low-speed rejoin gate floor 2500 м)
- `SP_JMP_MPS=200`
- `SP_ABS_M=400`
- `EKF_TRIPMS=500`

На 120 км/год літак проходить приблизно 33,3 м/с, тобто близько 167 м за повне
стандартне NAV-validity window 5 с. Абсолютний ліміт 400 м залишає запас для
відновлення після такої паузи, а implied-speed limit 200 м/с у шість разів
перевищує cruise speed. Математичні guard-тести охоплюють design envelope до
65 м/с (234 км/год): за 5 с це 325 м, тому залишається 75 м запасу absolute
limit; це не є flight або hardware validation. Це серійні fixed-wing values, а не універсальна
рекомендація: перевірте їх відносно максимальної швидкості та flight logs.

Під час першого fixed-wing-profile update H743 мігрує stored value лише тоді,
коли він досі точно дорівнює legacy migration sentinel (`0.8/500/1000/0`). Custom
operator value залишається без змін. Після update перечитайте ці чотири rows;
щоб свідомо замінити custom values, завантажте
`airdroper_filter_field_safe.param` або виконайте factory reset parameters за
наявності свіжого явно disarmed стану FC.

`UBX_RESET` є one-shot command, не saved setting:

- `UBX_RESET=1` - u-blox hot start
- `UBX_RESET=2` - u-blox cold start
- `UBX_RESET=3` - clear u-blox config and reinitialize

H743 DroneCAN тримає locked off raw FC GPS UART settings:

- `FCGPS_UART = 0`
- `FCGPS_FWD = 0`

У H743 v0.5.5+ `RJ_REQEKF` і `EKF_OKRJMS` також заблоковані у `0`; writes
ігноруються, зокрема ненульові значення зі старих journals. Колишня EKF
rejoin-умова була нездійсненною/циклічною; на H743 її замінює незалежне multi-evidence
recovery (barometric rate, pitot, attitude/course, SNR, UTC і dead-reckoned
anchor). `PT_ONLY=1` вимикає лише synthetic output/blending/nudge, але не
geometry, quality, stability, confidence або evidence checks.

Firmware auto-saves accepted values після короткого debounce. Один
60-секундний wear limiter охоплює auto-save, explicit commit і factory reset;
values залишаються active і dirty, доки deferred save не зможе виконатися.
A/B journal спочатку commits новий record, і лише після цього старий sector
може бути erased, тому interrupted write зберігає останній complete record.

## Дисплей

H743 DroneCAN `v0.4.0` використовує професійний висококонтрастний темний
інтерфейс на вбудованому кольоровому TFT-дисплеї ST7735 з фактичною
роздільною здатністю 80 x 160 пікселів. Це не OLED. Дисплей не має сенсорного
керування або кнопок перемикання сторінок.

Одразу після ввімкнення з'являються анімоване status ring та progress rail,
поки ініціалізується GNSS-приймач. Rounded boot tiles показують версію firmware
і стан node, потім boot screen переходить від GNSS initialization до
`READY` / `BOOT GUARD`, а далі відкриває dashboard. Після splash hero
залишається у стані
`FILTER CHECK / GUARD` протягом реального configurable startup spoof-guard
interval і не може показати `FILTER ONLINE / RUN`, доки ці перевірки ще
затримані. Напис `USB CONFIG` означає
звичайний USB-C management link застосунку. Він не означає, що ROM DFU вже
активний: для ROM DFU все одно потрібно тримати `BOOT0` під час reset або
power-up.

Dashboard постійно зберігає три області:

- верхній activity header для product, CAN і MAVLink
- великий кастомний штрихований та контурний hero `OK`, `!!` або `XX` з написом
  `FILTER ONLINE`, `FILTER CHECK`, `FILTER BLOCK` чи `FC ALERT` та короткою
  причиною, наприклад `RUN`, `GPS`, `CAN ERR`, `SENSOR` або причиною активного
  DR1
- footer зі станом GPS publication: `PUB+` означає recent Fix2, прийнятий у
  локальну DroneCAN transmit queue, `PUB?` — gate
  відкритий, але recent Fix2 немає, а `PUB-` — publication blocked/unavailable;
  далі показано `DR0`/`DR1` та DroneCAN node фільтра, наприклад `N42`

`PUB+` не є підтвердженням прийому від FC. Перед польотом окремо перевірте
DroneCAN/Mission Planner telemetry на FC.

У центральній частині використано proportional body text, компактні icons,
rounded information tiles, gradient health rails і segmented activity rails.
Автоматично перемикаються чотири сторінки:

| Сторінка | Що показує |
|----------|------------|
| **Overview** | Свіжість GPS fix і satellites, FC node health та generic UAVCAN node mode, ArduPilot `NotifyState`, arm і safety state |
| **Sensors** | Свіжість MS4525, differential pressure і sensor temperature; `*_dronecan_mag` builds також показують HMC5983 freshness і magnetic-field magnitude |
| **Links** | CAN та сумарні camera/filter MAVLink TX/RX counters, CAN errors, MAVLink dropped/expired counters |
| **System** | I2C error/recovery counters, firmware version/build, uptime або Mosaic SBF accepted/bad-CRC counters |

Page dots та underline у footer показують активну сторінку. Коли фільтр
справний, а FC гарантовано disarmed, кожна сторінка залишається приблизно п'ять
секунд, після чого UI переходить до наступної через eased five-frame slide.
Ручного вибору сторінки немає. Після arm або появи warning/alert автоматичне
перемикання та slide transitions зупиняються.
Sensor, CAN або MAVLink warning фіксує Sensors чи Links page, яка пояснює
проблему; поганий FC NodeStatus, GPS/guard warning або armed FC фіксує Overview.
Filter block чи high-priority ArduPilot notification вмикає dedicated alert
takeover у центральній області, а hero state, невелика activity animation і
footer залишаються видимими.
Rotation також чекає fresh FC arming-status broadcast, який явно підтверджує
disarmed state. Якщо arm state невідомий або FC armed, Overview у третьому рядку
коротко показує прихований sensor/link warning. Одночасні filter і FC alerts
позначаються як `DUAL ALERT`, тому жодна несправність не приховується.

Redesign змінює лише presentation. Стан дисплея не може відкрити spoofing gate
або перенаправити трафік: DR0/DR1 enforcement, DroneCAN GPS/sensor publication,
OpenIPC tunnel та власний MAVLink2 virtual port фільтра зберігають попередню
поведінку.

Для pixel-exact перегляду всіх сторінок і анімацій без прошивання плати виконайте:

```powershell
python tools/render_h743_display_preview.py
```

Потім відкрийте `dist/h743_display_preview.html`. Preview використовує той самий
portable C++ RGB565 renderer, що й H743 firmware, без відтворення графіки
браузерними шрифтами.

Overview показує generic UAVCAN node mode, а не точну назву ArduPilot flight
mode на кшталт Loiter, Auto, Guided або RTL. MAVLink tunnel працює незалежно
від сторінки дисплея.

Сприймайте екран як зручну локальну діагностику, а не як авторитетний flight
instrument. Його counters та freshness indicators не замінюють Mission Planner
pre-arm checks, DroneCAN inspection, sensor calibration або аналіз flight log.
Зокрема, у `*_dronecan_mag` build magnetic-field magnitude не є calibrated heading, а `FILTER ONLINE` не
доводить правильність compass orientation, pitot plumbing, CAN termination чи
MAVLink routing.

За замовчуванням `FILTER_DRONECAN_FC_NODE_ID=0`. Tunnel вимагає дві valid
Targetted transfers до node `42` від одного source, перш ніж bound цей FC.
Binding спливає через три секунди без valid tunnel transfer; перед прив'язкою
іншого node всі старі serial queues видаляються. Generic status broadcasts не
можуть захопити FC identity. На busy multi-node bus задайте
`FILTER_DRONECAN_FC_NODE_ID` під час build, щоб від старту закріпити tunnel і
display за одним FC node.

При lease expiry або коли зменшення uptime того самого `NodeStatus` виявляє
швидкий reboot FC, H743 видаляє обидва напрями обох MAVLink tunnels, скидає
MAVLink parser і очищує всі отримані від FC heartbeat, arm, EKF, attitude,
speed, barometer/bias, firmware-version та warning states. Новий binding
починається fail-closed. Після binding або виявленого reboot фільтр одразу
запитує повний набір FC telemetry, повторює запит кожні п'ять секунд, доки
обов'язкові fields stale, і refresh його кожні 30 секунд, коли вони fresh.

## DR0 / DR1

У DR0:

- `Fix2` публікується на кожен свіжий GNSS update, максимум 10 Hz
- `Auxiliary` публікується 1 Hz
- `NodeStatus` лишається online

У spoof/fault DR1:

- `Fix2` і `Auxiliary` зупиняються
- FC перестає отримувати свіжий GPS від цього node
- `NodeStatus` продовжується 1 Hz з warning health
- дисплей фіксується на червоній alert page `BLOCK` з активною причиною, а
  footer показує `PUB-` і `DR1`

No-fix, low satellites, boot guard, або GNSS reconfiguration теж можуть
suppress `Fix2/Auxiliary`, включно з latched no-fix/low-sat DR1 internally,
але ці стани лишають `NodeStatus` health `OK` і показують output block тільки
через vendor status bits та onboard screen. Це прибирає ArduPilot
`PreArm: DroneCAN: Node 42 unhealthy!`, коли GPS просто ще не готовий.

Зворотне так само важливе: `FC_LINK` та інші fault reasons ВСЕ Ж повідомляють
DroneCAN warning health. Тому `PreArm: DroneCAN: Node 42 unhealthy!` є
ОЧІКУВАНИМ супутником повідомлення `GNSS BLOCKED #1: FC LINK STALE`, а не
окремою CAN-несправністю. Не починайте перевіряти CAN wiring, termination чи
bitrate лише через те, що цей pre-arm рядок з'явився разом із блоком `FCLINK`.

Обидва MAVLink2 virtual ports залишаються активними у DR0 і DR1. DR1 блокує
тільки GPS `Fix2/Auxiliary`, але не відключає OpenIPC camera tunnel або MAVLink2
самого фільтра. S2/index `1` зберігає FC telemetry input, EKF-status evidence,
`STATUSTEXT`/`NAMED_VALUE`, parameters та іншу наявну MAVLink
logic. Фізичний `FCGPS_FWD` raw UART bypass залишається недоступним.

Є один навмисний виняток у `v0.5.29+`: private Mission Planner position records
`SP_*` виходять **лише через USB** і ніколи не входять у S2. Поки DR1 latched і
USB device configured та core CDC transmit-ready latch встановлений, H743 видає
transaction із частотою 2 Hz:

| Record | Значення |
|--------|----------|
| `SP_BEGIN` | Sequence transaction та однозначний reset assembler-а |
| `SP_G_LAT`, `SP_G_LON` | Receiver-reported/untrusted latitude і longitude, signed degrees x 1e7 |
| `SP_R_LAT`, `SP_R_LON` | Wind-blind DR reference latitude і longitude, signed degrees x 1e7 |
| `SP_FLAGS` | Raw bounds/freshness, reference validity/motion та DR1 bits |
| `SP_SEQ` | Sequence transaction і останній commit record |

Усі сім — стандартні MAVLink `NAMED_VALUE_INT` від system 42, component 191
з одним `time_boot_ms`. `SP_BEGIN` завжди перший, `SP_SEQ` — останній, а їхні
sequence мають збігатися; consumer має відкинути неповний, mismatched або
expired transaction. Navigation north fence тут не застосовується, бо
south-jump attack має залишатися видимим у private diagnostic, але finite WGS84
bounds і freshness явно передаються у `SP_FLAGS`. Raw freshness має fixed
ceiling 1.5 секунди й не подовжується operator-tunable navigation age. Encoder
працює лише в DR1, а
його єдиний production output sink — direct USB CDC. Він не викликає generic
MAVLink sender, CAN tunnel, DroneCAN publisher чи FC UART.

У Mission Planner FC має лишатися primary link, а H743 USB COM port додається
як secondary connection на 115200. Direct cable — це bench/tethered GCS path,
а не in-flight radio path. Процедура описана у live spoofing-map розділі
посібника з експлуатації. Починаючи з firmware `v0.5.30`, CDC приймає default
secondary-link поведінку Mission Planner, який відкриває порт без asserted DTR;
global workaround
**Reset APM on connect** не потрібен. Core latch може залишатися ready після
закриття COM port на host до від'єднання USB або transmit timeout; від'єднайте
USB, якщо private telemetry треба зупинити негайно. Це не створює жодного
output path до FC, S2 або CAN. USB/COMM2 і FC/S2/COMM0 мають незалежні MAVLink
sequence counters, тому додавання або втрата USB link не створює пропусків у
FC stream.

Cross-check GNSS-висоти проти FC barometer **зараз не активний**, і stream
`ALTITUDE` від польотного контролера не потрібен. ArduPilot не має stream entry
`MSG_ALTITUDE`, тому MAVLink-повідомлення `ALTITUDE` не може бути надане взагалі,
і цей cross-check ніколи не працював за всю історію продукту. Він залишається
підключеним, але вимкненим build flag. Сприймайте баро-порівняння висоти як
майбутню функцію, а не як робочий guard, і не намагайтеся налаштувати для нього
stream. Реально важливі для GPS output повідомлення FC — це `HEARTBEAT` і
`EKF_STATUS_REPORT`.

H743 DroneCAN `v0.5.30+` також явно запитує `AUTOPILOT_VERSION`. Доки не відома
підтримувана версія ArduPilot (4.6.1 або новіша), `Fix2/Auxiliary` негайно
suppressed; старіша повідомлена версія блокується так само. 15-секундний
startup/rebind grace затримує лише warnings і hard fault processing, а не GNSS
publication. Після нього unknown version дає `FC VERSION UNKNOWN` та
`AUTOPILOT_VERSION REQUIRED`, а old version — `FIRMWARE TOO OLD` та `UPDATE TO
ARDUPILOT 4.6.1+`.

Safety stream S2/index `1` працює fail-closed. Після startup і boot-guard grace
node 42 вимагає свіжі decoded FC `HEARTBEAT` та `EKF_STATUS_REPORT`; порожніх
tunnel keepalives недостатньо.

Suppression і DR1 latch — це два окремі рішення, і різниця важлива, коли ви
діагностуєте нестабільний лінк:

- **Suppression миттєвий.** Щойно будь-яке з повідомлень застаріває
  (`HEARTBEAT` > 3 с, `EKF_STATUS_REPORT` > 4 с), `Fix2/Auxiliary`
  зупиняються. Це fail-closed гарантія, і вона не має debounce.
- **Latch чекає 10 с** безперервної staleness перед входом у `DR1/FCLINK`.
  Короткий tunnel stall тому коштує кількох секунд GPS, а не повного циклу
  відновлення. Далі лінк має бути безперервно fresh 5 с, перш ніж таймер
  staleness скинеться, тож лінк, який "блимає" кожні кілька секунд, все одно
  latch-иться, а не утримує GPS мовчки й нескінченно.

Ні DR1 auto-recovery, ні normal rejoin не відновлять GPS publication, доки
обидва messages знову не стануть fresh і configured lock/rejoin gates не
пройдуть.

16-bit `NodeStatus.vendor_specific_status_code` має фіксовану layout без
перекриття:

| Bits | Значення |
|------|----------|
| 15 | DR1 latch active |
| 14 | GNSS output blocked з будь-якої причини |
| 13:7 | Spoof confidence, ціле число 0-100 |
| 6 | Enabled I2C sensor missing або stale після startup grace |
| 5:0 | Код `Dr1Reason` |

Consumers мають застосовувати masks; sensor flag розташований у bit 6, а не 7.

MS4525 `RawAirData` також не залежить від DR0/DR1; те саме стосується HMC5983
`MagneticFieldStrength2`, коли використано `*_dronecan_mag` build. Spoofing
decision блокує лише GNSS `Fix2/Auxiliary`; він навмисно не вимикає airspeed,
увімкнений optional compass, NodeStatus, camera MAVLink або MAVLink фільтра.
Несправний чи від'єднаний I2C sensor припиняє тільки свою valid sensor
publication. Після п'яти секунд sensor startup grace node 42 також показує
DroneCAN warning health і встановлює vendor-status bit 6, доки обидва enabled
sensors не дають fresh samples; це окремий pre-arm/maintenance fault.

GNSS-only guards активні: no fix, low satellites, position jump, altitude
rate/jump, SNR anomaly, hemisphere/geofence, heading reversal, GPS time sanity,
velocity-position consistency і receiver clock jump, якщо дані доступні.

### Вихід із DR1: відновлення вимагає доказів, ніколи — часу

`DR1_MAX_DURATION_MS` дорівнює `0`. DR1 **не** спливає за таймером. Єдині
шляхи назад — evidence quorum, ground release або power cycle.

Quorum потребує щонайменше трьох evidence rows, що погоджуються, **нуль**
що суперечать, утримуваних безперервно, **і щонайменше одного незалежного
witness**. Row рахується як witness лише тоді, коли його операнди були
фізично збуджені:

| Witness | Потрібно |
|---------|----------|
| Ground speed vs pitot | реальна повітряна швидкість, IAS >= 12 м/с і ground speed >= 6 м/с |
| Vertical rate | реальний набір або зниження >= 3 м/с |
| Course vs yaw | реальний розворот >= 12 град/с, зараховується лише на тому проході |

Усі три вимагають **руху**. Це навмисно: нерухомий планер не має фізичного
еталона, здатного суперечити spoofer-у, тож згода на стоянці не доводить
нічого.

**У польоті жодного манёвру не потрібно.** Зі справним pitot рівний крейс
безперервно тримає ground-speed witness. Орієнтовно: `DR_LOCK` 120 с + 60 с
hold = **~180 с** після fix-loss trip, подвоєно до ~240 с для
spoof-integrity trip, плюс 30 с за кожну попередню суперечливу спробу.

**На землі жоден witness недосяжний узагалі**, тож юніт, що спрацював під
час передпольотної підготовки, застряг би до power cycle. Це закриває ground
release. Він замінює witness на узгодженість позиції протягом dwell і
обмежений припаркованим, disarmed планером:

| Умова | Значення |
|-------|----------|
| FC disarmed, позитивно і нещодавно підтверджено | fail-closed; невідомий або stale стан — це НЕ disarmed |
| Ground speed / climb від FC | < 4 м/с / < 1 м/с (поріг швидкості вище виміряного dead-reckoning дрейфу FC: середнє 1.95 / макс 2.84 м/с на нерухомому юніті) |
| Власний pitot фільтра, якщо встановлений і живий | < 12 м/с (вище ~10.6 м/с уявного zero offset сенсора) |
| Узгодженість fix | 30 м горизонтально, 30 м вертикально |
| Власний spoof-індикатор приймача | нижче warning для loss trips; строго чистий для integrity trips |
| Named parked evidence | кожен доступний row не FAIL; GNSS-time має PASS; receiver speed finite, nonnegative, fresh не старша 1500 мс і не більша 4 м/с; speed та location мають одну epoch generation зі skew не більше 1500 мс |
| Optional GSV/SNR | можуть бути unavailable; відсутність не блокує release, але явний FAIL лишається veto |
| Утримується безперервно | 90 с loss / 240 с integrity, +60 с за кожен попередній release |

Parked path **не** використовує generic airborne pass count. Саме тому passive
GGA/RMC receiver може чесно recover на стоянці без вигаданих трьох PASS rows і
без обов'язкового optional GSV. Airborne witness quorum та його pass floor не
змінені.

З чим саме має узгоджуватися fix — залежить від причини trip. Для
signal-loss trip (`NO FIX`, `LOW SATS`, `FC LINK`) еталоном є позиція,
утримувана *до* trip. Для виявленого spoof (`SNR`, `JUMP`, `ALT`, `CONF`,
`HEADING`, ...) той pre-trip anchor довіри не має — slow-walk атакер уже
рухав його — тож сигнал, що повернувся, має натомість лишатися
**самоузгодженим**, горизонтально і вертикально, відносно еталона,
захопленого на старті dwell, упродовж довшого 240 с dwell і з обов'язковою
перевіркою висоти. Integrity releases додатково витрачають окремий ліміт —
**один на power cycle**. `SOUTH` не звільняється автоматично ніколи, за
жодного dwell: fix у південній півкулі для цього планера фізично неможливий
і завжди коштує свідомої дії людини.

`DR_LOCK` не обходиться, тож нижня межа — 120 + 90 + 10 с blend, близько
**3.5 хвилин** від loss trip до `DR0`, і близько **6 хвилин** для integrity
trip.

Після ground release радіус продовжує діяти, поки літак стоїть і disarmed.
Якщо fix виходить за нього, node 42 знову входить у DR1 із причиною
`PARKED_MOVE` (15). Це очікувано, якщо ви фізично перенесли disarmed планер
далі ніж на 30 м — швидкість кроку нижча за "parked" поріг, тож фільтр не
відрізнить це від fix, який "ведуть" убік. Це не несправність: юніт
звільняється знову з нової позиції після наступного dwell, і `PARKED_MOVE`
не витрачає одноразовий integrity-ліміт, тож перенесення після integrity
release не може заблокувати юніт. Загалом ground release обмежений чотирма
разами на power cycle. Operator status називає цю причину `PARKED MOVE`, а
короткий label на екрані плати — `PARKED`.

**Як читати recovery banner.** Debug-рядок 1 Hz називає точно те, що блокує
відновлення:

```
RJ ev3/3F0W0/1p hold=0/60s gnd=45/90s -
```

| Поле | Значення |
|------|----------|
| `ev3/3` | airborne evidence rows passing/required; це не parked-release contract |
| `F0` | airborne rows, що суперечать; ground release окремо veto кожен доступний FAIL |
| `W0/1` | airborne independent witnesses present/required |
| `p` / `a` | airborne speed row на слабкому pre-spoof envelope / на pitot |
| `hold=0/60s` | накопичений airborne evidence hold проти вимоги |
| `gnd=45/90s` | накопичений dwell ground release проти цілі; `0/N` означає, що умови зараз не виконані |
| останній tag | `-` означає відсутність named block; `EVM` — бракує required parked evidence, `EVF` — contradiction, `EVPg` — bounded короткий missing-evidence lapse |

На нерухомому стенді airborne `W0/1` нормальний і не блокує окремий named
parked path. Дивіться на `gnd=` та останній tag; не чекайте зміни показаного
airborne pass count.

## Перевірка

1. Прошийте `weact_mini_h743vitx_dronecan_usb` або ST-Link build. Лише для
   навмисно обладнаної magnetometer direct-flash плати використовуйте
   відповідний `*_dronecan_mag` environment.
2. Підключіть GNSS до `PA2/PA3`.
3. Перехрестіть 3.3 V OpenIPC UART: camera TX -> `PA10`, `PA9` -> camera RX,
   додайте common ground та окреме належне camera power.
4. Через окремий keyed connector підключіть MS4525 до shared `PB10` SCL,
   `PB11` SDA, 3.3 V і GND та перевірте його повний ordering code. Лише для
   `*_dronecan_mag` build підключіть HMC5983 паралельно й перевірте identity
   до power-up.
5. Підключіть `PB9/PB8` до SN65HVD230, а `CANH/CANL/GND` до FC CAN.
6. У ArduPilot увімкніть CAN driver, DroneCAN protocol, 1 Mbps і `GPS_TYPE=9`.
7. Налаштуйте S1 як node `42`/index `0`/115/MAVLink2 і S2 як node
   `42`/index `1`/115/MAVLink2.
8. Встановіть airspeed instance FC на DroneCAN (`ARSPD_TYPE=8` для instance 1)
   і перезавантажте FC. Лише для `*_dronecan_mag` build переконайтесь, що
   node-42 compass також з'явився.
9. Перевірте, що H743 screen світиться і показує GNSS/filter state.
10. Перевірте, що DroneCAN node ID `42` видно у DroneCAN/SLCAN tooling.
11. Перевірте, що ArduPilot бачить DroneCAN GPS, airspeed, camera MAVLink2 і
    filter system ID `42`. Для `*_dronecan_mag` build також перевірте node-42
    compass. Потім перевірте і **зворотний** напрям: фільтр не повинен
    показувати block `FCLINK` (hero card не `BLOCK`/`FCLINK`, немає
    `GNSS BLOCKED #1: FC LINK STALE`). Усе інше в цьому пункті підтверджує лише
    напрям filter -> FC, який працює навіть тоді, коли FC ніколи не стрімить
    `EKF_STATUS_REPORT`; відсутність `FCLINK` — єдина перевірка, що доводить: у
    напрямі FC -> filter реально йде `EKF_STATUS_REPORT`.
    Обережно з однією пасткою: normal statustext фільтра, який дійшов до GCS, нічого не
    доводить про tunnel, поки USB-C фільтра підключений до PC, бо прошивка
    дублює normal diagnostics одночасно у DroneCAN tunnel і USB CDC. (`SP_*`
    position diagnostics — навмисний USB-only виняток.) Перед тим як вважати
    normal GCS-повідомлення доказом роботи tunnel, від'єднайте USB фільтра.
12. За однакового тиску в обох pitot ports виконайте zero calibration; потім
    обережно подайте differential pressure і перевірте positive stable airspeed.
13. **Лише `*_dronecan_mag`:** після final installation відкалібруйте compass, перевірте axes/orientation
    і motor-current interference, а також кілька хвилин роботи з active LTE.
14. Викличте bench DR1 і переконайтесь, що GPS публікації зупинились, а
   `NodeStatus` залишився online.
15. Перевірте, що airspeed і обидва MAVLink2 канали працюють у DR1; для
    `*_dronecan_mag` build також перевірте compass. Приберіть причину DR1 і
    переконайтесь, що GPS publishing відновився.

## Якщо щось не працює

### FC LINK STALE: одна причина, чотири повідомлення

Відсутній FC `EKF_STATUS_REPORT` на tunnel index `1` дає всі чотири
повідомлення ОДРАЗОМ:

- `GNSS BLOCKED #1: FC LINK STALE`
- `PreArm: DroneCAN: Node 42 unhealthy!`
- `PreArm: Selected GPS Node 42 not set as instance 1`
- `EKF3 waiting for GPS config data`

Це ОДНА несправність, а не чотири. Фільтр працює fail-closed щодо свіжості FC
telemetry, тому без `EKF_STATUS_REPORT` він suppress `Fix2` і `Auxiliary`; далі
фільтр повідомляє DroneCAN warning health (звідси `Node 42 unhealthy!`),
ArduPilot не прив'язує GPS instance до цього node (звідси
`not set as instance 1`), а EKF не отримує GPS configuration (звідси
`EKF3 waiting for GPS config data`). Усі чотири зникають самі, як тільки `Fix2`
знову публікується. Не діагностуйте їх окремо.

Не "лікуйте" симптоми:

- Скидання `GPS1_CAN_OVRIDE` лише приховує рядок `not set as instance 1` і не
  повертає GPS.
- Додавання `GPS1_DELAY_MS` теж не допомагає: тут немає жодної timing проблеми,
  яку варто компенсувати, і жодне значення delay не змусить відсутнє
  повідомлення з'явитися.

Ні те, ні інше не торкається причини: FC не доставляє фільтру
`EKF_STATUS_REPORT`. Перевіряйте у такому порядку: stream rate `EXTRA3` на
MAVLink channel фільтра, `SYSID_THISMAV = 1`, MAVLink channel budget (існують
лише `SR0_`..`SR6_`), і тільки в кінці — CAN wiring.

Прошивка `v0.4.8+` називає, якої саме половини evidence бракує. DR1-повідомлення
несе ages як `DR: FC telemetry stale (hb=... ekf=...)`, а періодичний рядок
показує `FC rx=... hb=... ekf=... nack=N`:

- `hb=never` означає, що до фільтра взагалі не доходить MAVLink від FC. Це
  проблема tunnel, protocol або sysid: перевірте `CAN_D1_UC_S2_*`, `_PRO = 2` і
  `SYSID_THISMAV = 1`.
- `hb=0s ekf=never` означає, що tunnel працює і FC говорить, але FC не стрімить
  `EKF_STATUS_REPORT`. Це проблема stream rate/channel, а не проводів.

Airborne recovery не миттєве: має спливти 120 s DR lock, потім evidence quorum
із незалежним witness треба тримати 60 s, далі йде blend. Witness дає
climb/descent щонайменше 3 м/с, справжній turn або live pitot не нижче 12 м/с.
Straight-and-level cruise підходить зі справним pitot вище threshold; без pitot
потрібен sustained climb або turn.

На нерухомому стенді окремий H743 parked path може recover після свого dwell.
Він потребує named GNSS-time плюс fresh same-epoch receiver speed із таблиці
вище, а не airborne witness/pass count, і не потребує optional GSV. Power cycle
пропускає очікування, але більше не є обов'язковою умовою recovery.

### Інші несправності

- Node не видно: перевірте `CAN_Dx_PROTOCOL=1`, bitrate `1000000`, CANH/CANL,
  common ground, termination на кінцях шини, `PB9 -> TXD`, `PB8 <- RXD`.
- FC не бачить GPS: на `v0.5.30+` перевірте `FC VERSION UNKNOWN` /
  `AUTOPILOT_VERSION REQUIRED` або `FIRMWARE TOO OLD` / `UPDATE TO ARDUPILOT
  4.6.1+`. Фільтр явно запитує `AUTOPILOT_VERSION` і негайно suppress GPS до
  підтримуваної відповіді; 15-секундний grace затримує лише warnings. Також
  перевірте `GPS1_TYPE=9`, свіжий GNSS fix, footer `PUB+` /
  `DR0`, а також що hero card не показує `BLOCK` із причиною `FCLINK`, `GPS`,
  `NOFIX`, `SATS`, `JUMP`, `FENCE` або іншою DR1 причиною. `FCLINK` взагалі не є
  GNSS-несправністю — див. **FC LINK STALE: одна причина, чотири повідомлення**
  на початку цього розділу.
- Для firmware старішої за H743 DroneCAN `v0.1.2` перевірте
  `GPS_AUTO_CONFIG=1`.
- Якщо є кілька DroneCAN GPS nodes, задайте `GPS1_CAN_OVRIDE=42` або override
  для відповідного GPS instance.
- MAVLink tunnel не працює: перевірте `CAN_D1_UC_SER_EN=1`, S1 node `42`/index
  `0`/baud `115`/protocol `2` і S2 node `42`/index `1`/baud `115`/protocol `2`.
  Для CAN driver 2 використовуйте `CAN_D2_UC_*`.
- Перевірте camera wiring: camera TX -> `PA10`, `PA9` -> camera RX, 3.3 V logic,
  common ground і MAVLink2 at 115200. Якщо camera не boot-иться з UART,
  спробуйте `MAV_TELEM_DELAY=5` і перевірте її power supply.
- Не діагностуйте DR1 GPS block як несправність tunnel: MAVLink2 virtual ports
  навмисно залишаються активними, поки `Fix2/Auxiliary` suppressed.
  **Це справедливо для кожної причини DR1, КРІМ `FCLINK`.** Block `FCLINK`
  спричинений напрямом FC -> filter у tunnel index `1`, і сам tunnel зазвичай
  повністю справний — просто одне обов'язкове повідомлення не стрімиться. Для
  `FCLINK` СПОЧАТКУ перевіряйте stream rate `EXTRA3` на MAVLink channel фільтра,
  `SYSID_THISMAV = 1` і MAVLink channel budget (лише `SR0_`..`SR6_`), а CAN
  wiring, termination і bitrate — В ОСТАННЮ ЧЕРГУ.
- Airspeed/optional compass не видно: перевірте expected sensor firmware
  option. Production/default build вмикає лише MS4525; HMC5983 потребує
  direct-flash `*_dronecan_mag` build. Перевірте
  `PB10 -> SCL`, `PB11 <-> SDA`, 3.3 V power і common ground. Idle SCL/SDA
  повинні бути приблизно 3.3 V; **5 V pull-up небезпечний для H743**.
- Перевірте один коректний effective pull-up set, swapped SCL/SDA, shorts,
  cable length/noise та duplicate I2C addresses.
- Для MS4525 перевірте повний code `4525DO-DS3AI001DP`, address `0x28`, sign
  і magnitude з відомим малим pressure. Не маскуйте wrong sensor range тільки
  параметром `ARSPD_RATIO`. На FC має бути `ARSPDx_TYPE=8` (DroneCAN), не type
  `1` (local-I2C MS4525 на самому FC).
- **Лише `*_dronecan_mag`:** для HMC5983 перевірте address `0x1E` та ID `H43`. Якщо дешевий module не
  приймається або нестабільно калібрується, підозрюйте clone, а не послаблюйте
  identity check. У Mission Planner перевірте detected compass device ID,
  priority/orientation і повторіть calibration у final position.
- DR1 не вимикає airspeed або ввімкнений optional compass. Якщо sensor зникає
  у DR1, окремо діагностуйте I2C integrity, CAN load/errors і sensor health.
- USB-C DFU не стартує: тримайте `BOOT0` під час reset/power-up, використайте
  data-capable USB-C cable, від'єднайте ST-Link, перевірте RDP state. Якщо
  плата має RDP Level 1, raw PlatformIO app-only ROM DFU upload не зможе її
  оновити. Для вже активованої H743 використовуйте desktop app
  **USB-C ROM DFU** update path, або ST-Link/manual recovery для development
  board, яку треба свідомо відновити.
- Якщо secondary H743 USB port відкривається у Mission Planner з deasserted DTR,
  але telemetry немає, оновіть firmware до `v0.5.30+`: це перша версія, що
  підтримує default DTR-low secondary-link sequence.
- Якщо плата на H743 DroneCAN `v0.1.0` завантажується, синій LED блимає раз на
  кілька секунд, але екран чорний, оновіть H743 DroneCAN до `v0.1.1` або
  новішої. `v0.1.1` виправляє полярність backlight для WeAct LCD (`PE10`
  active-low).
- Дисплей гасне після boot: firmware вимикає backlight, якщо SPI writes до
  дисплея fail. DroneCAN GPS і guard logic продовжують працювати без екрана.

## Посилання на протоколи

- [Official WeAct MiniSTM32H7xx V12 schematic](https://github.com/WeActStudio/MiniSTM32H7xx/blob/master/Hardware/STM32H7xx%20SchDoc%20V12.pdf)
- [Official WeAct ST7735 LCD driver](https://github.com/WeActStudio/MiniSTM32H7xx/blob/master/SDK/HAL/STM32H743/03-LCD_Test/Drivers/BSP/ST7735/lcd.c)
- [DroneCAN `uavcan.tunnel.Targetted` DSDL](https://github.com/DroneCAN/DSDL/blob/master/uavcan/tunnel/3001.Targetted.uavcan)
- [DroneCAN `uavcan.equipment.air_data.RawAirData` DSDL](https://github.com/DroneCAN/DSDL/blob/master/uavcan/equipment/air_data/1027.RawAirData.uavcan)
- [DroneCAN `uavcan.equipment.ahrs.MagneticFieldStrength2` DSDL](https://github.com/DroneCAN/DSDL/blob/master/uavcan/equipment/ahrs/1002.MagneticFieldStrength2.uavcan)
- [ArduPilot DroneCAN serial-port setup](https://ardupilot.org/sub/docs/common-dronecan-serial.html)
- [ArduPilot DroneCAN setup](https://ardupilot.org/copter/docs/common-uavcan-setup-advanced.html)
- [ArduPilot advanced compass setup](https://ardupilot.org/copter/docs/common-compass-setup-advanced.html)
- [TE Connectivity `4525DO-DS3AI001DP`](https://www.te.com/en/product-4525DO-DS3AI001DP.html)
- [OpenIPC FPV/UART guidance](https://github.com/OpenIPC/wiki/blob/master/en/fpv.md)
