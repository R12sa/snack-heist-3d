# Shots for the Snack Heist gameplay showcase (Nights 1-3), laid out on the CURRENT house
# (maps made from the exported house: kids' room with 4 bunk beds upstairs west, parents' room upstairs east,
#  stairs x~305 from z -11 (ground floor) up to z 17 (upstairs), kitchen island x 315-327 z -24..-18,
#  dining table x 315-330 z 11..18, living-room couch x 269-283 z -20..-18 facing the TV at z -35).
# Walking uses world.route(), so characters go around walls and furniture and stand on the real stairs.
import math
from lib import *
import world
from shots import cam, close, hold, chest, kfill

PI = math.pi
F2B = 16.2
BUNK = (262.9, 19.72, -33.5)          # bottom bunk (kids' room, top-left x 262-269.5), feet west, head on the pillow east (yaw pi/2)
KID_DOOR = V(292.5, F2B, -19.0)       # kids' room doorway
PAR_DOOR = V(308.0, F2B, -20.0)       # parents' room doorway
SX = 305.25                           # stairs run x 302.7-307.8, from z -10 (ground floor) up to z 17 (upstairs)
STAIR_TOP = V(SX, F2B, 18.0)
STAIR_BOT = V(SX, F1, -12.0)
JAR_SPOT = (326.2, 5.45, -21.0)       # cookie jar on the island, east end
KID_JAR = V(329.0, F1, -21.0)         # kid standing east of the island
KID_HIDE3 = V(329.8, F1, -21.0)       # crouched east of the island (island x 316-326 between kid and the kitchen door)
CAKE_SPOT = (326.4, 4.74, 13.5)       # cake on the south-east corner of the dining table (x 314-327.5, z 12.5-18)
KID_CAKE = V(329.6, F1, 10.2)         # kid at the corner, between the end chair and the side chairs
COUCH_HIDE = V(280.6, F1, -23.5)      # crouched behind the couch back (back is the south side, z -19.7); dad walks the north side
PB = dict(dad=(323.0, 20.17, -27.6), mom=(327.1, 20.17, -27.9))   # parents' bed x 320.5-329.5, pillows z -34..-33; heads toward -z (yaw pi)
# soft things characters may sink into (x0,x1, y0,y1, z0,z1) - the checker ignores them
SOFT = [(320.4, 329.6, 19.8, 21.8, -34.6, -32.4), (267.2, 269.5, 19.3, 20.8, -36.2, -30.8)]

_ROUTES = {}
def stair_y(z, foot=.75):
    """height for feet on the real steps at z (max of the floor under heel and toe, so shoes never sink into a riser)"""
    ys = [world.ground(SX, z + d, 14.9 if z + d < 12 else F2B + 1) for d in (-foot, -foot / 2, 0, foot / 2, foot)]
    ys = [y for y in ys if y is not None and y < F2B + .2]
    return max(ys) if ys else F1

def STAIRS(up=True):
    pts = [V(SX, stair_y(z / 2, 1.3) + (.5 if -9.5 < z / 2 < 16.5 else 0), z / 2) for z in range(-24, 37)]
    pts[0] = V(SX, F1, -12.0); pts[-1] = V(SX, F2B, 18.0)
    return pts if up else pts[::-1]

def R(*pts):
    """walkable route through several points (cached)"""
    key = tuple((round(p.x, 2), round(p.y, 2), round(p.z, 2)) for p in pts)
    if key not in _ROUTES:
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            if abs(a.y - b.y) > 5:          # floor change = take the stairs
                up = b.y > a.y; lo, hi = (STAIR_BOT, STAIR_TOP) if up else (STAIR_TOP, STAIR_BOT)
                out += world.route(a, lo)[1:] if (a - lo).length > .5 else []
                out += STAIRS(up)[1:]
                out += world.route(hi, b)[1:] if (b - hi).length > .5 else []
            else: out += world.route(a, b)[1:]
        _ROUTES[key] = out
    return _ROUTES[key]

def jar_on_island(G): G['P']['jar'].location = B(*JAR_SPOT)
def cake_on_table(G): G['P']['cake'].location = B(*CAKE_SPOT); G['P']['cake'].rotation_euler = (0, 0, 0)
def cake_at_chest(G, ch, fwd=1.25, up=2.35):
    bpy.context.view_layer.update()
    G['P']['cake'].location = ch.body.matrix_world @ Vector((0, -fwd, up - .9)); G['P']['cake'].rotation_euler = (0, 0, ch.root.rotation_euler.z)

def parents_sleep(G, t, dad_awake=False):
    dad, mom = G['dad'], G['mom']
    dad.lie(*PB['dad'], headYaw=PI, breathe=0 if dad_awake else .06 * max(0, math.sin(t * 3.2))); dad.setface('sleep')
    mom.lie(*PB['mom'], headYaw=PI, breathe=.03 * math.sin(t * 2.2)); mom.setface('sleep')

def setup(G):
    jar_on_island(G); cake_on_table(G); G['S'].view_settings.exposure = .85

# ---------------------------------------------------------------- shots
def run_up(G, k, crouch=0.):
    kid = G['kid']
    p = kid.walk(STAIRS(True), k, 1.0, 1.0, crouch, lean=.22, armL=-1.0, armR=-1.0, armLz=.2, armRz=-.2); kid.setface('scared')
    cake_at_chest(G, kid); G['P']['cakeL'].energy = 14
    return p

def s_hook(t, G, L):
    p = run_up(G, .25 + seg(t, 0, L) * .6)
    kfill(G, SX, p.y + 7, p.z + 5, 700, 0xa8bcff)
    cam(G, SX + .4, F2B + 5.0, 19.4, SX, p.y + 3.0, p.z, 34, shake=.05, t=t)

def s_title(t, G, L):
    k = ease(t / L)
    G['lamp'].location = B(272, 22, -34); G['lamp'].data.energy = 400; G['lamp'].data.color = srgb(0xffb46a)
    kfill(G, 300, 40, -75, 40000, 0x8fa8ff)
    cam(G, lerp(322, 314, k), lerp(16, 13, k), lerp(-80, -68, k), 298, 13, -30, 50, t=t)

def s_loopbed(t, G, L):
    kid = G['kid']; route = R(V(272.0, F2B, -28.2), V(289.5, F2B, -19.0))
    k = seg(t, 0, L) * .4
    p = kid.walk(route, k, 1, .6, 1.0, headY=math.sin(t * 3) * .35); kid.setface('sneaky')
    G['nl'].location = B(271, 18, -36); G['nl'].data.energy = 60
    kfill(G, 272, F2B + 8, -26, 300, 0xa8bcff)
    cam(G, 278.0, F2B + 5.6, -20.5, p.x, F2B + 2.4, p.z, 46, t=t)

def s_loopsnack(t, G, L):
    kid, P = G['kid'], G['P']; r = seg(t, .1, .6)
    if t < .7:
        kid.pose(KID_JAR, -PI / 2, 0, 0, 0, armR=-1.7 * r, armL=-.2); kid.setface('sneaky')
        if t > .55: hold(P['jar'], kid, 'R')
    else:
        route = R(KID_JAR, V(330.0, F1, -26.5), V(312.0, F1, -26.5)); k = seg(t, .7, L) * .55
        kid.walk(route, k, 1, .6, .7, armL=-1.0, armR=-1.0, armLz=.25, armRz=-.25); kid.setface('yum'); chest(P['jar'], kid)
    P['jarL'].energy = 60
    kfill(G, 330, F1 + 8, -14, 300, 0xa8bcff)
    cam(G, 333.4, F1 + 5.4, -13.8, 327.0, F1 + 3.2, -21.5, 44, t=t)

def s_n1parents(t, G, L):
    parents_sleep(G, t)
    G['R']['parents'].data.energy *= .7
    kfill(G, 325, 28, -22, 900, 0xa8bcff)
    cam(G, lerp(318.5, 319.5, t / L), 27.5, -21.5, 325.0, 20.6, -30.5, 46, t=t)

def s_n1hall(t, G, L):
    kid = G['kid']; route = R(V(293.2, F2B, -20.0), V(297.5, F2B, -20.0), V(298.0, F2B, -4.0))
    k = seg(t, 0, L) * .8
    p = kid.walk(route, k, 1, .6, 1.0, headY=(-1.0 if t < 1.0 else -.3) + math.sin(t * 2) * .2)
    kid.setface('scared' if t < 1.1 else 'sneaky')
    G['lamp'].location = B(314, 19, -22); G['lamp'].data.energy = 60; G['lamp'].data.color = srgb(0xff9a4a)
    kfill(G, 299, F2B + 9, -8, 600, 0xa8bcff)
    cam(G, 300.2, F2B + 4.6, lerp(-1.0, -2.0, t / L), p.x, F2B + 2.4, p.z - 1, 46, t=t)

def s_n1jar(t, G, L):
    kid, P = G['kid'], G['P']; route = R(V(289.5, F2B, -19.0), V(272.0, F2B, -28.2))
    k = seg(t, 0, L - .4) * .53 + .47
    p = kid.walk(route, k, 1, .6, .6, armL=-1.0, armR=-1.0, armLz=.25, armRz=-.25)
    kid.setface('yum' if t > L - .6 else 'sneaky'); chest(P['jar'], kid)
    G['nl'].location = B(271, 18, -36); G['nl'].data.energy = 60
    kfill(G, p.x + 3, F2B + 7, p.z + 3, 260, 0xa8bcff)
    cam(G, 282.0, F2B + 5.4, -19.0, p.x, F2B + 2.6, p.z, 44, t=t)

def cat_bottom(G, t, mouth=0.):
    G['cat'].pose(V(SX, F1, -14.5), 0, sit=1, headX=.25, tailT=t, mouth=mouth)

def s_n2cat(t, G, L):
    kid = G['kid']; z = -3.0; sp = V(SX, stair_y(z, 1.0) + .05, z)
    kid.pose(sp, PI, 0, 0, 0, headX=.3, lean=-.05, armL=-.3, armR=-.3); kid.setface('scared')
    cat_bottom(G, t)
    kfill(G, SX, F1 + 7, -8, 500, 0xa8bcff)
    k = easeOut(t / L)
    cam(G, SX - 1.4, F1 + 1.6, -18.5, SX, lerp(F1 + 1.6, sp.y + 3.4, k), lerp(-14.5, z, k), lerp(44, 34, k), t=t)

def s_n2dad(t, G, L):
    dad = G['dad']; on = t > .15
    parents_sleep(G, t, dad_awake=True)
    dad.setface('sleep' if not on else ('shock' if t < .35 else 'angry'))
    if on: dad.head.rotation_euler = (0, 0, .35 * seg(t, .4, .9))
    G['lamp'].location = B(317.5, 22.5, -35.0); G['lamp'].data.energy = 280 if on else 0; G['lamp'].data.color = srgb(0xffc27a)
    G['R']['parents'].data.energy *= .5
    kfill(G, 321, 24, -30, 60, 0xa8bcff)
    h = dad.headpos()
    cam(G, h.x + 1.2, h.y + 5.2, h.z + 4.2, h.x + .3, h.y - .2, h.z + .6, lerp(44, 34, easeOut(seg(t, .15, .5))), shake=.05 if .15 < t < .5 else 0, t=t)

def hide_couch(G, t):
    """crouched with the couch back between the kid and the room"""
    G['kid'].pose(COUCH_HIDE, 0, 0, 0, 1.45, headY=.35 * math.sin(t * 2.0), headX=-.22, armL=-.9, armR=-.9, armLz=.1, armRz=-.1)

def couch_cam(G, t, L, tx=278.5):
    cam(G, lerp(285.6, 285.2, t / L), F1 + 3.9, -28.6, tx, F1 + 3.6, -16.0, 50, t=t)

def s_n2hide(t, G, L):
    hide_couch(G, t); G['kid'].setface('scared')
    G['R']['living'].data.energy *= .6
    kfill(G, 280, F1 + 8, -27, 1100, 0xa8bcff)
    couch_cam(G, t, L)

def s_n2pass(t, G, L):
    kid, dad = G['kid'], G['dad']
    hide_couch(G, t); kid.setface('scared' if t < 1.2 else 'shock')
    route = R(V(289.5, F1, -10.5), V(264.0, F1, -9.8)); k = seg(t, 0, L) * .9
    p = dad.walk(route, k, .9, .45, yaw=None, armR=-1.35, armRyaw=-.5 + .35 * math.sin(t * 2.2), headY=-.3 + .3 * math.sin(t * 2.2))
    dad.setface('angry'); dad.flash_on(True)
    G['R']['living'].data.energy *= .5
    kfill(G, 280, F1 + 8, -27, 900, 0xa8bcff)
    couch_cam(G, t, L, tx=lerp(281, 274, k))

PATROL_D = (V(302.0, F1, -14.0), V(305.5, F1, -17.5), V(310.0, F1, -17.5), V(311.5, F1, -16.0))
PATROL_M = (V(301.0, F1, -19.0), V(305.5, F1, -18.0), V(310.0, F1, -18.5), V(312.8, F1, -25.2))
def patrol(G, t):
    dad, mom = G['dad'], G['mom']
    dad.walk(R(*PATROL_D), seg(t, 0, 2.6), .9, .45, armR=-1.35, armRyaw=.55 * math.sin(t * 1.8), headY=.5 * math.sin(t * 1.8)); dad.setface('angry'); dad.flash_on(True)
    mom.walk(R(*PATROL_M), seg(t, .9, 3.0), .9, .45, armR=-1.35, armRyaw=.5 * math.sin(t * 1.6 + 1), headY=.45 * math.sin(t * 1.6 + 1)); mom.setface('angry'); mom.flash_on(True)

def hide_island(G, t, crouch=1.1):
    G['kid'].pose(KID_HIDE3, -PI / 2, 0, 0, crouch, headY=.4 * math.sin(t * 2), armL=-.9, armR=-.9, armLz=.25, armRz=-.25)

def island_cam(G, t, L):
    cam(G, lerp(335.0, 334.6, t / L), F1 + 3.4, -26.5, 318.0, F1 + 4.0, -19.0, 48, t=t)

def s_n3patrol(t, G, L):
    hide_island(G, t); G['kid'].setface('scared')
    patrol(G, t)
    G['R']['kitchen'].data.energy *= .4; G['R']['entry'].data.energy *= .5
    kfill(G, 333, F1 + 7, -25, 160, 0xa8bcff)
    island_cam(G, t, L)

def s_n3throw(t, G, L):
    kid, dad, mom, P = G['kid'], G['dad'], G['mom'], G['P']
    sw = seg(t, .15, .4)
    kid.pose(KID_HIDE3, -PI / 2, crouch=.6, armR=lerp(-2.7, -1.1, sw) if t > .15 else -2.7 * seg(t, 0, .15), armL=-.4); kid.setface('sneaky')
    if t < .4: hold(P['toy'], kid, 'R')
    else:
        u = seg(t, .4, 1.1); a = V(328.5, F1 + 5.6, -21.0); b = V(300.0, F1 + .3, -17.0)
        p = vl(a, b, u); p.y += math.sin(u * PI) * 3.5
        P['toy'].location = B(p.x, p.y, p.z); P['toy'].rotation_euler = (u * 9, u * 5, 0)
    patrol(G, 3.0)
    if t > 1.1:
        s = easeOut(seg(t, 1.1, 1.6)); toy = V(300, 0, -17)
        for ch, pos in ((dad, PATROL_D[-1]), (mom, PATROL_M[-1])):
            ch.pose(pos, lerp(ch.root.rotation_euler.z, yawTo(pos, toy), s), armR=-1.3); ch.setface('shock'); ch.flash_on(True)
    G['R']['kitchen'].data.energy *= .4; G['R']['entry'].data.energy *= .5
    kfill(G, 333, F1 + 7, -25, 160, 0xa8bcff)
    island_cam(G, t, L)

def s_n3cake(t, G, L):
    kid, P = G['kid'], G['P']; face = yawTo(KID_CAKE, V(CAKE_SPOT[0], 0, CAKE_SPOT[2]))
    if t < .55:
        kid.pose(KID_CAKE, face, armL=-1.5 * seg(t, 0, .35), armR=-1.5 * seg(t, 0, .35)); kid.setface('yum')
        if t > .4: cake_at_chest(G, kid)
    else:
        route = R(KID_CAKE, V(330.2, F1, 6.0), V(320.0, F1, 1.0), V(318.0, F1, -10.0)); k = seg(t, .55, L) * .45
        kid.walk(route, k, 1.0, 1.0, 0, lean=.2, armL=-1.0, armR=-1.0, armLz=.2, armRz=-.2); kid.setface('scared')
        cake_at_chest(G, kid)
    P['cakeL'].energy = 16
    kfill(G, 326, F1 + 9, 6, 320, 0xffd2a0)
    cam(G, 333.2, F1 + 6.2, 17.5, 328.0, F1 + 3.0, 10.0, 48, t=t)

def s_n3stairs(t, G, L):
    p = run_up(G, .05 + seg(t, 0, L) * .6)
    kfill(G, SX, p.y + 7, p.z - 4, 300, 0xa8bcff)
    cam(G, SX + .2, F1 + 4.4, -19.0, SX, p.y + 3.0, p.z, 36, shake=.04, t=t)

def kid_in_bunk(G, t, face):
    kid = G['kid']; kid.lie(*BUNK, headYaw=PI / 2, breathe=.03 * math.sin(t * 3)); kid.head.rotation_euler = (0, 0, 1.05)
    kid.setface(face)

def bunk_cam(G, t, L):
    h = G['kid'].headpos()
    cam(G, h.x - 1.2, h.y + 1.4, h.z + 6.4, h.x - 1.4, h.y - .5, h.z, 50, t=t)

def s_n3bed(t, G, L):
    kid_in_bunk(G, t, 'sleep' if t < .55 else 'sneaky')
    dad = G['dad']; dp = V(271.0, F2B, -27.6)
    dad.pose(dp, yawTo(dp, V(267.0, 0, -33.5)), armR=-1.0, headX=.35); dad.setface('angry'); dad.flash_on(True)
    G['nl'].location = B(271, 18, -36); G['nl'].data.energy = 40
    kfill(G, 269, 22.5, -30, 400, 0xa8bcff)
    cam(G, lerp(263.3, 263.7, t / L), 22.4, -26.0, 268.6, 20.6, -30.6, 60, t=t)   # over dad's shoulder

def s_perks(t, G, L):
    kid = G['kid']; k = seg(t, 0, L)
    kid.walk(R(V(297.5, F2B, -30.0), V(297.5, F2B, -4.0)), k, 1.0, 1.0, 0, lean=.2); kid.setface('happy')
    kfill(G, 297, F2B + 8, -6, 700, 0xa8bcff)
    cam(G, 300.0, F2B + 3.8, 2.0, 297.5, F2B + 3.0, lerp(-26, -6, k), 42, t=t)

def s_friends(t, G, L):
    team = [G['kid']] + G['friends']; k = seg(t, 0, L)
    for i, c in enumerate(team):
        z = lerp(-17.0, -7.0, k) - i * 3.4
        c.pose(V(297.5 + (.95 if i % 2 else -.95), F2B, z), 0, k * 10 * .9 + i * 1.3, .6, .9, headY=.35 * math.sin(t * 2 + i), armL=-.4, armR=-.4)
        c.setface(['sneaky', 'happy', 'sneaky', 'yum'][i])
    kfill(G, 297, F2B + 8, -14, 800, 0xa8bcff)
    cam(G, 300.0, F2B + 4.6, 2.0, 297.4, F2B + 2.4, lerp(-19, -14, k), 42, t=t)

def s_cta(t, G, L):
    k = ease(t / L)
    G['lamp'].location = B(272, 22, -34); G['lamp'].data.energy = 400; G['lamp'].data.color = srgb(0xffb46a)
    kfill(G, 300, 40, -75, 40000, 0x8fa8ff)
    cam(G, lerp(286, 290, k), lerp(11, 13, k), lerp(-74, -62, k), 296, 14, -30, 48, t=t)

def s_end(t, G, L):
    kid_in_bunk(G, t, 'sneaky' if t < 1.4 else 'yum')
    G['nl'].location = B(271, 18, -36); G['nl'].data.energy = 60
    kfill(G, 269, 22.5, -30, 160, 0xa8bcff)
    bunk_cam(G, t, L)

def _wrap(fn):
    def f(t, G, L):
        setup(G); fn(t, G, L)
    return f

SHOW = {k[2:]: _wrap(v) for k, v in dict(globals()).items() if k.startswith('s_') and callable(v)}
