# The boards in the lamp, where boards_pack.py placed them, with the main wire bundles through their holes:
# renderer anim/boards.html (PAGE=boards.html OUTD=boards node anim/stills_render.mjs). Housing see-through.
import numpy as np, trimesh, json, base64
exec(open('build27.py').read())
def b64(a,dt): return base64.b64encode(np.ascontiguousarray(a,dtype=dt).tobytes()).decode()
meshes=[]
def add(name,m,color,group,rough=0.6,metal=0.0,emissive=None,opacity=1.0,kind='std'):
    t=m if isinstance(m,trimesh.Trimesh) else to_tm(m)
    t=trimesh.graph.smooth_shade(t,angle=np.radians(30))
    meshes.append(dict(name=name,group=group,color=color,rough=rough,metal=metal,emissive=emissive,opacity=opacity,kind=kind,
        pos=b64(t.vertices,np.float32),nrm=b64(t.vertex_normals,np.float32),idx=b64(t.faces,np.uint32)))
add('housing',housing12(),'#7f93a8','ghost',0.5,opacity=0.24,kind='glass')
add('servo',servo6(),'#2f6fd6','parts',0.4); add('bearing',H6(bearing7()),'#c8ccd2','parts',0.25,0.9)
add('bar',led_bar(),'#b9bec6','parts',0.35,0.8); add('frame',H6(lens_frame7()+lenses6()),'#3a3f46','parts',0.6)
add('buttons',buttons8(),'#c9ced6','parts',0.3,0.9)
COL={'LDD':'#f0a04b','MP1584':'#e8c547','INA219':'#5b8def','MOSFET':'#9aa5b1','ESP32':'#3fb07a','MPU':'#b07fe0'}
placed=json.load(open('anim/boards_placed.json')); labels=[]; at={}
for name,r,p0,d in placed:
    p0=np.array(p0); d=np.array(d); key=[k for k in COL if name.startswith(k)][0]
    b=box(p0[0],p0[0]+d[0],p0[1],p0[1]+d[1],p0[2],p0[2]+d[2])
    add('b_'+name,b,COL[key],'boards',0.55,0.1)
    c=p0+d/2; at[name]=c; labels.append([name,float(c[0]),float(c[1]),float(c[2])])
def tube(pts,r=0.9,seg=12):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float); b=np.array(b,float)
        out.append(hull(mf.Manifold.sphere(r,seg).translate(a.tolist()),mf.Manifold.sphere(r,seg).translate(b.tolist())))
    return mf.Manifold.batch_boolean(out,mf.OpType.Add)
W=lambda x,y,w: (x,y,ZC+w)
SL=W(-37,-19,WIRE_SLOTS[0][1]); SR=W(-37,-19,WIRE_SLOTS[1][1])
routes=[   # (name, colour, radius, waypoints)
 ('LEDs + NTC: bar -> lens bay -> left pivot pocket -> left bay','#9467bd',1.3,[W(-38,3,-20),W(-44,-6,-30),W(-40,-10.3,-34),W(-40,-10.3,-44),W(-44,-6,-51)]),
 ('left bay -> box','#ff7f0e',1.1,[W(-40,-4,-52),W(-37,-12,-46),W(-37,-17,-43.85),SL,W(-37,-24,-43.6),W(-42,-32,-40)]),
 ('MPU -> box','#1f77b4',0.7,[W(-30,17,-50),W(-30,0,-45),W(-36,-14,-44),SL,W(-41,-30,-30),W(-41.8,-38,-10)]),
 ('box -> right bay','#2ca02c',1.1,[W(-41,-30,-5),W(-37,-27,30),W(-37,-22,41.6),SR,W(-37,-14,44),W(-40,-12,50)]),
 ('power in: back-wall grommet -> left bay -> box (INA219)','#d62728',1.4,[W(-12,-11.5,-56),W(-20,-11.5,-56),W(-30,-13,-48),W(-33,-17,-44),W(-33,-24,-43.6),W(-42,-30,-35)]),
 ('USB out: right bay -> floor grommet -> handle','#17becf',1.1,[W(-45,-14,55),W(-25,-15,60),W(-16.8,-17,62.8),W(-16.8,-26,62.8)]),
 ('servo','#2f6fd6',0.8,[W(-40,-1,50),W(-36,-12,46)]),
]
for nm,c,r,pts in routes: add('w_'+nm,tube(pts,r),c,'wires',0.5)
add('ground',box(-120,60,-75,-72,ZC-150,ZC+150),'#c4c9d0','ground',0.95)
I=np.eye(4).T.flatten().tolist(); Z=np.zeros(16).tolist()
def view(cap,cam,tgt,names,ground=True):
    m={g:I for g in ('ghost','parts','boards','wires')}; m['ground']=I if ground else Z
    lab=[l for l in labels if any(l[0].startswith(n) for n in names)]
    return dict(cap=cap,cut=False,m=m,cam=list(cam),tgt=list(tgt),night=False,beams=False,mark=False,labels=lab)
L=('LDD','MP1584 #1','MPU'); R=('MP1584 #2','MOSFET'); B=('INA219','ESP32')
tl=np.array([-40.0,0.0,ZC-52]); tr=np.array([-40.0,0.0,ZC+52]); tb=np.array([-40.0,-38.0,ZC-15])
views=[view('Left side bay: three LED drivers, buck #1, the MPU-6050 flat on top; their wires drop through the floor slot',tl+[-120,95,-150],tl,L),
       view('Right side bay: buck #2 and the USB MOSFET under the servo, the DRL MOSFET above it',tr+[-120,95,150],tr,R),
       view('Electronics box, seen from below with the lid off: INA219 and ESP32 on edge against the divider, USB-C down',tb+[-60,-170,-90],tb,B,ground=False),
       view('All of it, from above and behind',np.array([-38,-10,ZC])+[230,210,0],np.array([-38,-12,ZC]),L+R+B)]
open('anim/boards_data.js','w').write('window.DATA='+json.dumps(dict(meshes=meshes,frames=views))+';')
print('views',len(views),'meshes',len(meshes))
