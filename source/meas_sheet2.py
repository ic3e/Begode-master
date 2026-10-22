import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Rectangle
NEED='#e8590c'; OK='#2b8a3e'; INK='#222'
fig=plt.figure(figsize=(16,10.5),facecolor='white')
ax=fig.add_axes([0.02,0.12,0.6,0.78]); ax.set_aspect('equal'); ax.axis('off')
bx=fig.add_axes([0.64,0.12,0.35,0.78]); bx.set_aspect('equal'); bx.axis('off')
def poly(a,pts,fc,ec=INK,lw=1.4,z=1,**k): a.add_patch(Polygon(pts,closed=True,fc=fc,ec=ec,lw=lw,zorder=z,**k))
def dim(a,p,q,lab,col,off=(0,0),fs=15):
    a.annotate('',p,q,arrowprops=dict(arrowstyle='<->',color=col,lw=2.2,shrinkA=0,shrinkB=0),zorder=6)
    a.text((p[0]+q[0])/2+off[0],(p[1]+q[1])/2+off[1],lab,color=col,fontsize=fs,fontweight='bold',ha='center',va='center',zorder=7,bbox=dict(fc='white',ec='none',pad=1))
def ref(a,x0,y0,x1,y1): a.plot([x0,x1],[y0,y1],':',color='#868e96',lw=1.3,zorder=5)
# side view, front to the right. cover with the empty lamp pocket
poly(ax,[(-120,60),(40,60),(62,40),(62,12),(14,12),(14,-21),(62,-21),(62,-21)],'#cfd2d6')
poly(ax,[(-120,60),(40,60),(62,40),(62,22),(16,22),(16,-5),(-10,-5),(-10,20),(-120,20)],'#cfd2d6')
ax.add_patch(Rectangle((16,-21),46,43,fc='white',ec=INK,lw=1.6,ls='--',zorder=2))
ax.text(33,1,'empty space\nwhere the\nstock lamp was',ha='center',va='center',fontsize=11,color='#555',zorder=3)
ax.text(-55,40,'top cover',ha='center',fontsize=12,color='#555')
poly(ax,[(-60,20),(-10,20),(-10,-25),(-60,-25)],'#9aa0a6'); ax.text(-35,0,'black block',ha='center',color='white',fontsize=11)
ax.add_patch(Circle((-17,-16),2.2,fc='#ffd43b',ec=INK,zorder=4)); ax.annotate('lowest\nbolt hole',(-17,-16),(-100,-12),fontsize=11,va='center',arrowprops=dict(arrowstyle='->'))
poly(ax,[(-120,-34),(-17,-41),(66,-18),(68,-22),(68,-150),(-120,-150)],'#6c757d',z=0.5); ax.text(-50,-110,'shell',color='white',fontsize=13,ha='center')
# dims
ref(ax,62,22,62,80); ref(ax,16,22,16,80); dim(ax,(16,74),(62,74),'3',NEED,off=(0,6))
ref(ax,62,-21,90,-21); ref(ax,62,22,90,22); dim(ax,(84,-21),(84,22),'2',NEED,off=(6,0))
dim(ax,(56,-21),(56,22),'4',NEED,off=(0,8))
ref(ax,-17,-16,8,-16); ref(ax,8,-21,16,-21); dim(ax,(4,-16),(4,22),'5',NEED,off=(-6,0))
ax.text(72,-34,'old lamp underside:\n7.5 below the hole ✓',ha='left',fontsize=10,color=OK)
ax.annotate('FRONT →',(150,-140),fontsize=15,fontweight='bold',ha='right')
ax.set_xlim(-125,155); ax.set_ylim(-160,95); ax.set_title('Side view, stock lamp removed',fontsize=16)
# front view: opening
poly(bx,[(-95,70),(95,70),(95,-25),(-95,-25)],'#cfd2d6')
bx.add_patch(Rectangle((-72,-22),144,43,fc='white',ec=INK,lw=1.6,ls='--'))
bx.text(0,0,'opening',ha='center',va='center',fontsize=12,color='#555')
poly(bx,[(-130,-25),(-47.5,-25),(-47.5,-140),(-130,-140)],'#6c757d'); poly(bx,[(47.5,-25),(130,-25),(130,-140),(47.5,-140)],'#6c757d')
dim(bx,(-72,32),(72,32),'1',NEED,off=(0,7)); dim(bx,(-47.5,-70),(47.5,-70),'95 ✓',OK,off=(0,7),fs=12)
bx.text(0,-118,'6  how was the lamp held?\n(photo of the screw holes)',ha='center',fontsize=11,color=NEED,fontweight='bold')
bx.set_xlim(-135,135); bx.set_ylim(-160,95); bx.set_title('Front view, stock lamp removed',fontsize=16)
fig.text(0.02,0.975,'With the stock lamp out: the empty space it leaves',fontsize=18,fontweight='bold',va='top')
L=[('1','width of the opening, inside, left to right'),('2','height of the opening at the front'),
   ('3','depth: from the front edge of the cover back to the back wall of the space'),('4','height at the back of the space (if it is less than at the front)'),
   ('5','lowest bolt hole → top of the space (straight up)'),('6','a photo of how the lamp was fastened')]
for i,(n,t) in enumerate(L): fig.text(0.03+0.49*(i%2),0.085-0.027*(i//2),f'{n}  {t}',fontsize=11,color=NEED,va='center')
plt.savefig('../build_output/measurements_lamp_space.png',dpi=90,facecolor='white')
