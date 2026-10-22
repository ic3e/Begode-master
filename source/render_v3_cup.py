import numpy as np, trimesh, manifold3d as mf, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
exec(open('build11.py').read().split("\nif __name__=='__main__':")[0])
import types
mm=types.SimpleNamespace(); _g={}; exec(open('master_model.py').read().split("\nif __name__=='__main__':")[0],_g); mm.__dict__.update(_g)
O=OUT; AIM=-2.0
T=np.array([[-1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1.]])       # STL -> picture: x forward, y across, z up
light=np.array([0.45,-0.35,0.8]); light/=np.linalg.norm(light)
wheel=mm.model()
handle=trimesh.load('handle6.stl')
cap=trimesh.load(U+'euc_master_front_handle_p2.stl')
blocks=trimesh.load('lamp3_fixed.stl')
servo=to_tm(H(servo_model()[0]))
diffs=to_tm(diffuser(1)+diffuser(-1))
def head_parts(a,night):
    hs=H(box(0,HS_D,-HS/2,HS/2,-HS/2,HS/2)); lens=H(cu(TIR_D/2-0.5,HU0-0.5,HU0+2.6))
    return [(to_tm(tilt(H(head()),a)),'#3b3f44',False),(to_tm(tilt(hs,a)),'#c9ccd1',False),
            (to_tm(tilt(lens,a)),'#fff3a0' if night else '#d9dde2',night)]
CONTACT=np.array([mm.TC[0],mm.GROUND])
def pitch_mat(phi):   # + = nose down, about the tyre contact point
    c,s=np.cos(np.radians(phi)),np.sin(np.radians(phi)); M=np.eye(4); M[:2,:2]=[[c,-s],[s,c]]
    M[:2,3]=CONTACT-M[:2,:2]@CONTACT; return M
def rot2(p,c,deg):
    r=np.radians(deg); R=np.array([[np.cos(r),-np.sin(r)],[np.sin(r),np.cos(r)]]); return R@(np.asarray(p)-c)+c
def beam_wedge(phi,a,L=900,half=5):
    q=rot2([PX+HU0-0.5,PY],np.array([PX,PY]),a); M=pitch_mat(phi); q=M[:2,:2]@q+M[:2,3]
    e=np.radians(a-phi); h=np.radians(half)
    pts=[q]+[q+L*np.array([-np.cos(e+d),np.sin(e+d)]) for d in (h,-h)]
    return trimesh.Trimesh([[x,y,ZC] for x,y in pts],[[0,1,2]],process=False)
def tof_ray(phi):
    p=np.array([CX0-LEG_X1-4,TOF3_Y]); M=pitch_mat(phi); p=M[:2,:2]@p+M[:2,3]
    e=np.radians(-TOF_DOWN-phi); d=np.array([-np.cos(e),np.sin(e)])
    t=(mm.GROUND-p[1])/d[1]; q=p+t*d
    return np.array([[p[0],p[1],ZC+TOF3_W],[q[0],q[1],ZC+TOF3_W]]), t
def scene(phi,head_a,cup,night,drl):
    parts=[(m,c,False) for m,c in wheel]+[(handle,'#e0303a',False),(cap,'#e0303a',False),(blocks,'#3b3f44',False),
          (servo,'#2f6fd6',False),(trimesh.load(f'v6_cup_{cup}.stl'),'#4a4f55',False),
          (diffs,'#ffffff' if drl>0.5 else ('#f0f0e8' if drl>0 else '#9aa0a6'),drl>0)]
    parts+=head_parts(head_a,night)
    out=[]
    for m,c,em in parts:
        m=m.copy(); m.apply_transform(pitch_mat(phi)); out.append((m,c,em))
    return out
def draw(ax,meshes,el,az,lim,extra=(),lines=()):
    tris=[];cols=[]
    for m,c,em in meshes:
        m=m.copy(); m.apply_transform(T); base=np.array(matplotlib.colors.to_rgb(c))
        sh=np.ones(len(m.faces)) if em else np.clip(np.abs(m.face_normals@light)*0.65+0.35,0,1)
        tris.append(m.triangles); cols.append(np.c_[base[None,:]*sh[:,None],np.ones(len(sh))])
    for b,rgba in extra:
        b=b.copy(); b.apply_transform(T); tris.append(b.triangles); cols.append(np.array([rgba]*len(b.faces)))
    ax.add_collection3d(Poly3DCollection(np.vstack(tris),facecolors=np.vstack(cols),edgecolors='none'))
    for l,st in lines:
        l=(T[:3,:3]@l.T).T+T[:3,3]; ax.plot(l[:,0],l[:,1],l[:,2],st,lw=1.6)
    (x0,x1),(y0,y1),(z0,z1)=lim
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_zlim(z0,z1); ax.set_box_aspect((x1-x0,y1-y0,z1-z0))
    ax.view_init(el,az); ax.set_axis_off()


fig=plt.figure(figsize=(20,20),facecolor='white')
views=[('Side: cup holder OPEN','open',2,-90,((-240,330),(-300,300),(-330,140))),
       ('Side: cup holder FOLDED between the legs','folded',2,-90,((-240,330),(-300,300),(-330,140))),
       ('Front, from the side: OPEN','open',18,-35,((-150,260),(-230,90),(-240,120))),
       ('Front, from the side: FOLDED','folded',18,-35,((-150,260),(-230,90),(-240,120)))]
for i,(tt,cup,el,az,lim) in enumerate(views):
    ax=fig.add_subplot(2,2,i+1,projection='3d')
    draw(ax,scene(0,AIM,cup,False,1.0),el,az,lim)
    ax.set_title(tt,fontsize=20)
plt.tight_layout(); plt.savefig(O+'render_v3_cupholder_closeup.png',dpi=55,facecolor='white')
print('ok')
