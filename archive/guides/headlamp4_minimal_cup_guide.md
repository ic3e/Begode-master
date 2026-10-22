# v4: auto-levelling headlamp + minimal fold-under cup ring

The cup holder is now just a ring. It hangs from two small brackets under the lamp shelf and folds down
to hang flat under the headlamp. The lamp goes back to the slim v2 side blocks (no legs). The road
sensor sits in the front of the left block again. The electronics and firmware are v3 (6.5 / 12 V lamp
power, the beam follows the wheel's brightness).

## Using it

- **To fold:** swing the foot forward so it lies flat under the ring. Then lift the ring slightly, pull it
  towards you about 1 cm, and let it swing down. It hangs flat under the lamp, about 31 mm thick with the
  foot.
- **To open:** swing the ring up level, then push it back. It drops into its lock. The slot slopes down towards
  the back, so it stays locked by itself, and a cup's weight pushes it further in. It can't fold or flip
  up over bumps: it stops within about 3.5° downwards and 2° upwards.

## The ring

- **Size:** Ø80 mm inside, 22 mm tall.
- **Grip:** six springy fingers grip a 66 mm can or a 0.5 L bottle, and a takeaway coffee cup wedges in
  the ring.
- **Fold-flat foot:** a slim U on two M3 friction pivots on the outside of the ring's arms. Open, it
  hangs straight down and its crossbar sits 58 mm below the top of the ring, so cans and bottles stand
  on it while the fingers hold them upright. Folded, it lies flat just under the ring, the crossbar
  tucked under the ring's front edge. Tighten its two screws until it stays where you put it.

## Printed parts

| File | Qty | How |
|---|---|---|
| `master_handle_v7.stl` | 1 | handle with the two ring brackets (replaces v4–v6) |
| `master_handle_top_cap_p2.stl` | 1 | your original cap |
| `cup_ring_minimal.stl` | 1 | as exported: the ring and its arms lie flat, the fingers print upward, no supports (now with pilot holes for the foot) |
| `cup_ring_foot.stl` | 1 | as exported: crossbar side down, the two legs stand up; no supports |
| `headlamp_head.stl` | 1 | from v1 |
| `headlamp2_servo_block.stl`, `headlamp2_electronics_block.stl`, `headlamp2_lid.stl` | 1 each | from v2 |
| `headlamp2_drl_diffuser_x2.stl` | 2 | from v2 |

## Hardware

- 2 × M4 × 20 with nyloc nuts: **ring pins**. Head on the outside of each bracket, nut on the inside of
  the arm. Tighten only until there's no wobble: the pin has to slide in its slot.
- 4 × M4 × 20 with nuts: **lamp blocks to the handle** (top holes, as in v2).
- 2 × M3 × 10 self-tapping, plus a spring or rubber washer each: **foot pivots**, screwed into the pilot
  holes on the outside of the ring's arms.
- Everything else as in the v2 and v3 guides.

## Electronics and firmware

As in `headlamp3_build_guide.md`:
- **Driver and LED:** Mean Well LDD-1500L, a 3 V LED.
- **Voltage sense:** 47 k / 10 k divider into GPIO0.
- **Firmware:** `headlamp3_firmware.ino`. The road sensor's 15° aim is the same, so no firmware change
  is needed for the v2 block position.

## What I checked

- **Lock:** locked open, the ring stops within 3.5° downwards and 2° upwards.
- **Position:** open, the ring's top is 2 mm under the lamp.
- **Folding:** sliding forward to unlock is clear, and it folds down from the front of the slot with
  nothing in the way. Hanging folded, the pin can drop back in the slot without anything touching.
- **Clearances:** the lamp head clears the ring open and folded at ±13°. The road sensor's view misses
  the ring open, folded and the brackets.
- **Foot:** it swings between down and folded without touching the ring. With the foot folded, the ring
  still locks, unlocks, folds and hangs without touching anything. The foot clears the lamp head and the
  road sensor's view both down and folded.
- **Parts:** the handle, the ring and the foot are each one solid piece.
