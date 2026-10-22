# v7: built to your measurements. Lamp in front of the cover, can holder that swings up under it

Everything is now checked against a model of the wheel's front built from your caliper numbers, not
from photos. **Earlier handles (v4 to v9) don't fit the real wheel:** they run into the shells and the top
cover. Don't print any of them.

## What your measurements showed

| | Measured | What it means |
|---|---|---|
| Lowest bolt hole → block face | 7.3 mm | the reference everything else hangs off |
| Block face → lamp face | 50.3 mm | the stock lamp is **built into the top cover** |
| Block face → cover tip | 52.8 mm | |
| Block face → shell front | 58.7 mm | the shells come **further forward than the lamp** |
| Lamp underside | 7.5 mm below the lowest hole | |
| Cover underside above the lamp | 15.5 mm above the lamp's underside | |
| Shell top, front corner | 3 mm above the lamp's underside | the shell tops rise towards the front |
| Shell top under the holes | 24.9 mm below the lowest hole | |
| Bay between the shells | 95 wide, 50 deep to the cable | |
| Cross plate | 77 mm below the lamp, 37 mm when the suspension bottoms out | |

Your original handle fits this model with no overlap at all, so the numbers agree with each other.

## What changed

- **The lamp moved forward.** The stock lamp lives in the top cover, so the self-levelling lamp can't go
  where it is. The same lamp parts (head, servo block, electronics block, lid, diffusers) now hang **in
  front of the cover**, under the grip. They sit on new side plates that grow out of the handle's arms.
  The lamp's front is about 2.4 cm ahead of the grip, and its back is 8 mm in front of the cover tip.
- **The can holder swings instead of sliding.** It hangs from two swing arms on a hinge just under
  the front of the lamp.
  - **Swung in:** it lies flat under the lamp, with its back half in the bay between the shells. Only
    about 7 mm sticks out past the lamp's front.
  - **Swung out:** the arms hang just past straight down, so gravity holds them against their stop.
    The can hangs below and in front of the lamp.
- **Cans only, as agreed.** The basket is a 68.5 mm ring that holds the can near its top. A floor hangs
  80 mm below on three cords. The can's centre of gravity sits 14.5 mm below the pivots, so it hangs
  upright.
- **It still levels both ways.** A gimbal ring on the arms' pins handles forward/back, and the cup ring
  on the front and back pins inside it handles side to side.

## Using it

- **Out:** pull the basket down and forward until the arms stop. Drop the can in. Its weight pushes the
  floor out of the ring, and the floor drops until the cords go tight.
- **In:** take the can out and push the floor up into the ring (its little spring tabs hold it there).
  Then swing the basket up until the ring touches the three felt pads under the lamp shelf. The
  hinges are friction hinges, so it stays there.

## Printed parts (PETG or ASA, 4 walls)

| File | Qty | How |
|---|---|---|
| `master_handle_v10.stl` | 1 | handle + lamp side plates + shelf + hinge brackets (replaces every earlier handle). On its side, with supports under the grip |
| `master_handle_top_cap_p2.stl` | 1 | your original cap |
| `cup3_gimbal_ring.stl` | 1 | flat as exported, no supports |
| `cup3_ring.stl` | 1 | upright as exported, no supports |
| `cup3_floor.stl` | 1 | flat, can socket up |
| `cup3_swing_arm_left.stl`, `cup3_swing_arm_right.stl` | 1 each | flat |
| Lamp: `headlamp_head.stl`, `headlamp2_servo_block.stl`, `headlamp2_electronics_block.stl`, `headlamp2_lid.stl`, `headlamp2_drl_diffuser_x2.stl` (×2) | | unchanged, as before |

## Hardware

- **Hinges:** 2 × M4 × 20 with nyloc nuts and a rubber or wave washer each. Bolt head on the inside,
  nut on the outside of the bracket. Tighten until the swung-in basket stays up by itself.
- **Forward/back pivots:** 2 × M3 × 12, through each arm into the gimbal ring's side bosses.
- **Side-to-side pivots:** 2 × M3 × 8, through the gimbal ring's front and back holes into the cup ring's ears.
- **Cords:** 3 lengths of 2 mm cord, about 12 cm each (thin paracord core or Dyneema).
- **Felt:** 3 small self-adhesive felt dots, one on each pad under the shelf.
- **Lamp:** 4 × M4 × 20 with nuts, blocks to the side plates (as before).

## Assembly

1. **Cords:** tie the floor to the cup ring through the three pairs of holes, with a knot under the floor
   and inside the ring. Set the length so the floor's top face hangs **80 mm below the ring's top edge**, level.
2. **Side-to-side pivots:** put the cup ring inside the gimbal ring, ears to the front and back. Screw an
   M3 × 8 through each of the gimbal ring's front and back holes into the ears.
3. **Forward/back pivots:** screw an M3 × 12 through each arm's small hole into the gimbal ring's side bosses.
4. **Hinges:** bolt each arm's big hole to its bracket under the shelf with an M4 × 20.
5. **Test:** swing it out. It should stop just past straight down and stay there. Tilt the wheel: the
   basket hangs straight. Swing it in: the ring should sit flat against the three felt pads.

## What I checked (against the measured model)

- **Fit:** the handle, the lamp and the lamp head (tilted ±13°) don't touch the shells, the cover, the stock
  lamp or the controller.
- **Swung in:** clear of everything even with the suspension fully bottomed out. That leaves 11.7 mm above
  the cross plate, and 13.5 mm in front of the cable. Pressed on its pads, it can't tip even 2° either way.
- **Swinging:** the arms and the basket pass through the whole swing without touching anything.
- **Arm stop:** it catches the arms at their out position.
- **Out:** the basket swings ±25° forward/back and ±20° side to side, in any mix, without touching anything.
  A can in it stays clear of the lamp shelf, the arms and the wheel at all of those angles.
- **Road sensor and beam:** the road sensor's view is clear, in and out, with or without a can. The top of a
  can sits about 4 cm below the beam's lower edge.
- **Parts:** every part is one solid piece.

## Worth checking on the wheel before printing

- **Lifting the top cover:** the lamp's back is 8 mm in front of the cover tip. If the cover hinges at the
  back, its nose moves up and slightly forward as it opens. Lift it while holding a ruler 8 mm in front
  of the tip, and check it misses.
- **Lamp cable:** it now has to reach back from in front of the cover to the wheel's lamp plug. Run it along
  the underside of a side plate. Leave the bay free, because the basket sits there when swung in.
- **Slim cans:** 0.33 l "sleek" cans (58 mm) wobble in the 68.5 mm ring. A strip of foam tape inside the ring
  takes up the gap.
