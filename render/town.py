# Town maker: builds a brand-new Roblox-style town in seconds from a seed.
#   build_town(seed=7, theme='suburb', time='day', size=3) -> layout dict (spots for shots)
# Themes: suburb, city, beach, snow.  Time: day, sunset, night.
# All coordinates are Roblox-style studs (x, y up, z); ground top is y = 0.
import bpy, bmesh, math, random, json, os
from mathutils import Vector, Matrix
from lib import B, srgb, link, mat

ROAD, WALK, BLOCK = 22.0, 6.0, 72.0          # road width, sidewalk width, block size (lot area)
CELL = BLOCK + ROAD

THEMES = {
    'suburb': dict(ground=0x5fa84a, walls=[0xf2e6d0, 0xd9e8f5, 0xf5d6d6, 0xe9f2d0, 0xfff1b8, 0xcfd8e3, 0xf0d2b4], roofs=[0x8a3b2e, 0x3d4a5c, 0x5a4636, 0x2f5d4a, 0x7a2f3b],
                   tree='round', leaf=[0x3f8f3a, 0x4fa040, 0x2f7a35], lots=3, tall=False, sand=False, snow=False, water=False),
    'city':   dict(ground=0x8a8f96, walls=[0x9aa3ad, 0xc9b9a3, 0x7d8a99, 0xb3a28f, 0x5e6b7a, 0xd8d2c4], roofs=[0x4a4f57, 0x3a3f46],
                   tree='round', leaf=[0x3f8f3a, 0x4a9a42], lots=2, tall=True, sand=False, snow=False, water=False),
    'beach':  dict(ground=0xe8d29a, walls=[0xffffff, 0xbfe9f2, 0xffd6c9, 0xfff2b0, 0xc8f2d0, 0xf7c6e6], roofs=[0x2fa3c4, 0xe8743b, 0x3c7fbf, 0xf2c14e],
                   tree='palm', leaf=[0x3c9a3c, 0x55b046], lots=3, tall=False, sand=True, snow=False, water=True),
    'snow':   dict(ground=0xf2f6fa, walls=[0x8c4a3a, 0x6e5a4a, 0xd9cbb8, 0x4f6a80, 0xa63d3d, 0xe8e0d0], roofs=[0xffffff],
                   tree='pine', leaf=[0x2d5e3a, 0x356b43], lots=3, tall=False, sand=False, snow=True, water=False),
}

class MeshBuilder:
    """Collects boxes/wedges/cylinders/spheres into a few big meshes (fast to build and render)."""
    def __init__(s): s.groups = {}
    def _g(s, kind):
        if kind not in s.groups:
            bm = bmesh.new(); s.groups[kind] = (bm, bm.loops.layers.color.new('Col'))
        return s.groups[kind]
    def _add(s, kind, vs, fs, col, m):
        bm, cl = s._g(kind); c = (*srgb(col), 1)
        bv = [bm.verts.new(B(*(m @ Vector(v)))) for v in vs]
        for f in fs:
            try:
                ff = bm.faces.new([bv[i] for i in f])
                for l in ff.loops: l[cl] = c
            except ValueError: pass
    @staticmethod
    def M(x, y, z, sx, sy, sz, yaw=0.):
        return Matrix.Translation((x, y, z)) @ Matrix.Rotation(yaw, 4, 'Y') @ Matrix.Diagonal((sx, sy, sz, 1))
    def box(s, x, y, z, sx, sy, sz, col, yaw=0., kind='solid'):
        """x,z = center; y = BOTTOM"""
        vs = [(a, b, c) for a in (-.5, .5) for b in (0, 1) for c in (-.5, .5)]
        fs = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        s._add(kind, vs, fs, col, s.M(x, y, z, sx, sy, sz, yaw))
    def gable(s, x, y, z, sx, sy, sz, col, yaw=0., kind='solid'):
        """triangular roof prism, ridge along local x; y = bottom"""
        vs = [(-.5, 0, -.5), (.5, 0, -.5), (.5, 0, .5), (-.5, 0, .5), (-.5, 1, 0), (.5, 1, 0)]
        fs = [(0, 1, 2, 3), (0, 4, 5, 1), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2)]
        s._add(kind, vs, fs, col, s.M(x, y, z, sx, sy, sz, yaw))
    def cyl(s, x, y, z, r, h, col, n=12, kind='solid', r2=None):
        r2 = r if r2 is None else r2
        vs = [(math.cos(2*math.pi*i/n)*r, 0, math.sin(2*math.pi*i/n)*r) for i in range(n)] + \
             [(math.cos(2*math.pi*i/n)*r2, h, math.sin(2*math.pi*i/n)*r2) for i in range(n)]
        fs = [(i, (i+1) % n, n+(i+1) % n, n+i) for i in range(n)] + [tuple(range(n))[::-1], tuple(range(n, 2*n))]
        s._add(kind, vs, fs, col, Matrix.Translation((x, y, z)))
    def ball(s, x, y, z, r, col, kind='solid', squash=1.):
        nu, nv = 12, 8; vs = [(0, -r*squash, 0)]; fs = []
        for j in range(1, nv):
            t = math.pi*j/nv
            for i in range(nu):
                a = 2*math.pi*i/nu; vs.append((r*math.sin(t)*math.cos(a), -r*squash*math.cos(t), r*math.sin(t)*math.sin(a)))
        vs.append((0, r*squash, 0)); top = len(vs)-1
        for i in range(nu): fs.append((0, 1+(i+1) % nu, 1+i))
        for j in range(nv-2):
            for i in range(nu):
                a = 1+j*nu+i; b = 1+j*nu+(i+1) % nu; fs.append((a, b, b+nu, a+nu))
        base = 1+(nv-2)*nu
        for i in range(nu): fs.append((base+i, base+(i+1) % nu, top))
        s._add(kind, vs, fs, col, Matrix.Translation((x, y, z)))
    def finish(s, time):
        night = time == 'night'
        for kind, (bm, cl) in s.groups.items():
            me = bpy.data.meshes.new('town_'+kind); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
            o = bpy.data.objects.new('town_'+kind, me); link(o)
            m = bpy.data.materials.new('tm_'+kind); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
            vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'; nt.links.new(vc.outputs[0], b.inputs['Base Color'])
            b.inputs['Roughness'].default_value = {'solid': .7, 'shiny': .25, 'glass': .08, 'water': .05, 'emit': .5, 'win': .15}.get(kind, .7)
            if kind == 'glass': b.inputs['Alpha'].default_value = .35
            if kind == 'water': b.inputs['Roughness'].default_value = .03; b.inputs['Specular IOR Level'].default_value = .8
            if kind == 'emit' or (kind == 'win' and night):
                nt.links.new(vc.outputs[0], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 3. if kind == 'emit' else 1.6
            if kind == 'win' and not night:
                b.inputs['Base Color'].default_value = (.08, .12, .18, 1)
                nt.links.remove(b.inputs['Base Color'].links[0]); b.inputs['Specular IOR Level'].default_value = .9
            o.data.materials.append(m)

def build_town(seed=7, theme='suburb', time='day', size=3, specials=('school', 'gas', 'shop')):
    rnd = random.Random(seed); T = THEMES[theme]; mb = MeshBuilder()
    night = time == 'night'
    n = size; span = n * CELL + ROAD; half = span / 2
    lay = dict(seed=seed, theme=theme, time=time, size=size, ground_y=0.0, walk_y=.4, houses=[], specials={}, roads_x=[], roads_z=[], intersections=[],
               note='coords are Roblox-style (x, y up, z). Characters stand on y=0 on roads/grass, y=0.4 on sidewalks.')
    # ground
    mb.box(0, -2, 0, span + 400, 2, span + 400, T['ground'])
    if T['water']:
        mb.box(0, -1.5, half + 160, span + 400, 1.6, 300, 0x2a8fc4, kind='water')
        mb.box(0, -1.9, half + 30, span + 400, 1.95, 30, 0xf0dca8)
    # roads: lines at x = -half + ROAD/2 + i*CELL
    lines = [-half + ROAD / 2 + i * CELL for i in range(n + 1)]
    for c in lines:
        mb.box(c, 0, 0, ROAD, .05, span, 0x3a3d42); mb.box(0, 0, c, span, .05, ROAD, 0x3a3d42)
        lay['roads_x'].append(round(c, 2)); lay['roads_z'].append(round(c, 2))
        for k in range(int(span // 12)):
            p = -half + 6 + k * 12
            if all(abs(p - q) > ROAD / 2 + 2 for q in lines):
                mb.box(c, .05, p, .5, .02, 5, 0xf2c94c); mb.box(p, .05, c, 5, .02, .5, 0xf2c94c)
    for a in lines:
        for b in lines:
            lay['intersections'].append([round(a, 2), round(b, 2)])
            if not night or rnd.random() < 2:  # streetlights at intersections
                lx, lz = a + ROAD / 2 + 1.5, b + ROAD / 2 + 1.5
                mb.cyl(lx, 0, lz, .35, 16, 0x2b2b2b); mb.box(lx - 1.8, 15.6, lz, 4, .6, .8, 0x2b2b2b)
                mb.box(lx - 3.2, 15.2, lz, 1.4, .4, 1.0, 0xfff3c4, kind='emit')
                if night:
                    ld = bpy.data.lights.new('street', 'POINT'); ld.energy = 2500; ld.color = srgb(0xffc97a); ld.shadow_soft_size = .5
                    lo = bpy.data.objects.new('street', ld); link(lo); lo.location = B(lx - 3.2, 14.6, lz)
    # blocks
    blocks = [(lines[i] + ROAD / 2 + BLOCK / 2, lines[j] + ROAD / 2 + BLOCK / 2) for i in range(n) for j in range(n)]
    order = list(range(len(blocks))); rnd.shuffle(order)
    special_blocks = {sp: blocks[order[k]] for k, sp in enumerate(specials) if k < len(blocks) - 1}
    for bi, (bx, bz) in enumerate(blocks):
        # sidewalk ring + inner lawn
        for sgn in (-1, 1):
            mb.box(bx, 0, bz + sgn * (BLOCK / 2 - WALK / 2), BLOCK, .4, WALK, 0xc9c6bf)
            mb.box(bx + sgn * (BLOCK / 2 - WALK / 2), 0, bz, WALK, .4, BLOCK - 2 * WALK, 0xc9c6bf)
        inner = BLOCK - 2 * WALK
        mb.box(bx, 0, bz, inner, .3, inner, (0xf6f8fb if T['snow'] else (0xead6a0 if T['sand'] else (0x7e848c if T['tall'] else 0x58a044))))
        sp = next((k for k, v in special_blocks.items() if v == (bx, bz)), None)
        if sp: _special(mb, sp, bx, bz, inner, T, rnd, lay, night); continue
        if T['tall']: _towers(mb, bx, bz, inner, T, rnd, lay, night); continue
        # houses around the block edge, doors facing the road
        L = T['lots']; lot = inner / L
        for side in range(4):
            yaw = side * math.pi / 2           # side 0 faces +z road
            for k in range(L):
                if (side in (1, 3)) and k in (0, L - 1): continue  # corners already used
                u = -inner / 2 + lot * (k + .5); v = inner / 2          # front edge of the lot (next to the sidewalk)
                ex = bx + math.cos(yaw) * u + math.sin(yaw) * v; ez = bz - math.sin(yaw) * u + math.cos(yaw) * v
                _house(mb, ex, ez, yaw, min(lot - 3, 22), T, rnd, lay, night)
    mb.finish(time)
    _sky(time, T)
    return lay

def _house(mb, ex, ez, yaw, w, T, rnd, lay, night):
    d = rnd.uniform(15, 19); h = rnd.choice([11, 12, 18, 20]); wall = rnd.choice(T['walls']); roof = rnd.choice(T['roofs'])
    y0 = .3; back = d / 2 + 8                                       # front yard is 8 deep, so trees/mailbox stay off the sidewalk
    x, z = ex - math.sin(yaw) * back, ez - math.cos(yaw) * back
    mb.box(x, y0, z, w, h, d, wall, yaw)
    mb.gable(x, y0 + h, z, w + 1.6, rnd.uniform(5, 7), d + 1.6, roof, yaw + math.pi / 2)
    if T['snow']: mb.gable(x, y0 + h + .3, z, w + 1.7, 6.2, d + 1.7, 0xffffff, yaw + math.pi / 2)
    fx, fz = math.sin(yaw), math.cos(yaw)               # front direction
    rx, rz = math.cos(yaw), -math.sin(yaw)              # right direction
    def at(u, v): return x + rx * u + fx * v, z + rz * u + fz * v
    dx, dz = at(0, d / 2 + .05)
    mb.box(dx, y0, dz, 3.4, 7, .3, rnd.choice([0x6b3e26, 0x8a2f2f, 0x2f4a6b, 0xf2f2f2]), yaw)
    floors = 2 if h > 14 else 1
    for f in range(floors):
        for u in (-w / 3, w / 3):
            wx, wz = at(u, d / 2 + .05); mb.box(wx, y0 + 4 + f * 8, wz, 3.6, 3.2, .25, 0xffd98a, yaw, kind='win')
            wx, wz = at(u, -d / 2 - .05); mb.box(wx, y0 + 4 + f * 8, wz, 3.6, 3.2, .25, 0xffd98a, yaw, kind='win')
    px, pz = at(0, d / 2 + 4); mb.box(px, y0, pz, 3.4, .2, 8, 0xbdb6aa, yaw)          # path to door
    mx, mz = at(w / 2 - 1, d / 2 + 6.5); mb.cyl(mx, y0, mz, .2, 3.4, 0x444444); mb.box(mx, y0 + 3.4, mz, 1.2, 1, 1.8, 0x3b5b8a, yaw)  # mailbox
    tx, tz = at(-w / 2 + 2, d / 2 + 4); _tree(mb, tx, y0, tz, T, rnd)
    door = at(0, d / 2 + 2.5)
    lay['houses'].append(dict(id=len(lay['houses']), door=[round(door[0], 2), .3, round(door[1], 2)], faces_yaw=round(yaw, 4),
                              center=[round(x, 2), round(z, 2)], width=round(w, 1), depth=round(d, 1), height=h))

def _tree(mb, x, y, z, T, rnd):
    k = T['tree']; leaf = rnd.choice(T['leaf']); s = rnd.uniform(.85, 1.25)
    if k == 'palm':
        mb.cyl(x, y, z, .5 * s, 14 * s, 0x9a7a4e, r2=.35 * s)
        for i in range(6):
            a = i * math.pi / 3; mb.box(x + math.cos(a) * 2.6 * s, y + 13.4 * s, z + math.sin(a) * 2.6 * s, 6 * s, .4, 1.6 * s, leaf, -a)
    elif k == 'pine':
        mb.cyl(x, y, z, .5 * s, 3 * s, 0x5a3e2b)
        for j, r in enumerate((3.4, 2.6, 1.8)):
            mb.cyl(x, y + (2.5 + j * 2.8) * s, z, r * s, 4 * s, leaf, r2=.1)
            if T['snow']: mb.cyl(x, y + (5.4 + j * 2.8) * s, z, r * .45 * s, 1.0 * s, 0xffffff, r2=.05)
    else:
        mb.cyl(x, y, z, .55 * s, 6 * s, 0x6b4a32); mb.ball(x, y + 8.5 * s, z, 3.6 * s, leaf); mb.ball(x + 1.5 * s, y + 7.2 * s, z + .8 * s, 2.4 * s, leaf)

def _towers(mb, bx, bz, inner, T, rnd, lay, night):
    for qx in (-1, 1):
        for qz in (-1, 1):
            w = inner / 2 - 4; h = rnd.choice([30, 42, 55, 70, 90]); col = rnd.choice(T['walls'])
            x, z = bx + qx * inner / 4, bz + qz * inner / 4
            mb.box(x, .3, z, w, h, w, col); mb.box(x, .3 + h, z, w + 1, 1.2, w + 1, 0x4a4f57)
            for f in range(int(h // 7)):
                for side in range(4):
                    yaw = side * math.pi / 2; fx, fz = math.sin(yaw), math.cos(yaw)
                    lit = rnd.random() < (.55 if night else 1)
                    mb.box(x + fx * (w / 2 + .05), .3 + 3 + f * 7, z + fz * (w / 2 + .05), w * .8, 3.2, .25, 0xffe2a0 if lit else 0x1d2430, yaw, kind='win')
            mb.box(x, .3, z + qz * (w / 2 + .1), 6, 9, .3, 0x2b3a4a, 0 if qz > 0 else math.pi, kind='shiny')
            door = (x + qz * 0, z + qz * (w / 2 + 2))
            lay['houses'].append(dict(id=len(lay['houses']), door=[round(door[0], 2), .3, round(door[1], 2)], faces_yaw=0 if qz > 0 else round(math.pi, 4),
                                      center=[round(x, 2), round(z, 2)], width=round(w, 1), depth=round(w, 1), height=h, tower=True))

def _sign(text, x, y, z, yaw, size=3.5, col=0xffffff):
    cu = bpy.data.curves.new('sign', 'FONT'); cu.body = text; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = .15
    o = bpy.data.objects.new('sign_' + text, cu); link(o); o.location = B(x, y, z); o.rotation_euler = (math.pi / 2, 0, yaw)
    o.data.materials.append(mat(col, .4, 0, 2.0))

def _special(mb, sp, bx, bz, inner, T, rnd, lay, night):
    if sp == 'school':
        w, d, h = inner - 10, inner * .45, 22; x, z = bx, bz + inner / 2 - d / 2 - 4
        mb.box(x, .3, z, w, h, d, 0xb5523b); mb.box(x, .3 + h, z, w + 1, 1, d + 1, 0x8a8f96)
        for f in range(2):
            for u in range(-3, 4):
                mb.box(x + u * (w / 8), .3 + 5 + f * 9, z + d / 2 + .05, 4, 4, .25, 0xffe6a8, kind='win')
        mb.box(x, .3, z + d / 2 + .05, 6, 8, .3, 0x2f4a6b)
        mb.box(x, .3, bz - inner / 4 + 2, inner - 6, .1, inner / 2 - 8, 0x4a4f57)            # playground lot
        mb.cyl(x + w / 2 - 4, .3, z + d / 2 + 6, .25, 22, 0xdddddd); mb.box(x + w / 2 - 2.6, 18.5, z + d / 2 + 6, 3, 2, .1, 0xc8102e)
        _sign('SCHOOL', x, .3 + h - 4, z + d / 2 + .4, 0, 3.4)
        lay['specials']['school'] = dict(door=[x, .3, round(z + d / 2 + 3, 2)], faces_yaw=0, center=[x, z])
    elif sp == 'gas':
        x, z = bx, bz
        mb.box(x, .3, z, inner - 8, .2, inner - 8, 0x6b6f75)
        for qx in (-1, 1):
            for qz in (-1, 1): mb.box(x + qx * 12, .5, z + qz * 8, 1.2, 15, 1.2, 0xeeeeee)
        mb.box(x, 15.5, z, 30, 2, 22, 0xe23b3b); mb.box(x, 15.3, z, 28, .2, 20, 0xfff6d8, kind='emit')
        for qx in (-1, 1): mb.box(x + qx * 6, .5, z, 2, 5, 1.4, 0xdddddd); mb.box(x + qx * 6, 3.2, z + .75, 1.2, 1.2, .1, 0x2fb34a, kind='emit')
        sx, sz = x, z - inner / 2 + 10
        mb.box(sx, .3, sz, 24, 12, 12, 0xf2f2f2); mb.box(sx, .3, sz + 6.05, 18, 6, .25, 0x9fd3ff, kind='win')
        _sign('GAS', x, 16.2, z + 11.2, 0, 3.0)
        lay['specials']['gas'] = dict(door=[sx, .3, round(sz + 9, 2)], faces_yaw=0, center=[x, z])
    else:
        x, z = bx, bz + inner / 2 - 14
        mb.box(x, .3, z, inner - 10, 16, 20, 0x3f6fb5); mb.box(x, .3, z + 10.05, inner - 18, 8, .25, 0xbfe6ff, kind='win')
        mb.box(x, 12.5, z + 10.6, inner - 12, 1.2, 1.2, 0xffffff)
        _sign('SHOP', x, 13.2, z + 11.3, 0, 3.2)
        for k in range(-2, 3): _car(mb, x + k * 10, bz - 8, rnd)
        lay['specials']['shop'] = dict(door=[x, .3, round(z + 13, 2)], faces_yaw=0, center=[x, z])
    for k in range(3): _tree(mb, bx - inner / 2 + 4 + k * 4, .3, bz - inner / 2 + 4, T, rnd)

def _car(mb, x, z, rnd, yaw=0.):
    col = rnd.choice([0xd93a3a, 0x3a6fd9, 0xf2f2f2, 0x2b2b2b, 0xf2c14e, 0x3aa65a])
    mb.box(x, .9, z, 5, 2.2, 9, col, yaw, kind='shiny'); mb.box(x, 3.1, z - .5, 4.4, 1.8, 5, col, yaw, kind='shiny')
    mb.box(x, 3.25, z - .5, 4.5, 1.4, 4.4, 0x2a3440, yaw, kind='win')
    for qx in (-1, 1):
        for qz in (-1, 1): mb.box(x + qx * 2.4, 0, z + qz * 3, .9, 1.9, 1.9, 0x1a1a1a, yaw)

def _sky(time, T):
    S = bpy.context.scene
    if not S.world: S.world = bpy.data.worlds.new('w')
    S.world.use_nodes = True; bg = S.world.node_tree.nodes['Background']
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); link(sun)
    if time == 'night':
        bg.inputs[0].default_value = (.02, .03, .07, 1); bg.inputs[1].default_value = 1
        sun.data.energy = .7; sun.data.color = srgb(0x9fb4ff); sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    elif time == 'sunset':
        bg.inputs[0].default_value = (*srgb(0xf2a65a), 1); bg.inputs[1].default_value = .7
        sun.data.energy = 3; sun.data.color = srgb(0xffb070); sun.rotation_euler = (math.radians(78), 0, math.radians(-60))
    else:
        bg.inputs[0].default_value = (*srgb(0x9ccfff), 1); bg.inputs[1].default_value = 1.0
        sun.data.energy = 4.5; sun.data.color = srgb(0xfff4e0); sun.rotation_euler = (math.radians(40), 0, math.radians(35))
    sun.data.angle = math.radians(2)
