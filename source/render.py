import trimesh, sys, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
def render(meshes, out, views=((20,-60),(20,30),(90,-90),(0,-90),(0,0),(-30,120)), colors=None):
    fig = plt.figure(figsize=(18,12))
    allv = np.vstack([m.vertices for m in meshes])
    lo, hi = allv.min(0), allv.max(0); c=(lo+hi)/2; r=(hi-lo).max()/2
    light = np.array([0.3,-0.5,0.8]); light/=np.linalg.norm(light)
    for i,(el,az) in enumerate(views):
        ax = fig.add_subplot(2,3,i+1, projection='3d')
        for k,m in enumerate(meshes):
            base = np.array(matplotlib.colors.to_rgb((colors or ['#6aa0d8','#e0904a','#7cc47c','#c77cc4','#d8d06a'])[k%5]))
            sh = np.clip(np.abs(m.face_normals@light)*0.7+0.3,0,1)
            fc = base[None,:]*sh[:,None]
            pc = Poly3DCollection(m.triangles, facecolors=fc, edgecolors='none')
            ax.add_collection3d(pc)
        ax.set_xlim(c[0]-r,c[0]+r); ax.set_ylim(c[1]-r,c[1]+r); ax.set_zlim(c[2]-r,c[2]+r)
        ax.set_box_aspect((1,1,1)); ax.view_init(el,az); ax.set_title(f'el{el} az{az}')
        ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
    plt.tight_layout(); plt.savefig(out, dpi=70)
if __name__=='__main__':
    ms=[trimesh.load(p) for p in sys.argv[2:]]
    render(ms, sys.argv[1])
