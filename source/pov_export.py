# The rider's view at night (renderer: anim/pov.html, data in anim/pov_data.js): standing on the wheel, riding down
# a road through cruising, hard braking, accelerating and a bumpy stretch. The main picture is the levelled lamp;
# the inset is the same ride with the lenses held fixed (aimed the same, 2 deg down), for comparison.
# The lenses follow the firmware's rule (headlamp6_firmware.ino): head = aim - pitch, clamped to +-10 (TILT_MAX),
# moved at most 400 deg/s (SLEW) and not for less than 0.25 deg (DEADBAND); the servo's own lag on top.
import numpy as np, trimesh, json, base64
src=open('stills6_export.py').read().replace("exec(open('build26.py').read())","exec(open('build27.py').read())").replace('housing11()','housing12()')
exec(src.split("views=[")[0].replace("open('anim/stills6_data.js'","#"))
meshes=[m for m in meshes if m['group'] in ('body','head') and m['kind']!='beam']   # the road and the light are the page's
def pitched(p):   # the wheel pitched by p degrees about the tyre's contact point (+ = nose down)
    c=P(stand,[184.6,-357.7-255.0,ZC]); return T(*c)@Rz(p)@T(*(-c))@stand
FPS=30; DUR=14.0; N=int(FPS*DUR); AIM=2.0          # aim: 2 deg below level (cfg.aim = -2)
def smooth(t,t0,t1): x=np.clip((t-t0)/(t1-t0),0,1); return x*x*(3-2*x)
def bump(t,t0,t1): return smooth(t,t0,t0+0.6)*(1-smooth(t,t1-0.6,t1))
rng=np.random.default_rng(7); ph=rng.uniform(0,6.28,4)
def ride(t):   # wheel pitch (deg, + nose down), speed (m/s), what is happening
    p=0.25*np.sin(2.1*t+ph[0])+0.15*np.sin(5.3*t+ph[1])                     # never quite still
    p+=9.0*bump(t,2.5,5.0)                                                   # hard braking
    p-=7.0*bump(t,6.2,8.6)                                                   # accelerating
    sb=smooth(t,9.6,10.0)*(1-smooth(t,12.6,13.0))                            # broken asphalt
    p+=sb*(3.2*np.sin(2*np.pi*2.3*t+ph[2])+1.8*np.sin(2*np.pi*3.7*t+ph[3]))
    v=7.5-4.5*smooth(t,2.6,4.8)+5.0*smooth(t,6.2,8.4)-1.5*smooth(t,9.0,10.0)
    cap=('Cruising at night' if t<2.5 else 'Hard braking: the nose dips 9 deg' if t<5.6 else 'Back to cruising' if t<6.2 else
         'Accelerating: the nose lifts 7 deg' if t<9.4 else 'Broken asphalt' if t<13.0 else 'Cruising')
    return p,v,cap
dt=1.0/FPS; sub=40; cmd=AIM; mech=AIM; s=0.0; frames=[]
for i in range(N):
    t=i*dt
    for k in range(sub):                        # the 200 Hz loop, finer
        tt=t+k*dt/sub; p,v,_=ride(tt)
        want=np.clip(AIM-p,-10,10)              # firmware: want = aim + correction, in "beam down" degrees here
        if abs(want-cmd)>0.25: st=400*dt/sub; cmd+=np.clip(want-cmd,-st,st)
        mech+=(cmd-mech)*min(1,(dt/sub)/0.03)   # the MG90S gets there about 30 ms later
        s+=v*1000*dt/sub
    p,v,cap=ride(t)
    B=T(-s,0,0)@pitched(p)
    lean=60*np.clip(p/9,-1,1)                   # the rider leans back into the braking, forward into the pull
    bob=8*np.sin(2*np.pi*2.3*t)*smooth(t,9.6,10)*(1-smooth(t,12.6,13))
    eye=np.array([420-s+lean,1650+bob,ZC]); tgt=eye+np.array([-1000,-np.tan(np.radians(33))*1000,0])
    frames.append(dict(cap=cap,t=round(t,3),p=round(float(p),2),a=round(float(mech),2),v=round(v*3.6,1),
        body=np.asarray(B).T.flatten().round(3).tolist(),lev=head_mat(B,mech).T.flatten().round(4).tolist(),
        fix=head_mat(B,AIM).T.flatten().round(4).tolist(),cam=eye.round(1).tolist(),tgt=tgt.round(1).tolist()))
spots=[dict(x=float(LX)-0.5,w=float(w),half=float(h)) for w,h in zip(OPTIC_W,(14,4.5,14))]   # in the head's frame
open('anim/pov_data.js','w').write('window.DATA='+json.dumps(dict(meshes=meshes,frames=frames,spots=spots,ZC=ZC))+';')
print('frames',len(frames),'travel %.0f m'%(s/1000),'max |a| %.1f'%max(abs(f['a']) for f in frames))
