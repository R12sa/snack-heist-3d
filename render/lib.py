# Snack Heist Blender story: shared helpers. Roblox coords in, Blender coords out.
import bpy, math, os
from mathutils import Vector, Euler, Matrix
HERE = os.path.dirname(os.path.abspath(__file__))
F1, F2 = 1.1, 16.2
FPS = 24

def B(x, y, z): return Vector((x, -z, y))
def V(x, y, z): return Vector((x, y, z))          # roblox-space vector
def clamp(v, a=0., b=1.): return max(a, min(b, v))
def lerp(a, b, k): return a + (b - a) * k
def seg(t, a, b): return clamp((t - a) / (b - a)) if b != a else (1. if t >= a else 0.)
def ease(k): return 4*k*k*k if k < .5 else 1 - (-2*k+2)**3/2
def easeOut(k): return 1 - (1-k)**3
def easeIn(k): return k*k*k
def vl(a, b, k): return a.lerp(b, k)
def yawTo(a, b): return math.atan2(b.x - a.x, b.z - a.z)

def path(pts, k):
    L = [(pts[i+1]-pts[i]).length for i in range(len(pts)-1)]; tot = sum(L); s = clamp(k)*tot
    for i, l in enumerate(L):
        if s <= l or i == len(L)-1: return vl(pts[i], pts[i+1], clamp(s/l) if l else 0)
        s -= l
    return pts[-1].copy()
def plen(pts): return sum((pts[i+1]-pts[i]).length for i in range(len(pts)-1))
def pathDir(pts, k):
    a, b = path(pts, clamp(k-.01)), path(pts, clamp(k+.01))
    if (b-a).length < 1e-6: a, b = path(pts, clamp(k-.03)), path(pts, clamp(k+.03))
    return math.atan2(b.x-a.x, b.z-a.z)

# stairs: treads from z=-13.4 (y 1.86) to z=9.4 (y 16.2), x 301.2..306.7
def stairY(z):
    if z <= -13.4: return F1
    if z >= 9.4: return F2
    return 1.86 + (z + 13.4) * (16.2 - 1.86) / (9.4 + 13.4)

# ---------------- materials ----------------
def srgb(h):
    c = [((h >> 16) & 255)/255, ((h >> 8) & 255)/255, (h & 255)/255]
    return tuple(x/12.92 if x <= 0.04045 else ((x+0.055)/1.055)**2.4 for x in c)
_MATS = {}
def mat(col, rough=.55, metal=0., emit=0.):
    key = (col, rough, metal, emit)
    if key in _MATS: return _MATS[key]
    m = bpy.data.materials.new('c%06x' % col); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*srgb(col), 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = (*srgb(col), 1); b.inputs['Emission Strength'].default_value = emit
    _MATS[key] = m; return m
def face_mat(kind):
    key = ('face', kind)
    if key in _MATS: return _MATS[key]
    m = bpy.data.materials.new('face_'+kind); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(os.path.join(HERE, '..', 'assets', 'faces', kind+'.png')); tx.interpolation = 'Cubic'
    nt.links.new(tx.outputs['Color'], b.inputs['Base Color']); nt.links.new(tx.outputs['Alpha'], b.inputs['Alpha'])
    if kind == 'evil':
        nt.links.new(tx.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 1.5
    b.inputs['Roughness'].default_value = .5
    _MATS[key] = m; return m
def glassmat():
    if 'glassm' in _MATS: return _MATS['glassm']
    m = bpy.data.materials.new('glassm'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (.85, .95, 1, 1); b.inputs['Roughness'].default_value = .05; b.inputs['Alpha'].default_value = .18
    _MATS['glassm'] = m; return m

# ---------------- primitives ----------------
def link(o): bpy.context.scene.collection.objects.link(o); return o
def empty(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); link(e); e.parent = parent; e.location = loc; return e
def rbox(name, w, d, h, col, parent, loc, r=.16, rough=.55, emit=0.):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0)); o = bpy.context.object; o.name = name
    o.scale = (w, d, h); bpy.ops.object.transform_apply(scale=True)
    if r > 0:
        mod = o.modifiers.new('bev', 'BEVEL'); mod.width = r; mod.segments = 3; mod.limit_method = 'NONE'
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat(col, rough, 0, emit)); o.parent = parent; o.location = loc; return o
def cylz(name, r, h, col, parent, loc, verts=32, rough=.55, metal=0., emit=0.):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=(0, 0, 0)); o = bpy.context.object; o.name = name
    mod = o.modifiers.new('bev', 'BEVEL'); mod.width = min(.06, r*.3); mod.segments = 2; mod.limit_method = 'ANGLE'
    bpy.ops.object.shade_smooth(); o.data.materials.append(mat(col, rough, metal, emit)); o.parent = parent; o.location = loc; return o
def sph(name, r, col, parent, loc, rough=.5, emit=0.):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=20, ring_count=12, location=(0, 0, 0)); o = bpy.context.object; o.name = name
    bpy.ops.object.shade_smooth(); o.data.materials.append(mat(col, rough, 0, emit)); o.parent = parent; o.location = loc; return o

# ---------------- characters ----------------
FACES = ['smile', 'sleep', 'scared', 'angry', 'yum', 'sneaky', 'evil', 'shock', 'happy']
CH = {}
class Char:
    def __init__(s, name, skin, shirt, pants, shoes, hair=None, cap=None, stripe=None, long=False, scale=1.):
        s.name = name; s.S = scale
        s.root = empty(name); s.body = empty(name+'_body', s.root); s.body.scale = (scale,)*3
        rbox(name+'_torso', 2, 1, 2, shirt, s.body, (0, 0, 3))
        if stripe: rbox(name+'_stripe', 2.04, 1.04, .35, stripe, s.body, (0, 0, 3.2), r=.08)
        s.head = empty(name+'_head', s.body, (0, 0, 4.0))
        cylz(name+'_skull', .62, 1.2, skin, s.head, (0, 0, .62))
        s.faces = {}
        for k in FACES:
            bpy.ops.mesh.primitive_plane_add(size=1.1, location=(0, 0, 0)); f = bpy.context.object; f.name = name+'_f_'+k
            f.rotation_euler = (math.pi/2, 0, 0); f.location = (0, -.635, .62); f.parent = s.head
            f.data.materials.append(face_mat(k)); f.visible_shadow = False
            s.faces[k] = f
        if hair:
            cylz(name+'_hair', .68, .45, hair, s.head, (0, 0, 1.18), rough=.85)
            if long: rbox(name+'_hairB', 1.36, .35, 1.25, hair, s.head, (0, .55, .55), r=.12, rough=.85)
        if cap:
            cylz(name+'_cap', .68, .35, cap, s.head, (0, 0, 1.25))
            rbox(name+'_bill', 1.1, .7, .12, cap, s.head, (0, -.7, 1.12), r=.05)
        def limb(nm, x, z, col, col2):
            g = empty(name+'_'+nm, s.body, (x, 0, z)); rbox(name+'_'+nm+'m', 1, 1, 2, col, g, (0, 0, -1))
            if col2: rbox(name+'_'+nm+'e', 1.02, 1.02, .6, col2, g, (0, 0, -1.72), r=.12)
            return g
        s.armL = limb('armL', -1.5, 4, shirt, skin); s.armR = limb('armR', 1.5, 4, shirt, skin)
        s.legL = limb('legL', -.5, 2, pants, shoes); s.legR = limb('legR', .5, 2, pants, shoes)
        for o in [s.root, s.body, s.head, s.armL, s.armR, s.legL, s.legR]: o.rotation_mode = 'XYZ'
        s.cur = 'smile'; s.setface('smile'); CH[name] = s
        s.hide(True)
    def setface(s, k):
        for n, f in s.faces.items(): f.hide_render = s.hidden if hasattr(s, 'hidden') and s.hidden else (n != k)
        s.cur = k
    def hide(s, h=True):
        s.hidden = h
        for o in [s.root] + list(s.root.children_recursive):
            if o.type == 'MESH' and '_fl' not in o.name: o.hide_render = h and True or (o.name.startswith(s.name+'_f_') and not o.name.endswith('_'+s.cur))
        if h and hasattr(s, 'flash_on'): s.flash_on(False)
    def pose(s, p, yaw, phase=0., gait=0., crouch=0., **ex):
        """p = feet (roblox), yaw 0 = facing roblox +z"""
        if s.hidden: s.hide(False)
        s.root.location = B(p.x, p.y, p.z); s.root.rotation_euler = (ex.get('pitch', 0), ex.get('roll', 0), yaw)
        sw = math.sin(phase) * gait
        s.legL.rotation_euler = (sw - crouch*.5 + ex.get('legL', 0), 0, 0); s.legR.rotation_euler = (-sw - crouch*.5 + ex.get('legR', 0), 0, 0)
        s.armL.rotation_euler = (-sw*1.1 + ex.get('armL', 0), -ex.get('armLz', 0), ex.get('armLyaw', 0)); s.armR.rotation_euler = (sw*1.1 + ex.get('armR', 0), -ex.get('armRz', 0), ex.get('armRyaw', 0))
        s.body.location = (0, 0, -crouch*1.1*s.S + abs(math.cos(phase))*gait*.35*s.S + ex.get('bodyZ', 0))
        s.body.rotation_euler = (crouch*.35 + ex.get('lean', 0), 0, 0)
        s.head.rotation_euler = (ex.get('headX', 0), ex.get('headZ', 0), ex.get('headY', 0))
    def walk(s, pts, k, stride=1., gait=.7, crouch=0., **ex):
        p = path(pts, k); yaw = ex.pop('yaw', None)
        if yaw is None: yaw = pathDir(pts, k)
        moving = 0 < k < 1
        s.pose(p, yaw, k*plen(pts)*.9*stride, gait if moving else 0, crouch, **ex); return p
    def lie(s, x, top, z, headYaw=0., breathe=0.):
        """lying on back on a surface at height top; feet at (x,z); head toward roblox yaw headYaw"""
        if s.hidden: s.hide(False)
        h = Vector((math.sin(headYaw), -math.cos(headYaw), 0)); u = Vector((0, 0, 1))
        Z = h; Y = -u; X = Y.cross(Z)
        m = Matrix((X, Y, Z)).transposed().to_4x4()
        s.root.matrix_world = Matrix.Translation(B(x, top + .5*s.S + breathe, z)) @ m
        for o in [s.armL, s.armR, s.legL, s.legR, s.head]: o.rotation_euler = (0, 0, 0)
        s.body.location = (0, 0, 0); s.body.rotation_euler = (0, 0, 0)
    def headpos(s):
        bpy.context.view_layer.update(); w = s.head.matrix_world @ Vector((0, 0, .62)); return V(w.x, w.z, -w.y)
    def facing(s):
        bpy.context.view_layer.update(); f = s.head.matrix_world.to_3x3() @ Vector((0, -1, 0)); return math.atan2(f.x, -f.y)

def make_cast():
    kid = Char('kid', 0xf5cd30, 0x3b7bff, 0x2a4fb0, 0xf0f0f0, hair=0x5a3a1e, cap=0xff3b3b, stripe=0xffffff)
    dad = Char('dad', 0xe0ac7e, 0x2e8b57, 0x34343e, 0x222222, hair=0x2b1d14, scale=1.25)
    mom = Char('mom', 0xf1c27d, 0xa45bd6, 0x7a3fa8, 0x5a2a7a, hair=0x7a3b16, long=True, scale=1.18)
    return kid, dad, mom

# ---------------- Whiskers the cat ----------------
class Cat:
    def __init__(s):
        O, Dk, L = 0xe88c3a, 0xc46822, 0xfadaaa
        s.root = empty('cat'); s.b = empty('cat_b', s.root); s.root.scale = (1.25,)*3
        rbox('cat_body', 1.0, 2.0, .95, O, s.b, (0, 0, 1.0), r=.38)
        for y in (-.45, .1, .6): rbox('cat_st', 1.03, .2, .97, Dk, s.b, (0, y, 1.0), r=.08)
        s.hg = empty('cat_head', s.b, (0, -1.05, 1.55))
        rbox('cat_skull', 1.15, 1.0, 1.0, O, s.hg, (0, 0, 0), r=.36)
        rbox('cat_muz', .62, .3, .4, L, s.hg, (0, -.48, -.2), r=.13)
        sph('cat_nose', .09, 0xff7a9a, s.hg, (0, -.64, -.08))
        s.eyes = []
        for sx in (-1, 1):
            e = sph('cat_eye', .13, 0x7dff5a, s.hg, (.27*sx, -.5, .1), emit=1.6); e.scale = (1, .5, 1.15); s.eyes.append(e)
            p = sph('cat_pupil', .06, 0x111111, s.hg, (.27*sx, -.565, .1)); p.scale = (.6, .5, 1.6)
            bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=.24, depth=.45, location=(0, 0, 0)); ear = bpy.context.object
            ear.data.materials.append(mat(O)); ear.parent = s.hg; ear.location = (.36*sx, 0, .68); ear.rotation_euler = (0, 0, math.pi/4)
        s.mouth = rbox('cat_mouth', .3, .05, .02, 0x3a1010, s.hg, (0, -.64, -.32), r=0)
        s.legs = []
        for sx in (-1, 1):
            for sy in (-1, 1):
                g = empty('cat_leg', s.b, (.33*sx, .7*sy, .62)); rbox('cat_legm', .32, .32, .62, O, g, (0, 0, -.31), r=.1)
                rbox('cat_paw', .34, .38, .16, L, g, (0, -.03, -.56), r=.07); s.legs.append((g, sx*sy))
        s.tail = empty('cat_tail', s.b, (0, .95, 1.3))
        rbox('cat_t1', .24, .24, 1.3, O, s.tail, (0, 0, .6), r=.1); rbox('cat_t2', .26, .26, .4, Dk, s.tail, (0, 0, 1.35), r=.1)
        for o in [s.root, s.b, s.hg, s.tail] + [g for g, _ in s.legs]: o.rotation_mode = 'ZXY'
    def pose(s, p, yaw, ph=0., gait=0., sit=0., headX=0., tailT=0., mouth=0.):
        s.root.location = B(p.x, p.y, p.z); s.root.rotation_euler = (0, 0, yaw)
        s.b.rotation_euler = (-sit*.45, 0, 0); s.b.location = (0, 0, abs(math.cos(ph))*gait*.12 - sit*.12)
        for g, sg in s.legs:
            g.rotation_euler = (math.sin(ph)*gait*.7*sg + (0 if (sit and g.location.y > 0) else sit*.45), 0, 0)
        s.hg.rotation_euler = ((headX + sit*.4), 0, 0)
        s.tail.rotation_euler = (.5 - sit*.3, math.sin(tailT*3)*.5, 0)
        s.mouth.hide_render = mouth < .05; s.mouth.scale = (1, 1, 1 + mouth*12); s.mouth.location = (0, -.62, -.32 - mouth*.1)

# ---------------- props ----------------
def make_props():
    P = {}
    ck = empty('cookie')
    c = cylz('cookie_d', .75, .22, 0xc98b45, ck, (0, 0, 0), rough=.9); c.rotation_euler = (math.pi/2, 0, 0)
    for i in range(7):
        a = i*2.4; r = .2 + (i % 3)*.17; sph('chip', .12, 0x3a1f0e, ck, (math.cos(a)*r, -.12, math.sin(a)*r))
    P['cookie'] = ck
    jar = empty('jar', None, B(326.0, 4.95, -3.5))
    g = cylz('jar_glass', .95, 1.6, 0xcfe8ff, jar, (0, 0, .8), rough=.05); g.data.materials[0] = glassmat()
    cylz('jar_lid', 1.0, .25, 0xd94a4a, jar, (0, 0, 1.72)); sph('jar_knob', .2, 0xd94a4a, jar, (0, 0, 1.9))
    for k in range(4):
        cc = cylz('jar_ck', .7, .18, 0xc98b45, jar, (0, 0, .2 + k*.3), rough=.9); cc.rotation_euler = (0, .15*(k % 2), 0)
    jl = bpy.data.lights.new('jarL', 'POINT'); jl.energy = 0; jl.color = srgb(0xffd890); jl.shadow_soft_size = .3
    jlo = bpy.data.objects.new('jarL', jl); link(jlo); jlo.parent = jar; jlo.location = (0, -1.2, 2.2)
    P['jar'] = jar; P['jarL'] = jl
    cake = empty('cake', None, B(320, 4.95, 16))
    cylz('plate', 1.3, .12, 0xebebf0, cake, (0, 0, .06)); cylz('cake1', 1.05, .8, 0xffa0be, cake, (0, 0, .5)); cylz('cake2', .75, .6, 0xfff5fa, cake, (0, 0, 1.2))
    cylz('candle', .075, .5, 0x78c8ff, cake, (0, 0, 1.75)); fl = sph('flame', .13, 0xffbe3c, cake, (0, 0, 2.1), emit=8); fl.scale = (1, 1, 1.4)
    cl = bpy.data.lights.new('cakeL', 'POINT'); cl.energy = 12; cl.color = srgb(0xffb070); clo = bpy.data.objects.new('cakeL', cl); link(clo); clo.parent = cake; clo.location = (0, 0, 2.6)
    P['cake'] = cake; P['flame'] = fl; P['cakeL'] = cl
    sl = empty('slice'); rbox('slice_m', .8, .9, .8, 0xffa0be, sl, (0, 0, 0), r=.08); rbox('slice_t', .82, .92, .2, 0xfff5fa, sl, (0, 0, .45), r=.06)
    P['slice'] = sl
    return P

def flashlight(ch):
    f = empty(ch.name+'_flash', ch.armR, (0, -.35, -2.1)); f.rotation_mode = 'XYZ'
    body = cylz(ch.name+'_flb', .25, 1.3, 0x222222, f, (0, 0, 0))
    lens = cylz(ch.name+'_fll', .28, .05, 0xfff6c8, f, (0, 0, -.66), emit=20)
    sp = bpy.data.lights.new(ch.name+'_spot', 'SPOT'); sp.energy = 0; sp.spot_size = math.radians(48); sp.spot_blend = .5; sp.color = srgb(0xfff1c0); sp.shadow_soft_size = .15
    so = bpy.data.objects.new(ch.name+'_spot', sp); link(so); so.parent = f; so.location = (0, 0, -.75)
    ch.flash = f; ch.spot = sp; ch.flens = lens
    def on(v):
        body.hide_render = not v; lens.hide_render = not v; sp.energy = 2500 if v else 0
    ch.flash_on = on; on(False)
    return f

# ---------------- camera & lights ----------------
def camera():
    c = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); link(c); bpy.context.scene.camera = c
    c.data.sensor_fit = 'VERTICAL'; c.data.clip_start = .1; c.data.clip_end = 400; return c
def look(cam, px, py, pz, tx, ty, tz, fov=50, shake=0., t=0.):
    p = B(px, py, pz); tg = B(tx, ty, tz)
    if shake:
        p = p + Vector((math.sin(t*37.)*shake, math.cos(t*29.)*shake*.6, math.sin(t*23.+1)*shake*.8))
    cam.location = p; cam.rotation_euler = (tg - p).to_track_quat('-Z', 'Y').to_euler()
    cam.data.angle_y = math.radians(fov)
def area(name, x, y, z, energy, col=0xbfd0ff, size=6., tx=None, ty=None, tz=None):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.size = size; ld.color = srgb(col)
    o = bpy.data.objects.new(name, ld); link(o); o.location = B(x, y, z)
    if tx is not None: o.rotation_euler = (B(tx, ty, tz) - o.location).to_track_quat('-Z', 'Y').to_euler()
    return o
def point(name, x, y, z, energy, col=0xffd8a0, r=.5):
    ld = bpy.data.lights.new(name, 'POINT'); ld.energy = energy; ld.color = srgb(col); ld.shadow_soft_size = r
    o = bpy.data.objects.new(name, ld); link(o); o.location = B(x, y, z); return o
