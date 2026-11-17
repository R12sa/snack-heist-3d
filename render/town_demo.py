# 6-second test: the kid walks down a sidewalk in a new town, camera follows.
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import town, scene
a = sys.argv[sys.argv.index('--') + 1:]
seed, theme, tod, out = int(a[0]), a[1], a[2], a[3]
bpy.ops.wm.read_factory_settings(use_empty=True)
lay = town.build_town(seed=seed, theme=theme, time=tod, size=3)
kid, dad, mom = make_cast(); c = camera(); S = bpy.context.scene
r = lay['roads_x'][1]; wz = lay['roads_z'][1] + 22 / 2 + 3          # walk along the sidewalk next to a road
pts = [V(r + 16, .4, wz), V(r + 80, .4, wz)]
N = 144
def h(scene, *x):
    t = (scene.frame_current - 1) / 24; k = t / 6
    p = kid.walk(pts, k, 1, .7); kid.setface('happy' if t < 3 else 'sneaky')
    look(c, p.x - 14 + 4 * k, 7.5, p.z + 16, p.x + 3, 4.5, p.z, 44)
bpy.app.handlers.frame_change_pre.append(h)
scene._render_settings(S, (800, 450), 4)
S.frame_start, S.frame_end = 1, N; S.render.filepath = out + '/f_'
bpy.ops.render.render(animation=True)
