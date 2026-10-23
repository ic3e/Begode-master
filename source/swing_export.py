# How far the lenses tilt, and what that does on the road (renderers: anim/level.html for the wheel at night,
# anim/mech6.html for the cut close-ups; data in anim/level_data.js and anim/swing_data.js).
# The lens frame swings +-12 deg about the line through the LED chips (stops at +-12.4); the firmware levels over
# +-10 (TILT_MAX), so there is 2 deg in hand before the stops.
import numpy as np, trimesh, json, base64
src=open('stills6_export.py').read().replace("exec(open('build26.py').read())","exec(open('build27.py').read())").replace('housing11()','housing12()')
exec(src.split("views=[")[0].replace("open('anim/stills6_data.js'","#"))
# a fixed lamp's beam, for comparison: the middle optic's cone, fixed to the wheel (red)
fx=mf.Manifold.cylinder(L,7.5,7.5+L*np.tan(np.radians(4.5)),64).rotate([0,-90,0]).translate([LX,0,0])
fx=fx.translate([PX6,PY6,ZC]).rotate([0,0,2.0]) if False else fx.translate([0,0,0])
add('fixbeam',fx,'#ff4d4d','fixb',emissive='#ff4d4d',opacity=0.10,smooth=False,kind='beam')
Z16=np.zeros(16).tolist()
def pitched(p):   # the wheel pitched by p degrees about the tyre's contact point (+ = nose down)
    c=P(stand,[184.6,-357.7-255.0,ZC]); return T(*c)@Rz(p)@T(*(-c))@stand
def lview(cap,p,fixed=True):
    B=pitched(p); a=max(-10.0,min(10.0,-p))       # the firmware turns the lenses against the pitch, up to +-10
    v=view(cap,B,P(B,[300,-150,ZC])+np.array([-650,520,2900]),P(B,[-450,-250,ZC]),night=True,a=a,beams=True)
    v['m']['fixb']=(np.asarray(B@T(PX6,PY6,ZC)).T.flatten().round(4).tolist()) if fixed else Z16
    return v
views=[lview('Riding level: the beam reaches far down the road',0.0,fixed=False),
       lview('Braking, nose 10 deg down: the lenses tilt 10 deg up, the beam stays put (red: a fixed lamp)',10.0),
       lview('Accelerating, nose 8 deg up: the lenses tilt 8 deg down, the beam stays on the road (red: a fixed lamp)',-8.0)]
open('anim/level_data.js','w').write('window.DATA='+json.dumps(dict(meshes=meshes,frames=views))+';')
print('level views',len(views))

# ---- the cut close-ups: the lamp cut through the middle lens, the lens frame at -12, 0 and +12 ----
meshes=[]
def add2(name,m,color,group,rough=0.6,metal=0.0,emissive=None,opacity=1.0,kind='std'):
    t=trimesh.graph.smooth_shade(to_tm(m),angle=np.radians(35))
    meshes.append(dict(name=name,group=group,color=color,rough=rough,metal=metal,emissive=emissive,opacity=opacity,kind=kind,
        pos=b64(t.vertices,np.float32),nrm=b64(t.vertex_normals,np.float32),idx=b64(t.faces,np.uint32)))
half=lambda m: m-bx(-300,300,-300,300,ZC+0.0,ZC+400)
add2('housing',half(housing12()),'#2b2f35','fixed',0.75); add2('plate',half(top_plate11()),'#4b525b','fixed',0.6)
add2('window',half(window()),'#dfe9f2','fixed',0.03,opacity=0.25,kind='glass')
fins=bx(BAR_X0,BAR_X0+4,BAR_Y0,BAR_Y1,ZC-BAR_W/2,ZC+BAR_W/2)
for k in range(9):
    w=-BAR_W/2+1+k*(BAR_W-2)/8; fins+=bx(BAR_X0+3,BAR_X1,BAR_Y0,BAR_Y1,ZC+w-0.9,ZC+w+0.9)
add2('bar',half(fins),'#b9bec6','fixed',0.35,0.8)
add2('stars',half(mf.Manifold.batch_boolean([mf.Manifold.cylinder(STAR2,8,8,48).rotate([0,-90,0]).translate([BAR_X0,PY3,ZC+w]) for w in OPTIC_W],mf.OpType.Add)),'#d9a441','fixed',0.4,0.6)
add2('stops',stop6_lower()+stop6_upper(),'#e8262d','fixed',0.5)
add2('frame',half(H6(lens_frame7())),'#1b1d21','frame',0.55)
add2('lens',half(H6(lenses6())),'#c9d2dc','frame',0.05,0.4,emissive='#fff1b8')
axis=lambda: mf.Manifold.cylinder(160,0.7,0.7,24).rotate([0,-90,0]).translate([PX6+LF_U-0.6,PY6,ZC-0.1])
add2('aim',axis(),'#ffd400','frame',0.4,emissive='#ffd400')                      # where the beam points
add2('level_ref',axis(),'#7f8b99','fixed',0.5)                                   # level, for comparison
add2('pivot',mf.Manifold.cylinder(3,1.2,1.2,24).translate([PX6,PY6,ZC-1.5]),'#ff5a5f','fixed',0.5,emissive='#ff5a5f')
def tilt(a): return T(PX6,PY6,0)@Rz(a)@T(-PX6,-PY6,0)
def mats(**kw): return {k:(np.asarray(v).T.flatten().round(4).tolist()) for k,v in kw.items()}
C=np.array([-60.0,0.0,ZC])
frames=[]
for a,cap in ((-12.0,'Lenses tilted 12 deg up: the stop (red) holds them here; the firmware uses up to 10'),
              (0.0,'Level. The lenses tilt about the LED chips (red dot): only the lenses move, the LEDs stay put'),
              (12.0,'Lenses tilted 12 deg down, the other stop. The yellow line is where the beam points, grey is level')):   # + tips the front down
    frames.append(dict(cap=cap,m=mats(frame=tilt(a),fixed=np.eye(4)),hide=[],cam=list(C+[-10,25,190]),tgt=list(C+[0,0,0])))
open('anim/swing_data.js','w').write('window.DATA='+json.dumps(dict(meshes=meshes,frames=frames))+';')
print('swing frames',len(frames))
