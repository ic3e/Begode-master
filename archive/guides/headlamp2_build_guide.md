# Auto-levelling headlamp v2: road sensor + daytime running lights

Same lamp head as v1. This version adds:

- **Road sensor** (VL53L1X laser rangefinder) in the front of the electronics block. It looks 15° down
  at the road about 2.5 m ahead, works out how the road slopes compared with the wheel, and keeps the
  beam on the road. The gyro fills in between readings and cancels braking dips and bumps instantly.
  When the sensor has no reading (bright sun, rain on the window, a kerb in the way) the lamp falls back
  to gyro-only levelling and blends back smoothly when readings return.
- **Daytime running lights (DRL)**: a white LED strip behind a printed diffuser in the front of each
  side block, one either side of the lamp.
- **Light sensor** (LDR) in the lid. In **Auto** mode: daylight = DRL only, main beam off. Dark = main
  beam on, DRL dimmed to a position light. It switches the beam on within 2 s when it gets dark (tunnels),
  and off only after 15 s of daylight (so a street lamp doesn't count as day).
- **Settings on your phone** over Wi-Fi, because the board's button is sealed inside the box.

Leave the **wheel's own headlight setting ON**. The lamp is powered from the wheel's lamp plug and decides
day/night itself. If the wheel switches the plug off, the DRL goes off too.

## Before you buy anything: measure the wheel's lamp plug

Measure it with a multimeter, light on, DC. **9–28 V**: build as listed. **28–56 V**: use a 5 V buck rated
for that input instead of the MP1584 (e.g. an LM2596HV module). Anything else: send me the reading.

## Parts (about €30–35 from AliExpress)

Everything from v1:

| Part | ~€ |
|---|---|
| Cree XHP50.2 6 V or Luminus SST-40 on a 20 mm copper star | 3–5 |
| 26.5 mm TIR lens for a 20 mm star, 15–25° | 1–2 |
| 40 × 40 × 20 mm aluminium heat sink | 1–2 |
| Mean Well LDD-1500H LED driver | 5–7 |
| MP1584EN 5 V buck module (set to 5.0 V first) | 1 |
| ESP32-C3 SuperMini | 2–3 |
| MPU-6050 (GY-521) | 1–2 |
| MG90S metal-gear servo | 3 |
| 10 k NTC (B3950) + 10 k resistor | 0.5 |
| 2-pin plug matching the wheel's lamp plug (stock: yellow JST, XH type) | 0.5 |

New in v2:

| Part | Notes | ~€ |
|---|---|---|
| VL53L1X module (13 × 18 mm board, e.g. "GY-VL53L1X") | road sensor, 4 m range | 4–6 |
| 5 V white LED strip, 2835, 120 LEDs/m | about 12–16 LEDs: two short rows behind each diffuser | 2 |
| Logic-level MOSFET module (D4184 or AO3400 "trigger switch") | switches/dims the DRL from 3.3 V; **not** an IRF520 module | 1 |
| 5 mm LDR (GL5528) + 10 k resistor | light sensor | 0.5 |

Screws: 4 × M4 × 20 + nuts, 4 × M2 × 6 self-tapping, 6 × M3 × 8 self-tapping.

## Printed parts (PETG or ASA, 4 walls, 30 % infill)

| File | How |
|---|---|
| `headlamp_head.stl` (from v1) | open back on the bed |
| `headlamp2_servo_block.stl` | outer face on the bed (as exported) |
| `headlamp2_electronics_block.stl` | bottom on the bed (as exported) |
| `headlamp2_lid.stl` | flat |
| `headlamp2_drl_diffuser_x2.stl` | **print two**, white or natural (clear) PETG, 100 % infill, 1.2 mm thick |

## Wiring

```
wheel lamp plug +  ──┬── LDD-1500H VIN+            LDD LED+ / LED− ── LED star + / −
                     └── MP1584 IN+
wheel lamp plug −  ──── common ground (LDD VIN−, MP1584 IN−, everything below)
MP1584 OUT+ 5.0 V  ──┬── ESP32-C3 5V
                     ├── servo red
                     └── MOSFET module DC+  ── module OUT+ ── both LED strips +
                         MOSFET module DC−  ── module OUT− ── both LED strips −
ESP32-C3 3V3 ──┬── MPU-6050 VCC
               ├── VL53L1X VIN
               ├── 10 k ── GPIO3 ── NTC ── GND          (heat sink temperature)
               └── LDR ── GPIO1 ── 10 k ── GND           (light sensor)
GPIO6 ── SDA of MPU-6050 and VL53L1X      GPIO7 ── SCL of both
GPIO10 ── servo signal      GPIO5 ── LDD-1500H DIM      GPIO4 ── MOSFET module PWM/TRIG (its GND to GND)
```

## Assembly

1. **Head:** as in v1. Fit the TIR lens, solder the LED and run its wires and the NTC's out through the
   hollow pivot pin, glue the star to the heat sink, press the heat sink in, then fit the two M3 fin screws.
2. **DRL:** glue a diffuser into the recess in the front of each block, flush with the face (a thin bead
   of clear silicone around the edge). Cut the LED strip into short rows. In the **servo block**, stick
   them on the back wall of the light chamber behind the diffuser; their wires go down the small hole and
   along the channel into the servo cable hole. In the **electronics block**, stick them on the front of
   the inner carrier wall behind the diffuser; wires go through the notch at its bottom.
3. **Road sensor:** slide the VL53L1X board sideways into its slot low in the front of the electronics
   block, sensor facing out through the little window. **No glass or clear plastic in front of it**: a
   cover makes it see its own reflection. A drop of silicone holds it.
4. **Light sensor:** push the LDR up into the hole in the lid from inside, its head just showing; seal
   it with clear silicone.
5. **Servo and electronics:** as in v1. Lay the MPU-6050 **flat on the floor**, X arrow pointing forward.
   The ESP32-C3, MP1584, LDD-1500H and MOSFET module go behind the carrier wall on foam tape.
6. **Join and fit:** put the head's pin into the electronics block, press the servo block onto the horn,
   slide the lamp in between the handle's side plates from the front, and bolt each block with two M4 × 20.
   The servo/DRL cable and the power cable come up through the window in the handle's shelf into the two
   holes in the electronics block's floor.

## Firmware and settings

1. Arduino IDE, board *ESP32C3 Dev Module*, *USB CDC On Boot: Enabled*. In Library Manager install
   **"VL53L1X" by Pololu**. Flash `headlamp2_firmware/headlamp2_firmware.ino`.
2. Stand the wheel upright and still on flat ground and switch on (2 s gyro calibration).
3. On your phone, join Wi-Fi **Headlamp-xxxx**, password **masterlamp**, and open **http://192.168.4.1**.
   The Wi-Fi stays on for 10 minutes after switching on (or while your phone is connected), then turns
   itself off until the next power-up.
4. Tap **Calibrate: wheel upright on flat ground**. It stores what "level" is and measures how high the
   road sensor sits.
5. Check directions once: lift the nose and watch the page. `pitch` must go up and the head must tilt
   down. If not, set `PITCH_SIGN` / `SERVO_DIR` to −1 in the firmware (see the v1 guide).
6. **Day/night switching:** the page shows the live light reading. At dusk, set "Night starts below" a bit
   under the reading, and "Day starts above" well over it. The gap keeps it from flickering.
7. Set the **aim** (default 2° below the road), the **beam brightness**, and the **DRL brightness** for day
   and night. Everything is remembered.

## What I checked, and what I couldn't

- **Fit:** the head tilts ±13° without touching anything. The road sensor's view (as a 17° cone, wider
  than its real 15°) misses the head at any tilt, the cup holder open and folded, the handle and the servo
  block. Every part is one solid piece, and every cable hole opens onto the window in the handle's shelf.
- **Firmware:** it compiles cleanly against stand-in Arduino headers, but it hasn't been built with the
  real ESP32 tools or run on hardware.
- **Levelling filter:** simulated on braking and hill cases (see v1). The road-sensor maths was checked
  by hand: a 5° nose-down pitch on flat ground reads as a 4.9° road slope.
- **Sizes of bought parts** are nominal. Check the VL53L1X board (13 × 18 mm) and the LED strip width before
  printing.

## Be kind to oncoming people

The levelling keeps the beam steady and on the road, the visor cuts upward spill, and the default aim is
2° below the road. It is still a round beam, not a certified dipped headlight.
