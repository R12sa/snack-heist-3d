# Finds problems in every shot before rendering:
#   - characters going through walls or furniture (mesh overlap with the house, floors ignored)
#   - the camera stuck inside something / the main character blocked from view
# python render/check.py -- [shot1,shot2|all] [step_seconds]
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import *
import shots
try:
    import shots_show; SOFT = getattr(shots_show, 'SOFT', [])
except Exception: SOFT = []
from mathutils import Vector
from mathutils.bvhtree import BVHTree

a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
meta = json.load(open(os.path.join(ROOT, 'assets', 'voice', 'story.json')))
names = [m['shot'] for m in meta] if not a or a[0] == 'all' else a[0].split(',')
step = float(a[1]) if len(a) > 1 else .2
G = build(res=(320, 180), spp=1)
dg = bpy.context.evaluated_depsgraph_get()
char_objs = set()
for c in [G['kid'], G['dad'], G['mom']] + G.get('friends', []):
    char_objs |= {o.name for o in [c.root] + list(c.root.children_recursive)}
for k in ('cat',):
    char_objs |= {o.name for o in [G['cat'].root] + list(G['cat'].root.children_recursive)}
prop_objs = set()
for o in bpy.data.objects:
    if o.name.startswith(('jar', 'cake', 'cookie', 'slice', 'toy', 'duck', 'plate', 'candle', 'flame', 'chip')): prop_objs.add(o.name)

# static house BVH (walls only = polygons that are not floors/ceilings)
verts, polys, wall = [], [], []
for o in bpy.data.objects:
    if o.type != 'MESH' or o.name in char_objs or o.name in prop_objs: continue
    me = o.evaluated_get(dg).to_mesh(); M = o.matrix_world; base = len(verts)
    verts += [M @ v.co for v in me.vertices]
    N3 = M.to_3x3().inverted().transposed()
    for p in me.polygons:
        polys.append([base + i for i in p.vertices]); n = (N3 @ p.normal).normalized()
        zs = [verts[base + i].z for i in p.vertices]; c = sum((verts[base + i] for i in p.vertices), Vector()) / len(p.vertices)
        soft = any(b[0] <= c.x <= b[1] and b[2] <= c.z <= b[3] and b[4] <= -c.y <= b[5] for b in SOFT)
        # walls only: steep faces taller than a rug edge, not inside soft things (pillows)
        wall.append(abs(n.z) < .6 and max(zs) - min(zs) > .3 and not soft)
    o.evaluated_get(dg).to_mesh_clear()
HOUSE = BVHTree.FromPolygons(verts, polys, all_triangles=False)
print('house polys', len(polys), flush=True)

def char_bvh(c):
    vs, ps = [], []
    for o in [c.root] + list(c.root.children_recursive):
        if o.type != 'MESH' or o.hide_render or '_f_' in o.name or '_fl' in o.name: continue
        me = o.evaluated_get(dg).to_mesh(); M = o.matrix_world; b = len(vs)
        vs += [M @ v.co for v in me.vertices]; ps += [[b + i for i in p.vertices] for p in me.polygons]
        o.evaluated_get(dg).to_mesh_clear()
    return BVHTree.FromPolygons(vs, ps) if ps else None

report = []
for n in names:
    m = next(x for x in meta if x['shot'] == n); L = m['dur'] + m['gap']
    bad = {}
    t = 0.
    while t <= L + 1e-6:
        shots.reset(G); shots.SHOTS[n](t, G, L); bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        for c in [G['kid'], G['dad'], G['mom']] + G.get('friends', []):
            if c.hidden: continue
            cb = char_bvh(c)
            if not cb: continue
            hits = [j for i, j in cb.overlap(HOUSE) if wall[j]]
            if hits:
                p = c.root.matrix_world.translation
                bad.setdefault(c.name, []).append((round(t, 2), len(hits), (round(p.x, 1), round(p.z, 1), round(-p.y, 1))))
        # camera: inside something, or kid blocked
        cam = G['cam']; cp = cam.matrix_world.translation
        fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
        hit = HOUSE.ray_cast(cp, fwd, .6)
        if hit[0] is not None: bad.setdefault('CAMERA_IN_WALL', []).append(round(t, 2))
        if not G['kid'].hidden:
            hp = G['kid'].head.matrix_world @ Vector((0, 0, .6)); d = hp - cp
            h2 = HOUSE.ray_cast(cp, d.normalized(), d.length - .8)
            if h2[0] is not None: bad.setdefault('KID_BLOCKED', []).append(round(t, 2))
        t += step
    status = 'OK' if not bad else 'PROBLEM'
    print(f'{status:8s} {n}', flush=True)
    for k, v in bad.items(): print('    ', k, v[:6], ('... +%d' % (len(v) - 6)) if len(v) > 6 else '', flush=True)
    report.append(dict(shot=n, problems=bad))
json.dump(report, open(os.path.join(ROOT, 'check_report.json'), 'w'), indent=1)
