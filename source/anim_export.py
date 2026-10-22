# Exports the v8 lamp + can holder scene and a 26 s timeline (30 fps) for the three.js renderer.
import numpy as np, trimesh, json, base64
exec(open('build16.py').read())
FPS=30; AIM_W=2.0
def T(x=0,y=0,z=0): M=np.eye(4); M[:3,3]=[x,y,z]; return M
def Rz(d): c,s=np.cos(np.radians(d)),np.sin(np.radians(d)); M=np.eye(4); M[:2,:2]=[[c,-s],[s,c]]; return M
def Rx(d): c,s=np.cos(np.radians(d)),np.sin(np.radians(d)); M=np.eye(4); M[1:3,1:3]=[[c,-s],[s,c]]; return M
CONTACT=np.array([M2.TC[0],M2.GROUND])
def wheel_mat(phi,lean):
    P=T(*CONTACT,0)@Rz(phi)@T(-CONTACT[0],-CONTACT[1],0)
    L=T(0,M2.GROUND,ZC)@Rx(lean)@T(0,-M2.GROUND,-ZC)
    return L@P
def b64(a,dt): return base64.b64encode(np.ascontiguousarray(a,dtype=dt).tobytes()).decode()
meshes=[]
def add(name,m,color,group,rough=0.6,metal=0.0,emissive=None,opacity=1.0,smooth=True):
    t=m if isinstance(m,trimesh.Trimesh) else to_tm(m)
    if smooth: t=trimesh.graph.smooth_shade(t,angle=np.radians(35))
    t.fix_normals() if False else None
    meshes.append(dict(name=name,group=group,color=color,rough=rough,metal=metal,emissive=emissive,opacity=opacity,
        pos=b64(t.vertices,np.float32),nrm=b64(t.vertex_normals,np.float32),idx=b64(t.faces,np.uint32)))
# body (moves with the wheel)
for i,(m,c) in enumerate(model3()): add(f'wheel{i}',m,c,'body',0.75)
add('handle',trimesh.load('handle11.stl'),'#d9343d','body',0.45)
add('cap',trimesh.load(U+'euc_master_front_handle_p2.stl'),'#d9343d','body',0.45)
add('housing',housing(),'#2c3036','body',0.55)
add('tray',tray(),'#d9343d','body',0.45)
add('servo',H2(servo2()),'#2f6fd6','body',0.4)
add('drl',diffuser2(1)+diffuser2(-1),'#ffffff','body',0.3,emissive='#f4f8ff')
# head (tilts on the servo)
add('head',head2(),'#7a828e','head',0.45)
add('heatsink',box(HU1_2-HS2_D,HU1_2,-HS2/2,HS2/2,-HS2/2,HS2/2),'#c9ccd1','head',0.3,0.8)
add('lens',cu(TIR2_D/2-0.5,HU0_2-0.5,HU0_2+1.6),'#fff6c8','head',0.1,emissive='#fff1b0')
L=1600.0; a=np.radians(4.0)
beam=mf.Manifold.cylinder(L,7.5,7.5+L*np.tan(a),64).rotate([0,-90,0]).translate([HU0_2-0.5,0,0])
add('beam',beam,'#fff3c4','headbeam',emissive='#fff3c4',opacity=0.11,smooth=False)
# can holder
add('armR',arm_local(1),'#3b3f44','armR',0.5); add('armL',arm_local(-1),'#3b3f44','armL',0.5)
add('gimbal',gimbal_ring(),'#d9343d','gimbal',0.45)
add('ring',cup_ring(),'#2f3338','ring',0.5)
add('floor',floor_disc(),'#50575f','floor',0.5)
can=cylV(33,FLOOR_Y,FLOOR_Y+115,0,0)-cylV(29.5,FLOOR_Y+112,FLOOR_Y+116,0,0)
add('can',can,'#d7dbe0','can',0.3,0.55); add('canband',cylV(33.2,FLOOR_Y+40,FLOOR_Y+80,0,0),'#c81e1e','can',0.35,0.2)
cyl=mf.Manifold.cylinder(1,1,1,10).rotate([-90,0,0])      # unit cord along +Y
for k in range(3): add(f'cord{k}',cyl,'#e8a33a',f'cord{k}',0.8)
# world: ground and the beam's reference line
add('ground',box(-2600,900,M2.GROUND-5,M2.GROUND,-900,800),'#2a2d33','world',0.95)
p0=np.array([PX2+HU0_2,PY2])
ref=mf.Manifold.cylinder(1500,0.9,0.9,8).rotate([0,-90,0]).rotate([0,0,AIM_W]).translate([p0[0],p0[1],ZC])
add('ref',ref,'#7fd3ff','ref',emissive='#7fd3ff',opacity=0.75,smooth=False)

# ---- timeline ----
def ease(u): u=np.clip(u,0,1); return u*u*(3-2*u)
def seg(t,keys):   # piecewise eased interpolation over (time,value) keys
    for (t0,v0),(t1,v1) in zip(keys,keys[1:]):
        if t0<=t<=t1: return v0+(v1-v0)*ease((t-t0)/(t1-t0))
    return keys[-1][1] if t>keys[-1][0] else keys[0][1]
UP=-R_H/2+2.4+0.5-FLOOR_Y
def state(t):
    phi=seg(t,[(0,0),(1.5,0),(3.2,8),(4.6,8),(6.0,-6),(7.0,-6),(7.4,0)])
    if 7.4<t<8.8: phi=6*np.sin((t-7.4)*2*np.pi*1.6)*np.exp(-(t-7.4)*1.6)
    phi+=seg(t,[(13.8,0),(15.0,10),(16.0,10),(17.0,-8),(17.6,-8),(18.3,0)])
    lean=seg(t,[(18.6,0),(19.8,12),(21.2,12),(22.2,0)])
    th=seg(t,[(10.6,TH_IN),(12.4,TH_OUT),(24.0,TH_OUT),(25.4,TH_IN)])
    can_off=seg(t,[(12.6,190),(13.6,0),(22.4,0),(23.2,190)])
    floor_off=min(UP,can_off) if t<23.0 else seg(t,[(23.2,0),(23.8,UP)])
    can_on=12.5<t<23.25
    caption=('Self-levelling headlamp' if t<1.5 else 'Wheel tips nose-down: the head tilts back, the beam stays put' if t<4.8 else
             'Nose-up: same again' if t<7.2 else 'Bumps: the gyro reacts at once' if t<9.0 else 'Can holder, swung in under the lamp' if t<10.6 else
             'Swing it out' if t<12.5 else 'Drop a can in: the floor slides down on its cords' if t<13.8 else
             'Braking and tilting: the can hangs upright' if t<18.4 else 'On the kickstand, leaning 12°: still upright' if t<22.3 else
             'Can out, floor up, swing it back in' if t<25.4 else 'Begode Master · v8')
    return dict(phi=phi,lean=lean,th=th,can_off=can_off,floor_off=floor_off,can_on=can_on,caption=caption)
def cam(t,B):
    side=dict(pos=(-200,10,ZC+1300),tgt=(-200,-90,ZC)); wide=dict(pos=(-200,0,ZC+1900),tgt=(-200,-260,ZC))
    q34=dict(pos=(-560,30,ZC+430),tgt=(-115,-85,ZC)); front=dict(pos=(-760,-30,ZC),tgt=(-115,-95,ZC))
    keys=[(0,wide),(1.5,side),(9.0,side),(10.4,q34),(18.4,q34),(19.2,front),(22.3,front),(23.0,q34),(26,q34)]
    for (t0,a),(t1,b) in zip(keys,keys[1:]):
        if t0<=t<=t1:
            u=ease((t-t0)/(t1-t0)); pos=np.array(a['pos'])*(1-u)+np.array(b['pos'])*u; tgt=np.array(a['tgt'])*(1-u)+np.array(b['tgt'])*u; break
    else: pos=np.array(keys[-1][1]['pos']); tgt=np.array(keys[-1][1]['tgt'])
    if t>18.4:   # follow the lean so the holder stays in frame
        tw=(B@np.r_[tgt,1])[:3]; pos=pos+(tw-tgt); tgt=tw
    return pos.tolist(),tgt.tolist()
def colmaj(M): return [round(float(v),4) for v in M.T.flatten()]
frames=[]
N=int(26*FPS)
for i in range(N):
    t=i/FPS; s=state(t); B=wheel_mat(s['phi'],s['lean'])
    a_rel=float(np.clip(AIM_W-s['phi'],-TILT2,TILT2))
    Hm=B@T(PX2,PY2,0)@Rz(a_rel)@T(-PX2,-PY2,0)
    out=s['th']<TH_IN-1
    pitch=s['phi'] if out else 0.0; roll=-s['lean'] if out else 0.0
    g=gpos(s['th'])
    G=B@T(g[0],g[1],0)@Rz(-pitch)
    Rg=G@T(0,0,ZC)@Rx(roll)@T(0,0,-ZC)
    Fm=Rg@T(0,s['floor_off']-UP,0) if False else Rg@T(0,s['floor_off'],0)
    mats={'body':B,'head':Hm,'headbeam':Hm@T(PX2,PY2,ZC),'armR':B@T(HP[0],HP[1],0)@Rz(s['th']),'armL':B@T(HP[0],HP[1],0)@Rz(s['th']),
          'gimbal':G,'ring':Rg,'floor':Fm,'can':Rg@T(0,s['can_off'],0),'world':np.eye(4)}
    # head parts are modelled in head-local coords (H2 offsets): place them
    mats['head']=Hm@T(PX2,PY2,ZC)
    vis={'can':bool(s['can_on']),'ref':bool(t<9.3)}
    for k,a_ in enumerate((90,210,330)):
        c_,s_=np.cos(np.radians(a_)),np.sin(np.radians(a_))
        p=np.array([c_*35.1,R_H/2-3.5,ZC+s_*35.1]); q=np.array([c_*31.0,FLOOR_Y-1.2+s['floor_off'],ZC+s_*31.0])
        d=q-p; Ln=np.linalg.norm(d); y=d/Ln; x=np.cross(y,[0,0,1.0]); x/=np.linalg.norm(x); z=np.cross(x,y)
        S=np.eye(4); S[:3,0]=x*0.9; S[:3,1]=y*Ln; S[:3,2]=z*0.9; S[:3,3]=p
        mats[f'cord{k}']=Rg@S; vis[f'cord{k}']=bool(s['floor_off']<UP-8 and out)
    pos,tgt=cam(t,B)
    pip=None
    if 1.6<t<9.0:
        ptg=(B@np.array([PX2-8,PY2-2,ZC,1]))[:3]; pip=dict(cam=(ptg+np.array([0,0,185])).tolist(),tgt=ptg.tolist(),
            a=round(float(min(1,(t-1.6)/0.4,(9.0-t)/0.4)),3),txt=f'cutaway · wheel tipped {s["phi"]:+.1f}°, head turned {-(a_rel-AIM_W):+.1f}° the other way')
    frames.append(dict(m={k:colmaj(v) for k,v in mats.items()},vis=vis,cap=s['caption'],cam=pos,tgt=tgt,pip=pip,beam=round(float(0.11 if t<9.2 else 0.045),3)))
open('anim/data.js','w').write('window.DATA='+json.dumps(dict(meshes=meshes,frames=frames))+';')
print('frames',N,'meshes',len(meshes))
