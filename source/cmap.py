exec(open('build3.py').read().split("if __name__")[0])
ring=ring_lever(); bask=basket_lever(); pl=plate()
T1=list(range(0,-91,-10)); T2=list(range(0,91,10))
print('      '+''.join(f'{t:5d}' for t in T2)+'   <- basket angle')
for t1 in T1:
    r=rot_about(ring,A,t1)
    row=''
    for t2 in T2:
        b=rot_about(bask,B,t2)
        v=(r^b).volume()+(b^pl).volume()+(r^pl).volume()
        row+='    .' if v<0.05 else f'{min(v,9999):5.0f}'
    print(f'{t1:5d} '+row)
