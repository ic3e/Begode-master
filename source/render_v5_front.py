import numpy as np, trimesh, manifold3d as mf, matplotlib, types
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
exec(open('build13.py').read())
_g={}; exec(open('master_model.py').read().split("\nif __name__=='__main__':")[0],_g); MM=types.SimpleNamespace(**_g)
O=OUT; AIM=-2.0
T=np.array([[-1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1.]])
light=np.array([0.45,-0.35,0.8]); light/=np.linalg.norm(light)
wheel=MM.model()
handle=trimesh.load('handle8.stl'); cap=trimesh.load(U+'euc_master_front_handle_p2.stl')
blocks=to_tm(servo_block2()+elec_block2()+lid2()); servo=to_tm(H(servo_model()[0])); diffs=to_tm(diffuser(1)+diffuser(-1))
floor=ring_tops(True)[3]-RING_H+LIP
def can():   # 0.33 l can, in basket coords
    c=cylV(33,floor,floor+115,0,0)-cylV(29,floor+113,floor+116,0,0)
    return [(to_tm(c),'#c0c4ca',False),(to_tm(cylV(31,floor+108,floor+110,0,0)),'#d01818',False)]
def coffee():
    body=mf.Manifold.cylinder(104,30,45,96).rotate([-90,0,0]).translate([0,floor,ZC])
    lid=mf.Manifold.cylinder(6,46,44,96).rotate([-90,0,0]).translate([0,floor+104,ZC])
    sleeve=mf.Manifold.cylinder(40,36.5,42.5,96).rotate([-90,0,0]).translate([0,floor+35,ZC])
    return [(to_tm(body),'#f3efe6',False),(to_tm(sleeve),'#8b5a2b',False),(to_tm(lid),'#e8e8e8',False)]
def head_parts(a,night):
    hs=H(box(0,HS_D,-HS/2,HS/2,-HS/2,HS/2)); lens=H(cu(TIR_D/2-0.5,HU0-0.5,HU0+2.6))
    return [(to_tm(tilt(H(head()),a)),'#3b3f44',False),(to_tm(tilt(hs,a)),'#c9ccd1',False),(to_tm(tilt(lens,a)),'#fff3a0' if night else '#d9dde2',night)]
CONTACT=np.array([MM.TC[0],MM.GROUND])
def pitch_mat(phi):
    c,s=np.cos(np.radians(phi)),np.sin(np.radians(phi)); M=np.eye(4); M[:2,:2]=[[c,-s],[s,c]]
    M[:2,3]=CONTACT-M[:2,:2]@CONTACT; return M
def holder(state,drink=None,swing=0.0):
    xp=X_IN if state=='in' else X_OUT
    parts=[(to_tm(arm(1,xp)+arm(-1,xp)),'#3b3f44',False)]
    rings=basket(state!='in')
    cols=['#2f3338','#3a3f45','#454b52','#50575f']
    for r,c in zip(place_basket(rings,xp,swing),cols): parts.append((to_tm(r),c,False))
    if drink:
        for m,c,e in drink():
            mm=to_mf(m)^bx(-200,200,R1_TOP-1,400,-500,500)    # only the part above the rim shows; avoids draw-order glitches
            mm=mm.rotate([0,0,-swing]) if swing else mm
            parts.append((to_tm(mm.translate([xp,YP,0])),c,e))
    return parts
def scene(phi,state,drink=None,night=False,drl=1.0,swing=0.0):
    parts=[(m,c,False) for m,c in wheel]+[(handle,'#e0303a',False),(cap,'#e0303a',False),(blocks,'#3b3f44',False),(servo,'#2f6fd6',False),
          (diffs,'#ffffff' if drl>0.5 else '#f0f0e8',True)]+head_parts(AIM+phi,night)+holder(state,drink,swing)
    out=[]
    for m,c,em in parts:
        m=m.copy(); m.apply_transform(pitch_mat(phi)); out.append((m,c,em))
    return out
def beam_wedge(phi,L=900,half=5):
    a=AIM+phi; r=np.radians(a)
    q=np.array([[np.cos(r),-np.sin(r)],[np.sin(r),np.cos(r)]])@np.array([HU0-0.5,0])+[PX,PY]
    M=pitch_mat(phi); q=M[:2,:2]@q+M[:2,3]; e=np.radians(AIM); h=np.radians(half)
    pts=[q]+[q+L*np.array([-np.cos(e+d),np.sin(e+d)]) for d in (h,-h)]
    return trimesh.Trimesh([[x,y,ZC] for x,y in pts],[[0,1,2]],process=False)
def draw(ax,meshes,el,az,lim,extra=()):
    tris=[];cols=[]
    for m,c,em in meshes:
        m=m.copy(); m.apply_transform(T); base=np.array(matplotlib.colors.to_rgb(c))
        sh=np.ones(len(m.faces)) if em else np.clip(np.abs(m.face_normals@light)*0.65+0.35,0,1)
        tris.append(m.triangles); cols.append(np.c_[base[None,:]*sh[:,None],np.ones(len(sh))])
    for b,rgba in extra:
        b=b.copy(); b.apply_transform(T); tris.append(b.triangles); cols.append(np.array([rgba]*len(b.faces)))
    ax.add_collection3d(Poly3DCollection(np.vstack(tris),facecolors=np.vstack(cols),edgecolors='none'))
    (x0,x1),(y0,y1),(z0,z1)=lim
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_zlim(z0,z1); ax.set_box_aspect((x1-x0,y1-y0,z1-z0))
    ax.view_init(el,az); ax.set_axis_off()


lim=((-200,260),(-205,65),(-235,125))
tight=((-200,260),(-170,30),(-150,50))
ZOOM=1.0
views=[('Front: slid in under the lamp','in',None,5,0,tight),
       ('Front: pulled out with a coffee cup','out',coffee,5,0,tight),
       ('Front, from above: pulled out with a 0.33 l can','out',can,25,-25,lim),
       ('Front, from above: slid in','in',None,25,-25,lim)]
for i,(tt,st,dr,el,az,lim) in enumerate(views):
    ZOOM=2.3 if lim is tight else 1.5
    fig=plt.figure(figsize=(14,14),facecolor='white')
    ax=fig.add_subplot(1,1,1,projection='3d')
    draw(ax,scene(0,st,dr,False,1.0),el,az,lim)
    (x0,x1),(y0,y1),(z0,z1)=lim; ax.set_box_aspect((x1-x0,y1-y0,z1-z0),zoom=ZOOM)
    ax.set_title(tt,fontsize=26)
    plt.tight_layout(); plt.savefig(O+f'render_v5_front_big_{i+1}.png',dpi=90,facecolor='white'); plt.close(fig)
print('ok')
