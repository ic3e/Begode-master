# v6: the slide-out cup holder, now self-levelling both ways

Same drawer as v5, but the basket now hangs in a **two-axis gimbal**, like a ship's compass:

- **Basket and gimbal ring:** the basket (the same four telescoping rings) hangs on **front and back pins** inside a red
  **gimbal ring**, so it swings **side to side**.
- **Gimbal ring and arms:** the gimbal ring hangs on **left and right pins** from the slide arms, so it swings
  **forward and back**.
- **Stability:** both pin axes meet in one point **above** the drink's centre of gravity: 19 mm above a full can's, about
  32 mm above a full coffee's. Gravity keeps the drink upright whichever way the wheel tips.

What the side-to-side swing is for:

- **Parked on the kickstand:** the wheel leans about 10–15°, and the cup stays straight.
- **Cambered roads.**
- **Lifting or wheeling the wheel** with a drink in it.

In turns it hardly moves, because the wheel already leans with the apparent gravity there.

Lamp, electronics and firmware are unchanged (v2 lamp blocks, v3 electronics and firmware).

## What changed from v5

- **Gimbal ring:** a new part. Ring 1's pivot ears moved from the sides to the front and back.
- **Lower:** the pivots sit **12 mm lower**. Pitched forward, the wider gimbal ring would otherwise drift into the road
  sensor's view. As a bonus, the top of a can now sits 15 mm below the beam instead of 1.5 mm.
- **Wider:** the rails sit 6 mm further out on each side (still well inside the handle's side plates).
- **Further forward and shorter travel:** slid in, the stack sits about 2 cm further forward, and the drawer travels
  4.4 cm instead of 5.5. Both are needed so the gimbal ring's back screw clears the back cross piece.

## Using it

As in v5:

- **Out:** pull the drawer out until it clicks. The rings drop open; put the drink in.
- **In:** take the drink out, push the rings up flat and slide the drawer back in until it clicks.

Slid in, the back of ring 1 sits in a slot either side of its back ear. That holds it level both ways, and with
ring 1 held the gimbal ring can't swing either.

## Printed parts (PETG or ASA)

| File | Qty | How |
|---|---|---|
| `master_handle_v9.stl` | 1 | handle with the lamp shelf and the wider, lower rails (replaces v8) |
| `master_handle_top_cap_p2.stl` | 1 | your original cap |
| `cup2_gimbal_ring.stl` | 1 | flat as exported, bosses up, no supports |
| `cup2_ring1.stl` … `cup2_ring4.stl` | 1 each | upright as exported, no supports (ring 1 is new: its ears are at front and back) |
| `cup2_slide_arm_left.stl`, `cup2_slide_arm_right.stl` | 1 each | flat as exported |
| Lamp: `headlamp_head.stl`, `headlamp2_servo_block.stl`, `headlamp2_electronics_block.stl`, `headlamp2_lid.stl`, `headlamp2_drl_diffuser_x2.stl` (×2) | | as before |

## Hardware

- **Forward/back pivots:** 2 × M3 × 12, through each arm into the side bosses of the gimbal ring.
- **Side-to-side pivots:** 2 × M3 × 10, through the gimbal ring's front and back bosses into ring 1's ears.
- **Front stops:** 2 × M3 × 8, into the small hole near the front of each rail, after the arms are in.

Each screw grips the part it's screwed into and turns freely in the part it passes through. So stop tightening
just before the head touches, and add a drop of medium thread-locker so it doesn't back out.

## Assembly

1. **Basket:** drop ring 4 into ring 3, ring 3 into ring 2, and ring 2 into ring 1.
2. **Side-to-side pins:** lower ring 1 through the gimbal ring, with its two ears lined up with the gimbal ring's front and
   back bosses. Screw an M3 × 10 through each boss into the ear.
3. **Forward/back pins:** hold the gimbal ring between the two arms (pivot bosses facing in). Screw an M3 × 12 through
   each arm into the gimbal ring's side bosses.
4. **Rails:** slide the assembly in from the front, each slider into its rail. Fit the two front stops.
5. **Test:** pull it out and tilt the wheel by hand both ways. The basket should hang straight. Push it in: it should
   click and sit firm.

## What I checked

- **Swing:** pulled out, the basket swings **±25° forward/back and ±20° side to side, in any mix**. Nothing touches: not
  the rails, arms, lamp, handle or the rough wheel model. Ring 1 first meets the gimbal ring at 22° of roll.
- **Road sensor:** its view stays clear stowed, out, and at every one of those angles. That's why the pivots moved down.
- **Lamp head:** it clears everything at ±13°.
- **Slid in:** nothing rubs on the way in or out. Stowed, the holder can't tip more than 2° either way, and the inner
  rings rest on the ledge.
- **Assembly:** ring 1 with its ears passes through the gimbal ring.
- **Parts:** every part is one solid piece.

## Worth knowing

- **If it swings too much:** a two-way pendulum can sway on bumpy roads. If the coffee sways too much, tighten the four
  pivot screws a little so they add some friction. A rubber or felt washer under each screw head does the same more evenly.
- **Shell clearance:** the rails are now 6 mm wider and still end 2 mm in front of where the rough model puts the shells.
  Check that gap on the real wheel before printing.
