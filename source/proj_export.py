# Concept: a cut-off of our own, the way a car's projector low beam makes one. An LED, a blade whose straight edge
# runs across the middle of the LED's chip, and a glass aspheric lens with its focus on the chip: the lens throws
# the blade's edge onto the road as a sharp line, and no light goes above it. Bench rig first (one LED, a printed
# jig, a snapped utility-knife blade for the edge, a focus sleeve to find the lens's sweet spot), then a lamp head.
# Renderer: anim/proj.html (data anim/proj_data.js). Not fitted to the stock opening, not checked: a picture.
import numpy as np, trimesh, json, base64, manifold3d as mf
def b64(a,dt): return base64.b64encode(np.ascontiguousarray(a,dtype=dt).tobytes()).decode()
def box(x0,x1,y0,y1,z0,z1): return mf.Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
def cx(r,x0,x1,y=0,z=0,seg=64,r1=None): return mf.Manifold.cylinder(x1-x0,r,r if r1 is None else r1,seg).rotate([0,90,0]).translate([x0,y,z])
def cy(r,y0,y1,x=0,z=0,seg=48): return mf.Manifold.cylinder(y1-y0,r,r,seg).rotate([-90,0,0]).translate([x,y0,z])
def hull(*m): return mf.Manifold.batch_hull(list(m))
def to_tm(m): g=m.to_mesh(); return trimesh.Trimesh(g.vert_properties[:,:3],g.tri_verts,process=True)
meshes=[]
def add(name,m,color,group,rough=0.6,metal=0.0,emissive=None,opacity=1.0,kind='std',smooth=35):
    t=m if isinstance(m,trimesh.Trimesh) else to_tm(m)
    t=trimesh.graph.smooth_shade(t,angle=np.radians(smooth))
    meshes.append(dict(name=name,group=group,color=color,rough=rough,metal=metal,emissive=emissive,opacity=opacity,kind=kind,
        pos=b64(t.vertices,np.float32),nrm=b64(t.vertex_normals,np.float32),idx=b64(t.faces,np.uint32)))
# the optical axis is -x; the LED's chip (the lens's focus) at the origin; +y up
F_BACK,F_CT,LR=10.5,8.0,10.0              # aspheric lens Ø20, f about 15: flat side to the LED 10.5 mm away, 8 mm thick
def lens():
    sag=F_CT-2.0; R=(LR**2+sag**2)/(2*sag); x_edge=-(F_BACK+2.0); apex=-(F_BACK+F_CT)
    cap=mf.Manifold.sphere(R,128).translate([apex+R,0,0])^box(apex-1,x_edge,-20,20,-20,20)
    return cx(LR,x_edge,-F_BACK,seg=96)+cap
def heatsink():
    m=box(2.4,6.4,-12.5,12.5,-12.5,12.5)
    for k in range(7): z=-12.0+k*4.0; m+=box(6.3,22.4,-12.5,12.5,z-0.6,z+0.6)
    return m
star=cx(8,0.8,2.4,seg=64); pkg=box(0.0,0.8,-1.75,1.75,-1.75,1.75); chip=box(-0.05,0.02,-0.7,0.7,-0.7,0.7)
dome=mf.Manifold.sphere(1.3,48).translate([0,0,0])^box(-2,0,-2,2,-2,2)
def blade(): # snapped utility-knife blade, 0.4 mm, its sharp straight edge across the chip's middle (y 0): it hides the
             # lower half of the chip, whose light the lens would send upwards
    pts=[(-9.0,0.0),(9.0,0.0),(9.0,-14.0),(-6.0,-18.0),(-9.0,-18.0)]
    cs=mf.CrossSection([[(z,y) for z,y in pts]]); return mf.Manifold.extrude(cs,0.4).rotate([0,-90,0]).translate([-0.5,0,0])
def jig():   # printed body: clamps the heat sink, holds the blade in a slot, carries the tube for the focus sleeve
    b=box(-3.0,7.0,-16.0,16.0,-16.0,16.0)-box(2.3,7.1,-12.6,12.6,-12.6,12.6)      # the heat sink's base in its socket
    b-=cx(9.0,-3.1,2.4)                                                          # the star's window
    b-=box(-0.95,-0.45,-24.0,0.6,-9.6,9.6)                                       # the blade's slot (it slides up to the chip)
    b+=cx(13.0,-26.0,-3.0)-cx(11.25,-26.1,-2.9)                                  # the tube
    b+=box(-20.0,6.0,-36.0,-16.0,-6.0,6.0)                                       # post
    b+=box(-34.0,24.0,-40.0,-36.0,-26.0,26.0)                                    # foot
    b-=cy(1.6,-37.0,-15.0,x=-0.7,z=0.0)                                          # the blade's height screw, up from below
    b-=box(-22.0,-8.0,10.0,14.0,-2.0,2.0)                                        # a slot on top: the sleeve's lock screw
    return b
def sleeve():   # slides in the tube to set the focus; the lens sits against its front lip
    s=cx(11.1,-22.0,-8.0)-cx(10.1,-22.1,-7.9)
    return s+(cx(11.1,-F_BACK-2.6,-F_BACK-2.0)-cx(9.4,-F_BACK-2.7,-F_BACK-1.9))   # the lip over the lens's edge
def screw(): return cy(1.5,-39.0,-18.0,x=-0.7)+cy(2.8,-42.0,-39.0,x=-0.7)   # pushes the blade's lower edge up
half=lambda m: m-box(-500,500,-500,500,0.0,500)                                  # cut away the +z half (the near side)
# full rig (wall scene) and the cut one (close-up)
for nm,fn,col,rough,metal in (('jig',jig,'#e8742c',0.55,0.0),('sleeve',sleeve,'#e8742c',0.55,0.0)):
    add(nm,fn(),col,'full',rough,metal); add(nm+'_cut',half(fn()),col,'cut',rough,metal)
add('heatsink',heatsink(),'#b9bec6','both',0.35,0.8)
add('star',star,'#d9a441','both',0.4,0.6); add('pkg',pkg,'#f2f2ee','both',0.4)
add('chip',chip,'#ffe9a8','both',0.3,emissive='#fff1b8'); add('dome',dome,'#e8eef2','both',0.05,opacity=0.5,kind='glass')
add('blade',blade(),'#c9ced6','both',0.25,0.9,smooth=5)
add('lens',lens(),'#cfe3f2','full',0.02,opacity=0.35,kind='glass',smooth=60); add('lens_cut',half(lens()),'#cfe3f2','cut',0.02,opacity=0.45,kind='glass',smooth=60)
add('screw',screw(),'#9aa0a6','both',0.35,0.8)
# the beam leaving the lens: every ray at or below level, so its top is flat (the lens's top edge going straight on)
L=320.0; x0=-(F_BACK+F_CT); spread=np.radians(4.0); dn=np.radians(5.0)
disk=cx(LR,x0-0.1,x0,seg=64)
far=box(x0-L,x0-L+0.1,-LR-L*np.tan(dn),LR,-(LR+L*np.tan(spread)),LR+L*np.tan(spread))
add('beam',hull(disk,far),'#ffe9a8','beamg',0.5,emissive='#ffe9a8',opacity=0.035,kind='beam',smooth=5)
add('axis',cx(0.25,x0-L,x0),'#ffd400','beamg',0.4,emissive='#ffd400')
# the lab: table, wall 3 m away with tape at the lens's height
TBL=-40.0; WALL=-3000.0
add('table',box(-30,600,TBL-30,TBL,-500,500),'#6b5a48','room',0.8)   # the rig at the table's edge, so the beam reaches the wall
add('wall',box(WALL-20,WALL,TBL-800,1400,-1600,1600),'#e6e3dc','room',0.95)
add('tape',box(WALL+0.5,WALL+2,-6.0,6.0,-1200,1200),'#1d6fe0','room',0.6)
add('floor',box(WALL-200,2500,TBL-800,TBL-790,-3000,3000),'#3b3f45','room',0.9)
I=np.eye(4).T.flatten().tolist(); Z=np.zeros(16).tolist()
def frame(cap,cam,tgt,show,night=False,beams=False,labels=(),spot=None):
    m={g:(I if g in show else Z) for g in ('full','cut','both','beamg','room')}
    return dict(cap=cap,m=m,cam=[float(v) for v in cam],tgt=[float(v) for v in tgt],night=night,beams=beams,labels=list(labels),spot=spot)
labels=[['LED, its chip at the lens\'s focus',-1,2.5,0],['blade: its edge across the chip\'s middle',-1,-15,-3],
        ['aspheric lens Ø20, f ≈ 15',-15,11.5,0],['focus sleeve',-15,-12.5,-7],['heat sink',15,13,0],
        ['blade height screw',-0.7,-41,0],['printed jig',-8,-30,-4],['every ray leaves level or lower: a flat top',-75,13,0]]
frames=[frame('Bench rig, cut open: the blade hides the lower half of the chip, the lens projects its edge as the cut-off',
              np.array([-110,45,175]),np.array([-25,-8,0]),('cut','both','beamg'),beams=True,labels=labels),
        frame('The rig as printed: LED and heat sink at the back, blade slot, focus sleeve with the lens',
              np.array([-150,90,170]),np.array([-8,-12,0]),('full','both')),
        frame('At night, 3 m from a wall: a sharp flat top, just under the blue tape at the lamp\'s height',
              np.array([430,170,120]),np.array([-3000,-380,-60]),('full','both','room'),night=True,
              spot=dict(pos=[x0-1.0,0,0],tgt=[WALL,-55.0,0],angle=10.0,intensity=1.2e8))]
open('anim/proj_data.js','w').write('window.DATA='+json.dumps(dict(meshes=meshes,frames=frames))+';')
print('meshes',len(meshes),'frames',len(frames))
