# Lamp v6.2 stills: how it's built and how the air, water and sand go through it (renderer: anim/mech6.html).
import numpy as np, trimesh, json, base64
exec(open('build24.py').read())
def T(x=0,y=0,z=0): M=np.eye(4); M[:3,3]=[x,y,z]; return M
def Rz(d): c,s=np.cos(np.radians(d)),np.sin(np.radians(d)); M=np.eye(4); M[:2,:2]=[[c,-s],[s,c]]; return M
def b64(a,dt): return base64.b64encode(np.ascontiguousarray(a,dtype=dt).tobytes()).decode()
meshes=[]
def add(name,m,color,group,rough=0.6,metal=0.0,emissive=None,opacity=1.0,kind='std'):
    t=trimesh.graph.smooth_shade(to_tm(m) if not isinstance(m,trimesh.Trimesh) else m,angle=np.radians(35))
    meshes.append(dict(name=name,group=group,color=color,rough=rough,metal=metal,emissive=emissive,opacity=opacity,kind=kind,
        pos=b64(t.vertices,np.float32),nrm=b64(t.vertex_normals,np.float32),idx=b64(t.faces,np.uint32)))
hs=housing11(); pl=top_plate11(); ld=lid10(); gk=lid_tape()
CUTW=8.0                                              # section: everything on the near side of w = 8 taken away
half=lambda m: m-bx(-300,300,-300,300,ZC+CUTW,ZC+400)
add('housing',hs,'#2b2f35','housing',0.75); add('housing_cut',half(hs),'#2b2f35','housing',0.75)
add('plate',pl,'#4b525b','plate',0.6); add('plate_cut',half(pl),'#4b525b','plate',0.6)
add('lid',ld,'#2b2f35','lid',0.75); add('lid_cut',half(ld),'#2b2f35','lid',0.75)
add('gasket',gk,'#c0392b','lid',0.8); add('gasket_cut',half(gk),'#c0392b','lid',0.8)
add('window',window(),'#dfe9f2','housing',0.03,opacity=0.18,kind='glass')
add('frame',H6(lens_frame7()),'#1b1d21','frame',0.55); add('frame_cut',half(tilt6(H6(lens_frame7()),6)).translate([0,0,0]),'#1b1d21','fixed',0.55)
add('lenses',H6(lenses6()),'#c9d2dc','frame',0.05,0.4,emissive='#fff1b8')
add('horn',H6(cw(3.6,HW3+BOSS3-2.0,HW3+BOSS3,seg=32)+cw(2.2,HW3+BOSS3-2.0,HW3+BOSS3,u=HORN_UV[0]*1.1,v=HORN_UV[1]*1.1,seg=32)).translate([0,0,0]),'#f2f2f0','frame',0.5)
add('bearing',H6(bearing7()),'#c8ccd2','frame',0.25,0.9)
add('servo',servo6(),'#2f6fd6','servo',0.4)
fins=bx(BAR_X0,BAR_X0+4,BAR_Y0,BAR_Y1,ZC-BAR_W/2,ZC+BAR_W/2)
for k in range(9):
    w=-BAR_W/2+1+k*(BAR_W-2)/8; fins+=bx(BAR_X0+3,BAR_X1,BAR_Y0,BAR_Y1,ZC+w-0.9,ZC+w+0.9)
add('bar',fins,'#b9bec6','bar',0.35,0.8); add('bar_cut',half(fins),'#b9bec6','bar',0.35,0.8)
add('stars',mf.Manifold.batch_boolean([mf.Manifold.cylinder(STAR2,8,8,48).rotate([0,-90,0]).translate([BAR_X0,PY3,ZC+w]) for w in OPTIC_W],mf.OpType.Add),'#d9a441','bar',0.4,0.6)
add('buttons',buttons8(),'#c9ced6','housing',0.3,0.9)
# the flow: blue = air (and whatever water and sand it carries), down arrows = drains
def arrow(p0,p1,r=1.6,col='#1e90ff',name='flow'):
    p0=np.array(p0,float); p1=np.array(p1,float); d=p1-p0; L=np.linalg.norm(d); u=d/L
    shaft=mf.Manifold.cylinder(L-5,r,r,24); head=mf.Manifold.cylinder(5,r*2.4,0,24).translate([0,0,L-5])
    a=shaft+head
    z=np.array([0,0,1.0]); ax=np.cross(z,u); s=np.linalg.norm(ax); c=np.dot(z,u)
    if s<1e-9: R=np.eye(3) if c>0 else np.diag([1,-1,-1])
    else:
        ax/=s; K=np.array([[0,-ax[2],ax[1]],[ax[2],0,-ax[0]],[-ax[1],ax[0],0]]); R=np.eye(3)+s*K+(1-c)*K@K
    M=np.eye(4); M[:3,:3]=R; M[:3,3]=p0
    return a.transform(M[:3,:])
W0=ZC+0.0
path=[(-90,-38,W0+20),(-62,-38,W0+20),(-56,-28,W0+20),(-52,-18,W0+20),(-38,-18,W0+20),(-35,-6,W0+20),(-28,10,W0+20),(-20,4,W0+20),(-20,-20,W0+20),(-20,-40,W0+20)]
fl=mf.Manifold.batch_boolean([arrow(a,b) for a,b in zip(path,path[1:])],mf.OpType.Add)
add('flow',fl,'#1e90ff','flow',0.4,emissive='#1e90ff')
dr=mf.Manifold.batch_boolean([arrow((x,-46,W0+20),(x,-64,W0+20),1.2) for x in (-62,-55)],mf.OpType.Add)
add('drain',dr,'#2ecc71','flow',0.4,emissive='#2ecc71')
add('ground',box(-600,400,-72,-66,-500,400),'#c4c9d0','ground',0.95)
I=np.eye(4)
def tilt(a): return T(PX6,PY6,0)@Rz(a)@T(-PX6,-PY6,0)
def mats(**kw): return {k:(np.asarray(v).T.flatten().round(4).tolist()) for k,v in kw.items()}
C=np.array([-40.0,-10.0,ZC])
ALL=['frame_cut','bar_cut','housing','housing_cut','plate','plate_cut','lid','lid_cut','gasket','gasket_cut','window','frame','lenses','horn','bearing','servo','bar','stars','buttons','flow','drain']
def hide_except(*keep): return [n for n in ALL if n not in keep]
views=[
 dict(cap='1  The LEDs stay put on the heat sink; only the light lens frame tilts, about the LED chips',
      m=mats(frame=T(-30,10,0)@tilt(0),servo=T(-30,10,0),bar=T(25,10,0),housing=I,plate=I,lid=I,flow=I,ground=I),
      hide=hide_except('frame','lenses','horn','bearing','servo','bar','stars')+[],cam=list(C+[-170,170,250]),tgt=list(C+[-5,15,0])),
 dict(cap='2  Cut through: chin slots -> trap (drains below) -> passage -> fins -> out the back. The rest stays dry',
      m=mats(frame=tilt(6),servo=I,bar=I,housing=I,plate=I,lid=I,flow=I,ground=I,fixed=I),
      hide=['housing','plate','lid','gasket','servo','horn','window','frame','bar','stars','bearing'],cam=list(np.array([-42,-14,ZC])+[0,10,250]),tgt=list(np.array([-42,-14,ZC]))),
 dict(cap='3  Dry: lenses and the inside of the window, servo, bearing, electronics. Wet: only the duct and the aluminium fins',
      m=mats(frame=tilt(6),servo=I,bar=I,housing=I,plate=I,lid=I,flow=I,ground=I,fixed=I),
      hide=['housing','plate','lid','gasket','window','frame_cut','bar_cut','clamp_cut'],cam=list(np.array([-38,-5,ZC])+[-180,170,260]),tgt=list(np.array([-38,-8,ZC-10]))),
 dict(cap='4  Chin: + and - buttons in pockets, air slots either side, drains in the lid below',
      m=mats(frame=I,servo=I,bar=I,housing=I,plate=I,lid=I,flow=I,ground=I),
      hide=['housing_cut','plate_cut','lid_cut','gasket_cut','flow','drain','frame_cut','bar_cut','clamp_cut'],cam=list(np.array([-67.5,-36.0,ZC])+[-210,30,120]),tgt=list(np.array([-67.5,-36.0,ZC]))),
 dict(cap='5  Assembly: bar and lens frame + servo drop in from above; the top plate locks both (its fingers hold the bar)',
      m=mats(frame=T(0,65,0),servo=T(0,65,0),bar=T(0,95,0),housing=I,plate=T(0,135,0),lid=I,flow=I,ground=I),
      hide=['housing_cut','plate_cut','lid_cut','gasket_cut','flow','drain','frame_cut','bar_cut','clamp_cut'],cam=list(C+[-300,280,340]),tgt=list(C+[0,55,0])),
]
open('anim/mech6_data.js','w').write('window.DATA='+json.dumps(dict(meshes=meshes,frames=views))+';')
print('views',len(views))
