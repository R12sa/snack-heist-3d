# Shots for the Snack Heist gameplay showcase (Nights 1-3). Uses the real house.
import math
from lib import *
import shots as S
from shots import cam, close, hold, chest, kfill, KID_HIDE, DAD_TABLE, KID_BED, JAR_ISLAND

PI = math.pi
CAKE_HOME = (320, 4.95, 16)
CAKE_SPOT = V(319.4, F1, 12.0)          # kid at the dining table, cake moved to the near edge
HIDE2 = V(277.0, F1, -16.4)             # crouched behind the living-room couch (couch x 269-283, z -20..-18)

def cake_at_chest(G, kid, fwd=1.25, up=2.35):
    """carry the birthday cake in front of the chest (flame + light ride along)"""
    bpy.context.view_layer.update()
    G['P']['cake'].location = kid.body.matrix_world @ Vector((0, -fwd, up - .9))
    G['P']['cake'].rotation_euler = (0, 0, kid.root.rotation_euler.z)

def stair_run(G, t, L, z0, z1, carry=True):
    kid = G['kid']; k = seg(t, 0, L); z = lerp(z0, z1, k)
    kid.pose(V(304.0, stairY(z), z), 0, k * abs(z1 - z0) * .75, 1.0, 0, lean=.22, armL=-1.0, armR=-1.0, armLz=.2, armRz=-.2)
    kid.setface('scared')
    if carry: cake_at_chest(G, kid)
    return z

def s_hook(t, G, L):
    z = stair_run(G, t, L, -12.5, 6.5)
    kfill(G, 304, stairY(z) + 7, z + 4, 700, 0xa8bcff)
    G['P']['cakeL'].energy = 14
    cam(G, 304.4, F2 + 5.2, 13.0, 304.0, stairY(z) + 2.8, z, 32, shake=.05, t=t)

def s_title(t, G, L):
    k = ease(t / L)
    G['lamp'].location = B(276, 22, -27); G['lamp'].data.energy = 400; G['lamp'].data.color = srgb(0xffb46a)
    kfill(G, 300, 40, -75, 40000, 0x8fa8ff)
    cam(G, lerp(322, 314, k), lerp(16, 13, k), lerp(-80, -68, k), 298, 13, -30, 50, t=t)

def s_loopbed(t, G, L): S.s_out(t, G, L)

def s_loopsnack(t, G, L):
    kid, P = G['kid'], G['P']
    r = seg(t, .1, .6)
    if t < .7:
        kid.pose(V(325.8, F1, -15.6), -PI / 2, 0, 0, 0, armR=-1.9 * r, armL=-.2); kid.setface('sneaky')
        if t > .55: hold(P['jar'], kid, 'R')
    else:
        k = seg(t, .7, L)
        yaw = lerp(-PI / 2, PI, easeOut(seg(t, .7, 1.1)))
        p = vl(V(325.8, F1, -15.6), V(325.6, F1, -21.5), k)
        kid.pose(p, yaw, k * 6, .6, .7, armL=-1.0, armR=-1.0, armLz=.25, armRz=-.25); kid.setface('yum')
        chest(P['jar'], kid)
    P['jarL'].energy = 60
    kfill(G, 322, F1 + 8, -9, 300, 0xa8bcff)
    cam(G, 330.2, F1 + 5.4, -10.6, 325.5, F1 + 3.2, lerp(-15.8, -19, seg(t, .7, L)), 42, t=t)

def s_n1parents(t, G, L): S.s_parents(t, G, L)
def s_n1hall(t, G, L): S.s_hall(t, G, L)

def s_n1jar(t, G, L):
    kid, P = G['kid'], G['P']
    k = seg(t, 0, L - .5)
    p = kid.walk([V(266.5, F2, -10.2), V(262.4, F2, -6.4), V(259.8, F2, -3.6)], k, 1, .6, .6, armL=-1.0, armR=-1.0, armLz=.25, armRz=-.25)
    kid.setface('yum' if t > L - .6 else 'sneaky'); chest(P['jar'], kid)
    G['nl'].location = B(258.6, 19.0, -.6); G['nl'].data.energy = 60
    kfill(G, p.x + 3, F2 + 7, p.z - 3, 240, 0xa8bcff)
    cam(G, 270.6, F2 + 5.6, -15.0, lerp(264.5, 260.5, k), F2 + 2.6, lerp(-8, -4, k), 44, t=t)

def s_n2cat(t, G, L): S.s_cat(t, G, L)

def s_n2dad(t, G, L):
    S.s_dadwake(min(L, t + .4), G, L + .4)

def s_n2hide(t, G, L):
    kid = G['kid']
    kid.pose(HIDE2, 0, 0, 0, 1.0, headY=.55 * math.sin(t * 2.2), armL=-.9, armR=-.9, armLz=.25, armRz=-.25)
    kid.setface('scared')
    G['R']['living'].data.energy *= .6
    kfill(G, 280, F1 + 7, -11, 260, 0xa8bcff)
    cam(G, lerp(278.4, 277.8, t / L), F1 + 3.6, lerp(-10.0, -10.8, t / L), 277.0, F1 + 2.6, -18.0, 44, t=t)

def s_n2pass(t, G, L):
    kid, dad = G['kid'], G['dad']
    kid.pose(HIDE2, 0, 0, 0, 1.0, headY=lerp(.6, 1.25, seg(t, 0, L)), armL=-.9, armR=-.9, armLz=.25, armRz=-.25)
    kid.setface('scared' if t < 1.2 else 'shock')
    k = seg(t, 0, L)
    dad.walk([V(290.0, F1, -29.8), V(276.0, F1, -30.0), V(264.0, F1, -29.8)], k, .9, .45, armR=-1.35, armRyaw=.45 * math.sin(t * 2.2), headY=.4 * math.sin(t * 2.2))
    dad.setface('angry'); dad.flash_on(True)
    G['R']['living'].data.energy *= .5
    kfill(G, 279, F1 + 7, -11, 220, 0xa8bcff)
    cam(G, 279.4, F1 + 4.4, -11.4, lerp(283, 270, k), F1 + 4.6, -27.0, 48, t=t)

def patrol(G, t, dk=1.0):
    dad, mom = G['dad'], G['mom']
    dad.walk([V(305.5, F1, -23.0), V(309.5, F1, -22.0), V(311.4, F1, -16.5)], seg(t, 0, 3.0) * dk, .9, .45,
             armR=-1.35, armRyaw=.55 * math.sin(t * 1.8), headY=.5 * math.sin(t * 1.8)); dad.setface('angry'); dad.flash_on(True)
    mom.walk([V(315.5, F1, -3.0), V(315.8, F1, -8.5)], seg(t, .2, 2.2), .9, .45,
             armR=-1.35, armRyaw=.5 * math.sin(t * 1.6 + 1), headY=.45 * math.sin(t * 1.6 + 1)); mom.setface('angry'); mom.flash_on(True)

def s_n3patrol(t, G, L):
    kid = G['kid']
    kid.pose(KID_HIDE, 0, crouch=1.0, armL=-.9, armR=-.9, armLz=.25, armRz=-.25, headY=-.6); kid.setface('scared')
    patrol(G, t)
    G['R']['kitchen'].data.energy *= .4; G['R']['entry'].data.energy *= .5
    kfill(G, 322, F1 + 9, -8, 140, 0xa8bcff)
    cam(G, lerp(327.4, 326.6, t / L), F1 + 6.6, -26.8, 314.5, F1 + 4.6, -14.5, 48, t=t)

def s_n3throw(t, G, L):
    kid, dad, mom, P = G['kid'], G['dad'], G['mom'], G['P']
    sw = seg(t, .15, .4)
    kid.pose(KID_HIDE, -PI / 2 + .5, crouch=.55, armR=lerp(-2.7, -1.1, sw) if t > .15 else -2.7 * seg(t, 0, .15), armL=-.4, headY=-.2); kid.setface('sneaky')
    if t < .4: hold(P['toy'], kid, 'R')
    else:
        u = seg(t, .4, 1.1); a = V(324.2, F1 + 5.6, -13.8); b = V(309.0, F1 + .2, -26.0)
        p = vl(a, b, u); p.y += math.sin(u * PI) * 7
        P['toy'].location = B(p.x, p.y, p.z); P['toy'].rotation_euler = (u * 9, u * 5, 0)
    patrol(G, 3.0 + t * .2, 1.0)
    if t > 1.1:  # both turn toward the noise
        s = easeOut(seg(t, 1.1, 1.6))
        dad.pose(V(311.4, F1, -16.5), lerp(dad.root.rotation_euler.z, yawTo(V(311.4, 0, -16.5), V(309, 0, -26)), s), armR=-1.3); dad.setface('shock'); dad.flash_on(True)
        mom.pose(V(315.8, F1, -8.5), lerp(PI, yawTo(V(315.8, 0, -8.5), V(309, 0, -26)), s), armR=-1.3); mom.setface('shock'); mom.flash_on(True)
    G['R']['kitchen'].data.energy *= .4; G['R']['entry'].data.energy *= .5
    kfill(G, 326, F1 + 7, -9, 160, 0xa8bcff)
    cam(G, 329.0, F1 + 4.4, -9.8, 313.0, F1 + 4.0, -20.0, 48, t=t)

def s_n3cake(t, G, L):
    kid, P = G['kid'], G['P']
    G['P']['cake'].location = B(319.4, 4.95, 14.4)
    if t < .5:
        kid.pose(CAKE_SPOT, 0, armL=-1.5 * seg(t, 0, .35), armR=-1.5 * seg(t, 0, .35)); kid.setface('yum')
    else:
        s = easeOut(seg(t, .5, .95))
        kid.pose(CAKE_SPOT, lerp(0, PI, s), (t - .5) * 8, .8 * s, 0, armL=-1.0, armR=-1.0, armLz=.2, armRz=-.2); kid.setface('scared')
        cake_at_chest(G, kid)
    P['cakeL'].energy = 16
    kfill(G, 319, F1 + 9, 17, 320, 0xffd2a0)
    cam(G, 321.6, F1 + 8.4, 20.2, 319.4, F1 + 3.6, 12.8, 40, t=t)

def s_n3stairs(t, G, L):
    z = stair_run(G, t, L, -11.0, 5.0)
    G['P']['cakeL'].energy = 14
    kfill(G, 304, stairY(z) + 7, z - 4, 300, 0xa8bcff)
    cam(G, 304.6, F1 + 4.2, -21.0, 304.0, stairY(z) + 3.0, z, 36, shake=.04, t=t)

def s_n3bed(t, G, L):
    kid, dad = G['kid'], G['dad']
    kid.lie(*KID_BED, headYaw=0, breathe=.04 * math.sin(t * 6)); kid.head.rotation_euler = (0, 0, -1.0)
    kid.setface('sleep' if t < .55 else 'sneaky')
    dp = V(268.5, F2, -11.5)
    dad.pose(dp, yawTo(dp, V(256, 0, -3)), armR=-1.15); dad.setface('angry'); dad.flash_on(True)
    G['nl'].location = B(258.6, 19.0, -.6); G['nl'].data.energy = 40
    kfill(G, 259.5, 22.2, -3.5, 220, 0xa8bcff)
    cam(G, 259.6, 21.9, -2.0, 255.3, 20.6, -1.6, 32, t=t)

def s_perks(t, G, L):
    kid = G['kid']; k = seg(t, 0, L)
    kid.walk([V(297.2, F2, -16.0), V(297.2, F2, 4.0)], k, 1.0, 1.0, 0, lean=.2); kid.setface('happy')
    kfill(G, 297, F2 + 8, 2, 700, 0xa8bcff)
    cam(G, 297.6, F2 + 3.6, 9.2, 297.2, F2 + 3.2, lerp(-12, 2, k), 42, t=t)

def s_friends(t, G, L):
    team = [G['kid']] + G['friends']; k = seg(t, 0, L)
    for i, c in enumerate(team):
        z = lerp(-17.0, -6.5, k) - i * 3.6
        c.pose(V(297.2 + (i % 2) * 2.0 - 1.0, F2, z), 0, k * 10.5 * .9 + i, .6, .9, headY=.35 * math.sin(t * 2 + i), armL=-.4, armR=-.4)
        c.setface(['sneaky', 'happy', 'sneaky', 'yum'][i])
    kfill(G, 297, F2 + 8, -4, 800, 0xa8bcff)
    cam(G, 299.8, F2 + 4.0, 2.0, 297.0, F2 + 2.4, lerp(-15, -9, k), 42, t=t)

def s_cta(t, G, L):
    k = ease(t / L)
    G['lamp'].location = B(276, 22, -27); G['lamp'].data.energy = 400; G['lamp'].data.color = srgb(0xffb46a)
    kfill(G, 300, 40, -75, 40000, 0x8fa8ff)
    cam(G, lerp(286, 290, k), lerp(11, 13, k), lerp(-74, -62, k), 296, 14, -30, 48, t=t)

def s_end(t, G, L):
    kid = G['kid']; kid.lie(*KID_BED, headYaw=0, breathe=.03 * math.sin(t * 2.5)); kid.head.rotation_euler = (0, 0, -1.1)
    kid.setface('sneaky' if t < 1.4 else 'yum')
    G['nl'].location = B(258.6, 19.0, -.6); G['nl'].data.energy = 60
    kfill(G, 258.5, 21.5, -3.0, 120, 0xa8bcff)
    cam(G, 259.6, 21.9, lerp(-2.4, -1.8, t / L), 255.3, 20.6, -1.6, lerp(34, 28, t / L), t=t)

def _bright(fn):
    def f(t, G, L):
        G['S'].view_settings.exposure = .55; fn(t, G, L)
    return f

SHOW = dict(hook=s_hook, title=s_title, loopbed=s_loopbed, loopsnack=s_loopsnack, n1parents=s_n1parents, n1hall=s_n1hall, n1jar=s_n1jar,
            n2cat=s_n2cat, n2dad=s_n2dad, n2hide=s_n2hide, n2pass=s_n2pass, n3patrol=s_n3patrol, n3throw=s_n3throw, n3cake=s_n3cake,
            n3stairs=s_n3stairs, n3bed=s_n3bed, perks=s_perks, friends=s_friends, cta=s_cta, end=s_end)

SHOW = {k: _bright(v) for k, v in SHOW.items()}
