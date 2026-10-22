import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle, FancyBboxPatch, Arc
NEED='#e8590c'; OK='#2b8a3e'; INK='#222'
fig=plt.figure(figsize=(16,11),facecolor='white')
ax=fig.add_axes([0.02,0.1,0.62,0.8]); ax.set_aspect('equal'); ax.axis('off')
bx=fig.add_axes([0.66,0.1,0.33,0.8]); bx.set_aspect('equal'); bx.axis('off')
# ---------- side view (front of the wheel to the RIGHT) ----------
def poly(a,pts,fc,ec=INK,lw=1.4,z=1,**k): a.add_patch(Polygon(pts,closed=True,fc=fc,ec=ec,lw=lw,zorder=z,**k))
poly(ax,[(-120,40),(70,40),(78,30),(78,22),(55,20),(-120,20)],'#cfd2d6')                       # top cover with nose
ax.text(-60,30,'top cover (seat)',ha='center',va='center',fontsize=12,color='#555')
poly(ax,[(-60,20),(12,20),(12,-20),(-60,-20)],'#9aa0a6')                                         # controller / black block
ax.text(-26,4,'black block\n(handle bolts here)',ha='center',va='center',fontsize=11,color='white')
for y in (6,-6): ax.add_patch(Circle((3,y),1.8,fc='white',ec=INK,zorder=3))
ax.add_patch(Circle((5,-14),2.2,fc='#ffd43b',ec=INK,lw=1.5,zorder=4))                             # lowest hole = datum
ax.annotate('lowest\nbolt hole',(5,-14),(-100,-14),fontsize=11,va='center',arrowprops=dict(arrowstyle='->',color=INK))
poly(ax,[(16,19),(54,19),(54,-21.5),(16,-21.5)],'#495057')                                       # stock lamp
ax.text(35,-1,'lamp',ha='center',va='center',fontsize=12,color='white')
poly(ax,[(-120,-30),(-10,-27),(58,-18.5),(60,-22),(60,-150),(-120,-150)],'#6c757d',z=0.5)         # shell, top tilted
ax.text(-60,-125,'shell (side)',ha='center',va='center',fontsize=13,color='white')
ax.plot([0,60],[-99,-99],'--',color='#adb5bd',lw=2); ax.text(64,-99,'cross plate\n(between the shells)',ha='left',va='center',fontsize=10,color='#868e96')
def dim(a,p,q,lab,col,off=(0,0),fs=15,ha='center'):
    a.annotate('',p,q,arrowprops=dict(arrowstyle='<->',color=col,lw=2.2,shrinkA=0,shrinkB=0),zorder=6)
    a.text((p[0]+q[0])/2+off[0],(p[1]+q[1])/2+off[1],lab,color=col,fontsize=fs,fontweight='bold',ha=ha,va='center',zorder=7,
           bbox=dict(fc='white',ec='none',pad=1))
def ref(a,x,y0,y1,col='#868e96'): a.plot([x,x],[y0,y1],':',color=col,lw=1.3,zorder=5)
def refh(a,y,x0,x1,col='#868e96'): a.plot([x0,x1],[y,y],':',color=col,lw=1.3,zorder=5)
# horizontal: from the block's front face (x=12)
ref(ax,12,20,95); ref(ax,5,-14,95); ref(ax,54,19,95); ref(ax,60,-18.5,-160); ref(ax,78,22,95)
ax.plot([60,60],[-150,-160],':',color='#868e96')
dim(ax,(5,62),(12,62),'1',NEED,off=(0,5))
dim(ax,(12,74),(54,74),'2',NEED,off=(0,5))
dim(ax,(12,86),(78,86),'4',NEED,off=(0,5))
ref(ax,12,-20,-160); dim(ax,(12,-157),(60,-157),'3',NEED,off=(0,-6))
ax.text(12,99,'front face\nof the block',ha='center',va='bottom',fontsize=10,color='#555')
# vertical: from the lamp underside (y=-21.5)
refh(ax,-21.5,54,100); refh(ax,20,78,100); refh(ax,-18.5,58,100); refh(ax,-14,5,100,col='#f0b400')
dim(ax,(92,-21.5),(92,20),'5',NEED,off=(5,0))
dim(ax,(100,-21.5),(100,-14),'7.5 ✓',OK,off=(9,0),fs=12)
dim(ax,(84,-21.5),(84,-18.5),'',OK); ax.text(80,-31,'3 ✓',color=OK,fontsize=12,fontweight='bold',ha='center')
refh(ax,-28,-10,5); dim(ax,(-6,-14),(-6,-28),'6',NEED,off=(-6,0))
dim(ax,(40,-21.5),(40,-99),'77 ✓  (37 when\nthe suspension bottoms)',OK,off=(0,-10),fs=11)
ax.annotate('FRONT  →',(150,-170),fontsize=15,fontweight='bold',color=INK,ha='right')
ax.set_xlim(-125,155); ax.set_ylim(-175,110)
ax.set_title('Side view (looking at the right side of the wheel)',fontsize=16,pad=8)
# ---------- front view ----------
poly(bx,[(-75,22),(75,22),(75,-20),(-75,-20)],'#495057')
for i in range(4): bx.add_patch(Circle((-45+30*i,1),9,fc='#e9ecef',ec=INK,zorder=3))
poly(bx,[(-120,-18),(-47.5,-18),(-47.5,-150),(-120,-150)],'#6c757d'); poly(bx,[(47.5,-18),(120,-18),(120,-150),(47.5,-150)],'#6c757d')
bx.plot([-47.5,47.5],[-99,-99],'--',color='#adb5bd',lw=2)
bx.add_patch(Rectangle((-30,-150),60,52,fc='#343a40',ec=INK,zorder=0.5)); bx.text(0,-130,'tyre',ha='center',color='white',fontsize=11)
dim(bx,(-75,34),(75,34),'141.5 ✓',OK,off=(0,6),fs=12); ref(bx,-75,22,40); ref(bx,75,22,40)
dim(bx,(-47.5,-60),(47.5,-60),'95 ✓',OK,off=(0,6),fs=12)
bx.text(0,-84,'bay: 50 deep\nto the cable ✓',ha='center',va='center',fontsize=11,color=OK,fontweight='bold')
bx.set_xlim(-130,130); bx.set_ylim(-175,110); bx.set_title('Front view (already measured)',fontsize=16,pad=8)
# ---------- legend ----------
txt=[('1','lowest hole centre → front face of the black block (how far behind the face is the hole?)'),
     ('2','front face of the block → front face of the lamp'),
     ('3','front face of the block → front edge of the shells  (was your 53.1 measured like this?)'),
     ('4','front face of the block → front tip of the top cover'),
     ('5','lamp underside → underside of the top cover right above the lamp (= the room a lamp has)'),
     ('6','lowest hole → top of the shell straight below it')]
y=0.035
fig.text(0.02,0.975,'Measurements I still need (orange) and what we already have (green ✓)',fontsize=18,fontweight='bold',va='top')
for i,(n,t) in enumerate(txt):
    fig.text(0.03+0.49*(i%2),0.075-0.027*(i//2), f'{n}  {t}',fontsize=10.5,color=NEED if True else INK,va='center')
plt.savefig('../build_output/measurements_needed.png',dpi=90,facecolor='white')
