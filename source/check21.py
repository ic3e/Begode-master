import numpy as np, trimesh, manifold3d as mf
exec(open('build21.py').read())
orig=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))
handle=handle13()
hs=housing8(); pl=top_plate8(); win=window(); ld=lid3(); sv=H3(servo3()); df=diffuser5(1)+diffuser5(-1)
lamp=hs+pl
OBL=obstacles3(True); OBR=obstacles3(False)
print('housing + plate vs wheel (suspension bottomed):',round((lamp^OBL).volume(),2),' window vs wheel:',round((win^OBR).volume(),2),' lid:',round((ld^OBL).volume(),2))
print('vs handle: housing',round((hs^handle).volume(),2),' plate',round((pl^handle).volume(),2),' window',round((win^handle).volume(),2))
print('plate vs housing',round((pl^hs).volume(),2),' window vs housing',round((win^lamp).volume(),2),' diffusers vs housing',round((df^lamp).volume(),2))
print('window front X',round(win.bounding_box()[0],2),' cover tip',round(M2.COVER_X,2),' -> sits',round(win.bounding_box()[0]-M2.COVER_X,2),'mm behind it')
for a in (-TILT2,0,TILT2):
    hd=tilt3(H3(head8()),a); print(f'  head {a:+.0f}°: vs housing {(hd^hs).volume():.2f}  plate {(hd^pl).volume():.2f}  servo {(hd^sv).volume():.2f}  window {(hd^win).volume():.2f}')
print('servo vs housing',round((sv^hs).volume(),2),' vs plate',round((sv^pl).volume(),2))
# putting it together: head + servo go in from above as one unit, at their final place across the wheel
brg=H3(bearing7())
unit=H3(head8())+sv+brg
print('bearing vs housing',round((brg^hs).volume(),3),' vs plate',round((brg^pl).volume(),3),' vs head (pressed on, should be 0)',round((brg^H3(head8())).volume(),3))
for a in (-TILT2,TILT2): print(f'  bearing turned with head {a:+.0f}° (round, so same): vs housing',round((tilt3(brg,a)^hs).volume(),3))
hit=[round((unit.translate([0,d,0])^hs).volume(),2) for d in np.arange(0.5,45.5,0.5)]
print('head + servo lifted straight out of the open housing: worst overlap over 0.5-45 mm',max(hit))
print('top plate lifted off:',max(round((pl.translate([0,d,0])^(hs+unit)).volume(),2) for d in np.arange(0.5,20.5,0.5)))
print('bearing can lift?',round((brg.translate([0,0.3,0])^pl).volume(),2),'(>0: no)   head can move outboard?',round((brg.translate([0,0,-0.3])^hs).volume(),2),'(>0: no)')
b=H3(bearing7()); pin=H3(head8())^(bx(-200,200,-100,100,ZC+BRG_W0-0.01,ZC+BRG_W1+0.01))
print('pin length under the bearing',round(pin.bounding_box()[5]-pin.bounding_box()[2],2),' pin is a closed tube:',len(to_tm(H3(head8())^bx(-200,200,-100,100,ZC+BRG_W0+0.5,ZC+BRG_W0+1.0)).split(only_watertight=False))==1)
print('servo can lift?',round((sv.translate([0,0.3,0])^pl).volume(),2),'(>0: no)   slide across?',round((sv.translate([0,0,0.5])^hs).volume(),2),round((sv.translate([0,0,-0.6])^hs).volume(),2),'(>0: no)')
cone=mf.Manifold.cylinder(2600,0.5,2600*np.tan(np.radians(8.5)),48).rotate([0,90,0])
cone=cone.rotate([0,0,180+TOF_DOWN]).translate([LOW_X0-1,TOF5[1],ZC+TOF5[0]])^box(-3000,LOW_X0-1.5,M2.GROUND+5,300,-400,300)
print('road sensor view vs wheel/handle/lamp:',round((cone^OBR).volume(),1),round((cone^handle).volume(),1),round((cone^(lamp+win+ld)).volume(),1))
W=np.vstack([m.vertices for m,c in model3()]+[to_tm(handle).vertices])
L=np.vstack([to_tm(m).vertices for m in (hs,pl,win,ld,df)])
def margin(d): d=np.array(d,float); d/=np.linalg.norm(d); return (W@d).max()-(L@d).max()
named={'front':(-1,0,0),'front, 45° down':(-1,-1,0),'front-left':(-1,0,-1),'front-right':(-1,0,1),
       'left side':(0,0,-1),'right side':(0,0,1),'top (upside down)':(0,1,0),'back':(1,0,0)}
for k,d in named.items(): print(f'  fall {k:18s}: lamp sits {margin(d):6.1f} mm behind the first contact')
rng=np.random.default_rng(1); D=rng.normal(size=(20000,3)); D/=np.linalg.norm(D,axis=1)[:,None]
D=D[D[:,1]>-0.85]
m=(W@D.T).max(0)-(L@D.T).max(0); i=m.argmin()
print('worst of',len(D),'fall directions: lamp',round(m[i],1),'mm behind the first contact')
for nm,mm in (('housing',hs),('top plate',pl),('bearing',bearing7()),('window',win),('head',head8()),('lid',ld),('handle v13',handle)):
    t=to_tm(mm); print(nm,'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)))
# ---- v5.4: stops, buttons, USB ----
hd=lambda a: tilt3(H3(head8()),a)
lug=H3(box(LUG_U0,LUG_U1,-LUG_V,LUG_V,LUG_W0,LUG_W1)); stops=stop_lower()+stop_upper()
for a in (-11.5,-10,10,11.5):
    print(f'  head {a:+.1f}°: vs housing {(hd(a)^hs).volume():.2f}  plate {(hd(a)^pl).volume():.2f}  window {(hd(a)^win).volume():.2f}  servo {(hd(a)^sv).volume():.2f}')
for a in (-13,13):
    body_hit=((hd(a)-tilt3(lug,a))^(hs+pl+win+sv)).volume(); lug_hit=(tilt3(lug,a)^stops).volume()
    print(f'  head pushed to {a:+.0f}°: lug into the stops {lug_hit:.1f} mm3, rest of head into anything {body_hit:.2f} (0 = stops take it)')
lo,hi=0,0
for a in np.arange(10,13.01,0.1):
    if (tilt3(lug,a)^stops).volume()>0.01 and not hi: hi=a
    if (tilt3(lug,-a)^stops).volume()>0.01 and not lo: lo=a
print(f'  stops touch at +{hi:.1f}° / -{lo:.1f}°')
bt=buttons8()
print('buttons vs housing',round((bt^hs).volume(),2),' vs lid',round((bt^ld).volume(),2),' button heads below the chin face by',round(LOW_X0+BTN_POCKET_D-1.5-LOW_X0,1),'mm')
print('buttons vs wheel (suspension bottomed)',round((bt^OBL).volume(),2))
us=usb_socket()
print('USB socket vs handle',round((us^handle).volume(),2),' vs wheel',round((us^OBR).volume(),2),round((us^OBL).volume(),2))
x,y=USB_XY; cav=cw(USB_CAV[1],USB_CAV[0],USB_FACE,u=x,v=y).translate([0,0,ZC])
print('socket body fits its hole and cavity (body outside the cut):',round((us-(cav+cw(USB_R,USB_CAV[0],USB_FACE+3,u=x,v=y).translate([0,0,ZC]))-cw(11.0,USB_FACE,USB_FACE+2.5,u=x,v=y).translate([0,0,ZC])).volume(),2))
print('handle v13 vs wheel (suspension bottomed / not):',round((handle^OBL).volume(),2),round((handle^OBR).volume(),2),' vs housing',round((handle^hs).volume(),2))
