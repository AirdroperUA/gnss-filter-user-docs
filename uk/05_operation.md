# Робота під час виконання

> Де купити плату: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

## DR0 vs DR1

- **DR0**: штатний режим. Передавання GNSS на GPS UART FC увімкнене.
- **DR1**: захисний режим. Живе передавання GNSS на GPS UART FC заблоковане — FC отримує тишу.

Це не дозволяє підозрілим живим GNSS-даним потрапляти у навігаційний вхід FC, поки активний DR1.

**Чого це вимагає від літака.** DR1 — це навмисна, раптова й чиста втрата
GPS, і польотний контролер має вміти її пролетіти. Для ArduPlane це означає
**увімкнений (used) і відкалібрований сенсор повітряної швидкості**
(`ARSPD_USE=1`) та компас, що використовується для yaw. У мить, коли `Fix2`
зникає, EKF3 припиняє злиття GPS; з used airspeed він продовжує dead reckoning
за повітряною швидкістю та своєю оцінкою вітру і лишається основним
естиматором. Без нього EKF3 за лічені секунди втрачає горизонтальну
швидкість, `AP_AHRS` переходить на DCM, а DCM без GPS і без airspeed не має
доцентрової корекції: його оцінка положення дрейфує в кожному розвороті, і
автопілот «виправляє» уявну помилку реальним опусканням носа. Це штатна
поведінка ArduPlane без GPS, а не дефект жодної з прошивок, і саме такого
збою слід чекати від літака з `ARSPD_USE=0`. Літак, який не може летіти без
GPS, не повинен літати там, де може спрацювати DR1. Зауважте: різке
відключення — безпечний напрямок; GPS, що «згасає» або змішується, годував би
естиматор поганими даними, а це гірше за їх відсутність.

Чого чекати в журналі польотного контролера після відключення DR1, за
джерелами ArduPlane. `EKF variance` повторюватиметься: `ekf_check` повідомляє,
що дисперсія позиції перевищила `FS_EKF_THRESH`, поки росте невизначеність
dead reckoning; на fixed-wing це лише друкується. Чого *не* має бути з used
pitot — `EKF3 IMUx stopped aiding`: це означає, що airspeed не зливався. А
`AHRS: DCM active` і за кілька секунд `AHRS: EKF3 active` — це DCM-екскурсія
з [посібника H743 DroneCAN](13_h743_dronecan.md), яку прибирає біт 0
`AHRS_OPTIONS` після `ARSPD_USE=1`. `tools/analyze_dr1_transition.py`
розкладає все це з `.bin` або `.tlog`, прив'язуючись до повідомлення фільтра
`GNSS BLOCKED`.

У H743 DroneCAN-прошивці замініть "GPS UART FC" на DroneCAN GPS output:
у DR0 публікуються `Fix2/Auxiliary`, у DR1 ці GPS-повідомлення
припиняються. `NodeStatus` лишається online; spoof/fault DR1 reasons report
warning health, а no-fix, low-satellite і boot guard лишають node health `OK`.
Onboard screen показує `PUB`, `WHY`, CAN counters, arm/safety bits і ArduPilot
`NotifyState`, коли цей broadcast присутній. Повний H743 шлях: [H743 DroneCAN
Guide](13_h743_dronecan.md).

## GPS Data Integrity

У штатному DR0 режимі UART-прошивка не переписує GPS packets. Кожен byte,
отриманий з GNSS UART, парситься для guard state і той самий byte передається
на FC GPS UART. Фільтр не генерує нові NMEA sentences, не reserialize UBX і не
міняє checksums. Якщо захист переходить у DR1, forwarding навмисно
приглушується; FC може побачити тишу або обрізаний кінець поточного receiver
frame у момент блокування.

Прошивка може конфігурувати receiver під час boot. Наприклад, default u-blox
profile задає UART baud і message set, потрібні фільтру. Це змінює те, що
emits сам receiver, але коли byte вже прийшов у фільтр у DR0, UART output path
передає його без змін. Normal FC GPS back-channel drain/count only; він не
forward-иться до receiver, тому ArduPilot не може непомітно змінити receiver
message profile через фільтр.

H743 DroneCAN mode інший, бо там немає FC GPS UART. Він не tunneling raw NMEA
або UBX. Він перетворює live receiver fix fields у native DroneCAN
`Fix2/Auxiliary`: latitude/longitude, altitude, velocity, satellites, DOP і
accuracy масштабуються в DroneCAN units. У штатному режимі він не використовує
synthetic або blended GPS coordinates.

Вбудований статусний LED відповідає тому самому стану, який видно в логах:

- **DR0**: один короткий спалах приблизно кожні 6 секунд.
- **DR1**: швидке блимання, приблизно чотири рази на секунду.

### Діаграма станів

```
                    ┌──────────────────────────────────┐
                    │                                  │
                    ▼                                  │
              ┌──────────┐    guard-тригер       ┌──────────┐
   старт ───► │   DR0    │ ───────────────────►  │   DR1    │
              │ (норма)  │    (стрибок позиції,  │ (захист) │
              │          │     no-fix, SNR,      │          │
              │ GPS      │     поганий EKF тощо) │ GPS      │
              │ іде на FC│                       │ заблок.  │
              └──────────┘  ◄─────────────────── └──────────┘
                    ▲         умови rejoin:            │
                    │         • RJ_MIN_SATS виконано   │
                    │         • RJ_MAX_HD виконано     │
                    │         • RJ_STAB_MS витримано   │
                    │         • DR_LOCK_MS минув       │
                    │         • незалежні evidence    │
                    │                                  │
                    └──────────────────────────────────┘
                          rejoin guard (500 мс)
                          не дає одразу спрацювати знову
```

## Тригери DR1 (поточна прошивка)

- No-fix потребує щонайменше 3 різні невалідні GNSS-епохи, між першою та
  останньою з яких минуло не менше 600 мс. Low satellites (`sats < 5`)
  використовує peak count у ковзному вікні приблизно 3 секунди та потребує 3
  різні low-count епохи з інтервалом щонайменше 200 мс. Для обох шляхів діє
  startup guard.
- Також DR1 можуть викликати перевірки стрибка позиції, висоти, SNR та EKF (залежно від параметрів).
- Обидва released targets використовують default `EKF_TRIPMS=500`. Кожна bad
  EKF category, включно з `GPS_GLITCHING` і `UNINITIALIZED` після першого
  healthy report у FC session, потребує щонайменше 2 нові декодовані
  `EKF_STATUS_REPORT`, що охоплюють повний налаштований інтервал. Tune у zero
  все одно зберігає мінімум 2 reports; startup `UNINITIALIZED` дозволений лише
  до першого healthy report.
- Стрибок у південну півкулю: якщо широта GPS стає менше 0°, DR1 спрацьовує миттєво. У штатному режимі фільтр блокує будь-яку позицію південної півкулі від потрапляння на FC (всі дрони працюють у північній півкулі).
- Порушення гео-огорожі (якщо `FENCE_RAD > 0`): позиція за межами радіусу (до 2000 км) від першого фіксу.
- Розворот курсу: зміна на 150°+ при швидкості >5 м/с має бути підтверджена 3
  різними епохами; інтервали між ними не більші за 2,5 с, а всі 3 мають
  вміститися у 5 с. Потім високий score має протриматися зовнішнє
  1,5-секундне вікно до score-only входу в DR1.
- Аномалія часу GPS: відхилення >2 с між часом GPS та внутрішнім годинником.
- Максимальна тривалість DR1 (`DR1_MAXMS > 0`): автоматичний вихід з DR1 після заданого таймауту, але лише після завершення `DR_LOCK_MS`.

### Оцінка достовірності спуфінгу

Прошивка обчислює зважену оцінку (0–100) з до 10 сигналів виявлення. Бал
видно в Mission Planner як `DR_CONF` і записується в кожен лог подій. Вищі
значення означають більше ознак спуфінгу. Недоступні через target, transport
або protocol рядки не входять до знаменника.

### Доступність confidence-сигналів

| Сигнал | Вага | u-blox | UM980 / Mosaic NMEA | Mosaic SBF на H743 |
|--------|------|--------|---------------------|--------------------|
| Розходження вертикальної швидкості баро та GNSS | 20 | H743 DroneCAN | H743 DroneCAN | Так |
| Аномалія SNR span | 20 | Так | Так | Так |
| Receiver spoof verdict (`SEC-SIG`) | 25 | Лише H743 | Ні | Ні |
| Стандартне відхилення pseudorange | 15 | Так | Ні | Ні |
| Часова кореляція SNR | 12 | Так | Частково | Так, з `MeasEpoch` C/N0 |
| Розворот курсу | 12 | Так | Так | Так |
| Різка зміна GDOP | 8 | Так | Ні | Ні |
| Перевірка часу GPS | 12 | Так | Так | Так |
| Відповідність швидкість-позиція | 10 | Так | Частково | Так |
| Стрибок тактового зсуву | 11 | Так | Ні | Так |

Receiver-spoof verdict компілюється лише для H743 і потребує підтримуваний
u-blox. Barometric vertical-rate row компілюється лише у DroneCAN-збірках і
потребує свіжої барометричної телеметрії FC та вертикальної швидкості GNSS.
Pseudorange residual потребує UBX `NAV-SAT`, GDOP jump — `NAV-DOP`, а clock
row u-blox — `NAV-CLOCK`. Velocity-position consistency працює і з пасивним
NMEA, але точніше з NED velocity з NAV-PVT. Mosaic SBF відновлює binary C/N0
temporal і clock-bias coverage; pseudorange-residual та GDOP-jump scoring у
Mosaic mode недоступні.

## Стартова затримка

- `BOOT_DLYMS` задає вікно після старту, протягом якого DR/EKF-тригери не переводять систему в DR1.
- Збільшуйте `BOOT_DLYMS`, якщо DR1 з'являється одразу після вмикання і зникає після reset.

## Режими відмовостійкості (watchdog, перезавантаження в польоті, втрата лінку FC)

Фільтр розроблений так, щоб пережити кілька сценаріїв відмов без втручання оператора. Розуміння цих механізмів допомагає правильно читати логи та планувати відновлення.

### Апаратний watchdog (IWDG: 15 с boot, 2 с runtime)

STM32 запускає незалежний апаратний watchdog від internal LSI (~32 кГц).
Під час boot він дає **15 секунд** на receiver probing та іншу одноразову
initialization, а після завершення setup переходить на **2-секундний runtime
deadline**. Якщо parser path, CPU fault, stuck bus або interrupt не дає main
loop дійти до фінального reload, MCU reset відбудеться приблизно за дві секунди.

Коли debugger або provisioning-додаток зупиняє чип через SWD, прошивка H743 v0.4.3 і новіша заморожує цей watchdog на час debug-сесії (DBGMCU freeze bit), щоб тривалі flash-операції, як-от повний erase чипа, не переривалися посередині. У польоті це ні на що не впливає — заморозка діє лише поки debugger тримає core зупиненим.

Симптоми в логах:
- Неочікуваний `BOOT t=0ms` посеред польоту без ручного перезавантаження.
- GNSS interruption, повна тривалість якого включає runtime deadline, reboot,
  receiver autobaud і відповідний boot guard; не припускайте фіксовану межу
  recovery менше 15 секунд.

15-секундний boot allowance покриває worst-case receiver initialization;
2-секундний flight-time deadline починається лише після setup. Жоден із них не
є Mission Planner parameter.

### Перезавантаження в польоті при вже армованому FC

Якщо фільтр перезавантажується, а польотний контролер уже армований (brownout, електромагнітний імпульс, watchdog-reset у польоті), стандартне 20-секундне вікно `BOOT_DLYMS` автоматично скорочується до **2 секунд**, щоб пересилання GPS відновилося якнайшвидше. Фільтр визначає армований стан FC за прапорцем `SAFETY_ARMED` у `HEARTBEAT` — перший армований heartbeat після старту колапсує залишок вікна.

Послідовність:
- Фільтр стартує на T=0.
- Приблизно на T≈150 мс починає слухати MAVLink.
- Перший `HEARTBEAT` від FC з `SAFETY_ARMED=1` прибуває незабаром — зазвичай менше ніж за 1 с.
- Час звільнення boot DR guard переписується на `fc_armed_first_seen + 2000 мс`.
- Найгірший сумарний «сліпий» інтервал: час autobaud (u-blox ~2.9 с, UM980 короткий ~2.7 с, UM980 довгий ~11.5 с) плюс 2 с на settle. Типовий випадок для u-blox або короткого UM980: менше 5 с.
- На передньому фронті армування в GCS надсилається одне попередження `Boot DR guard shortcut: FC armed at boot, release in 2000ms`.

Якщо на момент перезавантаження FC **не армований** (наприклад, стенд перед польотом), застосовується повне вікно `BOOT_DLYMS` — це навмисно, бо холодний старт на столі не повинен довіряти першим секундам фіксу.

**Накопичений підсумок палива переживає перезавантаження лише тоді, коли разом
із ним зберігся надійний V2 record у BKPSRAM** (H743 DroneCAN `v0.5.28+`;
provenance V2 у `v0.5.30`). Фільтр довіряє record, а не reset-cause flag, тому
відновлює придатний record після watchdog, hard fault, brownout і навіть за
наявності POR/PDR indication. Він повідомляє `Reset in flight - fuel total kept:
N g`.

POR/PDR доводить лише електричне скидання. Він не доводить, що оператор зупинив
механічний двигун або заправився: глибоке просідання живлення в польоті може
стерти BKPSRAM, поки двигун продовжує працювати. Тому **кожен відсутній,
пошкоджений або legacy V1 backup record означає TOTAL LOST при кожному boot**,
зокрема при звичайному вмиканні живлення. Навіть збережений V2 fuel record
анулюється, якщо H743 tune journal відсутній, пошкоджений або не має valid
record: без durable settings місткості, густини та моделі provenance числового
total невідомий. Автоматичного shortcut «cold boot означає свіжий повний бак»
немає.

H743 DroneCAN v0.5.32 додає один вузький explicit exception для двигуна з
ручним запуском, GPIO pulse pickup якого не може повідомити healthy zero при
зупинці. У цьому стані ArduPilot передає точну MAVLink пару `RPM1=-1,
RPM2=-1`. Ця пара лишається **invalid/unavailable у всій звичайній fuel
model**: firmware ніде глобально не перетворює її на нуль, і пізніше в цій
сесії вона не може очистити running-engine latch. Вона може лише дозволити
одноразову cold manual-start declaration, коли щонайменше 3 секунди
безперервно виконуються всі умови:

- це справжній cold POR після повного зняття живлення (valid retained backup
  може існувати; він визначає fuel-total provenance, а не physical-stop
  eligibility);
- FC positively identified як supported ArduPilot family/version;
- FC свіжо повідомляє **DISARMED**;
- fresh RPM messages лишаються точно `-1/-1`; і
- throttle свіжо закритий.

Автоматичної зміни стану все одно немає. Для LOST/unconfigured total readiness
повідомляє `Cold manual-start ready: write positive FUEL_CAPG`. Для trustworthy
retained total натомість з'являється `Cold OFF ready; write FUEL_CAPG only if refuelled`;
не стирайте surviving total лише для очищення latch. Навмисний
**позитивний** запис `FUEL_CAPG` після фактичної заправки або при
re-establishing LOST/unconfigured total за достовірно відомим паливом на борту
є підтвердженням оператора, що двигун із ручним запуском у цій cold session ще
не запускали.
Прийнятий запис очищає лише RAM engine latch, обнуляє
fuel total і витрачає one-shot. `FUEL_DENS` можна записати, доки готове те саме
cold evidence, але density write не витрачає one-shot; після фактичної зміни
густини дочекайтеся `Tune saved`, а тоді запишіть позитивний `FUEL_CAPG`. Zero
відхиляється з `Cold FUEL_CAPG must be positive weighed fuel`.
Будь-який armed report, RPM не менше 1, open-throttle observation або observed
reset FC peer/session назавжди скасовує one-shot до наступного повного зняття
живлення. Кожен reset H743 повертає консервативний engine-may-be-running latch.
Reset button, watchdog, brownout або warm reboot не відновлює eligibility:
потрібно повністю зняти живлення й знову виконати cold conditions.

При lost total фільтр **не надсилає жодного DroneCAN ICE Status packet**: EFI
backend ArduPilot має стати stale/unhealthy, а не прийняти хибний numeric total.
Кожні 60 с повторюється `Fuel total LOST - write FUEL_CAPG to restart it`, а
warning ladder мовчить. Посадіть літак або лишайтеся на землі та дочекайтеся
або normal fresh stopped-engine quorum (FC fresh disarmed, RPM fresh valid
zero, throttle fresh closed), або описаної вище cold manual-start declaration.
Лише тоді навмисно запишіть позитивний `FUEL_CAPG` для фактично залитого
палива. Після звичайного вмикання без
придатного retained record цей запис потрібно повторити, **навіть якщо числове
значення `FUEL_CAPG` не змінилося**. Самого disarmed indication недостатньо, і
запис відхиляється з `FUEL_CAPG blocked: engine not confirmed stopped`, доки
всі три fresh observations не збігаються. Прийнятий запис обнулить running
total і скасує ще не застосоване 25-секундне нарахування старого відновленого
total. Якщо числова місткість не змінилася, він може одразу зняти lost-total
lockout. Якщо місткість змінилася, total лишається TOTAL LOST, а EFI мовчить до
успішного asynchronous save tune journal і повідомлення `Tune saved`;
`FUEL_CAPG written - fuel total zeroed` саме по собі не доводить persistence чи
відновлення EFI. `Tune save failed` лишає total lost, а save — pending для
повторної спроби. Вигаданий нуль читався б як повний бак — саме цього цей path
не має надсилати.

`FUEL_DENS` використовує той самий normal stopped-engine quorum або готову
cold manual-start declaration. Density write не витрачає cold one-shot; його
витрачає лише прийнятий позитивний `FUEL_CAPG`. Фактична зміна
густини позначає total як LOST до застосування нового значення, скасовує старий
pending capacity commit і тримає EFI silent. До успішного verified save density
journal записи місткості відхиляються з
`FUEL_CAPG blocked: wait for FUEL_DENS save`; failed save лишає стан blocked і LOST. `Tune saved` знімає pending-density
block, але не відновлює паливо. Лише після цього наступний stop-authorized
positive `FUEL_CAPG` встановлює fresh zero за нової густини.

Спроба factory reset позначає fuel total як LOST у BKPSRAM **до** початку першої
flash operation. Тому навіть спроба, що повідомила storage failure, може
консервативно лишити EFI silent. Після будь-якої спроби factory reset перевірте
всю конфігурацію fuel model, не запускайте двигун і запишіть `FUEL_CAPG` для
фактичного палива на борту; успішний запис зі зміненою місткістю все одно
потребує `Tune saved`, перш ніж EFI відновиться.

Кожен boot також починається з консервативного припущення, що двигун міг
працювати. Зазвичай цей latch очищає лише fresh disarmed state разом із fresh
valid zero RPM і fresh closed throttle. Єдиний exception — explicit positive
`FUEL_CAPG` у one-shot cold manual-start window вище; звичайний write,
unavailable RPM sentinel після запуску двигуна і link silence latch не
очищають. Після відновлення придатного V2
record firmware додає фіксоване **25-секундне нарахування за номінальною
потужністю** за неспостережуваний reset gap. Цей bound покриває до 2 с
застарілості backup save, найдовший шлях налаштування UM980 приблизно 11.5 с,
інший startup overhead і запас. У H743 немає Phase-C boot wait. Це навмисно
консервативне обмежене нарахування, а не доказ точної витрати палива.
Integration clock також
запускається ще під час ранньої ініціалізації backup, тому будь-який додатковий
час receiver/setup нараховується, а не мовчки відкидається.

Restore захищений durable write-ahead marker. Одразу після копіювання known V2
total у runtime retained record у BKPSRAM переписується як TOTAL LOST ще до
початку risky setup. Успішний boot замінює цей marker на known record лише після
інтегрування і фіксованого 25-секундного нарахування, і першого measured
interval. Якщо до завершення цього known commit станеться ще один reset,
наступний boot лишиться LOST, а EFI буде suppressed, доки normal stopped quorum
або newly eligible cold authorization не дозволить positive `FUEL_CAPG`. Це не
дає repeated setup resets повторно
використовувати один stale known total, нарахувавши його неспостережуваний час
лише один раз.

> **Ніколи не виконуйте Phase-C maintenance при працюючому двигуні.** Фіксований
> 25-секундний allowance покриває обмежену reset/startup роботу, а не довільно
> довгу maintenance session, яку оператор залишив підключеною.

### Staleness MAVLink від FC (fail-safe при втраті лінку)

Ця логіка працює через фізичний FC telemetry UART у UART-збірках і через
virtual port S2/index `1` у H743 DroneCAN.

Прямий FC-link guard для DR1 контролює два safety streams: `HEARTBEAT` і
`EKF_STATUS_REPORT`. Heartbeat стає stale через 3 с. EKF status стає stale
через 4 с на H743 (через 2 с на F401 з прямим UART). Якщо хоча б один із них
лишається поза своїм freshness-вікном ще 2 безперервні секунди, фільтр входить
у DR1. Так одиничний затриманий кадр відрізняється від стійкої втрати лінку.

Інші поля не запускають FC-link guard безпосередньо. Stale `ATTITUDE` або
`VFR_HUD` заморожує/прибирає відповідне synthetic-motion evidence, а stale
`SCALED_PRESSURE` прибирає barometric evidence, щоб заморожене значення не
створило хибне порівняння. `ALTITUDE` не є частиною цього шляху: ArduPilot не
має streamable MAVLink `ALTITUDE`, тому де застосовне барометричне джерело,
прошивка використовує `SCALED_PRESSURE`. При втраті лінку фільтр **не**
виходить примусово з DR1.

При trip з'являється `DR: FC telemetry stale (hb=... ekf=...)`: `never`
означає, що stream не був декодований після boot, а числа показують вік у
секундах.

Fuel accounting навмисно продовжується крізь цю відмову. Коли fresh armed
state, running RPM або open throttle уже показали, що engine може працювати,
тиша не очищає latch. Після втрати RPM estimator нараховує rated-power burn і
продовжує cumulative total. Очистити latch може лише fresh explicit agreement:
disarmed + zero RPM + closed throttle. Cold `-1/-1` declaration уже
unavailable після будь-якого running evidence, тому вона не може перетворити
failed pickup на false stop після запуску. Той самий update виконується під час
FC-version hard block, тому fail-closed navigation state не заморожує fuel
clock мовчки.

### Gate identity прошивки FC

FC version — окремий publication gate, а не vote recovery з DR1. Починаючи з
H743 DroneCAN v0.5.30, filter явно надсилає message-interval request і
`MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES` для `AUTOPILOT_VERSION`. GNSS output
suppressed одразу, поки version невідома, і лишається suppressed для ArduPilot
старішого за 4.6.1. Grace 15 с починається лише після появи FC transport target
і відкладає тільки repeating warning/hard processing block; GPS він ніколи не
дозволяє. Після grace невідомий FC показує `FC VERSION UNKNOWN` та
`AUTOPILOT_VERSION REQUIRED`; відомий старий FC — `FIRMWARE TOO OLD` і
`UPDATE TO ARDUPILOT 4.6.1+`. Peer reset/rebind скидає попередній version
credit і знову стартує fail-closed.

H743 DroneCAN `v0.2.0+` не має фізичного FC MAVLink UART, але S2/index `1`
передає MAVLink2 фільтра й повертає FC telemetry. Тому EKF-status trip,
barometric vertical-rate evidence, arm-state logic і MAVLink `STATUSTEXT`/`NAMED_VALUE`
логи працюють, якщо S2 налаштовано. Camera S1/index `0` також активний у DR0 і
DR1; у DR1 зупиняється лише публікація native GPS `Fix2/Auxiliary`.

### Максимальна тривалість DR1 (`DR1_MAXMS`)

За замовчуванням, після активації DR1 фільтр залишається у DR1 доти, доки нормальні ворота повернення не звільнять його — жодного таймаут-виходу за часом. Якщо профіль місії не може дозволити відкритий термін DR1 (наприклад, далекомагістральний політ, де втрата GPS на весь залишок маршруту гірша за частково-відновлений GPS), встановіть `DR1_MAXMS` у ненульове значення в мілісекундах. Коли воно досягнуто, фільтр примусово виходить з DR1 і поновлює пересилання, навіть якщо підозра на спуфінг залишається високою.

`DR1_MAXMS` не може обійти `DR_LOCK_MS`: якщо максимальний таймер спрацював першим, фільтр усе одно залишається у DR1 до завершення блокувального вікна. За замовчуванням `DR1_MAXMS=0` — примусовий вихід за максимальною тривалістю вимкнено. **Використовуйте обережно** — значення за замовчуванням безпечніше для більшості місій.

Для стендових тестів можна використовувати короткі значення DR lock, щоб не чекати хвилини між спробами. Після перевірки на стенді встановіть `DR_LOCK_MS=120000` або більше для реальних польотів, щоб кожен тригер DR1 утримував захист щонайменше 2 хвилини перед тим, як будь-який шлях rejoin або forced-exit зможе повернути DR0.

## Діагностика пересилання GNSS

- `FCGPS_FWD=1` примусово вмикає FC GPS UART і сире пересилання GNSS навіть у DR1, до стартової північної перевірки та під час спрацювання огорожі півкулі. Лише для стендової діагностики.
- `FCGPS_FWD=0` — штатний anti-spoof режим.
- H743 DroneCAN не має `FCGPS_FWD` raw UART bypass. Перевіряйте шлях через
  DroneCAN/SLCAN tooling і onboard screen: node ID `42` лишається online,
  `Fix2/Auxiliary` публікуються тільки коли output allowed.

## Режим приймача

- `GNSS_TYPE=0`: режим u-blox/UBX.
- `GNSS_TYPE=1`: режим UM980/UM981/UM982 NMEA.
- `GNSS_TYPE=2`: режим Septentrio Mosaic X5. H743 DroneCAN приймає SBF або NMEA; UART-збірки використовують NMEA.
- Зміна `GNSS_TYPE` застосовується після перезавантаження STM32.
- У `GNSS_TYPE=1` або UART/F401 `GNSS_TYPE=2` STM32 очікує один фізичний NMEA-потік на `A2/A3` і пересилає цей самий потік на GPS UART FC.
- У H743 DroneCAN `GNSS_TYPE=2` STM32 може парсити Mosaic SBF на `A2/A3` і публікувати GPS через CAN.

## Приклад логів (GCS)

Нижче приклад формату статусних повідомлень у GCS.

- У вкладці Mission Planner `Messages` ці періодичні логи STM32-фільтра зазвичай з’являються приблизно раз на **10 секунд**.
- Зазвичай ви бачите два сусідні рядки:
  - рядок зведення GNSS: `data=... fix=... nav=... SATS=... SNR=...`
  - рядок режиму/стану: `ARM=... DR=... BLEND=... LAT=... LONG=...`
- У H743 DroneCAN `v0.2.0+` ці повідомлення йдуть через S2/index `1`;
  налаштуйте цей virtual port, перш ніж вважати відсутність логів несправністю.
- Якщо під час тюнінгу логів або SNR Mission Planner показує лише сирі назви параметрів, встановіть [AirDroper Mission Planner Mod](https://gps.airdroper.org/download/mission-planner-mod) і оновіть список параметрів.
- `fix` — це вік останнього валідного позиційного/висотного фіксу; `nav` — вік останнього валідного GNSS nav-data кадру, який бачить фільтр.
- `SNR=NA` означає, що фільтр зараз не отримує придатні SNR-дані від приймача. Для u-blox це зазвичай означає, що приймач не видає `NAV-SAT`. Для NMEA-приймачів, таких як UM980 або Mosaic X5, це означає, що не надходять речення `GSV`. Для H743 DroneCAN Mosaic SBF це означає, що `MeasEpoch` відсутній, застарілий або не має придатного C/N0.
- На u-blox у прошивці v1.6.12+ тривалий `SNR=NA` також виводить рядок `snrdbg n... a... l... s... g... o... b...`: кількість NAV-SAT кадрів, вік кадру, останню довжину, кількість супутників за приймачем, супутники з придатним C/N0, oversize-дропи та malformed/checksum-дропи.
- На u-blox у прошивці v1.6.15+ команда відновлення заново вмикає NAV-SAT через legacy `CFG-MSG` і `CFG-VALSET` на UART1/UART2 лише коли NAV-SAT кадри відсутні або застарілі. Рядок на кшталт `NAV-SAT cfg ack legacy=1 u1=1 u2=1` показує, які шляхи приймач підтвердив.
- На u-blox у прошивці v1.6.16+ таймер відновлення запускається, коли SNR уперше стає застарілим, але переписування конфігурації все одно чекає, поки застаріє сам NAV-SAT. Це скорочує відновлення після періодичного `SNR=NA`, спричиненого зміною NAV-SAT на боці приймача, приблизно з двох вікон застарівання до одного.
- На u-blox у прошивці v1.6.18+ штатний захищений режим зчитує байти FC GPS back-channel, але не пропускає їх у приймач, тому записи автоконфігу ArduPilot не можуть вимкнути `NAV-SAT`.
- На u-blox у прошивці v1.6.19+, якщо приймач відповідає, але до DR1 залишається на `SATS=0`, фільтр автоматично надсилає u-blox cold start і reinit STM32 приблизно через 2 хвилини. Він не запускає `UBX_RESET=3` автоматично. Після автоматичної спроби він логує `If stuck: bench UBX_RESET=3`; використовуйте стендові кроки recovery нижче лише якщо захоплення супутників усе ще не відновлюється.
- На u-blox у прошивці v1.6.21+, якщо здоровий fix уже є, а потім NAV-SAT зникає, перше повторне увімкнення NAV-SAT запускається приблизно через 8 секунд замість штатного 30-секундного вікна застарілого SNR. Startup і no-fix випадки залишають повільніший шлях.
- На u-blox у прошивці v1.6.22+ прямий режим autoconfig (`UBX_BAUD=0`) під час старту очищає/завантажує стандартні налаштування приймача, повторно сканує baud приймача, потім застосовує і зберігає UBX-профіль фільтра. Ручний режим baud (`UBX_BAUD>0`) пропускає це стартове очищення і залишає профіль приймача під контролем оператора або виробника.
- Якщо `SNR_EN=1` і `SNR=NA` тримається понад 30 секунд, у GCS фіксується попередження `WARNING: SNR_EN=1 but SNR=NA/stale (no fresh GSV/NAV-SAT?)`. SNR-захист не може спрацювати, поки відсутні SNR-дані.
- Якщо `SATS=0`, `fix=9999ms`, а `nav` свіжий, приймач відповідає, але не має валідного позиційного фікса. На u-blox у прошивці v1.6.15+ параметр відновлення `UBX_RESET=1` робить hot start, `UBX_RESET=2` cold start, `UBX_RESET=3` очищає збережену конфігурацію приймача і завантажує стандартні налаштування.
- На u-blox у прошивці v1.6.15+ стан без фікса або без супутників також виводить `ubxpvt ...`, `ubxrf ...`, `ubxsig ...` і `ubxgnss ...`. `ubxpvt` показує прапори фікса NAV-PVT, `ubxrf` — стан антени/RF, стан глушіння і придушення CW-перешкод, `ubxsig` — явний стан глушіння/спуфінгу, якщо приймач це підтримує, а `ubxgnss` — увімкнені блоки GNSS-сузір'їв.

### Відновлення u-blox без фікса

Якщо в логах є `SATS=0`, `fix=9999ms`, свіжий `nav` і `ubxpvt f0 ... sv0`,
приймач відповідає, але не має валідного позиційного фікса. На стенді спробуйте:

1. Встановіть параметр Mission Planner `UBX_RESET` у `3`.
2. Дочекайтесь `UBX_RESET=3 clearing u-blox config` і `u-blox config cleared; reinit in 5s`.
3. Повністю перезапустіть живлення GPS/фільтра.
4. Перевірте надворі з відкритим небом протягом 10-15 хвилин.
5. Тримайте `SNR_EN=0`, доки приймач знову не отримає стабільний фікс.

`UBX_RESET=3` видаляє збережену конфігурацію приймача u-blox у BBR/Flash.
Використовуйте це лише для відновлення або стендової діагностики, не як
звичайне польотне налаштування.
Прошивка v1.6.22+ не запускає `UBX_RESET=3` автоматично, але прямий u-blox
autoconfig може автоматично очищати збережену конфігурацію u-blox під час старту
перед завантаженням стандартних налаштувань приймача і записом профілю фільтра. Для
custom/gateway приймачів, які повинні зберігати профіль оператора або
виробника, встановіть `UBX_BAUD>0`.

![Приклад логів](../diagrams/log_example.jpg)

## Послідовність повернення з DR1

Коли умови rejoin виконані:

1. Запускається таймер стабільності rejoin.
2. За потреби відпрацьовує blend на `BLEND_MS`.
3. Фільтр виходить із DR1 і відновлює DR0 (пересилання GNSS).

## Live map спуфінгу в Mission Planner

H743 DroneCAN `v0.5.29+` та
[AirDroper Mission Planner Mod](https://gps.airdroper.org/download/mission-planner-mod)
можуть показати, як під час DR1 рухається координата, яку повідомляє приймач.
Plugin додає компактний status strip, вікно **Details** і Flight Data map overlay:

- **червоний значок літака** — receiver-reported, untrusted GNSS position і
  trail: місце, яке заявляє приймач, а не виміряна фізична істина;
- **помаранчевий значок літака** — wind-blind DR reference estimate фільтра;
  він може дрейфувати через вітер або завмерти при stale speed/yaw telemetry;
- **зелений значок літака** — position estimate польотного контролера, також
  не ground truth;
- **фіолетова пунктирна лінія** — live provisional RF-**вісь**
  (`пеленг / пеленг+180°`), а не стрілка чи позиція джерела;
- тонкі фіолетові лінії — фіналізовані осі, а фіолетова мішень із пунктирним
  колом — строгий advisory-перетин трьох осей;
- connector lines показують distance і bearing від DR/FC estimates до
  недовіреної координати приймача.

Якщо fresh heading недоступний, aircraft замінюється ненапрямленою точкою;
plugin ніколи не вигадує курс на північ.

Панель також показує DR0/DR1, active і latched trip reasons, confidence, event
count, freshness потоку, u-blox RF/jamming diagnostics та live fit осі або
причину відмови від оцінки. Коли samples stale, live markers і RF-вісь
ховаються. Confidence нормалізований за доступними свідченнями, тому нуль сам
по собі не доводить, що сигнал чистий.

### Підключення двох каналів

1. Встановіть Mission Planner Mod і перезапустіть Mission Planner.
2. Підключіть FC звичайним способом і залиште його primary connection.
3. Другим USB-C кабелем підключіть H743-фільтр напряму до комп'ютера GCS.
4. У Mission Planner **Connection Options** додайте COM port H743 як secondary
   MAVLink connection на `115200`. Mission Planner виконає свій normal
   parameter request; окремий parameter step не потрібен.
5. Відкрийте Flight Data і натисніть **Details** у смузі AirDroper. Під час DR1
   вважайте червону/помаранчеву точки актуальними лише тоді, коли поле
   **Private USB stream** показує `LIVE (private USB: COM...)` і називає COM
   port H743.

USB-пристрій H743 має VID/PID `0483:5740` і product
`AirDroper_GNSS_Filter_H743_DroneCAN`. Звичайний DR status може приходити через
primary FC link, але live receiver і DR-reference coordinates виходять лише
через це private USB connection. Вони ніколи не входять у S2, CAN або шлях до
FC. Так зберігається абсолютне правило: у DR1 GNSS position не має досягти FC.

Firmware v0.5.30+ приймає Mission Planner secondary connection із DTR
deasserted і чисто re-enumerates CDC під час boot. USB також має власну MAVLink
transmit sequence, окрему від FC/S2, тому interleaved normal і private `SP_*`
frames не створюють sequence holes на жодному link. Сам private `SP_*` feature
з'явився у v0.5.29; DTR і sequence corrections починаються з v0.5.30.

Direct cable придатний для стенда або GCS, фізично tethered до літака. Для
untethered/long-range використання потрібен окремий out-of-band radio чи
companion path; наявний FC tunnel ці координати не нестиме. Перед польотом на
стенді подайте рухому false solution і одночасно запишіть raw CAN: USB має
показати track, а CAN не повинен містити `Fix2`, `Auxiliary` чи private records
`SP_*`.

## Пошук джерела завад: live і post-flight оцінка напрямку

H743 DroneCAN `v0.5.27+` видає радіоспостереження, потрібні для оцінки ПЕЛЕНГА
на джерело завад або спуфер. Mission Planner plugin `v0.3.0+` може підганяти їх
live, а `tools/df_analyze.py` — ті самі записи після польоту. **Фільтр не
обчислює пеленг на борту** і не повертає нічого з цього у виявлення чи
відновлення — він лише видає телеметрію, і тест гарантує, що ця підсистема
ніколи не може записати стан фільтра чи ввімкнути DR1. Ця ізоляція навмисна:
пеленг, здатний впливати на DR1, дав би зловмиснику важіль, яким він керує
потужністю передавача й позицією.

**Як пеленг узагалі можливий з однією антеною.** Миттєво — ніяк: одна антена
це один фазовий центр, тож інтерферометрії немає. Пеленг дає РУХ. Наземне
джерело приходить біля або нижче горизонту — саме там, де падає підсилення
патч-антени і де її затіняє планер, — тож прийнята потужність завади
модулюється з курсом однопелюстковою формою, максимум якої вказує на джерело.
Підгонка цієї модуляції на розвороті дає пеленг із точністю приблизно ±20–45°.

Записи — це `NAMED_VALUE_INT`, тож ArduPilot логує їх у dataflash автоматично.
Fit використовує курс, переданий у `DF_YAW`. Одна вісь не визначає position чи
range; plugin `v0.3.0+` може окремо перетнути кілька фіналізованих осей за
строгими gates нижче:

| Запис | Вміст |
|-------|-------|
| `DF_RF` | AGC, індикатор завад, стан завад і статус антени, упаковані бітами |
| `DF_NOIS` | рівень шуму приймача |
| `DF_SNR` | максимальний/мінімальний C/N0 і кількість супутників, з яких вони взяті |
| `DF_YAW` | останній fresh курс FC під час видачі RF record, у сотих частках градуса |

Курс може бути застарілим до двох секунд; його точний age не передається.
Викликана цим фазова похибка не входить у показаний fit sigma, тому sigma не є
повною гарантією точності. Частота — 1 Гц у звичайному режимі і 5 Гц, щойно
приймач повідомляє про підвищені завади або спрацьовує DR1: 1 Гц дає аліасинг
пелюстки на розвороті 20°/с.

### Live у Mission Planner

Для відкритої RF-осі достатньо звичайного telemetry link FC. Другий private
USB-кабель додатково потрібен для червоної/помаранчевої tracks і map
intersection трьох осей. Відкрийте вікно AirDroper **Details** і дивіться поле
**Approx. jammer/spoofer axis**:

- `COLLECTING` — ще немає 20 придатних RF/yaw samples;
- `ABSTAIN - turn geometry` — літак повернув недостатньо;
- `ABSTAIN - no directional lobe` — пелюстка не перевершила noise і range trend;
- `ABSTAIN - RF metrics disagree` — RF observables показують несумісні напрямки;
- `LIVE PROVISIONAL / UNVALIDATED AXIS b / b+180°` — прийнятий fit відкритого
  сегмента, який може рухатися з надходженням нових samples.

Коли axis прийнята, Mission Planner малює двосторонню фіолетову пунктирну лінію
через фіксоване середнє позицій, що супроводжували fit. Старий пеленг не
переноситься у поточну позицію літака. Лінія довільно має 3 км у кожен бік і
**не** означає, що джерело стоїть на endpoint. Виконайте розворот щонайменше
на 90°; повне коло значно краще. Live fitter використовує fixed segments до
120 секунд і починає спочатку після telemetry gap понад 10 секунд.

### Попередній перетин трьох осей

Для live фіолетової осі достатньо normal FC link, але map intersection також
потребує secondary USB-C H743. Anchor може бути тільки рухома wind-blind
DR reference. Червона receiver-reported позиція керована атакувальником і
ніколи не використовується.

1. В одній зоні спостереження повільно повертайте щонайменше 20 секунд і
   зберіть мінімум 40 RF/yaw samples. Натисніть **Capture qualified axis**,
   коли кнопка стане активною.
2. Повторіть ще у двох зонах так, щоб **кожна пара** anchors була рознесена
   щонайменше на 500 м, а кожна пара axis directions відрізнялася мінімум на
   30°. Три осі треба фіналізувати за 180 секунд; остання stale через 30 секунд.
   Потрібен великий кут перетину.
3. Дивіться **Provisional RF intersection**. До трьох осей воно показує
   `ABSTAIN - third independent finalized axis required`; для кожного іншого
   gate також є явна причина відмови.
4. Прийнятий результат показує фіолетову мішень і пунктирне коло
   **geometry sensitivity**. **Center RF intersection** центрує карту, а
   **Reset RF axes** очищає осі перед іншим джерелом або подією.

Location gates навмисно строгіші за live-axis gates: кожний segment повинен мати
мінімум 40 samples за 20–120 секунд, sigma не гірше 15°, `F >= 8`, geometry
`>= 1e-3`, дві узгоджені RF metrics, стабільний пеленг, щонайменше 90% покриття
рухомою DR reference та обмежену yaw-age sensitivity. Набір потребує однакових
private-USB session, DR event і metric, трьох pairwise-separated anchors і
directions, доброї crossing geometry, обмеженого range й узгодження кожної
збереженої осі. При stale або
провалі будь-якого gate мішень одразу зникає.

Local intersection solver обмежений діапазоном 70°S–70°N і поза ним показує
`ABSTAIN`; так projection distortion залишається всередині показаного
sensitivity bound.

Напис **UNVALIDATED INTERFERENCE-AXIS INTERSECTION — ADVISORY ONLY** означає
саме це. Результат припускає одне нерухоме джерело; RF-осі не відкалібровані,
DR anchors можуть дрейфувати, а пунктирне коло показує чутливість відомої
геометрії, не confidence чи accuracy. Це не ground truth, waypoint або
navigation/targeting input; у FC нічого не передається.

### Post-flight аналіз

1. Пролетіть **повне коло** крізь зону завад. Прямий проліт не годиться:
   підгонці потрібен розкид за курсом, без нього інструмент утримається від
   відповіді.
2. Заберіть `.bin` лог з польотного контролера.
3. Виконайте `python tools/df_analyze.py flight.bin`.

Plugin та інструмент незалежно підганяють кожну метрику й не показують вісь,
коли придатні metrics не узгоджуються. Два обмеження варто зрозуміти, перш ніж
діяти за числом:

- **Вважайте результат ВІССЮ, а не напрямком, доки не звірите його з відомим
  джерелом.** Припущення про полярність AGC не перевірене; якщо воно
  зворотне — пеленг розвернуто на 180° при тій самій якості підгонки, і ніщо у
  виводі цього не викаже.
- **Один пеленг — це напрямок, а не позиція.** Хоча дві математичні лінії
  завжди перетинаються, live plugin вимагає три незалежні осі, щоб несумісний
  segment не перетворився на правдоподібну позицію.

Інструмент застосовує не лише шумовий, а й геометричний фільтр, і радше
утримається, ніж вгадає — утримання є правильною відповіддю на політ, у якому
було замало розвороту.

## Вихід події DR1

- Пін: `B5`.
- Поведінка: високий рівень 3 секунди при кожному переході DR0 -> DR1, потім низький.
- Призначення: зовнішній логер/маяк/індикатор.

## Watchdog відновлення GNSS

Фільтр автоматично намагається відновити зупинений GNSS-приймач, якщо валідний фікс не отримано.

- Через **15 с** без фіксу: надсилається гарячий перезапуск.
- Через **45 с** без фіксу: надсилається холодний/заводський перезапуск.
- Кожні **120 с** після холодного перезапуску, якщо фікс досі відсутній: повторна спроба холодного перезапуску.
- Всі таймери скидаються одразу після отримання валідного фіксу.

**u-blox**: гарячий старт — UBX `CFG-RST` з `navBbrMask=0x0000`; холодний — `navBbrMask=0xFFFF`.

**UM980/981/982**: гарячий старт надсилає `RESET\r\n` на GNSS UART; холодний/заводський — `FRESET\r\n`.
Після `FRESET` STM32 чекає завершення boot приймача і повторно знаходить активну швидкість GNSS.

**Mosaic X5 / пасивний NMEA**: STM32 не надсилає команд reset до приймача. Якщо no-fix триває, прошивка лише повторює сканування baud для пасивного NMEA. Reset або переконфігурацію Mosaic робіть через Septentrio RxTools/Web UI.

Повідомлення про відновлення логуються в GCS (`INFO` для гарячого, `WARNING` для холодного та повторів).

## Операційні перевірки

- Якщо FC постійно показує `No Fix`, перевірте, чи AUX-логіка RC не примусово вимикає GPS на FC.
- На H743 DroneCAN також перевірте screen `WHY` row, `PUB` state, CAN counters
  і DroneCAN node status.
- Якщо карта показує стрибки під час спуфінгу, орієнтуйтесь на стан DR і логи фільтра, а не на картографічну трасу.
