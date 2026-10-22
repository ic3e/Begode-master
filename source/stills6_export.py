# Lamp v6.2 on the Master: exterior stills (renderer: anim/stills6.html). The wheel is the dressed render model
# (render_wheel.py) over the measured outline; the clearances in the captions are measured on this scene.
import numpy as np, trimesh, json, base64
exec(open('build25.py').read()); exec(open('render_wheel.py').read())
def T(x=0,y=0,z=0): M=np.eye(4); M[:3,3]=[x,y,z]; return M
def Rz(d): c,s=np.cos(np.radians(d)),np.sin(np.radians(d)); M=np.eye(4); M[:2,:2]=[[c,-s],[s,c]]; return M
def Rx(d): c,s=np.cos(np.radians(d)),np.sin(np.radians(d)); M=np.eye(4); M[1:3,1:3]=[[c,-s],[s,c]]; return M
def b64(a,dt): return base64.b64encode(np.ascontiguousarray(a,dtype=dt).tobytes()).decode()
meshes=[]; allW=[]
def add(name,m,color,group,rough=0.6,metal=0.0,emissive=None,opacity=1.0,smooth=True,kind='std'):
    t=m if isinstance(m,trimesh.Trimesh) else to_tm(m)
    if group=='body': allW.append(t.vertices)
    if smooth: t=trimesh.graph.smooth_shade(t,angle=np.radians(35))
    meshes.append(dict(name=name,group=group,color=color,rough=rough,metal=metal,emissive=emissive,opacity=opacity,kind=kind,
        pos=b64(t.vertices,np.float32),nrm=b64(t.vertex_normals,np.float32),idx=b64(t.faces,np.uint32)))
for n,m,c,r,mt in wheel_parts()+body_parts():
    near=n.endswith('1') and not n.endswith('-1')           # the +w side: cut away in the fallen-forward view
    add(('wheelR_' if near else 'wheel_')+n,m,c,'body',r,mt)
add('wheel_cover',cover3(),'#1c1e22','body',0.8)
add('wheel_plate',M2.plate(),'#9ea3a9','body',0.4,0.7)
add('wheel_block',M2.box_ctrl(),'#1b1c1e','body',0.7)   # the black controller block: the handle's three bolts go into its sides
BLACK='#1c1e22'
add('handle',handle15(1),BLACK,'body',0.7); add('cap',trimesh.load(U+'euc_master_front_handle_p2.stl'),BLACK,'body',0.7)
add('usb',usb_receptacle(),'#b8bdc4','body',0.3,0.9)
add('housing',housing11(),'#16181b','body',0.75); add('lid',lid10(),'#16181b','body',0.75)
add('plate',top_plate11(),'#16181b','body',0.75)
add('buttons',buttons8(),'#c9ced6','body',0.3,0.9)
add('servo',servo6(),'#2f6fd6','body',0.4)
fins=bx(BAR_X0,BAR_X0+4,BAR_Y0,BAR_Y1,ZC-BAR_W/2,ZC+BAR_W/2)
for k in range(9):
    w=-BAR_W/2+1+k*(BAR_W-2)/8; fins+=bx(BAR_X0+3,BAR_X1,BAR_Y0,BAR_Y1,ZC+w-0.9,ZC+w+0.9)
add('bar',fins,'#b9bec6','body',0.35,0.8)
add('drl',drl_prism(1,x0=HOUSE_X0+0.4,x1=HOUSE_X0+FACE)+drl_prism(-1,x0=HOUSE_X0+0.4,x1=HOUSE_X0+FACE),'#ffffff','body',0.3,emissive='#eef4ff')
add('window',window(),'#dfe9f2','body',0.03,0.0,opacity=0.16,smooth=False,kind='glass')
# the tilting part, in its own frame about the pivot (the LED chips)
add('frame',lens_frame7(),'#1b1d21','head',0.55)
add('lens',lenses6(),'#c9d2dc','head',0.05,0.4,emissive='#fff1b8')
L=2200.0; LX=to_tm(lenses6()).bounds[0][0]
for k,(w,a) in enumerate(zip(OPTIC_W,(14,4.5,14))):
    beam=mf.Manifold.cylinder(L,7.5,7.5+L*np.tan(np.radians(a)),64).rotate([0,-90,0]).translate([LX,0,w])
    add(f'beam{k}',beam,'#fff3c4','head',emissive='#fff3c4',opacity=0.075 if a>10 else 0.11,smooth=False,kind='beam')
add('ground',box(-3500,1500,-6,0,-1500,1500),'#c4c9d0','ground',0.95)
W=np.vstack(allW)
Lv=np.vstack([to_tm(m).vertices for m in (housing11(),window(),lid10())])
def head_mat(B,a): return B@T(PX6,PY6,ZC)@Rz(a)
def on_ground(B): # lift so the lowest point of the wheel touches y=0 (the ground)
    y=(np.c_[W,np.ones(len(W))]@B.T)[:,1].min(); return T(0,-y,0)@B
stand=on_ground(np.eye(4))
front=on_ground(Rz(90))            # fallen forward, face down
side=on_ground(Rx(90))             # fallen onto the right side
def lamp_low(B): return (np.c_[Lv,np.ones(len(Lv))]@B.T)[:,:3]
def view(cap,B,cam,tgt,night=False,a=2.0,beams=False,cut=False):
    return dict(cap=cap,cut=cut,m={'body':np.asarray(B).T.flatten().round(4).tolist(),'head':head_mat(B,a).T.flatten().round(4).tolist(),'ground':np.eye(4).flatten().tolist()},
                cam=list(cam),tgt=list(tgt),night=night,beams=beams,mark=cut)
P=lambda B,p: (B@np.r_[p,1])[:3]
lampS=P(stand,[-62,0,ZC])
whole=P(stand,[110,-280,ZC])
Lf=lamp_low(front); lp=Lf[Lf[:,1].argmin()]
Ls=lamp_low(side); ls=Ls[:,1].min()
add('gapmark',mf.Manifold.cylinder(lp[1],1.6,1.6,16).rotate([-90,0,0]).translate([lp[0],0,lp[2]]),'#e8262d','ground',0.4,emissive='#e8262d',smooth=False,kind='mark')
print('lamp lowest point: fallen forward %.1f mm, fallen on its side %.1f mm above the ground'%(lp[1],ls))
views=[view('Lamp v6.2 on the Master',stand,whole+np.array([-1500,560,1150]),whole+np.array([-40,30,0])),
       view('Flush in the stock opening, behind a clear window; + and - under the chin',stand,lampS+np.array([-420,170,330]),lampS+np.array([0,-50,0])),
       view('Night: three LEDs, levelled; running lights through their slots',stand,lampS+np.array([-520,120,-300]),lampS+np.array([-60,-50,0]),night=True,beams=True),
       view('Face: three optics behind the window, running-light slots, chin air intake and buttons',stand,lampS+np.array([-330,25,0]),lampS+np.array([0,-20,0])),
       view('Fallen forward (near side cut away): handle and shells take the ground, the lamp stays %.0f mm clear'%lp[1],front,np.array([lp[0]+40,70,lp[2]+560]),np.array([lp[0]+40,30,lp[2]]),cut=True),
       view('USB-C flush in the handle\'s leg: no bump, a silicone plug closes it',stand,P(stand,[USB_C[0],USB_C[1],ZC+USB_FACE])+np.array([-160,90,260]),P(stand,[USB_C[0],USB_C[1],ZC+USB_FACE])),
       view('Fallen onto its side: pad and pedal take it, the lamp stays %.0f mm clear'%ls,side,P(side,[-60,-120,ZC])+np.array([-900,350,200]),P(side,[-60,-120,ZC])+np.array([0,-30,0]))]
open('anim/stills6_data.js','w').write('window.DATA='+json.dumps(dict(meshes=meshes,frames=views))+';')
print('views',len(views),'meshes',len(meshes))
