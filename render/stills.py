# Still frames for checking shots: python render/stills.py -- shot1,shot2 0.3,0.8 outdir
import bpy, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import *
import shots
a = sys.argv[sys.argv.index('--') + 1:]
names, fr, out = a[0].split(','), [float(x) for x in a[1].split(',')], a[2]
meta = {m['shot']: m for m in json.load(open(os.path.join(ROOT, 'assets', 'voice', 'story.json')))}
G = build(res=(640, 360), spp=4); os.makedirs(out, exist_ok=True)
for n in names:
    L = meta[n]['dur'] + meta[n]['gap'] if n in meta else 3.0
    for f in fr:
        shots.reset(G); shots.SHOTS[n](f * L, G, L); bpy.context.view_layer.update()
        G['S'].render.filepath = os.path.join(out, f'{n}_{int(f*100):02d}.jpg'); bpy.ops.render.render(write_still=True)
