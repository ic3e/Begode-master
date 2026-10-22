import trimesh, sys, numpy as np
for p in sys.argv[1:]:
    m = trimesh.load(p)
    print(p.split('/')[-1], 'faces', len(m.faces), 'watertight', m.is_watertight)
    print(' bounds', m.bounds.round(2), 'extents', m.extents.round(2))
    print(' volume cm3', round(m.volume/1000,2), 'bodies', len(m.split(only_watertight=False)))
