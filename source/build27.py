# Lamp v6.3: the boards placed, and room for their wires. Packing the real module sizes into the dry spaces
# (pack in boards_export.py) showed:
# - everything fits, with the MPU-6050 flat at the top of the left bay (the electronics box is only 16 mm deep,
#   front to back, so it won't lie flat there with its X arrow forward), and small AO3400 MOSFET modules
#   (about 18 x 11 mm; the D4184 boards with screw terminals don't fit beside the servo);
# - the left side bay reached the electronics box only through gaps about 2 mm wide: no room for the drivers'
#   wires. A slot through each side bay's floor now drops straight into the electronics box (both dry, so the
#   seal is unchanged): 5 x 10 mm on the right, 2.3 x 10 mm on the left.
exec(open('build26.py').read())
WIRE_SLOTS=((-1,-43.85,1.15),(1,41.6,2.5))   # side, w centre, half width; x -42..-32 (the box below runs -45..-29)
# left: the bearing block (w -42.6..-36.6) sits over the box there, so the slot uses the strip between it and the
# box's side wall (w -44.5), eating 0.5 mm into the wall's inside (1.5 mm stays to the outside). Right: open floor.
def wire_slots():
    out=[]
    for s,w,r in WIRE_SLOTS:
        out.append(hull(cylV(r,HOUSE_Y0-3.0,HOUSE_Y0+3.5,-42.0+r,w),cylV(r,HOUSE_Y0-3.0,HOUSE_Y0+3.5,-32.0-r,w)))
    return mf.Manifold.batch_boolean(out,mf.OpType.Add)
def housing12():
    h=housing11()-wire_slots()
    z0,z1=zw(-28.6,-19.5); h+=bx(-64.0,-59.6,PASS_Y0-ROOF_T,-22.6,z0,z1)   # a notch left by the old road sensor's mount, with a 0.2 mm skin: solid
    return h
