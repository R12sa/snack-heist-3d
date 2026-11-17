# Build the walk grid for the house once: python render/nav_build.py
import bpy, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene, world
from lib import V
scene.load_house()
t = time.time(); world.init('/nonexistent')
print('bvh', round(time.time() - t, 1), flush=True)
t = time.time(); nav = world.build_nav(240, 362, -40, 27, 1.0, r=float(os.environ.get("NAV_R", "1.5")))
print('nav', round(time.time() - t, 1), len(nav['cells']), flush=True)
world.save_nav(nav, os.path.join(scene.ROOT, 'assets', 'nav_house.json'))
for nm, x, z in [('kidbed_TL', 266.5, -33), ('kidbed_TR', 277, -33), ('kidbed_BL', 266.5, -1), ('parentsbed', 325, -31), ('island', 321, -21), ('table', 322, 14.5), ('couch_seat', 276, -19), ('couch_back', 276, -18.0)]:
    print(nm, [round(world.ground(x, z, b), 2) for b in (12, 28)])
