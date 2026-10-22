# Source scripts

Each `buildN.py` builds one design step on top of the previous one (they `exec` each other). Run
everything from this folder; the original handle and cap are read from `../reference/`, and outputs go to
`../build_output/`.

| Script | What it is |
|---|---|
| `build.py`, `build2.py` | handle v1 (side-folding cup) and v2 (corner hinges) |
| `build3.py`, `build5.py`, `build7.py` | folding cup holders v3–v5 |
| `build4.py`, `build6.py`, `build8.py` | handles v3–v5 with a holder for the stock lamp |
| `build9.py` | headlamp v1: servo-levelled head, servo and electronics blocks |
| `build10.py` | headlamp v2: road sensor, daytime running lights, light sensor |
| `build11.py` | headlamp v3: lamp and cup holder unit, handle v6 |
| `build12.py` | minimal fold-under cup ring, handle v7 |
| `build13.py` + `check13.py`, `export13.py` | slide-out self-levelling cup holder, handle v8 |
| `build14.py` + `check14.py`, `export14.py` | two-axis gimbal cup holder, handle v9 |
| `master_model.py` | rough Master traced from photos (used up to v9; its front end is wrong) |
| `master_model2.py` | the wheel's front rebuilt from the caliper measurements (`../reference/MEASUREMENTS.md`) |
| `build15.py` + `check15.py`, `export15.py` | v10: lamp in front of the cover, swing-up can holder |
| **`build16.py` + `check16.py`, `export16.py`** | **v11 (current): lamp in the stock opening, tray, handle v11** |
| `render*.py`, `master_render*.py`, `lamp_render.py` | matplotlib renders of each version (`render_v8.py` is current) |
| `meas_sheet.py`, `meas_sheet2.py` | the measurement sheets |
| `anim_export.py`, `anim/` | the animation |
| others | small helpers used while tracing the handle STL (`holes.py`, `slices.py`, `stlinfo.py`, …) |

## Animation

```
python3 anim_export.py                 # writes anim/data.js (meshes + 780 frames of positions)
cd anim && npm install
python3 -m http.server 8765 --bind 127.0.0.1 &
node render.mjs 0 780                  # frames/f0000.png …
ffmpeg -framerate 30 -i frames/f%04d.png -c:v libx264 -crf 17 -pix_fmt yuv420p animation.mp4
```

Every position in the animation comes from the same functions the checks use, so the motion is the
checked motion. `render.mjs` uses headless Chromium (Playwright). No GPU is needed: it falls back to
software WebGL.
