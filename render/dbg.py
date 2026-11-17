# python dbg.py -- shot t [shot t ...] : which body parts hit which house polygons
import bpy, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import *
import shots
from mathutils import Vector
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index('--') + 1:]
meta = json.load(open(os.path.join(ROOT, 'assets', 'voice', 'story.json')))
G = build(res=(320, 180), spp=1); dg = bpy.context.evaluated_depsgraph_get()
skip = set()
for c in [G['kid'], G['dad'], G['mom'], G['cat']] + G.get('friends', []): skip |= {o.name for o in [c.root] + list(c.root.children_recursive)}
verts, polys, cen = [], [], []
for o in bpy.data.objects:
    if o.type != 'MESH' or o.name in skip or o.name.startswith(('jar','cake','cookie','slice','toy','duck','plate','candle','flame','chip')): continue
    me = o.evaluated_get(dg).to_mesh(); M = o.matrix_world; b = len(verts); vs = [M @ v.co for v in me.vertices]; verts += vs
    N3 = M.to_3x3().inverted().transposed()
    for p in me.polygons:
        n = (N3 @ p.normal).normalized(); zs = [vs[i].z for i in p.vertices]
        if abs(n.z) < .6 and max(zs) - min(zs) > .3: polys.append([b + i for i in p.vertices]); c = sum((vs[i] for i in p.vertices), Vector()) / len(p.vertices); cen.append((c, n))
    o.evaluated_get(dg).to_mesh_clear()
H = BVHTree.FromPolygons(verts, polys, all_triangles=False)
for k in range(0, len(a), 2):
    n, t = a[k], float(a[k + 1]); m = next(x for x in meta if x['shot'] == n); L = m['dur'] + m['gap']
    shots.reset(G); shots.SHOTS[n](t, G, L); bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    print('=====', n, t)
    for c in [G['kid'], G['dad'], G['mom']] + G.get('friends', []):
        if c.hidden: continue
        for o in [c.root] + list(c.root.children_recursive):
            if o.type != 'MESH' or o.hide_render or '_f_' in o.name: continue
            me = o.evaluated_get(dg).to_mesh(); M = o.matrix_world
            vs = [M @ v.co for v in me.vertices]; ps = [list(p.vertices) for p in me.polygons]; o.evaluated_get(dg).to_mesh_clear()
            if not ps: continue
            hits = BVHTree.FromPolygons(vs, ps).overlap(H)
            if not hits: continue
            cs = [cen[j][0] for _, j in hits]
            xs, ys, zs = [q.x for q in cs], [q.z for q in cs], [-q.y for q in cs]
            ns = {(round(cen[j][1].x, 1), round(cen[j][1].y, 1)) for _, j in hits}
            print(f'  {o.name:14s} {len(hits):4d}  x {min(xs):.1f}..{max(xs):.1f}  y {min(ys):.1f}..{max(ys):.1f}  z {min(zs):.1f}..{max(zs):.1f}  normals(xz) {list(ns)[:3]}')
