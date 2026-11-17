# Better characters: rounded parts, elbows, knees, hands, shoes, real hair, curved faces.
# Same controls as the old ones (pose / walk / lie / setface / hide / headpos / facing), plus:
#   pose(..., elbowL=, elbowR=, kneeL=, kneeR=)   (all auto if left out)
import bpy, bmesh, math
from mathutils import Vector, Matrix
import lib
from lib import empty, rbox, cylz, sph, mat, face_mat, FACES, B, V, CH

def curved_face(name, parent, kind, r=.635, h=1.0, z0=.12, arc=1.5, n=20):
    """face decal wrapped around the front of the head (front = -Y)"""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); uv = bm.loops.layers.uv.new('UV')
    cols = []
    for i in range(n + 1):
        a = -arc / 2 + arc * i / n
        x, y = math.sin(a) * r, -math.cos(a) * r
        cols.append((bm.verts.new((x, y, z0)), bm.verts.new((x, y, z0 + h)), i / n))
    for i in range(n):
        (a0, a1, u0), (b0, b1, u1) = cols[i], cols[i + 1]
        f = bm.faces.new((a0, b0, b1, a1))
        for l, (u, v) in zip(f.loops, ((u0, 0), (u1, 0), (u1, 1), (u0, 1))): l[uv].uv = (u, v)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); lib.link(o); o.parent = parent
    for p in me.polygons: p.use_smooth = True
    o.data.materials.append(face_mat(kind)); o.visible_shadow = False
    return o

class Char2(lib.Char):
    def __init__(s, name, skin, shirt, pants, shoes, hair=None, cap=None, stripe=None, long=False, scale=1.,
                 sleeve=None, collar=None, belt=None, sole=0xf2f2f2, glasses=False, hairstyle='short', accent=None):
        s.name = name; s.S = scale; sleeve = sleeve if sleeve is not None else shirt
        s.root = empty(name); s.body = empty(name + '_body', s.root); s.body.scale = (scale,) * 3
        # torso: chest + waist, rounded
        rbox(name + '_chest', 2.0, 1.0, 1.25, shirt, s.body, (0, 0, 3.38), r=.22)
        rbox(name + '_waist', 1.86, .94, .8, shirt, s.body, (0, 0, 2.42), r=.18)
        if belt: rbox(name + '_belt', 1.9, .98, .2, belt, s.body, (0, 0, 2.1), r=.06); rbox(name + '_buckle', .3, .08, .16, 0xd9b45a, s.body, (0, -.5, 2.1), r=.02)
        if stripe: rbox(name + '_stripe', 2.03, 1.03, .28, stripe, s.body, (0, 0, 3.15), r=.08)
        if collar: rbox(name + '_collar', 1.1, .2, .22, collar, s.body, (0, -.47, 3.93), r=.07); rbox(name + '_collarB', 1.2, .9, .16, collar, s.body, (0, .02, 4.02), r=.07)
        if accent: rbox(name + '_pocket', .42, .06, .42, accent, s.body, (.5, -.5, 3.45), r=.05)
        rbox(name + '_neck', .62, .55, .25, skin, s.body, (0, 0, 4.02), r=.1)
        # head: rounded classic Roblox head
        s.head = empty(name + '_head', s.body, (0, 0, 4.05))
        hd = cylz(name + '_skull', .62, 1.2, skin, s.head, (0, 0, .62), verts=40)
        hd.modifiers[0].width = .22; hd.modifiers[0].segments = 5
        s.faces = {k: curved_face(name + '_f_' + k, s.head, k) for k in FACES}
        if glasses:
            F = 0x1a1a1a
            for sx in (-1, 1):
                cx = .25 * sx
                rbox(name + '_gT', .36, .04, .045, F, s.head, (cx, -.69, .9), r=0); rbox(name + '_gB', .36, .04, .045, F, s.head, (cx, -.69, .6), r=0)
                rbox(name + '_gO', .045, .04, .34, F, s.head, (cx + .16 * sx, -.68, .75), r=0); rbox(name + '_gI', .045, .04, .34, F, s.head, (cx - .16 * sx, -.69, .75), r=0)
                rbox(name + '_gArm', .04, .5, .04, F, s.head, (.6 * sx, -.42, .86), r=0)
            rbox(name + '_bridge', .12, .04, .04, F, s.head, (0, -.7, .8), r=0)
        s._hair(name, hair, cap, long, hairstyle)
        # arms with elbows + hands, legs with knees + shoes
        def arm(nm, x):
            g = empty(name + '_' + nm, s.body, (x, 0, 3.95))
            rbox(name + '_' + nm + 'u', .9, .92, 1.08, sleeve, g, (0, 0, -.5), r=.2)
            e = empty(name + '_' + nm + '_elbow', g, (0, 0, -1.0))
            rbox(name + '_' + nm + 'f', .84, .86, .62, skin if sleeve != shirt or True else shirt, e, (0, 0, -.28), r=.18)
            rbox(name + '_' + nm + 'h', .8, .86, .5, skin, e, (0, -.02, -.78), r=.2)
            hand = empty(name + '_' + nm + '_hand', e, (0, -.05, -.85))
            return g, e, hand
        def leg(nm, x):
            g = empty(name + '_' + nm, s.body, (x, 0, 2.05))
            rbox(name + '_' + nm + 't', .94, .96, 1.1, pants, g, (0, 0, -.52), r=.18)
            k = empty(name + '_' + nm + '_knee', g, (0, 0, -1.02))
            rbox(name + '_' + nm + 's', .9, .92, .7, pants, k, (0, 0, -.32), r=.16)
            rbox(name + '_' + nm + 'sh', .98, 1.28, .36, shoes, k, (0, -.14, -.8), r=.16)
            rbox(name + '_' + nm + 'so', 1.0, 1.32, .12, sole, k, (0, -.14, -.98), r=.05)
            return g, k
        s.armL, s.elbowL, s.handL = arm('armL', -1.47); s.armR, s.elbowR, s.handR = arm('armR', 1.47)
        s.legL, s.kneeL = leg('legL', -.5); s.legR, s.kneeR = leg('legR', .5)
        for o in [s.root, s.body, s.head, s.armL, s.armR, s.legL, s.legR, s.elbowL, s.elbowR, s.kneeL, s.kneeR]: o.rotation_mode = 'XYZ'
        s.cur = 'smile'; s.hidden = False; s.setface('smile'); CH[name] = s
        s.hide(True)

    def _hair(s, name, hair, cap, long, style):
        H = s.head
        if cap:
            c = cylz(name + '_cap', .67, .42, cap, H, (0, 0, 1.24), verts=40); c.modifiers[0].width = .12
            bill = rbox(name + '_bill', 1.05, .75, .1, cap, H, (0, -.78, 1.1), r=.05); bill.rotation_euler = (-.12, 0, 0)
            rbox(name + '_capbtn', .16, .16, .08, cap, H, (0, 0, 1.47), r=.04)
            rbox(name + '_logo', .34, .05, .22, 0xffffff, H, (0, -.66, 1.28), r=.03)
            if hair:
                for sx in (-1, 1): rbox(name + '_tuft', .2, .5, .35, hair, H, (.6 * sx, .05, .95), r=.08)
                rbox(name + '_back', 1.0, .25, .35, hair, H, (0, .58, .98), r=.1)
            return
        if not hair: return
        top = cylz(name + '_hair', .67, .42, hair, H, (0, 0, 1.18), verts=40, rough=.8); top.modifiers[0].width = .15
        if style == 'long' or long:
            rbox(name + '_bangs', 1.15, .25, .35, hair, H, (0, -.55, 1.12), r=.12)
            rbox(name + '_hairB', 1.38, .4, 1.5, hair, H, (0, .48, .55), r=.18)
            for sx in (-1, 1): rbox(name + '_hairS', .22, .9, 1.2, hair, H, (.66 * sx, .12, .68), r=.1)
            sph(name + '_bun', .32, hair, H, (0, .62, 1.25), rough=.8)
        else:
            rbox(name + '_fringe', 1.05, .22, .22, hair, H, (0, -.55, 1.18), r=.09)
            for sx in (-1, 1): rbox(name + '_burn', .14, .3, .45, hair, H, (.63 * sx, -.1, .9), r=.06)

    def pose(s, p, yaw, phase=0., gait=0., crouch=0., **ex):
        lib.Char.pose(s, p, yaw, phase, gait, crouch, **ex)
        sw = math.sin(phase) * gait
        aL, aR = s.armL.rotation_euler.x, s.armR.rotation_euler.x
        s.elbowL.rotation_euler = (ex.get('elbowL', -(.22 + .25 * gait + .15 * max(0, -aL))), 0, 0)
        s.elbowR.rotation_euler = (ex.get('elbowR', -(.22 + .25 * gait + .15 * max(0, -aR))), 0, 0)
        kL = .08 + crouch * 1.05 + gait * 1.1 * max(0, math.sin(phase + 1.2))
        kR = .08 + crouch * 1.05 + gait * 1.1 * max(0, math.sin(phase + 1.2 + math.pi))
        s.kneeL.rotation_euler = (ex.get('kneeL', kL), 0, 0); s.kneeR.rotation_euler = (ex.get('kneeR', kR), 0, 0)

    def lie(s, *a, **k):
        lib.Char.lie(s, *a, **k)
        for o in (s.elbowL, s.elbowR, s.kneeL, s.kneeR): o.rotation_euler = (0, 0, 0)

def make_cast2():
    kid = Char2('kid', 0xf5cd30, 0x3b7bff, 0x22325e, 0xf4f4f4, hair=0x5a3a1e, cap=0xff3b3b, stripe=0xffffff,
                sole=0xff3b3b, accent=0x2a5fd6)
    dad = Char2('dad', 0xe0ac7e, 0x2e8b57, 0x3a3f4a, 0x4a2e1e, hair=0x2b1d14, scale=1.25, collar=0x247048, belt=0x3b2a1e,
                sole=0x2a1d14, glasses=True, accent=0x247048)
    mom = Char2('mom', 0xf1c27d, 0xa45bd6, 0x5b3a8a, 0xe7e7ef, hair=0x7a3b16, long=True, scale=1.18, collar=0xff8ab8,
                sole=0xff8ab8, hairstyle='long')
    return kid, dad, mom
