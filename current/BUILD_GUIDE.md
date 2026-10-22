# v8: self-levelling lamp built into the stock lamp opening

The stock lamp comes out and the new lamp takes its place, flush with the top cover. Its housing is held
by the cover's two M4 screws from above, and by a tray that bolts to the handle. So the handle gets two
more mounting points, as you wanted. The can holder (from v7) swings up under it.

Everything is checked against the model of your wheel built from your caliper measurements.

## What changed from v7

- **Lamp:** no longer sticks out in front of the cover; it sits in the opening (134 × 36.8 × 49.3 mm).
- **Head:** smaller, so it fits. To tilt ±10° and still keep the whole lens above the cover's front lip, it uses a
  **20 mm optic on a 16 mm LED board** and a **25 × 25 × 20 mm heat sink**. One LDD-1500L driver, about
  5 W, roughly 450–550 lm out of the optic.
- **Levelling range:** ±10° (it was ±13°). The firmware limit is set to 10° in `headlamp4_firmware.ino`.
- **Road sensor and light sensor:** now in the front face: the road sensor top left, the light sensor top
  right. The daytime running lights sit either side of the head.
- **Handle v11:** loses the lamp side plates. It gains webs that run back to its tabs (where the stock
  lamp's ears used to bolt on), side rails inside the bay, and a crossbar under the lamp's front that carries
  the hinges for the can holder.
- **Can holder:** the same ring, floor and gimbal ring as v7. Only the swing arms are shorter (42 mm between
  holes). Swung in, its back half sits in the bay, and the front sticks out about 6 cm in front of the
  cover (about 3 cm past the grip).

## Bought parts that changed

| Part | Notes |
|---|---|
| 20 mm TIR optic for a 16 mm star, 15–25° | replaces the 26.5 mm optic |
| Cree XM-L2 or Luminus SST-20, 3 V, on a **16 mm** copper star | replaces the 20 mm star |
| 25 × 25 × 20 mm aluminium heat sink | replaces 40 × 40 × 20 |

Everything else is as in the v3 guide: LDD-1500L, ESP32-C3, MPU-6050, VL53L1X, MG90S, MP1584, MOSFET
module, LDR, NTC and the voltage divider.

## Printed parts (PETG or ASA, 4 walls)

| File | Qty | How |
|---|---|---|
| `master_handle_v11.stl` | 1 | on its side, supports under the grip (replaces every earlier handle) |
| `master_handle_top_cap_p2.stl` | 1 | your original cap |
| `lamp4_housing.stl` | 1 | top face on the bed, as exported |
| `lamp4_head.stl` | 1 | open back on the bed, as exported |
| `lamp4_tray.stl` | 1 | flat, pads up |
| `lamp4_drl_diffuser_x2.stl` | 2 | white or clear PETG, 100 % infill |
| `cup3_gimbal_ring.stl`, `cup3_ring.stl`, `cup3_floor.stl` | 1 each | as in v7 |
| `cup4_swing_arm_left.stl`, `cup4_swing_arm_right.stl` | 1 each | flat (new, shorter) |

## Hardware

- **Lamp to cover:** the stock lamp's 2 M4 screws, plus 2 M4 nuts in the slots under the bosses in the housing's top.
- **Tray to housing:** 4 × M3 × 10 self-tapping.
- **Tray to handle:** 4 × M3 × 10 self-tapping, into the crossbar and the two webs.
- **Lamp inside:** 2 × M2 × 6 (servo horn to head), 2 × M2 × 8 (servo to its posts), 2 × M3 × 8 self-tapping
  (the heat sink's fins).
- **Can holder (as v7):**
  - 2 × M4 × 20 with nylocs and rubber washers for the hinges
  - 2 × M3 × 12 for the forward/back pivots
  - 2 × M3 × 8 for the side-to-side pivots
  - 3 cords
  - 3 felt dots

## Assembly

1. **Head:** fit the optic and the LED star, then the heat sink from the back (2 × M3 into the fins). The LED
   and heat-sink sensor wires go out through the hollow pin.
2. **Housing,** working upside down:
   - Put the two M4 nuts in the slots under the top bosses.
   - Fit the head: pin into the bearing on the left, horn boss on the right.
   - Fit the servo on its two posts, with its spline in the horn.
   - Put the electronics on foam tape in the left compartment.
   - Slide the road sensor board into its slot behind the little tunnel. Don't put glass or film in front of it.
   - Glue the diffusers into their recesses, with the LED strip rows behind them.
   - Push the LDR into its hole.
   - The servo cable crosses to the left under the head, through the notches at the bottom of the partitions.
     The power lead leaves through the back.
3. **Into the wheel:** push the housing up into the opening from below, and screw the cover's two M4
   screws down into it. That holds it while you work.
4. **Handle:** bolt it on as before.
5. **Tray:** fit it under the housing: 4 screws up into the housing, 4 into the handle.
6. **Can holder:** as in v7. Tie the cords so the floor hangs 80 mm below the ring's top edge. Then fit
   the side-to-side pivots, the forward/back pivots, and the hinges.
7. **Firmware:** flash `headlamp4_firmware/headlamp4_firmware.ino`. Then calibrate on the settings page, as in v2.

## What I checked (against the measured wheel)

- **Fit:** the housing fits the opening and stays clear of the shells, the cover and the controller.
- **Head:** it tilts ±10° without touching anything (2–3 mm spare at the top). The lens stays above the cover's
  front lip the whole way: at its lowest it's still 4 mm above it.
- **Handle and tray:** they don't touch the wheel or each other.
- **Can holder:**
  - **Swung in:** clear even with the suspension bottomed out (12 mm above the cross plate, 13.5 mm in front of
    the cable). Pressed on its pads, it can't tip even 2° either way.
  - **Swinging:** clear the whole way.
  - **Arm stop:** it catches at the out position.
  - **Out:** ±25° forward/back and ±20° side to side in any mix without touching anything, with or without a can.
- **Road sensor:** its view is clear of the handle, the can holder (in and out), the can and the wheel.
- **Beam:** the top of a can sits about 18 mm below the beam's lower edge.
- **Parts:** every part is one solid piece.
- **Firmware:** it compiles against stand-in Arduino headers.

## Worth knowing

- **Top cover:** the lamp is screwed to it, like the stock lamp was. To lift the cover, take out the two top
  screws first.
- **Heat:** the head sits in a half-closed opening. Air comes in around the head and leaves through the slot in
  the tray. When you stand still with the beam on, the heat-sink sensor turns the beam down. That's expected.
- **Slim 58 mm cans** wobble in the ring. A strip of foam tape inside fixes that.
