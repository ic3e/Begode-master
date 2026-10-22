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
| `build16.py` + `check16.py`, `export16.py` | v11: lamp in the stock opening, tray, can holder, handle v11 |
| `build17.py` + `check17.py`, `export17.py`, `render_v9.py` | lamp v5: three LEDs on one tilting bar, electronics box, handle v12 |
| `build18.py` + `check18.py`, `export18.py`, `stills_export.py` | lamp v5.1: window, angled running lights, chin vent and baffle, drop check |
| `build19.py` + `check19.py`, `export19.py` | lamp v5.2: open-top housing and top plate, so head and servo can be fitted |
| `build20.py` + `check20.py`, `export20.py` | lamp v5.3: 6800 ball bearing on the head's pin |
| `build21.py` + `check21.py`, `export21.py`, `mech_export.py` | lamp v5.4 + handle v13: head stops, chin buttons, USB-C port in the handle |
| **`build22.py` + `check22.py`, `export22.py`, `mech6_export.py`** | **lamp v6 (current): sealed; fixed LEDs behind a bulkhead, tilting lens frame, drained air duct. check22 includes a flood-fill seal test** |
| `render*.py`, `master_render*.py`, `lamp_render.py` | matplotlib renders of earlier versions |
| `meas_sheet.py`, `meas_sheet2.py` | the measurement sheets |
| `anim_export.py`, `anim/index.html`, `anim/render.mjs` | the v8 animation |
| `stills_export.py`, `anim/stills.html`, `anim/stills_render.mjs` | the v5.1 stills (`current/renders/`) |
| `mech_export.py`, `anim/mech.html` | the mechanism stills: `PAGE=mech.html OUTD=mech node stills_render.mjs` |
| others | small helpers used while tracing the handle STL (`holes.py`, `slices.py`, `stlinfo.py`, …) |

## Animation (v8, with the can holder)

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

## Stills (lamp v5.1)

```
python3 stills_export.py               # writes anim/stills_data.js (meshes + six camera views)
cd anim && python3 -m http.server 8766 --bind 127.0.0.1 &
node stills_render.mjs                 # anim/stills/f0000.png …   (env W, H, OUTD to change size / folder)
```

The fallen views use the drop check's own ground planes, and the red marker is the measured gap between the
lamp and the ground.
