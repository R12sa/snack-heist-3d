# Snack Heist story shots. Each shot: fn(t, G, L) -> sets the scene at time t (seconds).
import math, bpy
from lib import *
from mathutils import Vector, Matrix

PI = math.pi
JAR_ISLAND = V(323.3, 4.85, -15.6)        # cookie jar on the kitchen island (east end)
KID_HIDE = V(325.9, F1, -13.4)            # crouched by the island, facing north
DAD_TABLE = V(318.0, F1, 11.2)            # at the dining table, facing north (cake)
KID_BED = (255.2, 19.7, -6.3)             # bottom bunk, feet

def reset(G):
    for c in [G['kid'], G['dad'], G['mom']] + G.get('friends', []):
        if not c.hidden: c.hide(True)
    if 'toy' in G['P']: G['P']['toy'].location = (0, 0, -500)
    G['dad'].flash_on(False); G['mom'].flash_on(False)
    G['cat'].root.location = (0, 0, -500)
    P = G['P']
    P['jar'].location = B(JAR_ISLAND.x, JAR_ISLAND.y, JAR_ISLAND.z); P['jar'].rotation_euler = (0, 0, 0); P['jarL'].energy = 0
    P['cookie'].location = (0, 0, -500); P['slice'].location = (0, 0, -500)
    for k, o in G['R'].items(): o.data.energy = G['R0'][k]
    G['lamp'].data.energy = 0; G['nl'].data.energy = 0; G['kfill'].data.energy = 0

def hold(obj, ch, arm='R', off=(0, -.1, -2.3), rot=None):
    bpy.context.view_layer.update()
    h = getattr(ch, 'handR' if arm == 'R' else 'handL', None)
    if h is not None: obj.location = h.matrix_world @ Vector((0, off[1] - .1, -.15))
    else: obj.location = (ch.armR if arm == 'R' else ch.armL).matrix_world @ Vector(off)
    if rot is not None: obj.rotation_euler = rot

def chest(obj, ch, fwd=1.3, up=3.0):
    bpy.context.view_layer.update()
    obj.location = ch.body.matrix_world @ Vector((0, -fwd, up - .9)); obj.rotation_euler = (0, 0, ch.root.rotation_euler.z)

def kfill(G, x, y, z, e, col=0xffe2b8):
    G['kfill'].location = B(x, y, z); G['kfill'].data.energy = e; G['kfill'].data.color = srgb(col)

def cam(G, *a, **k): look(G['cam'], *a, **k)
def close(G, ch, dist=4.5, ang=0., dy=.3, fov=30, tdy=0., t=0., shake=0.):
    h = ch.headpos(); yaw = ch.facing() + ang
    p = h + V(math.sin(yaw) * dist, dy, math.cos(yaw) * dist)
    look(G['cam'], p.x, p.y, p.z, h.x, h.y + tdy, h.z, fov, shake=shake, t=t)

# ---------------------------------------------------------------- shots
def stare_stage(t, G, turned=True):
    kid, dad, P = G['kid'], G['dad'], G['P']
    kid.pose(KID_HIDE, 0, crouch=.85, headX=-.05, armL=-1.0, armR=-1.0, armLz=.25, armRz=-.25); kid.setface('shock')
    chest(P['jar'], kid)
    dad.pose(DAD_TABLE, PI if turned else 0, armR=-1.2 if turned else -1.75, armL=-.2); dad.setface('shock' if turned else 'yum')
    hold(P['slice'], dad, 'R', (0, -.3, -2.25))
    P['cakeL'].energy = 12
    kfill(G, 316, F1 + 9, -2, 900, 0xbfd0ff)

def s_hook(t, G, L):
    stare_stage(t, G, turned=True)
    k = t / L
    cam(G, lerp(323.8, 323.4, k), F1 + 4.8, lerp(-21.0, -20.0, k), 319.0, F1 + 4.8, lerp(4.0, 6.0, k), lerp(44, 38, k), t=t)

def s_bed(t, G, L):
    kid = G['kid']; kid.lie(*KID_BED, headYaw=0, breathe=.03*math.sin(t*2.5)); kid.head.rotation_euler = (0, 0, -1.1)
    kid.setface('sleep' if t < .55 else ('sneaky' if t < 1.6 else 'yum'))
    if .55 <= t < .7: kid.setface('shock')
    G['nl'].location = B(258.6, 19.0, -.6); G['nl'].data.energy = 60
    kfill(G, 258.5, 21.5, -3.0, 120, 0xa8bcff)
    cam(G, 259.6, 21.9, lerp(-2.2, -1.6, t / L), 255.3, 20.6, -1.6, lerp(34, 29, t / L), t=t)

def s_jar(t, G, L):
    P = G['P']; P['jarL'].energy = 120 + 25 * math.sin(t * 5)
    k = ease(t / L)
    G['R']['kitchen'].data.energy *= .55
    cam(G, lerp(317.6, 319.6, k), lerp(F1 + 6.4, F1 + 5.6, k), lerp(-8.4, -11.2, k), 323.3, 5.9, -15.6, lerp(34, 26, k), t=t)

def s_out(t, G, L):
    kid = G['kid']
    k = seg(t, .05, L)
    p = kid.walk([V(259.6, F2, -3.4), V(262.2, F2, -6.2), V(266.0, F2, -9.6)], k, 1, .6, 1.0, headY=math.sin(t*3)*.35)
    kid.setface('sneaky')
    G['nl'].location = B(258.6, 19.0, -.6); G['nl'].data.energy = 60
    kfill(G, p.x + 2, F2 + 7, p.z - 3, 220, 0xa8bcff)
    cam(G, lerp(271.5, 271.0, t/L), F2 + 6.2, lerp(-15.5, -15.0, t/L), lerp(261, 264.5, k), F2 + 2.4, lerp(-4.5, -8.5, k), 46, t=t)

def s_hall(t, G, L):
    kid = G['kid']
    k = seg(t, 0, L)
    kid.walk([V(293.6, F2, -18.0), V(296.4, F2, -16.2), V(297.2, F2, -12.5), V(297.2, F2, -8.0)], k, 1, .6, 1.0,
             headY=(-1.0 if t < 1.0 else -.3) + math.sin(t * 2) * .2)
    kid.setface('scared' if t < 1.1 else 'sneaky')
    kfill(G, 299, F2 + 9, -6, 260, 0xa8bcff)
    G['lamp'].location = B(310, 19, -20); G['lamp'].data.energy = 60; G['lamp'].data.color = srgb(0xff9a4a)
    cam(G, 297.6, F2 + 3.6, lerp(-3.0, -3.6, t / L), lerp(298, 297.5, k), F2 + 2.4, lerp(-17, -12, k), 52, t=t)

def s_parents(t, G, L):
    dad, mom = G['dad'], G['mom']
    dad.lie(322.6, 20.3, -5.2, PI/2, breathe=.06 * max(0, math.sin(t * 3.2))); dad.setface('sleep')
    mom.lie(322.9, 20.3, -1.3, PI/2, breathe=.03 * math.sin(t * 2.2)); mom.setface('sleep')
    G['R']['parents'].data.energy *= .7
    kfill(G, 324, 26, -9, 260, 0xa8bcff)
    cam(G, lerp(317.0, 317.8, t / L), 27.6, lerp(-2.8, -3.2, t / L), 327.0, 20.8, -3.3, 44, t=t)

def s_stairs(t, G, L):
    kid = G['kid']
    k = seg(t, 0, L)
    z = lerp(7.0, -9.0, k); y = stairY(z)
    hop = seg(k, .42, .62); y += math.sin(hop * PI) * 1.4
    air = 0 < hop < 1
    kid.pose(V(304.0, y, z), PI, k * 16 * .9, .15 if air else .6, .4, headY=math.sin(t*2.5)*.25, legL=-.6 if air else 0, legR=.3 if air else 0)
    kid.setface('scared' if air else 'sneaky')
    kfill(G, 304, y + 7, z - 4, 260, 0xa8bcff)
    cam(G, 304.6, F1 + 4.2, -21.0, 304.0, y + 3.0, z, lerp(38, 33, k), t=t)

def cat_at_stairs(G, t, mouth=0., sit=1.):
    G['cat'].pose(V(304.0, F1, -17.6), 0, sit=sit, headX=.25, tailT=t, mouth=mouth)

def s_cat(t, G, L):
    kid = G['kid']; z = -9.0
    kid.pose(V(304.0, stairY(z), z), PI, 0, 0, .4, headX=.25); kid.setface('scared')
    cat_at_stairs(G, t)
    kfill(G, 304, F1 + 6, -14, 120, 0xa8bcff)
    k = easeOut(t / L)
    cam(G, 302.3, stairY(z + 3.5) + 6.0, z + 3.5, 304.0, F1 + 1.8, -17.6, lerp(40, 26, k), t=t)

def s_catclose(t, G, L):
    cat_at_stairs(G, t)
    kfill(G, 305, F1 + 5, -13, 90, 0xa8bcff)
    k = t / L
    cam(G, lerp(304.9, 304.6, k), F1 + 2.5, lerp(-13.4, -14.4, k), 304.0, F1 + 2.35, -17.6, 30, t=t)

def s_plead(t, G, L):
    kid = G['kid']; z = -9.0; y = stairY(z)
    meow = t > L - .9
    kid.pose(V(304.0, y, z), PI, 0, 0, .6, armR=-2.75, armRz=.35, headX=.15 if not meow else -.1, lean=.1); kid.setface('scared' if not meow else 'shock')
    cat_at_stairs(G, t, mouth=1. if meow and t < L - .25 else 0.)
    kfill(G, 304, y + 6, z - 4, 160, 0xa8bcff)
    if not meow:
        k = t / (L - .9)
        close(G, kid, lerp(6.2, 5.2, k), 0, .2, 32, t=t)
    else:
        cam(G, 304.5, F1 + 2.7, -13.2, 304.0, F1 + 2.0, -17.6, 30, shake=.08, t=t)

def s_dadwake(t, G, L):
    dad, mom = G['dad'], G['mom']
    on = t > .55
    dad.lie(322.6, 20.3, -5.2, PI/2); dad.setface('sleep' if not on else ('shock' if t < .75 else 'angry'))
    mom.lie(322.9, 20.3, -1.3, PI/2); mom.setface('sleep')
    if on: dad.head.rotation_euler = (0, 0, -.35 * seg(t, .8, 1.3))
    G['lamp'].location = B(331.5, 23.0, -9.6); G['lamp'].data.energy = 280 if on else 0; G['lamp'].data.color = srgb(0xffc27a)
    G['R']['parents'].data.energy *= .5
    kfill(G, 326, 25, -8, 60, 0xa8bcff)
    cam(G, 325.6, 24.0, -6.4, 329.3, 20.9, -5.2, lerp(30, 24, easeOut(seg(t, .55, .9))), shake=.05 if .55 < t < .9 else 0, t=t)

def s_grab(t, G, L):
    kid, P = G['kid'], G['P']
    run = [V(307.5, F1, -23.0), V(312.0, F1, -21.8), V(321.5, F1, -21.6), V(325.6, F1, -19.0), V(325.8, F1, -15.6)]
    k = seg(t, 0, 1.45)
    if t < 1.45:
        kid.walk(run, easeOut(k) * .15 + k * .85, 1.15, 1.0, 0, lean=.25); kid.setface('scared')
    else:
        r = seg(t, 1.45, 1.75); back = seg(t, 1.85, 2.1)
        kid.pose(V(325.8, F1, -15.6), -PI / 2, 0, 0, 0, armR=-2.0 * r + back * .9, armL=-.2, lean=-.05)
        kid.setface('sneaky' if t < 1.8 else 'yum')
        if t > 1.75: hold(P['jar'], kid, 'R', (0, -.1, -2.6))
    P['jarL'].energy = 80
    kfill(G, 318, F1 + 10, -15, 500, 0xa8bcff)
    cam(G, lerp(311.8, 312.6, t / L), F1 + 7.4, -28.0, lerp(314.0, 323.5, seg(t, 0, 1.5)), F1 + 3.2, lerp(-22, -17, seg(t, 0, 1.5)), 46, t=t)

def s_hide(t, G, L):
    kid, P = G['kid'], G['P']
    c = easeOut(seg(t, 0, .45))
    pos = vl(V(325.8, F1, -15.6), KID_HIDE, c)
    kid.pose(pos, lerp(-PI / 2, 0, c), 0, 0, c * .95, armL=-1.0, armR=-1.0, armLz=.25, armRz=-.25, headY=math.sin(t * 3) * .3 * c); kid.setface('scared')
    chest(P['jar'], kid)
    kfill(G, 322, F1 + 8, -5, 260, 0xa8bcff)
    cam(G, 326.4, F1 + 4.2, lerp(-6.6, -7.4, t / L), 325.9, F1 + 3.0, -13.4, 40, t=t)

def dad_path_in():
    return [V(305.5, F1, -23.0), V(309.5, F1, -22.0), V(311.6, F1, -15.0), V(312.4, F1, -9.0)]
def dad_path_cake():
    return [V(312.4, F1, -9.0), V(314.0, F1, -3.0), V(317.2, F1, 3.0), DAD_TABLE]

def s_dadin(t, G, L):
    kid, dad, P = G['kid'], G['dad'], G['P']
    kid.pose(KID_HIDE, 0, crouch=.95, armL=-1.0, armR=-1.0, armLz=.25, armRz=-.25, headY=-.5 + .15 * math.sin(t * 2)); kid.setface('scared')
    chest(P['jar'], kid)
    k = seg(t, 0, L)
    dad.walk(dad_path_in(), k, .9, .45, armR=-1.4, armRyaw=.6 * math.sin(t * 1.9), headY=.55 * math.sin(t * 1.9)); dad.setface('angry'); dad.flash_on(True)
    G['R']['kitchen'].data.energy *= .6
    kfill(G, 324, F1 + 7, -6, 160, 0xa8bcff)
    cam(G, 330.6, F1 + 5.0, lerp(-8.0, -8.5, t / L), 312.0, F1 + 4.2, -18.0, 46, t=t)

def s_cake(t, G, L):
    kid, dad, P = G['kid'], G['dad'], G['P']
    kid.pose(KID_HIDE, 0, crouch=.8, armL=-1.0, armR=-1.0, armLz=.25, armRz=-.25, headY=lerp(-.6, .1, seg(t, 0, 1.5)), headX=-.05); kid.setface('scared' if t < 1.4 else 'shock')
    chest(P['jar'], kid)
    k = seg(t, 0, L - .5)
    dad.walk(dad_path_cake(), k, .9, .45, armR=-1.35 if t < L - .8 else -.3); dad.setface('angry' if t < 1.6 else 'yum'); dad.flash_on(t < L - .8)
    P['cakeL'].energy = 14
    kfill(G, 322, F1 + 9, -3, 300, 0xa8bcff)
    cam(G, 320.5, F1 + 5.0, -10.5, lerp(314, 318.0, k), F1 + 5.0, lerp(-6, 9, k), 46, t=t)

def s_eat(t, G, L):
    dad, P = G['dad'], G['P']
    bite = t > .35
    a = -1.75 + .2 * math.sin(t * 9) if bite else lerp(-.3, -1.75, seg(t, 0, .35))
    dad.pose(DAD_TABLE, 0, armR=a, armRyaw=-.55, headX=.08); dad.setface('yum')
    hold(P['slice'], dad, 'R', (0, -.3, -2.25))
    P['cakeL'].energy = 14
    kfill(G, 319, F1 + 8, 16, 160, 0xffd2a0)
    close(G, dad, lerp(7.0, 6.2, t / L), -.12, .5, 32, tdy=-.5, t=t)

def s_turn(t, G, L):
    kid, dad, P = G['kid'], G['dad'], G['P']
    tr = ease(seg(t, .55, 1.05))
    kid.pose(KID_HIDE, 0, crouch=.85 - .25 * seg(t, 0, .4), headX=-.05, armL=-1.0, armR=-1.0, armLz=.25, armRz=-.25); kid.setface('sneaky' if t < 1.0 else 'shock')
    chest(P['jar'], kid)
    dad.pose(DAD_TABLE, lerp(0, PI, tr), armR=-1.75 + .55 * tr); dad.setface('yum' if t < 1.05 else 'shock')
    hold(P['slice'], dad, 'R', (0, -.3, -2.25))
    P['cakeL'].energy = 14
    kfill(G, 316, F1 + 9, -2, 900, 0xbfd0ff)
    zoom = easeOut(seg(t, 1.05, 1.4))
    cam(G, 324.0, F1 + 4.4, -19.0, lerp(320.0, 318.0, zoom), F1 + 5.8, lerp(4, 11.0, zoom), lerp(44, 22, zoom), t=t)

def s_stare(t, G, L):
    stare_stage(t, G, turned=True)
    G['kid'].setface('shock'); G['dad'].setface('shock')
    blink = (t % 1.0) > .9
    if t < L / 2:
        close(G, G['dad'], lerp(6.0, 5.4, t / L), 0, .1, 28, t=t)
        if blink: G['dad'].setface('sleep')
    else:
        close(G, G['kid'], lerp(5.0, 4.5, t / L), 0, .2, 28, t=t)
        if blink: G['kid'].setface('sleep')

def s_dadsays(t, G, L):
    stare_stage(t, G, turned=True)
    dad = G['dad']
    dad.pose(DAD_TABLE, PI, armR=-1.1, armL=-1.45 * seg(t, .1, .4), lean=.1 * seg(t, 0, .5), headX=.1); dad.setface('sneaky')
    hold(G['P']['slice'], dad, 'R', (0, -.3, -2.25))
    close(G, dad, lerp(5.2, 5.8, t / L), .15, .1, 30, t=t)

def s_deal(t, G, L):
    stare_stage(t, G, turned=True)
    kid = G['kid']
    kid.pose(KID_HIDE, 0, crouch=.85, headX=.25 * max(0, math.sin(seg(t, .1, .7) * 2 * PI)), armL=-1.0, armR=-1.0, armLz=.25, armRz=-.25); kid.setface('sneaky' if t < .15 else 'happy')
    close(G, kid, 4.8, -.1, .2, 28, t=t)

def split_stage(t, G):
    kid, dad, P = G['kid'], G['dad'], G['P']
    dad.pose(V(318.0, F1, -9.9), PI, armR=-1.7 + .3 * max(0, math.sin(t * 6)), armRyaw=-.45, armL=-.2); dad.setface('yum')
    hold(P['slice'], dad, 'R', (0, -.3, -2.25))
    kid.pose(V(321.0, F1, -10.2), PI, armL=-1.0 - .55 * max(0, math.sin(t * 4.5 + 2)) ** 3, armLyaw=.4, armR=-.2); kid.setface('yum')
    hold(P['cookie'], kid, 'L', (0, -.35, -2.3), rot=(0, 0, PI))
    P['jar'].location = B(324.0, 4.85, -14.2); P['jarL'].energy = 40
    P['cakeL'].energy = 10

def s_split(t, G, L):
    split_stage(t, G)
    kfill(G, 319.5, F1 + 9, -18, 420, 0xffe0b8)
    cam(G, lerp(318.6, 320.4, t / L), F1 + 7.4, -25.0, 319.5, F1 + 5.6, -11.3, 34, t=t)

def s_mom(t, G, L):
    kid, dad, mom = G['kid'], G['dad'], G['mom']
    split_stage(t if t < 1.2 else 1.2, G)
    k = seg(t, .3, 1.5)
    mp = vl(V(305.6, F1, -24.4), V(309.4, F1, -22.6), easeOut(k))
    mom.pose(mp, yawTo(mp, V(319.4, F1, -10)), k * 6, .45 if 0 < k < 1 else 0, armR=-1.45); mom.setface('evil'); mom.flash_on(True)
    if t > 1.6:
        s = easeOut(seg(t, 1.6, 1.9))
        dad.pose(V(318.0, F1, -9.9), lerp(PI, PI + .9, s), armR=-2.0, armL=-.2, headY=.4 * s); dad.setface('shock')
        kid.pose(V(321.0, F1, -10.2), lerp(PI, PI + .7, s), armL=-2.2, armR=-.2, headY=.4 * s, bodyZ=.35 * math.sin(seg(t, 1.6, 1.85) * PI)); kid.setface('shock')
        hold(G['P']['slice'], dad, 'R', (0, -.3, -2.25)); hold(G['P']['cookie'], kid, 'L', (0, -.35, -2.3))
    G['R']['kitchen'].data.energy *= .45
    kfill(G, 321, F1 + 9, -6, 160, 0xa8bcff)
    cam(G, lerp(327.0, 326.4, t / L), F1 + 6.4, -26.5, 315.0, F1 + 5.0, -15.5, 44, shake=.06 if 1.6 < t < 2.0 else 0, t=t)

def s_end(t, G, L):
    mom = G['mom']
    mom.pose(V(309.4, F1, -22.6), yawTo(V(309.4, 0, -22.6), V(319.4, 0, -10)), armR=-1.45, headX=-.05); mom.setface('evil'); mom.flash_on(True)
    G['R']['kitchen'].data.energy *= .35; G['R']['entry'].data.energy *= .4
    kfill(G, 311, F1 + 5, -19.5, 90, 0xff8080)
    k = easeOut(t / L)
    close(G, mom, lerp(7.5, 5.8, k), 0, -.4, 30, t=t)

SHOTS = dict(hook=s_hook, bed=s_bed, jar=s_jar, out=s_out, hall=s_hall, parents=s_parents, stairs=s_stairs, cat=s_cat,
             catclose=s_catclose, plead=s_plead, dadwake=s_dadwake, grab=s_grab, hide=s_hide, dadin=s_dadin, cake=s_cake,
             eat=s_eat, turn=s_turn, stare=s_stare, dadsays=s_dadsays, deal=s_deal, split=s_split, mom=s_mom, end=s_end)

try:
    import shots_show
    SHOTS.update(shots_show.SHOW)
except ImportError:
    pass
