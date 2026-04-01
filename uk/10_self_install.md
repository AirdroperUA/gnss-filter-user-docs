# Самостійна установка

> Де купити плату: [GPS Spoofing Filter](https://airdroper.org/product/gps-spoofing-filter/)

Цей посібник описує прошивку прошивки GNSS-фільтра на чисту плату
STM32F401CC BlackPill за допомогою ліцензійного ключа, придбаного в магазині.

Кожний ліцензійний ключ активує **одну плату**. Прошивка криптографічно
прив'язана до апаратного ID вашої конкретної плати і не може бути скопійована на іншу.

---

## Що потрібно

| Елемент | Примітки |
|---------|----------|
| STM32F401CC BlackPill V2.0 плата | WeAct Studio або аналог |
| ST-Link V2 програматор | Оригінальний або клон, ~$3 |
| 4 з'єднувальні дроти | 3V3, GND, SWDIO, SWCLK |
| ПК з Windows та інтернетом | |
| Ліцензійний ключ | З вашої покупки (напр. `GF-XXXX-XXXX-XXXX`) |

### Програмне забезпечення

1. **STM32CubeProgrammer** (безкоштовно) — завантажте з
   [st.com](https://www.st.com/en/development-tools/stm32cubeprog.html)
   та встановіть. Інструменту провізіонування потрібен `STM32_Programmer_CLI` у вашому PATH.

2. **Інструмент провізіонування** — завантажте `gnss-provision.exe` зі сторінки завантажень магазину.
   Або якщо у вас є Python 3.8+:
   ```
   pip install requests pyserial pynacl
   ```
   Потім використовуйте `tools/gnss_provision.py` з репозиторію прошивки.

---

## Як працює провізіонування

```
  ┌──────────┐      ST-Link       ┌──────────────┐      Internet     ┌──────────────┐
  │ Your PC  │ ◄────(SWD)────────►│  BlackPill   │                   │   License    │
  │          │                    │  STM32F401   │                   │   Server     │
  │ gnss-    │                    │              │                   │              │
  │ provision│ ──── read UID ───► │  (blank)     │                   │              │
  │  .exe    │                    │              │                   │              │
  │          │ ── license + UID ──────────────────────────────────►  │  validates   │
  │          │                    │              │                   │  generates   │
  │          │ ◄── bootloader + firmware + metadata ──────────────── │  per-board   │
  │          │                    │              │                   │  firmware    │
  │          │ ──── flash ──────► │  (running!)  │                   │              │
  │          │ ──── set RDP1 ───► │  (locked)    │                   │              │
  └──────────┘                    └──────────────┘                   └──────────────┘
```

Кожна плата отримує унікальний ключ шифрування. Прошивка криптографічно
прив'язана до апаратного ID вашої плати і не може бути перенесена на іншу плату.

---

## Крок 1 — Підключення ST-Link

Підключіть ST-Link до SWD-роз'єму BlackPill:

| Пін ST-Link | Пін BlackPill |
|-------------|---------------|
| 3V3 | 3V3 |
| GND | GND |
| SWDIO | DIO (PA13) |
| SWCLK | CLK (PA14) |

Живлення BlackPill від ST-Link 3V3 (або USB, обидва варіанти працюють).

```
  ST-Link V2                   BlackPill
  ┌──────────┐                ┌──────────────┐
  │      3V3 ├────────────────┤ 3V3          │
  │      GND ├────────────────┤ GND          │
  │    SWDIO ├────────────────┤ DIO (PA13)   │
  │    SWCLK ├────────────────┤ CLK (PA14)   │
  └──────────┘                └──────────────┘
```

## Крок 2 — Активація та прошивка

Відкрийте термінал і виконайте:

```
gnss-provision activate --license GF-XXXX-XXXX-XXXX --server https://license.airdroper.org
```

Інструмент виконає наступне:
1. Підключиться до плати через ST-Link
2. Зчитає унікальний апаратний ID плати
3. Зв'яжеться з сервером ліцензій для генерації персоналізованої прошивки
4. Прошиє завантажувач, додаток і метадані
5. Увімкне захист від зчитування (RDP Level 1)

Ви маєте побачити приблизно таке:
```
Connecting to target via ST-Link...
Reading board UID...
Board UID: aabbccddeeff1122334455 (short: 12345678)
Contacting license server...
Firmware version: 1.4.3
  Bootloader: 32696 bytes
  Application: 73732 bytes
  Metadata: 148 bytes
Erasing flash...
Writing bootloader (0x08000000)...
Writing application (0x08008000)...
Writing metadata (0x0801FC00)...
Setting readout protection (RDP Level 1)...

Provisioning complete!
```

## Крок 3 — Перевірка

1. Від'єднайте ST-Link
2. Подайте живлення на плату через USB або бортову систему живлення
3. Підключіться до Mission Planner і перевірте повідомлення про старт фільтра
   у вкладці Messages (напр. `GNSS filter v1.4.3 UID=12345678`)

---

## Оновлення прошивки

Після початкової прошивки оновлення виконуються через протокол Phase-C UART
і **не** потребують ST-Link.

### Що потрібно для оновлення

| Елемент | Примітки |
|---------|----------|
| USB-UART адаптер | CP2102, CH340, або FTDI, ~$2 |
| 3 з'єднувальні дроти | TX, RX, GND |

### Підключення

| USB-UART адаптер | Пін BlackPill |
|------------------|---------------|
| TX | PA10 (USART1 RX) |
| RX | PA9 (USART1 TX) |
| GND | GND |

**Від'єднайте контролер польоту** від PA9/PA10 під час оновлення.
Це ті самі піни, що використовуються для MAVLink-телеметрії FC.

```
  USB-UART adapter             BlackPill
  ┌──────────┐                ┌──────────────┐
  │       TX ├────────────────┤ PA10 (RX)    │
  │       RX ├────────────────┤ PA9  (TX)    │
  │      GND ├────────────────┤ GND          │
  └──────────┘                └──────────────┘
     (disconnect FC from PA9/PA10 first)
```

### Процедура оновлення

1. Підключіть USB-UART адаптер як показано вище
2. Відкрийте термінал і виконайте:
   ```
   gnss-provision update --license GF-XXXX-XXXX-XXXX --uid <your-24-char-uid> --uart COM5 --server https://license.airdroper.org
   ```
   Замініть `COM5` на порт вашого адаптера. UID — це повний 24-символьний
   hex-рядок, показаний під час початкової активації.
3. Коли з'явиться запит, **натисніть кнопку reset** на BlackPill
4. Інструмент прошиє нову прошивку через UART (~30-60 секунд)
5. Плата автоматично перезавантажиться після завершення

---

## Усунення неполадок

| Проблема | Рішення |
|----------|---------|
| "STM32_Programmer_CLI not found" | Встановіть STM32CubeProgrammer і додайте його теку `bin` до PATH |
| "Failed to connect" | Перевірте підключення ST-Link (3V3, GND, SWDIO, SWCLK). Спробуйте інший USB-порт. |
| "Invalid license key" | Перевірте ключ з листа про покупку |
| "License already activated on a different board" | Кожний ключ працює лише на одній платі. Зверніться до підтримки для заміни. |
| "Timeout: no response from bootloader" (оновлення) | Натисніть кнопку reset на BlackPill, поки інструмент очікує |
| Попередження RDP Level 1 при повторній прошивці | Плата вже захищена. Mass erase відбудеться автоматично. |
