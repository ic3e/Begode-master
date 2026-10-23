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
| `build22.py` + `check22.py`, `export22.py` | lamp v6: sealed; fixed LEDs behind a bulkhead, tilting lens frame, drained air duct; flood-fill seal test |
| `build23.py` + `check23.py`, `export23.py`, `mech6_export.py` | lamp v6.1: v6 with fewer parts (no road sensor, clamp, diffusers or gasket) |
| `build24.py` + `check24.py`, `export24.py`, `print_check.py` | lamp v6.2 + handle v14: v6.1 made ready for the slicer; `print_check.py` checks the STLs as a slicer sees them |
| `build25.py` | handle v15 / v16: the USB-C port flush in the leg instead of a socket in a boss (v15, outer face), then on the leg's inside (v16) |
| `build26.py` + `check25.py`, `export25.py` | lamp v6.2 + handle v17: the lamp tabs braced with gussets and fillets, the USB wire inside their root |
| `build27.py` + `check27.py`, `export27.py` | lamp v6.3 + handle v17: wire slots from the side bays into the electronics box |
| **`build28.py` + `check28.py`, `export28.py`** | **lamp v6.4 + handle v18 (current): the road sensor's hood behind the face; the riding buttons on the handle's leg** |
| **`stills64_export.py`, `anim/stills64.html`** | **the v6.4 stills (`current/renders/render_v64_*`): face, road sensor, riding buttons, night** |
| `proj_export.py`, `anim/proj.html` | concept renders of a projector cut-off bench rig (`current/renders/concept_projector_*`): `PAGE=proj.html OUTD=proj node stills_render.mjs` |
| **`boards_pack.py`, `boards_export.py`, `anim/boards.html`** | **the boards (and, from v6.4, the road sensor) fitted at their real sizes, and their render (`current/renders/boards_*`): `PAGE=boards.html OUTD=boards node stills_render.mjs`** |
| **`wiring_diagram.py`** | **the wiring diagram (`current/renders/wiring_diagram.png`)** |
| **`swing_export.py`, `anim/swing.html`, `anim/level.html`** | **how far the lenses tilt (`tilt_*`) and the beam held level on the wheel (`level_*`): `PAGE=swing.html OUTD=swing` / `PAGE=level.html OUTD=level node stills_render.mjs`** |
| **`pov_export.py`, `anim/pov.html`** | **the rider's view at night, levelled lamp vs a fixed one (`rider_pov.*`): `PAGE=pov.html OUTD=pov node stills_render.mjs`, then ffmpeg at 30 fps** |
| `render*.py`, `master_render*.py`, `lamp_render.py` | matplotlib renders of earlier versions |
| `meas_sheet.py`, `meas_sheet2.py` | the measurement sheets |
| `anim_export.py`, `anim/index.html`, `anim/render.mjs` | the v8 animation |
| `stills_export.py`, `anim/stills.html` | the v5.1 stills (`archive/renders/`) |
| **`stills6_export.py`, `render_wheel.py`, `anim/stills6.html`, `anim/stills_render.mjs`** | **the v6.2 stills (`current/renders/render_v62_*`); the wheel dressed from the owner's 360 photos** |
| **`mech6_export.py`, `anim/mech6.html`** | **how it's built and how the air goes through (`render_v62_1..5`)** |
| **`printbed_export.py`, `anim/printbed.html`** | **the print preview: each STL on the bed with its supports (`current/renders/print_*`): `PAGE=printbed.html OUTD=printbed node stills_render.mjs`** |
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

## Stills (lamp v6.2)

```
python3 stills6_export.py              # writes anim/stills6_data.js (meshes + six camera views)
cd anim && python3 -m http.server 8766 --bind 127.0.0.1 &
PAGE=stills6.html OUTD=stills6 W=2400 H=1350 node stills_render.mjs   # anim/stills6/f0000.png …
```

The wheel in these is `render_wheel.py`: the measured outline (shells, cover, tyre at rest) dressed with what
the owner's 360 turntable GIF shows: faceted side pads, the silver suspension rail over the axle, the rear
battery pack, a knobby tyre, spoked rim, spiked pedals, fender, red rear linkage and tail light. It is for
pictures only; the checks still use the measured model. The fallen views put the wheel's lowest point on the
ground, and the red marker is the gap between the lamp and the ground, measured in the same scene.
The v5.1 stills (`stills_export.py`) are kept for the record.
