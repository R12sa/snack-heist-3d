# Quick look at a town: python render/town_preview.py -- seed theme time out.jpg
import bpy, sys, os, json, time, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import town, scene
a = sys.argv[sys.argv.index('--') + 1:]
seed, theme, tod, out = int(a[0]), a[1], a[2], a[3]
t0 = time.time()
bpy.ops.wm.read_factory_settings(use_empty=True)
lay = town.build_town(seed=seed, theme=theme, time=tod, size=3)
print('built in', round(time.time() - t0, 2), 's', len(lay['houses']), 'buildings')
kid, dad, mom = make_cast()
h = lay['houses'][0]; d = V(*h['door'])
kid.pose(d, h['faces_yaw'] + math.pi); kid.setface('happy')
c = camera(); S = bpy.context.scene
look(c, 160, 120, -160, 0, 0, 0, 42)
scene._render_settings(S, (960, 540), 6)
S.render.filepath = out; bpy.ops.render.render(write_still=True)
f = h['faces_yaw']; look(c, d.x + math.sin(f) * 22 + 8, 9, d.z + math.cos(f) * 22, d.x, 5, d.z, 45)
S.render.filepath = out.replace('.jpg', '_close.jpg'); bpy.ops.render.render(write_still=True)
print('total', round(time.time() - t0, 1))
