# Self-levelling headlamp for the Begode Master front handle

Replaces the stock lamp. It fits in the lamp slots of `master_handle_v5_lamp_cup.stl`, under the grip
and above the folding cup holder. One LED with a TIR lens sits in a head that a servo tilts up to ±12°,
so the beam stays steady when the wheel dips under braking, rocks over bumps or tilts back.

## Before you buy anything: measure the wheel's lamp plug

The lamp runs off the stock 2-pin headlight plug, so the wheel's light button keeps working.
**Measure that plug's voltage with the light switched on** (multimeter on DC, red probe on the red wire).

| Plug voltage | What to do |
|---|---|
| 9–28 V | Build it as listed below. |
| 28–56 V | Swap the MP1584 for a 5 V buck rated for that input (e.g. an LM2596HV module). The LDD-1500H still works. |
| Anything else | Stop and send me the reading. |

The lamp draws about 10–12 W at full brightness. That's roughly what a stock lamp uses, but if the
light flickers or the wheel complains, lower `LED_MAX` in the firmware.

## Parts (about €20–25 from AliExpress)

| Part | Notes | ~€ |
|---|---|---|
| LED: Cree XHP50.2 **6 V** or Luminus SST-40 on a 20 mm copper (DTP) star | ~1000–1300 lm at 1.5 A | 3–5 |
| TIR lens, 26.5 mm, for 20 mm star, 15–25° | 15 mm tall; a 10° spot throws further but lights less of the road | 1–2 |
| Aluminium heat sink 40 × 40 × 20 mm | the common 3D-printer one | 1–2 |
| Mean Well **LDD-1500H** LED driver | 9–56 V in, 1.5 A, has a dimming input | 5–7 |
| MP1584EN 5 V buck module | powers the board and servo; set it to 5.0 V before connecting | 1 |
| ESP32-C3 SuperMini | the brain | 2–3 |
| MPU-6050 (GY-521 board) | gyro + accelerometer | 1–2 |
| MG90S metal-gear servo | 9 g size, with its horns | 3 |
| 10 k NTC thermistor (B3950) + 10 k resistor | heat sink temperature; optional but recommended | 0.5 |
| 2-pin plug matching the wheel's lamp plug | the stock one is a yellow JST (XH-type); check yours | 0.5 |
| Thermal adhesive (or thermal pad + glue) | LED star to heat sink | 2 |

Screws: 4 × M4 × 20 + 4 M4 nuts (blocks to the handle), 4 × M2 × 6 self-tapping (servo tabs, horn),
2 × M3 × 8 self-tapping (heat sink), 4 × M3 × 8 self-tapping (lid).

## Printed parts (PETG or ASA, 4 walls, 30 % infill)

| File | Orientation |
|---|---|
| `headlamp_head.stl` | open back on the bed (as exported); support only under the front lip if your printer can't bridge 27 mm |
| `headlamp_servo_block.stl` | outer face on the bed (as exported) |
| `headlamp_electronics_block.stl` | bottom on the bed (as exported) |
| `headlamp_lid.stl` | flat |

The heat sink runs at up to ~70 °C at full power standing still. PETG copes with that; PLA does not.

## Wiring

```
wheel lamp plug +  ──┬── LDD-1500H  VIN+          LDD  LED+ ── LED star +
                     └── MP1584     IN+           LDD  LED− ── LED star −
wheel lamp plug −  ──┬── LDD-1500H  VIN−  (common ground for everything)
                     └── MP1584     IN−
MP1584 OUT+ (5.0 V) ─┬── ESP32-C3 5V
                     └── servo red
MP1584 OUT−        ──┬── ESP32-C3 GND, servo brown, MPU-6050 GND
ESP32-C3 3V3       ──┬── MPU-6050 VCC
                     └── 10 k resistor ── GPIO3 ── NTC ── GND
ESP32-C3 GPIO6 ── MPU-6050 SDA        ESP32-C3 GPIO7 ── MPU-6050 SCL
ESP32-C3 GPIO10 ── servo orange (signal)
ESP32-C3 GPIO5 ── LDD-1500H DIM
```

## Assembly

1. **Head:** fit the TIR lens from the back, against the front lip. Solder ~25 cm wires to the LED star
   and thread them sideways out through the hollow pivot pin. Glue the star to the heat sink with
   thermal adhesive, press the heat sink into the back of the head against the lens, and fix it with the
   two M3 screws through the side holes (they pinch the outer fins). Glue the NTC between two fins and
   run its wires out through the pivot pin too.
2. **Servo:** before fitting, power it once with the firmware running and the wheel standing level, so
   it sits at its "level" position. Put it in the servo block (shaft towards the head) and screw the tabs
   down with two M2 screws. Cut the single-arm horn to fit the recess in the head's servo-side boss and
   screw it in with two M2 screws, pointing back.
3. **Electronics:** stick the MPU-6050 **flat on the floor** of the electronics block, its X arrow pointing
   forward. Mount the ESP32-C3, MP1584 and LDD-1500H around it with double-sided foam tape.
4. **Join:** push the head's pivot pin into the electronics block, then press the servo block onto the
   horn's spline. Slide the whole lamp in between the handle's side plates from the front, resting on the
   shelf, and bolt each block in with two M4 × 20 through the outer slots (nuts in the slots on top).
5. **Cables:** the servo cable drops out of the bottom of the servo block, through the window in the
   shelf, across under the shelf and up into the electronics block. The power cable comes up through
   the same window into the second hole in the electronics block's bottom.
6. Seal the lid and the cable holes with a bead of silicone. A drop of conformal coating (or nail
   varnish) on the boards helps in rain.

## First start and setup

1. Flash `headlamp_firmware/headlamp_firmware.ino` with the Arduino IDE. Board: *ESP32C3 Dev Module*,
   *USB CDC On Boot: Enabled*. No extra libraries needed.
2. Stand the wheel level and still, then switch on: it spends 2 s calibrating the gyro, then the LED
   ramps up.
3. Open the serial monitor (115200). Lift the nose: `pitch` must go **positive**. If it goes negative,
   set `PITCH_SIGN` to -1.
4. Lift the nose again and watch the head: it must tilt **down** to cancel it. If it tilts up, set
   `SERVO_DIR` to -1.
5. If the head isn't level at rest, set `SERVO_TRIM_DEG` (the horn spline only fits every ~18°).
6. Aim the beam with the board's BOOT button: short press = 0.5° up, long press (~1 s) = 0.5° down.
   Holding it for more than 3 s while the wheel stands level stores "this is level". Both are remembered.

What it does while you ride:
- **Fast pitch** (braking dip, bumps, the start of tilt-back) is cancelled fully.
- **Slow changes** (a long hill) are followed halfway (`LEVEL_GAIN = 0.5`), so the beam settles on the road
  ahead instead of pointing at the sky or the ground.
- **If the wheel falls over or is picked up**, the head parks and the LED dims to 15 %.
- **The LED dims** from 60 °C on the heat sink (down to 30 % at 80 °C).

## Be kind to oncoming people

A TIR lens makes a round beam. Keep the aim a couple of degrees down (the default is −2°). The visor
over the lens cuts the upward spill, and the levelling keeps the beam from flashing upwards over bumps.
This is not a certified road lamp.
