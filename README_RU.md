![kivok banner](banner.png)

# 🎥 kivok.py — управление клавиатурой через кивки головой
![Kivok](https://img.shields.io/badge/Kivok-Менеджер%20сетевых%20блокировок-660000?style=for-the-badge&labelColor=330000)

[🇬🇧 English](README.md)

**kivok.py** — это скрипт на Python, который отслеживает движения головы через веб-камеру и преобразует резкие кивки в нажатия клавиш.  
Подходит для экспериментов с hands-free интерфейсами, accessibility-решений и просто как прикольный хак.

![kivok banner](./assets/kivok_demo.png)

---

## ⚡ Возможности
- Отслеживание лица в реальном времени с помощью OpenCV.  
- Активация трекинга при «моргании» (коротком исчезновении лица с камеры).  
- Распознавание резких кивков вверх/вниз.  
- Эмуляция нажатий клавиш (по умолчанию: стрелки `↑` и `↓`).  
- Звуковой сигнал при активации.  
- Отладочный режим с визуализацией (рамка вокруг лица, статус трекинга).  

---

## 🔧 Зависимости
- Python 3.10+  
- [OpenCV](https://pypi.org/project/opencv-python/)  
- [NumPy](https://numpy.org/)  

Системные утилиты для эмуляции клавиш:  
- **Wayland** → [`wtype`](https://github.com/atx/wtype)  
- **X11** → [`xdotool`](https://www.semicomplete.com/projects/xdotool/)  

Для звука: `paplay` (часть PulseAudio).  

---

## 🚀 Установка
```bash
# Установка зависимостей
pip install --user opencv-python numpy

# Для Wayland
sudo apt install wtype

# Для X11
sudo apt install xdotool

# Для звука
sudo apt install pulseaudio-utils
````

---

## ▶️ Запуск

```bash
python3 kivok.py
```

Клавиша `q` в окне камеры — завершение работы.

---

## ⚙️ Конфигурация

В начале файла можно настроить параметры:

* `BLINK_DURATION` — время «моргания» для активации.
* `MOVEMENT_THRESHOLD` — чувствительность кивка (в пикселях).
* `COOLDOWN_DURATION` — минимальная задержка между действиями.
* `SOUND_FILE` — путь к звуковому файлу при активации.
* `DEBUG_VISUALS` — включить/выключить визуализацию.

---

## 🧩 Ограничения

* Используется Haar Cascade (устаревший детектор лиц, чувствителен к освещению). Для более точного трекинга рекомендуется [Mediapipe](https://developers.google.com/mediapipe).
* Работает только с одной камерой (по умолчанию `/dev/video0`).
* Нужны внешние утилиты (`wtype` или `xdotool`).

---

## 📌 Пример использования

* Hands-free навигация по PDF или браузеру (стрелки вверх/вниз).
* Управление презентацией.
* Тестирование accessibility-интерфейсов.
