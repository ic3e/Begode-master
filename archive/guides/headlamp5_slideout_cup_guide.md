# v5: slide-out, self-levelling cup holder under the headlamp

The cup holder is now a little drawer under the lamp.

- **Slid in:** it is a flat 20 mm stack that sits under the headlamp, like your sketch.
- **Pulled out:** about 5.5 cm, until it clicks. The basket then drops open into a 75 mm deep cup that
  holds a **0.33 l can** or a **takeaway coffee cup**.
- **Self-levelling:** the basket hangs on two pivots near its top, like the gimbal cup holders on boats,
  so gravity keeps the drink upright when the wheel pitches (braking, accelerating, tilt-back). The
  pivots sit **above** the drink's centre of gravity: 17 mm above it for a full can, about 30 mm for a full
  coffee. That's what makes it hang upright instead of tipping over.
- **No sideways pivot:** when you lean into a turn, the wheel and the drink lean together with the
  "apparent gravity", so the coffee doesn't slop sideways.

Lamp, electronics and firmware are unchanged (v2 lamp blocks, v3 electronics and firmware).

## Using it

- **Out:** pull the basket forward until it clicks. The rings drop open by themselves; put the drink in.
- **In:** take the drink out, push the rings up flat and slide the basket back until it clicks. The
  ledge under the back has a sloped front that helps lift the rings as it goes in. Stowed, the back of the stack sits in
  a slot, which stops it swinging, and a ledge holds the inner rings up.
- **On the road:** braking pushes the drawer against its front stop. The click keeps it from sliding back
  under acceleration.

## Printed parts (PETG or ASA)

| File | Qty | How |
|---|---|---|
| `master_handle_v8.stl` | 1 | handle with the lamp shelf and the two cup rails (replaces v4–v7) |
| `master_handle_top_cap_p2.stl` | 1 | your original cap |
| `cup_gimbal_ring1.stl` … `cup_gimbal_ring4.stl` | 1 each | upright as exported, no supports |
| `cup_slide_arm_left.stl`, `cup_slide_arm_right.stl` | 1 each | flat as exported |
| Lamp: `headlamp_head.stl`, `headlamp2_servo_block.stl`, `headlamp2_electronics_block.stl`, `headlamp2_lid.stl`, `headlamp2_drl_diffuser_x2.stl` (×2) | | as before |

## Hardware

- 2 × M3 × 12 screws: **basket pivots**, through each arm into the pilot hole in ring 1's ear. The ring
  swings on the screw shank, so don't clamp the arm.
- 2 × M3 × 8 screws: **front stops**, screwed down into the small hole near the front of each rail, after
  the arms are in.
- Lamp: as in the v2 and v3 guides (4 × M4 × 20 for the lamp blocks).

## Assembly

1. **Basket:** drop ring 4 (the one with the floor) into ring 3 from the top, ring 3 into ring 2, and
   ring 2 into ring 1. Each hangs on the lip of the one outside it.
2. **Pivots:** hold ring 1 between the two arms (pivot bosses facing in) and screw the two M3 × 12
   pivots from the outside of each arm into ring 1's ears. The screw heads ride inside the rails later.
3. **Rails:** slide the whole basket-and-arms in from the front, each slider into its rail.
4. **Stops:** fit the two front stop screws. Pull out and push in a few times. It should click at both
   ends, and the basket should swing freely when out.

## What I checked

- **Sliding:** the arms slide the whole way without rubbing; only the click bumps touch, and they seat at
  both ends. The flat stack slides out without hitting anything.
- **Stowed:** slid in, the stack is held level (it can't swing more than 2°) and the inner rings can't drop.
- **Out:** opened, the basket swings a full ±25° without touching the rails, lamp, handle or wheel.
- **Clearances:** the road sensor's view, the lamp head (±13°) and the rough Master model are all clear,
  stowed and out.
- **Beam:** out, the top of a can sits just below the beam's lower edge (about 1.5 mm), and a coffee cup
  about 5 mm below it.
- **Parts:** every part is one solid piece.

## Worth knowing

- **Click strength:** the printed clicks are small. If the drawer slides back too easily under hard
  acceleration, a tiny M5 ball-spring plunger in the rail top makes a stronger click.
- **Shell clearance:** the rails end 2 mm in front of where the rough wheel model puts the shells. Check
  that gap on the real wheel before printing.
