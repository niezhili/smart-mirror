# Smart Mirror — Demo Dashboard

A standalone, interactive demo page that showcases **all Smart Mirror modules** — no hardware required. Open `index.html` in any modern browser.

## Modules Showcased

### Frontend (MagicMirror²)
| Module | Position | Status |
|--------|----------|--------|
| MMM-CustomClock | top_center | ✅ Live digital clock |
| MMM-CustomWeather | top_left | ✅ Simulated weather |
| MMM-NewsScroller | top_right | ✅ Rotating headlines |
| MMM-quotes | lower_third | ✅ Rotating quotes |
| MMM-DHT11 | bottom_left | ✅ Simulated sensor |
| MMM-MonthlyCalendar | bottom_center | ✅ Live calendar |
| MMM-LanguageSwitch | bottom_right | ✅ Toggle zh↔en |
| MMM-BackgroundImage | fullscreen_below | ✅ Animated particles |

### Backend (Python Services)
Voice Activity Detection, Speech Recognition (Paraformer), LLM (Qwen), TTS (Huoshan), Face Recognition, Human Detection, Gaze Estimation, IoT Control, Weather Service, Home Control

## Keyboard Shortcuts
- **L** — Toggle language (中文 / English)
- **N** — Advance news headline
- **Q** — Rotate quote
- **V** — Simulate voice interaction
- **Esc** — Close system panel
- **⚙** (top-right) — Toggle system module list

## How to present
1. Open `index.html` in full-screen (F11)
2. Let the clock tick, news scroll, and quotes rotate automatically
3. Press `V` to demo the voice assistant workflow
4. Press `L` to show bilingual support
5. Click **⚙** to show the full system architecture
