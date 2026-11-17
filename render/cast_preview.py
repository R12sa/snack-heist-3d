# Turntable-ish look at the cast: python render/cast_preview.py -- out.jpg
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import scene, town
out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
town.build_town(seed=7, theme='suburb', time='day', size=1)
kid, dad, mom = make_cast(); cat = Cat()
x0 = 52
kid.pose(V(x0, .4, 0), .25, 1.0, .6); kid.setface('happy')
dad.pose(V(x0 - 6, .4, -1), .35, armR=-1.2); dad.setface('smile')
mom.pose(V(x0 + 6, .4, -1), .15, armL=-.6); mom.setface('sneaky')
cat.pose(V(x0 + 2.5, .4, 3), 0, sit=1)
c = camera(); S = bpy.context.scene
look(c, x0 + 3, 6.5, 22, x0, 4.2, 0, 34)
scene._render_settings(S, (1280, 720), 12)
S.render.filepath = out; bpy.ops.render.render(write_still=True)
look(c, x0 + 1.2, 5.4, 6.5, x0, 4.9, 0, 26)
S.render.filepath = out.replace('.jpg', '_kid.jpg'); bpy.ops.render.render(write_still=True)
