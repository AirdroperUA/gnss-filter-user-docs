# Лабораторна валідація антиспуф-захисту (тільки оборонний підхід)

> Де купити плату: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

Цей документ присвячений лише оборонній перевірці стійкості до GNSS-спуфінгу.

## 1) Межі та призначення

- Мета: підтвердити, що STM32-фільтр захищає навігацію FC, коли GNSS-дані стають підозрілими.
- Дозволене застосування: тільки законні, авторизовані та ізольовані лабораторні умови.
- Не включено: інструкції, що підвищують можливість атаки (налаштування пристроїв, методи передачі, покроковий спуфінг приймача).

## 2) Відео-референс

- Відео: https://www.youtube.com/watch?v=EFvWup8oCCE
- Сприймайте відео як демонстрацію оборонного процесу валідації.
- Використовуйте його разом із чеклістом цього документа та збереженими логами.

## 3) Цілі оборонної валідації

1. Підтвердити нормальну роботу в DR0 при здоровому GNSS.
2. Підтвердити перехід у DR1 при появі спуф-подібних аномалій.
3. Підтвердити блокування пересилання GNSS під час DR1.
4. Підтвердити контрольоване повернення в DR0 лише після виконання умов rejoin.
5. Підтвердити відсутність коливань DR0/DR1 на стабільних вхідних даних.

Для WeAct H743 DroneCAN "блокування пересилання GNSS" означає, що DroneCAN
`Fix2/Auxiliary` перестають публікуватися, а `NodeStatus` лишається online.
Warning health означає spoof/fault DR1 reason або enabled I2C sensor, який
missing/stale після startup grace. Перевіряйте onboard screen і DroneCAN/SLCAN
tooling разом із логами польотного контролера. Повний H743 setup:
[H743 DroneCAN Guide](13_h743_dronecan.md).

## 4) Рекомендоване лабораторне середовище

- RF-ізольована зона тестування під контролем кваліфікованих спеціалістів.
- Жодних випромінювальних тестів поруч із реальними бортами, аеродромами або публічними операціями.
- Якщо у вашій авторизованій RF-лабораторії використовується окрема SDR-платформа, поширений набір обладнання: **HackRF One + PortaPack H2**.
- Повне логування:
  - статусні повідомлення фільтра,
  - повідомлення FC,
  - таймлайн умов тесту для кожного прогону.

Примітка: цей документ не містить інструкцій з налаштування або використання HackRF/PortaPack.

## 5) Сценарії тестів (релевантні до спуфінгу)

Використовуйте контрольовані, дозволені джерела аномалій та перевіряйте очікувану реакцію фільтра:

1. **Великий стрибок позиції**
   - Очікування з `FCGPS_FWD=0`: вхід у DR1, блокування пересилання GNSS.
   - Очікування на H743 DroneCAN: `PUB BLK DR1`, немає нових
     `Fix2/Auxiliary`, node лишається online.
2. **Нереалістична обчислена швидкість**
   - Очікування: вхід у DR1 і утримання захисного стану.
3. **Аномалії по висоті**
   - Очікування: вхід у DR1 при провалі висотних перевірок узгодженості.
4. **SNR-аномалії (якщо увімкнено у вашому профілі)**
   - Очікування: вхід у DR1 після відпрацювання hold-таймера.
5. **Сценарій відновлення**
   - Очікування: повернення в DR0 тільки після виконання умов якості/часу.

## 6) Що перевіряти в логах

- Зміни стану DR (`DR=0` -> `DR=1` -> `DR=0`).
- Тренд GNSS до/під час аномалій (`age`, `SATS`, `SNR`, стан DR).
- Наявність повідомлень про причину входу в DR1.
- Повідомлення про rejoin під час повернення в DR0.
- Відсутність небезпечних навігаційних стрибків FC під час DR1.

H743 DroneCAN `v0.2.0+` надсилає MAVLink `STATUSTEXT` і `NAMED_VALUE` через
S2/index `1`, якщо цей virtual port налаштовано. Перевіряйте ці записи разом з
екраном, node ID `42`, `NodeStatus` і GPS `Fix2/Auxiliary`. Camera S1/index `0`
та filter S2/index `1` мають лишатися активними в DR1, коли `Fix2/Auxiliary`
заблоковано.

## 7) Типові збої валідації

- **DR1 не вмикається під час аномалії**
  - Пороги захисту занадто м'які або аномалія недостатня для поточного профілю.
- **DR1 вмикається надто часто**
  - Профіль занадто суворий, стартова нестабільність або слабка базова якість GNSS.
- **Немає стабільного повернення в DR0**
  - Не виконуються умови rejoin по якості/часу.
- **Нестабільні результати між прогонами**
  - Слабкий контроль стенду, неповні логи або різні умови тесту.

## 8) Критерії проходження перед польотами

Усі пункти мають бути виконані:

1. DR1 стабільно спрацьовує на спуф-подібних аномаліях у повторних прогонах.
2. Під час DR1 пересилання GNSS залишається заблокованим з `FCGPS_FWD=0`.
   Для H743 DroneCAN замініть цей пункт на: DroneCAN `Fix2/Auxiliary`
   лишаються suppressed у DR1, а `NodeStatus` лишається online.
3. Повернення в DR0 стабільне та відтворюване.
4. Поведінка FC залишається контрольованою (без небезпечних навігаційних стрибків).
5. Логи та записи умов тесту повністю збережені для рев'ю.

## 9) Докази кваліфікації релізу

Модульні тести та успішне складання прошивки необхідні, але не кваліфікують
збірку для польоту. Для кожного кандидата створіть окремий запис доказів і не
просувайте його у виробничий каталог, доки не пройдено всі застосовні пункти.

Зафіксуйте SHA-256 прошивки, семантичну версію, назву збірки, ревізію плати,
приймач і його прошивку, польотний контролер і його прошивку, активні датчики,
дату, оператора, експорт конфігурації та посилання на сирі логи фільтра,
приймача, CAN і FC. Після будь-якої зміни коду або конфігурації потрібен повний
повторний прогін; результати попереднього кандидата не переносяться.

Обов'язкове покриття hardware-in-the-loop:

- Normal-flight envelope для точного артефакту: прошийте саме той binary,
  SHA-256 якого записано у evidence package. Перевірте takeoff і перші 60 с
  набору; тривалий набір, зниження та dive на максимальній штатній швидкості;
  агресивні turns, steep bank і course-reversal geometry; straight cruise у
  контрольованих/безпечно змодельованих випадках вітру щонайменше 15 м/с і
  30 м/с. Додайте короткі multipath, fix, SNR та EKF glitches. У clean-flight
  envelope не повинно бути unintended DR1, а після навмисного DR1 має пройти
  очікувана послідовність rejoin.
- Реальний трафік приймачів: u-blox NAV-PVT/NAV-SAT, deployed profile
  Unicore/UM980 GGA/RMC/AGRICA і Septentrio Mosaic SBF. STM32 має розбирати
  GGA/RMC, пересилати, але не розбирати AGRICA, і показувати `SNR=NA` без
  optional GSV. GSV перевірте як окремий optional-evidence case; його
  відсутність не повинна блокувати recovery. Пошкоджені, обрізані, затримані та
  перемішані кадри мають переривати безперервність detector-а, а не
  задовольняти hold-таймер.
- H743 parked recovery: з підтверджено disarmed і нерухомим FC доведіть, що
  passive receiver може release без GSV, коли всі доступні evidence rows не
  FAIL, GNSS time PASS, а fresh finite nonnegative receiver speed не більша за
  4 м/с у тому самому location epoch (age і skew не більше 1500 мс). Stale або
  mismatched speed, швидкість понад 4 м/с чи будь-який явний FAIL мають
  заборонити release. Окремо пройдіть незмінений airborne witness quorum і
  розрізніть `EVM`, `EVF` та `EVPg`.
- FC-version і dual-link gates: почніть без `AUTOPILOT_VERSION`, потім дайте
  ArduPilot старіший за 4.6.1, потім підтримувану версію. Unknown і old version
  мають негайно suppress `Fix2/Auxiliary`; перевірте explicit capability
  request, 15-секундну затримку warnings/hard processing та документовані
  повідомлення. У Mission Planner 1.3.83 завантажте та перепідключіть secondary
  H743 USB з deasserted DTR. Під normal і `SP_*` load доведіть, що USB/COMM2 та
  FC/S2/COMM0 мають окремі безперервні MAVLink sequence.
- Утримання координат: перевірте `LOG_LOC=0` і `1`. Raw coordinates можуть
  з'являтися лише у true-DR0 periodic status з `LOG_LOC=1`; trip/transition text
  і всі DR1, synthetic або blend status лишаються redacted. Переконайтеся, що
  `SP_*` є лише у direct USB, а одночасний raw CAN не містить у DR1 `Fix2`,
  `Auxiliary`, `SP_*` чи filter status з координатами.
- Fuel provenance і degraded operation: перевірте valid V2 records із warm та
  POR/PDR reset flags, legacy V1, corrupt/missing records з усіма reset flags і
  repeated resets. Кожен invalid або missing record має дати TOTAL LOST;
  shortcut cold-boot/fresh-tank немає. Звичайне вмикання без valid retained
  record має припинити кожен ICE Status packet, доки fresh stopped-engine quorum
  (disarmed + valid zero RPM + closed throttle) не дозволить оператору повторно
  записати `FUEL_CAPG`, навіть якщо його числове значення не змінилося; EFI
  backend FC тим часом має стати stale/unhealthy. Доведіть, що disarmed alone,
  stale/missing RPM, nonzero RPM, stale/missing throttle і open throttle кожен
  відхиляє reset та видає `FUEL_CAPG blocked: engine not confirmed stopped`.
  Повторіть quorum matrix для `FUEL_DENS` і вимагайте
  `FUEL_DENS blocked: engine not confirmed stopped` для кожного відхиленого
  запису.
  Кожен boot має встановити engine-may-be-running latch, а
  очистити його можуть лише ті самі fresh three-way evidence; сам parameter
  write не можна використовувати як stop evidence. Valid restore має
  додати точно фіксоване 25-секундне reset-gap нарахування за номінальною
  потужністю, що покриває до 2 с застарілості save, найдовший шлях налаштування
  UM980 приблизно 11.5 с, інший startup overhead і запас; у H743 немає Phase-C
  boot wait. Вважайте це обмеженим консервативним нарахуванням, а не доказом
  точної витрати, і
  перевірте, що elapsed setup time після ранньої backup initialization
  нараховується, а не відкидається. Після restore known V2 перевірте retained
  storage і доведіть, що до risky setup firmware надійно записує той самий
  numeric state із provenance TOTAL_LOST. Викличте resets під час setup, першого
  update і magic-last known commit: кожен interrupted path має завантажитися як
  LOST або invalid, suppress усі EFI packets і вимагати stopped-quorum
  `FUEL_CAPG`. Дайте одному first update завершитися й доведіть, що 25-секундне
  нарахування та перший measured interval обидва інтегровані до commit
  оновленого known record; лише пізніший reset може відновити цей charged known
  record. Окремо відновіть valid record, виконайте прийнятий reset `FUEL_CAPG`
  до першого fuel update і доведіть, що pending 25-секундне нарахування
  скасовано та не може потрапити в щойно встановлений total. Змініть числове
  значення `FUEL_CAPG` і доведіть, що TOTAL LOST записано до runtime assignment,
  усі ICE Status suppressed навіть після accepted-write text, а zero total стає
  known лише після успішного asynchronous completion journal. Інжектуйте
  failures start/program/verify/timeout journal: кожен path із `Tune save failed`
  має лишатися LOST, а лише наступний успішний `Tune saved` може відновити EFI.
  За наявності valid V2 backup record окремо зітріть, пошкодьте й залиште H743
  tune journal без жодного valid record; кожен випадок має анулювати surviving
  numeric total, бо provenance місткості, густини та моделі unavailable.
  Запустіть factory reset із failure до початку flash і під час flash та
  доведіть, що durable LOST marker передує першій можливій flash operation і
  може консервативно лишитися після failed attempt.
  Змініть `FUEL_DENS` за valid stopped-engine quorum і доведіть, що LOST marker
  передує runtime assignment, будь-який старий CAPG commit intent скасовано, а
  EFI packets не з'являються. До завершення persistence density кожна спроба
  місткості має відхилятися з `FUEL_CAPG blocked: wait for FUEL_DENS save`.
  Інжектуйте failure save density і доведіть, що block та TOTAL LOST лишаються;
  після verified `Tune saved` pending-density latch має очиститися, але EFI —
  лишитися silent. Лише **наступний** stopped-quorum запис `FUEL_CAPG` може
  встановити fresh zero за нової густини. Успішний save лише густини не повинен
  відновлювати EFI або дозволяти cumulative FC-visible volume рухатися назад.
  Також доведіть, що
  fuel burn триває крізь повну втрату FC-telemetry і FC-version block,
  нараховуючи rated power без RPM.
- Fuel safety Phase-C: **ніколи не виконуйте Phase-C maintenance при працюючому
  двигуні**. Імітуйте running inputs на безпечному стенді й доведіть, що
  підключена maintenance session може перевищити фіксований 25-секундний budget;
  її не можна представляти як повністю враховану витрату палива.
- Operator labels: викличте reason 15 і перевірте, що Mission Planner показує
  `PARKED_MOVE`/`PARKED MOVE`, а екран плати — `PARKED`.
- Межі навігації: неможлива висота, зниження 2D-fix без довіреної висоти,
  перезапуск сесії з позицією без status, повна дата UTC та її перехід, кешовані
  UTC-кадри, короткі SNR-імпульси, чистий SNR без fix і пропущені/пошкоджені
  SEC-SIG опитування.
- Збої DroneCAN/FDCAN: відсутність ACK, bus-off, домінантна шина, повторне
  підключення кабелю, помилка stop/start периферії, заповнена шина, tunnel-трафік
  і конфлікт node ID. Вузол має відновитися або безпечно заблокувати публікацію
  з видимою помилкою; підозрілі fix не повинні публікуватися мовчки.
- Збої датчиків: затиснуті SDA/SCL, відсутні зовнішні pull-up, відключення та
  підключення під час роботи, ідентифікація підтримуваних/чужих пристроїв,
  полярність тиску MS4525 і орієнтація магнітометра відносно фізичного еталона.
- Збої живлення та reset: доведіть runtime-дедлайн watchdog, примусово пройдіть
  timeout/error гілки flash-busy і вимкніть живлення на кожній фазі запису
  tune-журналу. Наступний boot має вибрати повний CRC-valid запис або defaults.
- Захищене оновлення: перевірте реальне RDP1 обладнання через ST-Link і ROM DFU.
  Помилка мережі, підпису, target, версії, UID чи валідації bundle має статися до
  erase. Після успішного захищеного оновлення повторно перевірте параметри та
  виконайте commissioning, бо mass erase знищує збережене налаштування.
- Secure boot: відхиліть змінений app, metadata, rollback, неправильний target і
  app, скопійований на інший MCU UID. Переконайтеся, що прямий PlatformIO upload
  phase-B payload заборонено, а provisioning встановлює bootloader, UID-bound
  app і відповідну signed metadata як один перевірений комплект.
- Remote operator waiver: released targets мають компілюватися з
  `FILTER_REMOTE_OPERATOR_WAIVER_ENABLE=0`. Надішліть forged і replayed
  `MAV_CMD_USER_1` waiver commands та перевірте, що вони не змінюють recovery
  state і не обходять independent-evidence quorum. Lab-only opt-in build має
  вважати command і його public magic value неавтентифікованими та може
  вмикати їх лише за окремим authenticated transport.

Архівуйте підписаний чекліст разом з артефактами релізу. Невиконаний пункт є
явним блокером релізу, а не припущеним проходженням.
