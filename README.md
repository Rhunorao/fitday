# FitDay — Weekly Training Companion

A single-file training app for your iPhone home screen. It shows the right day automatically — workout, meals, and supplements for Monday through Sunday — with tap-to-check tracking that resets every Monday.

**Live app:** https://rhunorao.github.io/fitday/

---

## Make your own copy (5 minutes)

Want this app with **your own plan**? Fork it and it's yours:

1. **Create a free GitHub account** (github.com) if you don't have one.
2. Click **Fork** at the top of this repo. That gives you your own copy under your username.
3. In **your fork**, go to **Settings → Pages**, set *Source* to **Deploy from a branch**, pick branch **main** and folder **/ (root)**, and save.
4. After a minute your app is live at `https://YOUR-USERNAME.github.io/fitday/`.
5. Open that link in Safari on your iPhone → **Share → Add to Home Screen**. It installs like a real app (full screen, works offline).

### Clean out the Whoop integration (recommended)

This repo includes an optional Whoop sync that only works for the original owner's account. In your fork, delete these — the app works fine without them:

- `whoop.json`
- `.whoop_refresh.enc`
- `scripts/`
- `.github/`

(Without Whoop, the sleep/recovery/steps/burn rings simply stay empty — everything else works.)

### Put in your own schedule

All plan data lives in **`index.html`** in one place: the `DAYS` object (search for `const DAYS`). Each day has:

- `name`, `focus` (e.g. `"Push — Chest / Shoulders"`), `carb` (`HIGH` / `MEDIUM` / `LOW`), `hue` (the day's accent color)
- `kcal`, `p`, `c`, `f` — calorie and macro targets shown in the app
- `workout` — list of exercises: `{n: name, sr: "4 × 8-10", cue: "technique note", rest: "90s"}`
- `meals` — list of meals: `{n: name, t: "1–2 PM", main: "...", sub: "...", note: "...", m: "550 kcal · 54g protein"}`
- `supps` — supplement rows: `{g: "Morning", n: "Creatine 5g", s: "instructions"}`

Edit the file right on GitHub (open `index.html` → pencil icon → commit), and your app updates itself a minute later. You can also ask Claude to edit it for you — point it at your fork.

### Good to know

- Checkmarks are saved on the device and **clear every Monday** for a fresh week.
- The app auto-opens today's schedule; the top strip switches days.
- One HTML file, no build step, no dependencies, free hosting on GitHub Pages.
