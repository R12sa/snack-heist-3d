# World helpers for the real house: floor height under any point, and paths that go around walls/furniture.
#   ground(x, z, below=None)       -> floor height (Roblox y) under a point
#   route(a, b)                    -> list of V points from a to b that never cross walls (uses a walk grid)
#   clear_line(a, b)               -> True if a character can walk straight from a to b
# The walk grid is cached in assets/nav_<place>.json so every computer gets the same paths.
import bpy, os, json, math, heapq
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from lib import B, V

BVH = None; WALL = None; NAV = None; NAVPATH = None
SKIP_PREFIX = ('kid', 'dad', 'mom', 'f1', 'f2', 'f3', 'cat', 'jar', 'cake', 'cookie', 'slice', 'toy', 'duck', 'plate', 'candle', 'flame', 'chip', 'cam')

def init(nav_path):
    """build the collision tree from all static meshes, load/build the walk grid"""
    global BVH, WALL, NAVPATH
    dg = bpy.context.evaluated_depsgraph_get(); verts, polys, wall = [], [], []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.startswith(SKIP_PREFIX) or o.parent is not None and o.parent.name.startswith(SKIP_PREFIX): continue
        me = o.evaluated_get(dg).to_mesh(); M = o.matrix_world; b = len(verts)
        verts += [M @ v.co for v in me.vertices]; N3 = M.to_3x3().inverted().transposed()
        for p in me.polygons:
            polys.append([b + i for i in p.vertices]); wall.append(abs((N3 @ p.normal).normalized().z) < .6)
        o.evaluated_get(dg).to_mesh_clear()
    BVH = BVHTree.FromPolygons(verts, polys, all_triangles=False); WALL = wall; NAVPATH = nav_path
    if os.path.exists(nav_path): _load(nav_path)

def ground(x, z, below=None):
    """highest floor at (x,z) under height `below` (Roblox y). None if nothing."""
    top = 60 if below is None else below
    h = BVH.ray_cast(B(x, top, z), Vector((0, 0, -1)), 80)
    return None if h[0] is None else h[0].z

def ray_free(a, b):
    """straight segment a->b (Roblox coords) hits nothing"""
    pa, pb = B(a.x, a.y, a.z), B(b.x, b.y, b.z); d = pb - pa
    return BVH.ray_cast(pa, d.normalized(), d.length)[0] is None

def clear_line(a, b, r=1.1):
    """a character (radius r) can walk straight from a to b: test at knee and chest, centre and both sides"""
    d = Vector((b.x - a.x, 0, b.z - a.z))
    if d.length < 1e-3: return True
    side = Vector((-d.z, 0, d.x)).normalized() * r
    for hgt in (1.0, 3.4):
        for s in (-1, 0, 1):
            o = Vector((side.x * s, hgt, side.z * s))
            if not ray_free(V(a.x + o.x, a.y + o.y, a.z + o.z), V(b.x + o.x, b.y + o.y, b.z + o.z)): return False
    return True

# ---------------- walk grid ----------------
def build_nav(x0, x1, z0, z1, step=1.0, r=1.1):
    """grid of standable cells with all floor heights at each (x,z) (handles stairs and 2 floors)"""
    cells = {}
    nx, nz = int((x1 - x0) / step) + 1, int((z1 - z0) / step) + 1
    for i in range(nx):
        for j in range(nz):
            x, z = x0 + i * step, z0 + j * step; y = 60.
            while True:
                h = BVH.ray_cast(B(x, y, z), Vector((0, 0, -1)), 80)
                if h[0] is None: break
                fy = h[0].z
                up = BVH.ray_cast(B(x, fy + .05, z), Vector((0, 0, 1)), 6)
                head_ok = up[0] is None or up[0].z - fy > 5.2
                if h[1].z > .7 and head_ok and fy > -3:
                    # keep away from walls: 8 short rays at knee and chest
                    ok = True
                    for k in range(8):
                        a = k * math.pi / 4; dv = Vector((math.cos(a), math.sin(a), 0))
                        for hh in (.9, 3.2):
                            if BVH.ray_cast(B(x, fy + hh, z), dv, r)[0] is not None: ok = False; break
                        if not ok: break
                    if ok: cells.setdefault((i, j), []).append(round(fy, 2))
                y = fy - .3
                if y < -3: break
    return dict(x0=x0, z0=z0, step=step, nx=nx, nz=nz, cells={f'{i},{j}': v for (i, j), v in cells.items()})

def save_nav(nav, path):
    json.dump(nav, open(path, 'w')); _load(path)

def _load(path):
    global NAV
    NAV = json.load(open(path)); NAV['_c'] = {tuple(map(int, k.split(','))): v for k, v in NAV['cells'].items()}

def _node(p):
    s = NAV['step']; i, j = round((p.x - NAV['x0']) / s), round((p.z - NAV['z0']) / s)
    best = None
    for di in range(-3, 4):
        for dj in range(-3, 4):
            for y in NAV['_c'].get((i + di, j + dj), []):
                d = (di * di + dj * dj) * s * s + ((y - p.y) * 2) ** 2
                if best is None or d < best[0]: best = (d, (i + di, j + dj, y))
    return best[1] if best else None

def route(a, b, smooth=True):
    """shortest walkable path from a to b (V points, y = floor height)"""
    s = NAV['step']; A, Bn = _node(a), _node(b)
    if A is None or Bn is None: return [a, b]
    def pos(n): return V(NAV['x0'] + n[0] * s, n[2], NAV['z0'] + n[1] * s)
    openq = [(0, A)]; came = {A: None}; g = {A: 0}
    while openq:
        _, cur = heapq.heappop(openq)
        if cur == Bn: break
        i, j, y = cur
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if not di and not dj: continue
                for y2 in NAV['_c'].get((i + di, j + dj), []):
                    if abs(y2 - y) > 1.3: continue
                    if di and dj and not (any(abs(q - y) < 1.3 for q in NAV['_c'].get((i + di, j), [])) and any(abs(q - y) < 1.3 for q in NAV['_c'].get((i, j + dj), []))): continue
                    nb = (i + di, j + dj, y2); c = g[cur] + math.hypot(di, dj) * s + abs(y2 - y)
                    if c < g.get(nb, 1e9):
                        g[nb] = c; came[nb] = cur
                        h = math.hypot(nb[0] - Bn[0], nb[1] - Bn[1]) * s + abs(nb[2] - Bn[2])
                        heapq.heappush(openq, (c + h, nb))
    if Bn not in came: return [a, b]
    path = []; n = Bn
    while n: path.append(pos(n)); n = came[n]
    path.reverse(); path[0] = V(a.x, path[0].y, a.z); path[-1] = V(b.x, path[-1].y, b.z)
    if not smooth: return path
    out = [path[0]]; k = 0
    while k < len(path) - 1:
        far = k + 1
        for m in range(len(path) - 1, k, -1):     # furthest point we can walk to in a straight line on the same floor
            if all(abs(path[q].y - path[k].y) < .05 for q in range(k, m + 1)) and clear_line(path[k], path[m], .9): far = m; break
        if far == k + 1 or abs(path[far].y - path[k].y) > .05:
            far = k + 1
        out.append(path[far]); k = far
    return out
