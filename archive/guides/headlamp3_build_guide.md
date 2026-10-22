# Headlamp v3: lamp and cup holder as one unit

The auto-levelling lamp (road sensor, gyro, daytime running lights) and the folding cup holder are now
one unit:

- **Legs:** the lamp's two side blocks run on down the front as legs.
- **Cup holder:** the ring and tray hinge between the legs on long side arms, like a motorcycle holder.
  Fold the tray up, then the ring down: they lie flat between the legs, right under the lamp, about as far
  forward as the front of the grip. The folded ring keeps the tray shut.
- **Road sensor:** it moved into the front of the left leg.
- **Handle v6:** it loses the separate hanger and gains a second bolt per side, because the lamp blocks
  now carry the cup as well.

Everything not mentioned here is as in `headlamp2_build_guide.md`.

## Power: what the wheel's lamp plug gives

About **6.5 V in the wheel's dim mode, 12 V at full brightness, about 20 W**. The wheel also raises the
brightness while accelerating. That changes two parts from v2, because the old LED driver needs at
least 9 V:

| v2 part | v3 part | Why |
|---|---|---|
| Mean Well LDD-**1500H** | Mean Well LDD-**1500L** (6–36 V in, 1.5 A) | keeps working at 6.5 V in dim mode |
| XHP50.2 **6 V** LED | Luminus SST-40 / SFT-40 or Cree XHP50.2 **3 V** LED, on a 20 mm copper star | a 3 V LED leaves the driver room to regulate at 6.5 V |

Brighter option: put **two LDD-1500L in parallel** on the same LED (inputs together, outputs together,
both DIM pins on GPIO5). That gives 3 A, about 1300–1500 lm, instead of 1.5 A and about 700–800 lm.

**Power budget at full:** LED 5 W (or 10 W with two drivers), DRL 3 W, servo and electronics 1–2 W.
That's about 9–15 W, inside the wheel's ~20 W.

The MP1584 5 V buck works from 6.5 V too.

**Voltage sense (new):** a 47 k resistor from the plug + to **GPIO0**, and a 10 k resistor from GPIO0 to
GND. The firmware reads the plug voltage and scales the main beam with it, so the wheel's dim/full setting
and its "brighter when accelerating" carry straight through to the new lamp. You can switch this off on
the settings page ("Beam follows the wheel") and set how bright the beam is in the wheel's dim mode.

## Printed parts (PETG or ASA, 4 walls, 30 % infill)

| File | Qty | How |
|---|---|---|
| `master_handle_v6.stl` | 1 | as before (on its side, supports under the round grip) |
| `master_handle_top_cap_p2.stl` | 1 | your original cap |
| `headlamp_head.stl` | 1 | open back on the bed |
| `headlamp3_servo_block_leg.stl` | 1 | outer face on the bed (as exported) |
| `headlamp3_electronics_block_leg.stl` | 1 | outer face on the bed (as exported) |
| `headlamp2_lid.stl` | 1 | flat |
| `headlamp2_drl_diffuser_x2.stl` | 2 | white or natural PETG, 100 % infill |
| `headlamp3_cup_ring.stl` | 1 | as exported (arms up) |
| `headlamp3_cup_tray.stl` | 1 | floor on the bed |

The old cup holder plate, ring and tray, and the v4/v5 handles, are no longer needed.

## Hardware

- 4 × M4 × 35 with nyloc nuts: **stub axles** for the ring and tray, pushed in from the outside of each
  leg, nut on the inside of the arm. Tighten the ring's pair until it stays up by itself.
- 8 × M4 × 20 with nuts: **blocks to the handle's side plates**. Two per side at the top (nut slots open
  upwards), two per side low down (nut slots open from below).
- From v2: 4 × M2 × 6, 6 × M3 × 8 self-tapping.

## Wiring (changes from v2)

```
wheel lamp plug + ──┬── LDD-1500L VIN+   (both drivers, if you fit two)
                    ├── MP1584 IN+
                    └── 47 k ── GPIO0 ── 10 k ── GND       (wheel voltage sense)
LDD-1500L LED+/LED− ── LED star (3 V LED)
everything else: as in v2
```

## Assembly (changes from v2)

1. **Road sensor:** it now goes into the **front of the left leg**. Slide the board in sideways from the
   leg's inner face, sensor facing out through the window, and seal with a drop of silicone. Its wires run
   up inside the leg and through the block wall into the electronics box.
2. **Cup holder:** hold the tray's arms against the insides of the legs at the lower holes, push an
   M4 × 35 through from the outside each side, and fit the nylocs. Do the same with the ring at the upper
   holes. Fold the tray up, then the ring down over it, to check.
3. **Fitting:** the lamp unit goes in from the front between the handle's side plates, resting on the shelf.
   Bolt it with all eight M4 × 20.

## Firmware

Flash `headlamp3_firmware/headlamp3_firmware.ino` (Pololu "VL53L1X" library, as in v2). The settings page
adds a live "wheel lamp ... V" readout, the **Beam follows the wheel** switch, and **Beam in the wheel's dim
mode**. On the first test, check that the readout shows about 12 V at full and about 6.5 V in dim. If it's
off, adjust `VIN_DIVIDER` in the firmware.

## What I checked, and what I couldn't

- **Folding:** the ring and tray fold (tray first) without touching each other, the legs, the lamp or the
  handle. Both stop within 2° of level when open. Folded, the tray can't swing open past the ring.
- **Head and sensor:** the lamp head clears everything to ±13°. The road sensor's view (as a 17° cone)
  misses the cup holder open and folded, the legs, the handle and the head. Its wire path from the slot to
  the electronics box is continuous.
- **Parts:** every part is one solid piece. The folded pack sits 62–89 mm in front of the blocks, between
  the legs; the handle's grip front is at 92.5.
- **Firmware:** v3 compiles cleanly against stand-in Arduino headers, but it hasn't been built with the
  real ESP32 tools or run on hardware.
- **Bought parts:** sizes are nominal. **Measure the plug yourself once** to confirm 6.5 / 12 V.
