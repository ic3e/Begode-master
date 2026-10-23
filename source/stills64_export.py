# Lamp v6.4 + handle v18 stills (renderer: anim/stills64.html): the road sensor's eye behind the window, the handle's
# two buttons on the leg's back by the USB port, and the lamp at night.
import numpy as np, trimesh, json, base64
src=open('stills6_export.py').read().replace("exec(open('build26.py').read())","exec(open('build28.py').read())")
src=src.replace('housing11()','housing13()').replace("handle17(1)","handle18(1)")
exec(src.split("views=[")[0].replace("open('anim/stills6_data.js'","#"))
tb,tc=tof_board()
add('tof_board',tb,'#1d3d8f','body',0.5); add('tof_chip',tc,'#111111','body',0.3)
add('hb_switches',hb_switches(),'#c9ced6','body',0.3,0.9)
Z16=np.zeros(16).tolist()
def v4(cap,cam,tgt,**kw):
    v=view(cap,stand,cam,tgt,**kw); return v
lampS=P(stand,[-62,0,ZC]); eye=P(stand,[-57,2,ZC-53]); hb=P(stand,[*_leg_pt(11.5,15.0),ZC+HB_W])
usb=P(stand,[USB16_C[0],USB16_C[1],ZC+MOUTH16])
views=[v4('Lamp v6.4: the road sensor looks out through the window, left of the lenses',lampS+np.array([-330,25,-60]),lampS+np.array([0,-15,-10])),
       v4('Road sensor (VL53L1X) in its hood behind the window, tilted 25 deg down at the road',eye+np.array([-120,40,-70]),eye),
       v4('Two sealed buttons on the back of the handle\'s leg, by the USB port: dip, main, high, flash',hb+np.array([95,95,55]),hb+np.array([0,-2,0])),
       v4('Night: three LEDs, levelled; the beam dips for oncoming traffic',lampS+np.array([-520,120,-300]),lampS+np.array([-60,-50,0]),night=True,beams=True,a=6.0)]
open('anim/stills64_data.js','w').write('window.DATA='+json.dumps(dict(meshes=meshes,frames=views))+';')
print('views',len(views),'meshes',len(meshes))
