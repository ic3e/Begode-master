# Lamp v5.1: three-LED self-levelling headlamp in the stock lamp opening

The stock lamp comes out, and this lamp sits flush in its opening in the top cover. There is no cup
holder any more.

- **The light:** three LEDs with optics in a row: one narrow optic for reach, two wide ones for spread.
- **Levelling:** all three sit on one finned heat-sink bar, which a servo tilts ±10° to hold the beam
  steady when the wheel pitches (braking, accelerating, bumps, hills). The road sensor, gyro, daytime
  running lights, day/night switching and phone settings page all work as before.
- **Brightness:** about **1200 lm** at the default 90 % setting, about 2.5× the single-LED v4.
- **Electronics:** they sit in a box that hangs down into the bay between the shells, with a lid underneath,
  so you can reach them without taking the lamp out.
- **Mounting:** the lamp is held by the cover's two stock M4 screws, and by two webs that run back to the
  handle's tabs.
- **Looks (v5.1):** a clear 1.5 mm polycarbonate window sits flush in the opening, 0.7 mm behind the cover's front
  edge, over a black face. The running lights are two angled light lines that follow the Master's faceted shape.
  The window keeps rain and grit off the optics.
- **Drops:** whichever way the wheel falls, the handle grip, the shells or the tyre hit the ground first. The
  lamp stays at least 20 mm clear (25 mm when it falls flat on its face).

![Lamp v5.1](renders/render_v51_closeup.png)

Everything is checked against the model of your wheel built from your caliper measurements
(`../reference/MEASUREMENTS.md`). Prices and shops: [`PARTS.md`](PARTS.md). Eesti keeles:
[`BUILD_GUIDE_et.md`](BUILD_GUIDE_et.md), [`PARTS_et.md`](PARTS_et.md).

## Bought parts

| Part | Qty | Notes |
|---|---|---|
| Luminus SST-20 (or Cree XM-L2 / XP-L), 3 V, on a **16 mm** copper star | 3 | 4000–5000 K |
| 20 mm TIR optic for a 16 mm star | 3 | 1 × 10° round (centre, reach), 2 × **elliptical** wide (sides: a flat, wide band of light) |
| Clear polycarbonate sheet, 1.5 mm | 1 | cut to `stl/lamp51_window_1.5mm_polycarbonate.svg` (133 × 35.8 mm, chamfered corners) |
| Thin double-sided foam tape, 0.5 mm, 3–5 mm wide | | holds the window on the lamp face and seals it |
| Finned aluminium heat-sink bar | 1 | flat face **64 × 25 mm**, no deeper than 20 mm, fins running front to back. Cut it from an extruded profile |
| Mean Well LDD-1500L | 3 | one per LED; works from the wheel's 6.5 V dim mode |
| ESP32-C3 SuperMini | 1 | |
| MPU-6050 (GY-521) | 1 | |
| VL53L1X module (13 × 18 mm) | 1 | road sensor |
| MG90S metal-gear servo | 1 | |
| MP1584EN buck module, set to 5.0 V | 1 | |
| Logic-level MOSFET module (D4184 / AO3400) | 1 | daytime running lights |
| 5 V white LED strip, 2835, 120/m | about 14 LEDs | daytime running lights |
| GL5528 LDR + 10 k; 10 k NTC (B3950) + 10 k; 47 k + 10 k | | light sensor, heat-sink temperature, wheel voltage |
| Plug that matches the wheel's lamp plug (stock: yellow JST-XH, 2 pin) | 1 | |
| 26 AWG silicone wire | | the 8 wires through the hollow pivot pin |

## Printed parts (PETG or ASA, 4 walls)

| File | Qty | How |
|---|---|---|
| `stl/master_handle_v12.stl` | 1 | your handle plus two webs at the back. On its side, supports under the grip |
| `stl/master_handle_top_cap_p2.stl` | 1 | your original cap |
| `stl/lamp51_housing.stl` | 1 | top face on the bed, as exported. Black ASA, "fuzzy skin" on in the slicer for the shells' grainy look |
| `stl/lamp51_head.stl` | 1 | open back on the bed, as exported |
| `stl/lamp51_lid.stl` | 1 | outside face on the bed |
| `stl/lamp51_drl_diffuser_left.stl`, `stl/lamp51_drl_diffuser_right.stl` | 1 each | white or clear PETG, 100 % infill (the angled light lines) |

## Hardware

- **Lamp to cover:** the stock lamp's 2 M4 screws, into 2 **M4 heat-set inserts** (5.7 mm long, 5.6 mm OD).
  Melt the inserts into the two bosses on the housing's top.
- **Lamp to handle:** 2 × M3 × 10 self-tapping, up through the handle's webs into the housing.
- **Lid:** 4 × M3 × 8 self-tapping.
- **Inside the lamp:**
  - 3 × M3 × 8 self-tapping (heat-sink fins)
  - 2 × M2 × 6 (servo horn to head)
  - 2 × M2 × 8 (servo to its posts)

## Wiring

```
wheel lamp plug + ──┬── LDD-1500L #1, #2, #3  VIN+
                    ├── MP1584 IN+
                    └── 47 k ── GPIO0 ── 10 k ── GND         (wheel voltage)
wheel lamp plug − ──── common ground
LDD #n  LED+ / LED− ── LED #n            (each LED on its own driver; don't join the LED− wires)
LDD DIM #1 + #2 + #3 ── GPIO5            (all three together)
MP1584 OUT 5.0 V ──┬── ESP32-C3 5V, servo red, MOSFET module DC+ (→ both DRL strips)
ESP32 3V3 ──┬── MPU-6050 VCC, VL53L1X VIN
            ├── 10 k ── GPIO3 ── NTC ── GND (NTC glued to the heat-sink bar)
            └── LDR ── GPIO1 ── 10 k ── GND
GPIO6 SDA / GPIO7 SCL ── MPU-6050 and VL53L1X      GPIO10 ── servo      GPIO4 ── MOSFET module
```

**Power:** the three LEDs at the default 90 % draw about 13 W. Add about 3 W for the running lights by day,
and about 1 W for the rest. That stays within the wheel's roughly 20 W lamp output. At night the running
lights drop to a position light. Don't raise "Beam" on the settings page to 100 % unless you've measured the
plug and it gives more.

## Assembly

1. **Head:**
   - Glue the three stars to the heat-sink bar with thermal adhesive. The narrow optic goes in the middle, in
     line with the head's three apertures.
   - Glue the NTC to the bar.
   - Slide the bar into the head from the back and fix it with the three M3 screws into the fins.
   - Run the 6 LED wires and the 2 NTC wires out through the hollow pin.
2. **Housing,** upside down:
   - Melt the two M4 inserts into the top bosses.
   - Put the head's pin into the bearing on the left, with its horn boss on the right.
   - Fit the servo on its two posts, with its spline in the horn.
   - Glue the two angled diffusers into their recesses, with LED strip rows behind them.
   - Push the LDR into its hole near the top of the face. It looks out through the window.
3. **Electronics box:** put the three LDD-1500L, the ESP32, the MPU-6050 (flat, X arrow forward), the buck and
   the MOSFET module on foam tape in the box under the head. Slide the road sensor board into its slot behind
   the little tunnel beside the chin vent. Don't put glass or film in front of it; it stays outside the window.
4. **Window:** run the foam tape round the edge of the lamp's face and press the polycarbonate window onto it.
   Peel the protective film off last.
5. **Into the wheel:** push the lamp up into the opening from below, then screw the cover's two M4 screws
   down into the inserts.
6. **Handle:** bolt it on as usual, then fit the two M3 screws up through its webs into the lamp.
7. **Lid:** close it with 4 × M3. Take it off any time to reach the electronics.
8. **Firmware:**
   - Flash `firmware/headlamp5_firmware/headlamp5_firmware.ino` (Arduino IDE, board *ESP32C3 Dev Module*,
     Pololu "VL53L1X" library).
   - Join the Wi-Fi **Headlamp-xxxx** (password **masterlamp**), open **192.168.4.1**, and tap "Calibrate"
     with the wheel upright on flat ground.
   - Set the aim (default 2° below the road) and the brightness.

## What I checked (against the measured wheel)

- **Fit:** the housing and lid stay clear of the shells, the cover, the controller and the motor cable.
- **Suspension:** with the suspension bottomed out, the lid stays 4.5 mm above the cross plate.
- **Head:** it tilts ±10° without touching the housing, the servo or the window (4–5 mm spare at the top, 6 mm below).
- **Window:** it fits inside the opening and sits 0.7 mm behind the cover's front edge.
- **Drops:** I tested about 18,000 fall directions. In every one, the handle grip, the shells or the tyre touch the
  ground first, and the lamp stays at least 19.8 mm clear: 25 mm falling straight forward, 48 mm onto a front
  corner, 91 mm onto a side.
  The lenses stay above the cover's front lip the whole way: at the lowest they're still 2.3 mm above it.
- **Handle:** handle v12 doesn't touch the wheel, and its webs line up with the lamp's screw bosses.
- **Road sensor:** its view is clear of everything. It looks at the road about 2.2 m ahead.
- **Parts:** every part is one solid piece.
- **Firmware:** it compiles against stand-in Arduino headers. It hasn't run on real hardware yet.

## Worth knowing

- **Heat:** the window seals the front, so air comes in through the chin vent under the lamp. It rises under
  the front half of the head, passes the heat sink, and drops behind a baffle to the slots in the back of the
  electronics box. Keep the vent clear of mud. When you stand still with the beam on,
  the heat-sink sensor turns the beam down. That's expected.
- **Aim:** set it on the phone page (see the main README). There's no screw adjustment; the head does it.
- **Top cover:** the lamp is screwed to it, like the stock lamp. Take out the two top screws before lifting
  the cover.
- **Measure the plug once** before first use, light on (expect about 6.5 V dim and 12 V full). If the page's
  voltage reading is off, adjust `VIN_DIVIDER` in the firmware.
