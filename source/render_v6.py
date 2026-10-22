import numpy as np, trimesh, manifold3d as mf, matplotlib, types, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
exec(open('build14.py').read())
_g={}; exec(open('master_model.py').read().split("\nif __name__=='__main__':")[0],_g); MM=types.SimpleNamespace(**_g)
O=OUT; AIM=-2.0
T=np.array([[-1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1.]])
light=np.array([0.45,-0.35,0.8]); light/=np.linalg.norm(light)
wheel=MM.model()
handle=trimesh.load('handle9.stl'); cap=trimesh.load(U+'euc_master_front_handle_p2.stl')
blocks=to_tm(servo_block2()+elec_block2()+lid2()); servo=to_tm(H(servo_model()[0])); diffs=to_tm(diffuser(1)+diffuser(-1))
floor=ring_tops(True)[3]-RING_H+LIP
def can():
    c=cylV(33,floor,floor+115,0,0)-cylV(29,floor+113,floor+116,0,0)
    return [(c,'#c0c4ca',False),(cylV(31,floor+108,floor+110,0,0),'#d01818',False)]
def coffee():
    body=mf.Manifold.cylinder(104,30,45,96).rotate([-90,0,0]).translate([0,floor,ZC])
    lid=mf.Manifold.cylinder(6,46,44,96).rotate([-90,0,0]).translate([0,floor+104,ZC])
    sleeve=mf.Manifold.cylinder(40,36.5,42.5,96).rotate([-90,0,0]).translate([0,floor+35,ZC])
    return [(body,'#f3efe6',False),(sleeve,'#8b5a2b',False),(lid,'#e8e8e8',False)]
def head_parts(a,night):
    hs=H(box(0,HS_D,-HS/2,HS/2,-HS/2,HS/2)); lens=H(cu(TIR_D/2-0.5,HU0-0.5,HU0+2.6))
    return [(to_tm(tilt(H(head()),a)),'#3b3f44',False),(to_tm(tilt(hs,a)),'#c9ccd1',False),(to_tm(tilt(lens,a)),'#fff3a0' if night else '#d9dde2',night)]
CONTACT=np.array([MM.TC[0],MM.GROUND])
def wheel_mat(phi,lean):   # pitch about the tyre contact point, then lean about the contact line
    c,s=np.cos(np.radians(phi)),np.sin(np.radians(phi)); P=np.eye(4); P[:2,:2]=[[c,-s],[s,c]]
    P[:2,3]=CONTACT-P[:2,:2]@CONTACT
    c,s=np.cos(np.radians(lean)),np.sin(np.radians(lean)); L=np.eye(4); L[1:3,1:3]=[[c,-s],[s,c]]
    p=np.array([MM.GROUND,ZC]); L[1:3,3]=p-L[1:3,1:3]@p
    return L@P
def holder(state,drink=None,pitch=0.0,roll=0.0,clip=True):
    xp=X_IN if state=='in' else X_OUT
    parts=[(to_tm(arm(1,xp)+arm(-1,xp)),'#3b3f44',False)]
    g=gimbal(state!='in')
    cols=['#e0303a','#2f3338','#3a3f45','#454b52','#50575f']
    for r,c in zip(place_gimbal(g,xp,pitch,roll),cols): parts.append((to_tm(r),c,False))
    if drink:
        for m,c,e in drink():
            if clip: m=m^bx(-200,200,R1_TOP-1,400,-500,500)   # only the part above the rim shows; avoids draw-order glitches
            parts.append((to_tm(place(m,xp,pitch,roll)),c,e))
    return parts
def scene(phi=0,lean=0,state='out',drink=None,night=False,clip=True):
    # the cup hangs level: relative to the wheel it swings by -phi... (+pitch = wheel nose-down) and -lean
    parts=[(m,c,False) for m,c in wheel]+[(handle,'#e0303a',False),(cap,'#e0303a',False),(blocks,'#3b3f44',False),(servo,'#2f6fd6',False),
          (diffs,'#ffffff',True)]+head_parts(AIM+phi,night)+holder(state,drink,phi if state=='out' else 0,-lean if state=='out' else 0,clip)
    Mx=wheel_mat(phi,lean); out=[]
    for m,c,em in parts:
        m=m.copy(); m.apply_transform(Mx); out.append((m,c,em))
    return out
def draw(ax,meshes,el,az,lim,zoom=1.0,title=''):
    tris=[];cols=[]
    for m,c,em in meshes:
        m=m.copy(); m.apply_transform(T); base=np.array(matplotlib.colors.to_rgb(c))
        sh=np.ones(len(m.faces)) if em else np.clip(np.abs(m.face_normals@light)*0.65+0.35,0,1)
        tris.append(m.triangles); cols.append(np.c_[base[None,:]*sh[:,None],np.ones(len(sh))])
    ax.add_collection3d(Poly3DCollection(np.vstack(tris),facecolors=np.vstack(cols),edgecolors='none'))
    (x0,x1),(y0,y1),(z0,z1)=lim
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_zlim(z0,z1); ax.set_box_aspect((x1-x0,y1-y0,z1-z0),zoom=zoom)
    ax.view_init(el,az); ax.set_axis_off(); ax.set_title(title,fontsize=24)
def around(phi,lean,half):   # plot limits centred on the cup holder, wherever the lean puts it
    p=wheel_mat(phi,lean)@np.array([X_OUT,YP-40,ZC,1]); q=T@p
    return tuple((q[i]-half[i],q[i]+half[i]) for i in range(3))
def save(fig,name): plt.tight_layout(); fig.savefig(O+name,dpi=80,facecolor='white'); plt.close(fig); print(name)

which=sys.argv[1:] or ['1','2','3','4']
if '1' in which:   # parked on the kickstand, whole wheel, from the front
    fig=plt.figure(figsize=(14,14),facecolor='white'); ax=fig.add_subplot(1,1,1,projection='3d')
    draw(ax,scene(0,12,'out',can,clip=False),4,0,((-260,260),(-400,240),(-700,140)),1.25,'Parked on the kickstand, leaning 12°: the can still hangs straight down')
    save(fig,'render_v6_kickstand_front.png')
if '2' in which:   # same, close-up
    fig=plt.figure(figsize=(14,14),facecolor='white'); ax=fig.add_subplot(1,1,1,projection='3d')
    draw(ax,scene(0,12,'out',coffee),4,0,around(0,12,(150,130,130)),1.6,'Close-up: the wheel leans 12°, the coffee stays upright')
    save(fig,'render_v6_kickstand_close.png')
if '3' in which:   # leaning and braking at once
    fig=plt.figure(figsize=(14,14),facecolor='white'); ax=fig.add_subplot(1,1,1,projection='3d')
    draw(ax,scene(8,10,'out',coffee),12,-35,around(8,10,(170,170,150)),1.5,'Leaning 10° and braking 8° at once: both axes swing')
    save(fig,'render_v6_lean_and_brake.png')
if '4' in which:   # the mechanism, no drink
    fig=plt.figure(figsize=(20,20),facecolor='white')
    cases=[('Slid in: flat, locked level both ways',0,0,'in',None,22,-35),
           ('Out: gimbal ring (red) on the side pins',0,0,'out',None,22,-35),
           ('Out, wheel leaning 20°: the basket rolls on the front/back pins',0,20,'out',None,6,0),
           ('Out, wheel 20° nose-down: the gimbal ring swings, stays level',20,0,'out',None,2,-90)]
    for i,(tt,phi,lean,st,dr,el,az) in enumerate(cases):
        ax=fig.add_subplot(2,2,i+1,projection='3d')
        draw(ax,scene(phi,lean,st,dr),el,az,around(phi,lean,(150,150,120)),1.5,tt)
    save(fig,'render_v6_gimbal_closeup.png')
