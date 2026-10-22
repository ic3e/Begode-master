# Lamp v5.2 mechanism stills: how the head tilts and how it is fitted (renderer: anim/mech.html).
import numpy as np, trimesh, json, base64
exec(open('build19.py').read())
def T(x=0,y=0,z=0): M=np.eye(4); M[:3,3]=[x,y,z]; return M
def Rz(d): c,s=np.cos(np.radians(d)),np.sin(np.radians(d)); M=np.eye(4); M[:2,:2]=[[c,-s],[s,c]]; return M
def b64(a,dt): return base64.b64encode(np.ascontiguousarray(a,dtype=dt).tobytes()).decode()
meshes=[]
def add(name,m,color,group,rough=0.6,metal=0.0,emissive=None,opacity=1.0,kind='std'):
    t=trimesh.graph.smooth_shade(to_tm(m) if not isinstance(m,trimesh.Trimesh) else m,angle=np.radians(35))
    meshes.append(dict(name=name,group=group,color=color,rough=rough,metal=metal,emissive=emissive,opacity=opacity,kind=kind,
        pos=b64(t.vertices,np.float32),nrm=b64(t.vertex_normals,np.float32),idx=b64(t.faces,np.uint32)))
hs=housing6()
cut=hs-bx(-200,200,PY3+0.0,100,-300,300)-bx(-200,HOUSE_X0+FACE+0.01,-100,100,-300,300)   # top and face cut away
add('housing',hs,'#2b2f35','housing',0.75)
add('housing_cut',cut,'#2b2f35','housing',0.75)
add('plate',top_plate6(),'#4b525b','plate',0.6)
add('lid',lid3(),'#2b2f35','housing',0.75)
add('head',H3(head3()),'#1b1d21','head',0.55)
add('heatsink',H3(box(HU1_3-HS3_D,HU1_3,-HS3_H/2,HS3_H/2,-HS3_W/2,HS3_W/2)),'#b9bec6','head',0.35,0.8)
add('lens',H3(mf.Manifold.batch_boolean([cu(TIR2_D/2-0.5,HU0_3-0.5,HU0_3+1.6,w=w) for w in OPTIC_W],mf.OpType.Add)),'#c9d2dc','head',0.05,0.4,emissive='#fff1b8')
add('horn',H3(horn6()),'#f2f2f0','horn',0.5)
add('servo',H3(servo3()),'#2f6fd6','servo',0.4)
add('ground',box(-600,400,-62,-56,-500,400),'#c4c9d0','ground',0.95)
I=np.eye(4)
def tilt(a,B=I): return B@T(PX3,PY3,0)@Rz(a)@T(-PX3,-PY3,0)
def mats(**kw): return {k:(np.asarray(v).T.flatten().round(4).tolist()) for k,v in kw.items()}
C=np.array([-40.0,0.0,ZC])
views=[
 dict(cap='1  On the bench: screw the horn to the head, press the servo onto the horn',
      m=mats(head=I,horn=T(0,0,14),servo=T(0,0,34),housing=T(0,-900,0),plate=T(0,-900,0),ground=I),
      hide=['housing','housing_cut','plate','lid'],cam=list(C+[-170,190,230]),tgt=list(C+[0,0,22])),
 dict(cap='2  Lower head + servo in from above, then the top plate locks them',
      m=mats(head=T(0,70,0),horn=T(0,70,0),servo=T(0,70,0),housing=I,plate=T(0,118,0),ground=I),
      hide=['housing_cut'],cam=list(C+[-300,250,330]),tgt=list(C+[0,48,0])),
 dict(cap='3  Pin in the left bearing, servo shaft on the right: the servo turns the head directly, ±10°',
      m=mats(head=tilt(8),horn=tilt(8),servo=I,housing=I,plate=I,ground=I),
      hide=['housing','plate'],cam=list(C+[-230,190,190]),tgt=list(C+[0,0,4])),
 dict(cap='4  The left side: the hollow pin turns in a 4 mm bearing, the LED wires come out through it',
      m=mats(head=tilt(-8),horn=tilt(-8),servo=I,housing=I,plate=I,ground=I),
      hide=['housing','plate'],cam=list(C+[-170,170,-230]),tgt=list(C+[0,0,-20])),
]
open('anim/mech_data.js','w').write('window.DATA='+json.dumps(dict(meshes=meshes,frames=views))+';')
print('views',len(views))
