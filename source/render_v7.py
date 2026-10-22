import numpy as np, trimesh, manifold3d as mf, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
exec(open('build15.py').read())
O=OUT; AIM=-2.0
T=np.array([[-1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1.]])
light=np.array([0.45,-0.35,0.8]); light/=np.linalg.norm(light)
wheel=M2.model()
handle=trimesh.load('handle10.stl'); cap=trimesh.load(U+'euc_master_front_handle_p2.stl')
blocks=to_tm(mv(servo_block2()+elec_block2()+lid2())); servo=to_tm(mv(H(servo_model()[0]))); diffs=to_tm(mv(diffuser(1)+diffuser(-1)))
RED='#d9343d'
def can():
    c=cylV(33,FLOOR_Y,FLOOR_Y+115,0,0)-cylV(29,FLOOR_Y+113,FLOOR_Y+116,0,0)
    return [(c,'#c0c4ca'),(cylV(31,FLOOR_Y+108,FLOOR_Y+110,0,0),'#d01818')]
def head_parts(a,night):
    hs=H(box(0,HS_D,-HS/2,HS/2,-HS/2,HS/2)); lens=H(cu(TIR_D/2-0.5,HU0-0.5,HU0+2.6))
    return [(to_tm(mv(tilt(H(head()),a))),'#3b3f44',False),(to_tm(mv(tilt(hs,a))),'#c9ccd1',False),(to_tm(mv(tilt(lens,a))),'#fff3a0' if night else '#d9dde2',night)]
CONTACT=np.array([M2.TC[0],M2.GROUND])
def wheel_mat(phi,lean):
    c,s=np.cos(np.radians(phi)),np.sin(np.radians(phi)); P=np.eye(4); P[:2,:2]=[[c,-s],[s,c]]
    P[:2,3]=CONTACT-P[:2,:2]@CONTACT
    c,s=np.cos(np.radians(lean)),np.sin(np.radians(lean)); L=np.eye(4); L[1:3,1:3]=[[c,-s],[s,c]]
    p=np.array([M2.GROUND,ZC]); L[1:3,3]=p-L[1:3,1:3]@p
    return L@P
def holder(th,drink=False,pitch=0.0,roll=0.0,clip=True):
    parts=[(to_tm(arm(1,th)+arm(-1,th)),'#3b3f44',False)]
    for m,c in zip(place_holder(th,pitch,roll),[RED,'#2f3338','#50575f']): parts.append((to_tm(m),c,False))
    if th<TH_IN-1:   # the three cords the floor hangs on
        cords=[]
        for a in (90,210,330):
            c_,s_=np.cos(np.radians(a)),np.sin(np.radians(a))
            p=mf.Manifold.sphere(0.9,8).translate([c_*35.1,R_H/2-3.5,ZC+s_*35.1]); q=mf.Manifold.sphere(0.9,8).translate([c_*31.0,FLOOR_Y-1.2,ZC+s_*31.0])
            cords.append(hull(p,q))
        parts.append((to_tm(place(mf.Manifold.batch_boolean(cords,mf.OpType.Add),gpos(th),pitch,roll)),'#e8a33a',False))
    if drink:
        for m,c in can():
            if clip: m=m^bxw(-200,200,R_H/2-1,400,-500,500)   # only the part above the ring shows
            parts.append((to_tm(place(m,gpos(th),pitch,roll)),c,False))
    return parts
def scene(th,phi=0,lean=0,drink=False,night=False,clip=True):
    out_=th<TH_IN-1
    parts=[(m,c,False) for m,c in wheel]+[(handle,RED,False),(cap,RED,False),(blocks,'#3b3f44',False),(servo,'#2f6fd6',False),
          (diffs,'#ffffff',True)]+head_parts(AIM+phi,night)+holder(th,drink,phi if out_ else 0,-lean if out_ else 0,clip)
    Mx=wheel_mat(phi,lean); res=[]
    for m,c,em in parts:
        m=m.copy(); m.apply_transform(Mx); res.append((m,c,em))
    return res
def draw(ax,meshes,el,az,lim,zoom=1.0,title=''):
    tris=[];cols=[]
    for m,c,em in meshes:
        m=m.copy(); m.apply_transform(T); base=np.array(matplotlib.colors.to_rgb(c))
        sh=np.ones(len(m.faces)) if em else np.clip(np.abs(m.face_normals@light)*0.65+0.35,0,1)
        tris.append(m.triangles); cols.append(np.c_[base[None,:]*sh[:,None],np.ones(len(sh))])
    ax.add_collection3d(Poly3DCollection(np.vstack(tris),facecolors=np.vstack(cols),edgecolors='none'))
    (x0,x1),(y0,y1),(z0,z1)=lim
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_zlim(z0,z1); ax.set_box_aspect((x1-x0,y1-y0,z1-z0),zoom=zoom)
    ax.view_init(el,az); ax.set_axis_off(); ax.set_title(title,fontsize=22)
def around(pt,phi,lean,half):
    q=T@(wheel_mat(phi,lean)@np.array([pt[0],pt[1],ZC,1]))
    return tuple((q[i]-half[i],q[i]+half[i]) for i in range(3))
def save(fig,name): plt.tight_layout(); fig.savefig(O+name,dpi=75,facecolor='white'); plt.close(fig); print(name)
C=(-95,-40)
which=sys.argv[1:] or ['1','2','3']
if '1' in which:   # side views: in, half-way, out with a can, braking
    fig=plt.figure(figsize=(20,20),facecolor='white')
    cases=[('Swung in: under the lamp, back half in the bay',TH_IN,0,False),('Swinging out',(TH_IN+TH_OUT)/2,0,False),
           ('Out, with a 0.33 l can',TH_OUT,0,True),('Braking 10° nose-down: the can stays upright',TH_OUT,10,True)]
    for i,(tt,th,phi,dr) in enumerate(cases):
        ax=fig.add_subplot(2,2,i+1,projection='3d')
        draw(ax,scene(th,phi,0,dr,clip=False),2,-90,around(C,phi,0,(190,190,175)),1.55,tt)
    save(fig,'render_v7_side.png')
if '2' in which:   # front three-quarter: in and out
    fig=plt.figure(figsize=(20,11.5),facecolor='white')
    for i,(tt,th,dr) in enumerate((('Swung in',TH_IN,False),('Out, with a can',TH_OUT,True))):
        ax=fig.add_subplot(1,2,i+1,projection='3d')
        draw(ax,scene(th,0,0,dr),16,-35,around(C,0,0,(170,170,140)),1.5,tt)
    save(fig,'render_v7_front.png')
if '3' in which:   # kickstand lean, from the front, whole wheel and close
    fig=plt.figure(figsize=(20,11),facecolor='white')
    ax=fig.add_subplot(1,2,1,projection='3d')
    draw(ax,scene(TH_OUT,0,12,True,clip=False),4,0,((-260,260),(-380,280),(-640,170)),1.2,'On the kickstand, leaning 12°')
    ax=fig.add_subplot(1,2,2,projection='3d')
    draw(ax,scene(TH_OUT,0,12,True),4,0,around((GD[0],GD[1]+10),0,12,(120,120,105)),1.5,'Close-up: the can hangs straight')
    save(fig,'render_v7_lean.png')
