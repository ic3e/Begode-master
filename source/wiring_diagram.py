# The lamp's wiring as a diagram, laid out the way the boards sit (left bay | electronics box | right bay). Every
# pin carries a tag with its net: pins with the same tag are joined. The thick arrows are the bundles and the hole
# each one goes through. Same connections as the build guide's wiring list and the firmware's pins.
# Writes current/renders/wiring_diagram.png.
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams['font.family']='DejaVu Sans'
NET={'BAT+':'#d62728','PWR':'#d62728','GND':'#333333','5V':'#ff7f0e','3V3':'#d4a600','DIM':'#2ca02c','NTC':'#2ca02c','LDR':'#2ca02c',
     'SDA':'#1f77b4','SCL':'#1f77b4','SERVO':'#2ca02c','DRL_EN':'#2ca02c','DRL-':'#e377c2','USB_EN':'#2ca02c','USB_SW':'#17becf',
     'USB+':'#17becf','USB-':'#17becf','BTN+':'#2ca02c','BTN-':'#2ca02c','LED1+':'#9467bd','LED1-':'#9467bd','LED2+':'#9467bd',
     'LED2-':'#9467bd','LED3+':'#9467bd','LED3-':'#9467bd','HUP':'#8c564b','HDN':'#8c564b'}
fig,ax=plt.subplots(figsize=(24,14)); ax.set_xlim(0,240); ax.set_ylim(0,140); ax.axis('off')
def zone(x,y,w,h,t,fc='#f3f5f8'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.6,rounding_size=2',fc=fc,ec='#9aa3ad',lw=1.5))
    ax.text(x+1.5,y+h-1.5,t,fontsize=13,weight='bold',color='#4a5560',va='top')
def board(x,y,w,t,pins,fc='#ffffff',side='r'):
    h=4.2+3.0*len(pins)
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.3,rounding_size=1',fc=fc,ec='#333',lw=1.4))
    ax.text(x+w/2,y+h-1.8,t,fontsize=10.5,ha='center',va='center',weight='bold')
    for k,(pin,net) in enumerate(pins):
        py=y+h-5.0-3.0*k
        if side=='r':
            ax.text(x+w-0.8,py,pin,fontsize=8.5,ha='right',va='center'); ax.plot([x+w,x+w+3],[py,py],color='#333',lw=1.2)
            tag(x+w+3,py,net,'l')
        else:
            ax.text(x+0.8,py,pin,fontsize=8.5,ha='left',va='center'); ax.plot([x-3,x],[py,py],color='#333',lw=1.2)
            tag(x-3,py,net,'r')
    return h
def tag(x,y,net,anchor):
    c=NET[net]; w=1.25*len(net)+2.2
    x0=x if anchor=='l' else x-w
    ax.add_patch(FancyBboxPatch((x0,y-1.1),w,2.2,boxstyle='round,pad=0.05,rounding_size=0.6',fc=c,ec=c))
    ax.text(x0+w/2,y,net,fontsize=7.8,ha='center',va='center',color='white',weight='bold')
def bundle(a,b,t,c='#6b7684'):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='<|-|>,head_width=0.6,head_length=1.2',mutation_scale=12,lw=5,color=c,alpha=0.45,zorder=0))
    ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+1.6,t,fontsize=8.5,ha='center',va='bottom',color='#333',
            bbox=dict(boxstyle='round,pad=0.25',fc='white',ec='#c4cbd3'))
ax.text(120,137,'Begode Master headlamp v6.4: wiring',fontsize=18,weight='bold',ha='center')
ax.text(120,133,'Pins with the same tag are joined. Boards are drawn where they sit; the grey arrows are the wire bundles and the hole each goes through.',fontsize=11,ha='center',color='#4a5560')
zone(3,8,70,118,'LEFT SIDE BAY'); zone(85,8,70,118,'ELECTRONICS BOX'); zone(167,8,70,118,'RIGHT SIDE BAY')
# left bay
y=100
for k in range(3):
    board(6,y-k*20,24,'LDD-1500L #%d'%(k+1),[('VIN+','PWR'),('VIN-','GND'),('DIM','DIM'),('LED+','LED%d+'%(k+1)),('LED-','LED%d-'%(k+1))],'#fff4e6')
board(6,38,24,'MP1584 #1 (set 5.0 V)',[('IN+','PWR'),('IN-','GND'),('OUT+','5V'),('OUT-','GND')],'#fff4e6')
board(6,13,24,'MPU-6050',[('VCC','3V3'),('GND','GND'),('SDA','SDA'),('SCL','SCL')],'#e8f1fb')
ax.text(18,11.0,'flat, X arrow forward, on foam tape',fontsize=7.5,ha='center',color='#4a5560')
board(53,106,18,'wheel lamp plug',[('+','BAT+'),('-','GND')],'#fde8e8',side='l')
board(53,78,18,'LED 1 / 2 / 3',[('1 +','LED1+'),('1 -','LED1-'),('2 +','LED2+'),('2 -','LED2-'),('3 +','LED3+'),('3 -','LED3-')],'#f1e8fb',side='l')
board(53,60,18,'NTC (bar face)',[('a','NTC'),('b','GND')],'#f1e8fb',side='l')
board(53,42,18,'DRL strip, left',[('+','5V'),('-','DRL-')],'#fbe8f4',side='l')
board(53,16,18,'VL53L1X',[('VIN','3V3'),('GND','GND'),('SDA','SDA'),('SCL','SCL')],'#fde6ef',side='l')
ax.text(62,13.8,'in its hood at the face',fontsize=7.5,ha='center',color='#4a5560')
# electronics box
board(92,58,26,'ESP32-C3 SuperMini',[('5V','5V'),('GND','GND'),('3V3','3V3'),('GPIO5','DIM'),('GPIO3','NTC'),('GPIO1','LDR'),('GPIO6','SDA'),
      ('GPIO7','SCL'),('GPIO10','SERVO'),('GPIO4','DRL_EN'),('GPIO0','USB_EN'),('GPIO20','BTN+'),('GPIO21','BTN-'),
      ('GPIO8','HUP'),('GPIO9','HDN')],'#e8f6ea')
board(92,36,26,'resistors',[('10k 3V3-','3V3'),('to GPIO3','NTC'),('10k GPIO1-','LDR'),('to GND','GND')],'#ffffff')
board(92,14,26,'chin buttons',[('+ a','BTN+'),('- a','BTN-'),('b (both)','GND')],'#eeeeee')
ax.text(105,11.4,'in the button box, nuts reached from the electronics box',fontsize=7.5,ha='center',color='#4a5560')
# right bay
board(130,96,22,'INA219',[('VIN+','BAT+'),('VIN-','PWR'),('VCC','3V3'),('GND','GND'),('SDA','SDA'),('SCL','SCL')],'#e8f1fb')
board(170,86,26,'MP1584 #2 (set 5.1 V)',[('IN+','PWR'),('IN-','USB_SW'),('OUT+','USB+'),('OUT-','USB-')],'#fff4e6')
board(170,63,26,'MOSFET #2 (USB)',[('gate','USB_EN'),('load -','USB_SW'),('supply -','GND')],'#eeeeee')
board(170,40,26,'MOSFET #1 (DRL)',[('gate','DRL_EN'),('load -','DRL-'),('supply -','GND')],'#eeeeee')
board(170,12,26,'MG90S servo',[('signal','SERVO'),('+','5V'),('-','GND')],'#e8eefb')
board(218,100,17,'USB-C (handle)',[('VBUS','USB+'),('GND','USB-'),('CC1 22k','USB+'),('CC2 22k','USB+')],'#e6f7fa',side='l')
board(218,76,17,'DRL strip, right',[('+','5V'),('-','DRL-')],'#fbe8f4',side='l')
board(218,52,17,'LDR (face)',[('a','3V3'),('b','LDR')],'#eeeeee',side='l')
board(218,24,17,'handle buttons',[('▲ a','HUP'),('▼ a','HDN'),('b (both)','GND')],'#f3ebe6',side='l')
ax.text(226.5,21.6,'C&K KSC6 on the leg,\nby the USB port',fontsize=7.5,ha='center',va='top',color='#4a5560')
ax.text(226.5,98,'22 k from CC1 and CC2\nto VBUS, at the socket',fontsize=7.5,ha='center',va='top',color='#4a5560')
# bundles and holes
bundle((72,36),(86,36),'floor slot, left\n2.3 x 10 mm\nBAT+, PWR, GND,\n5V, 3V3, DIM,\nNTC, SDA, SCL,\nDRL-')
bundle((154,36),(168,36),'floor slot, right\n5 x 10 mm\nPWR, GND, 5V,\n3V3, SERVO,\nDRL_EN, USB_EN,\nLDR, DRL-,\nHUP, HDN')
ax.text(38,130,'Into the left bay: the LED and NTC wires from the bar, through the hole in the left pivot pocket;\nthe wheel\'s power cable through the grommet in the back wall.',fontsize=8.5,ha='center',va='top',color='#4a5560')
ax.text(202,130,'Out of the right bay: the USB wire and the buttons\' three, through the grommet in the side floor, into the handle.\nDRL strips: the left one\'s wires cross by the box.',fontsize=8.5,ha='center',va='top',color='#4a5560')
L=[('BAT+','wheel power'),('GND','common ground'),('5V','5.0 V'),('3V3','3.3 V'),('DIM','signals'),('SDA','I2C'),
   ('LED1+','LEDs, a driver each'),('DRL-','DRL, switched -'),('USB+','USB, own ground'),('HUP','handle buttons')]
for k,(n,t) in enumerate(L): ax.add_patch(FancyBboxPatch((4+k*23.5,1.0),3,1.6,boxstyle='round,pad=0.05',fc=NET[n],ec=NET[n])); ax.text(8+k*23.5,1.8,t,fontsize=8,va='center')
plt.savefig('../current/renders/wiring_diagram.png',dpi=110,bbox_inches='tight'); print('ok')
