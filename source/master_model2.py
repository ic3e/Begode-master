# Begode Master, front end corrected to the owner's caliper measurements (Oct 2026).
# Datum: the handle STL frame (-X forward, +Y up, Z across, centre Z=-70.5). Every number in REAL is
# measured from the lowest handle bolt hole (STL X -2, Y -13.2) or the block face it sits behind.
# The rest of the wheel (tyre, pedals, cover top) is the old photo-traced model, moved to sit right
# under the measured front: it is for pictures, the front is what the checks use.
import numpy as np, manifold3d as mf, trimesh
_g={}; exec(open('master_model.py').read().split("\nif __name__=='__main__':")[0],_g)
ZC=-70.5; to_tm=_g['to_tm']; bx=_g['bx']; ex=_g['ex']; ex_soft=_g['ex_soft']
HOLE=np.array([-2.0,-13.2])
BLOCK_X=HOLE[0]-7.3              # front face of the black block (1)
LAMP_X=BLOCK_X-50.3              # stock lamp face (2)
SHELL_X=BLOCK_X-58.7             # front edge of the shells (3)
COVER_X=BLOCK_X-52.8             # front tip of the top cover (4)
LAMP_Y=HOLE[1]-7.5               # stock lamp underside (flat metal)
COVER_Y=LAMP_Y+15.5              # top cover underside above the lamp (5)
SHELL_TOP_FRONT=LAMP_Y+3.0       # shell top at its front corner
SHELL_TOP_HOLE=HOLE[1]-24.9      # shell top straight below the hole (6)
BAY_W=95.0                       # between the shells
CABLE_X=SHELL_X+50.0             # the motor cable, 50 mm into the bay
PLATE_REST=LAMP_Y-77.0           # cross plate over the tyre (moves with the suspension)
PLATE_LOW=LAMP_Y-37.0            # ... when the suspension bottoms out
DY=PLATE_REST-5-(_g['TC'][1]+_g['TR'])   # lifts the old tyre so its top sits just under the cross plate
TC=np.array([_g['TC'][0],_g['TC'][1]+DY]); TR=_g['TR']; GROUND=TC[1]-TR

def shell_pts():
    s=(SHELL_TOP_HOLE-SHELL_TOP_FRONT)/(HOLE[0]-SHELL_X)
    return [(SHELL_X,SHELL_TOP_FRONT),(HOLE[0],SHELL_TOP_HOLE),(357,SHELL_TOP_HOLE),(360,-115),(150,-122),
            (132,-145),(132,-300),(112,-340),(40,-352),(-50,-342),(SHELL_X,-300)]
def shells(sharp=False):
    p=shell_pts(); w0=BAY_W/2
    if sharp: return [ex(p,ZC+w0,ZC+135),ex(p,ZC-135,ZC-w0)]
    return [ex_soft(p,ZC+w0,ZC+135,6,7,+1),ex_soft(p,ZC-135,ZC-w0,6,7,-1)]
def cover():
    side=[(COVER_X,COVER_Y),(COVER_X,22),(-45,58),(-5,86),(355,86),(392,72),(392,24),(BLOCK_X,24),(BLOCK_X,COVER_Y)]
    c=ex_soft(side,ZC,ZC+73,6,6,+1)+ex_soft(side,ZC-73,ZC,6,6,-1)
    return c
def stock_lamp():   # the broken 4-LED lamp, staying in the cover
    body=bx(LAMP_X,BLOCK_X-6,LAMP_Y,COVER_Y+1,ZC-70.75,ZC+70.75)
    lens=[mf.Manifold.cylinder(2,7,7,32).rotate([0,90,0]).translate([LAMP_X-0.6,LAMP_Y+7.7,ZC+w]) for w in (-53,-17.7,17.7,53)]
    return body,mf.Manifold.batch_boolean(lens,mf.OpType.Add)
def box_ctrl(): return bx(BLOCK_X,180,-36,24,ZC-66.5,ZC+66.5)
def cable(): return bx(CABLE_X,BLOCK_X,-52,LAMP_Y,ZC-22,ZC+22)
def plate(low=False):
    y=PLATE_LOW if low else PLATE_REST
    return bx(SHELL_X+1,60,y-3,y,ZC-BAY_W/2,ZC+BAY_W/2)
def lower():   # old photo-traced parts, lifted with the tyre
    arms,panels=_g['frame']()
    mv=lambda m: m.translate([0,DY,0])
    parts=[(mv(_g['tyre']()),'#1e1e1e'),(mv(_g['rim']()),'#b8bcc2'),(mv(_g['hub']()),'#2a2a2a')]
    parts+=[(mv(m),'#18191b') for m in _g['lower_boxes']()]+[(mv(m),'#151515') for m in _g['pedals']()]
    parts+=[(mv(m),'#c9ccd1') for m in arms]
    return parts
def obstacles(low=True):
    # what the checks treat as solid near the front: shells, cover, stock lamp, controller, cable,
    # and (low=True) everything under the cross plate when the suspension bottoms out
    sb,_=stock_lamp()
    o=shells(True)+[cover(),sb,box_ctrl(),cable()]
    if low: o.append(bx(SHELL_X-2,200,-400,PLATE_LOW,ZC-BAY_W/2,ZC+BAY_W/2))
    return mf.Manifold.batch_boolean(o,mf.OpType.Add)
def model():
    sb,lens=stock_lamp()
    parts=[(m,'#2b2d31') for m in shells()]+[(cover(),'#232427'),(sb,'#3a3d42'),(lens,'#d9dde2'),(box_ctrl(),'#1b1c1e'),
           (cable(),'#111111'),(plate(),'#9ea3a9')]+lower()
    return [(to_tm(m),c) for m,c in parts]

if __name__=='__main__':
    for k in ('BLOCK_X','LAMP_X','SHELL_X','COVER_X','LAMP_Y','COVER_Y','SHELL_TOP_FRONT','SHELL_TOP_HOLE','CABLE_X','PLATE_REST','PLATE_LOW','DY','GROUND'):
        print(k,round(globals()[k],1))
    print('tyre centre',np.round(TC,1),'top',round(TC[1]+TR,1))
    ms=model(); print('parts',len(ms))
