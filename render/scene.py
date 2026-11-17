# Builds the full scene: your house (from assets/house.gltf) + cast + props + lights + render settings.
import bpy, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
ROOT = os.path.abspath(os.path.join(HERE, '..'))

def load_house():
    baked = os.path.join(ROOT, 'assets', 'house.blend')
    if os.path.exists(baked) and 'bake_house' not in sys.argv[0]:
        bpy.ops.wm.open_mainfile(filepath=baked); return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, 'assets', 'house.gltf'))
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
        if not b: continue
        if b.inputs['Roughness'].default_value < .3 and b.inputs['Alpha'].default_value > .95 and not b.inputs['Roughness'].is_linked:
            b.inputs['Roughness'].default_value = .5
        b.inputs['Specular IOR Level'].default_value = .35

def place():
    """assets/place.json picks where the story happens: {"place": "house"} or
    {"place": "town", "seed": 7, "theme": "suburb|city|beach|snow", "time": "day|sunset|night", "size": 3}"""
    p = os.path.join(ROOT, 'assets', 'place.json')
    return json.load(open(p)) if os.path.exists(p) else {'place': 'house'}

def build(res=(960, 540), spp=8):
    P0 = place(); TOWN = None
    if P0.get('place') == 'town':
        import town
        bpy.ops.wm.read_factory_settings(use_empty=True)
        TOWN = town.build_town(seed=P0.get('seed', 7), theme=P0.get('theme', 'suburb'), time=P0.get('time', 'day'), size=P0.get('size', 3))
        json.dump(TOWN, open(os.path.join(ROOT, 'assets', 'town_layout.json'), 'w'), indent=1)
    else:
        load_house()
    S = bpy.context.scene
    if not S.world: S.world = bpy.data.worlds.new('w')
    S.world.use_nodes = True
    kid, dad, mom = make_cast(); cat = Cat(); P = make_props()
    import chars2; friends = chars2.make_friends()
    flashlight(dad); flashlight(mom)
    cam = camera()
    R = {}
    if TOWN is not None:
        lamp = point('lamp', 0, 0, -500, 0, 0xffc27a, .4); nl = point('nightlight', 0, 0, -500, 0, 0xffb060, .2); kf = point('kfill', 0, 0, -500, 0, 0xffffff, 2.0)
        P['jar'].location = (0, 0, -500); P['cake'].location = (0, 0, -500)
        _render_settings(S, res, spp)
        return dict(S=S, kid=kid, dad=dad, mom=mom, cat=cat, P=P, cam=cam, R=R, R0={}, lamp=lamp, nl=nl, kfill=kf, TOWN=TOWN, friends=friends)
    R['kidroom'] = area('A_kid', 272, 29.5, -14, 2200, 0x9fb4ff, 14, 272, 16, -14)
    R['hall2'] = area('A_hall2', 297, 29.5, -8, 1100, 0x9fb4ff, 8, 297, 16, -8)
    R['parents'] = area('A_par', 320, 29.5, -12, 1800, 0x9fb4ff, 12, 320, 16, -12)
    R['entry'] = area('A_entry', 300, 14.5, -14, 1300, 0x9fb4ff, 9, 300, 1, -14)
    R['kitchen'] = area('A_kit', 320, 14.5, -12, 2200, 0x9fb4ff, 12, 320, 1, -12)
    R['dining'] = area('A_din', 318, 14.5, 14, 1500, 0x9fb4ff, 12, 318, 1, 14)
    R['living'] = area('A_liv', 268, 14.5, -14, 1800, 0x9fb4ff, 14, 268, 1, -14)
    G0 = {k: o.data.energy for k, o in R.items()}
    lamp = point('lamp', 0, 0, -500, 0, 0xffc27a, .4); nl = point('nightlight', 0, 0, -500, 0, 0xffb060, .2); kf = point('kfill', 0, 0, -500, 0, 0xffffff, 2.0)
    point('hallNL', 293.6, 18.0, -6.0, 25, 0xffb060, .2)
    sun = bpy.data.objects.new('moon', bpy.data.lights.new('moon', 'SUN')); sun.data.energy = 1.2; sun.data.color = srgb(0x9fb4ff); sun.data.angle = .05
    sun.rotation_euler = (math.radians(55), 0, math.radians(200)); link(sun)
    bg = S.world.node_tree.nodes['Background']; bg.inputs[0].default_value = (.01, .015, .04, 1); bg.inputs[1].default_value = 1
    _render_settings(S, res, spp)
    return dict(S=S, kid=kid, dad=dad, mom=mom, cat=cat, P=P, cam=cam, R=R, R0=G0, lamp=lamp, nl=nl, kfill=kf, TOWN=None, friends=friends)

def _render_settings(S, res, spp):
    # bake bevel modifiers into plain meshes so nothing is re-computed every frame
    dg = bpy.context.evaluated_depsgraph_get()
    for o in [o for o in bpy.data.objects if o.type == 'MESH' and o.modifiers]:
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); o.modifiers.clear(); o.data = me
    S.render.engine = 'CYCLES'; c = S.cycles
    c.samples = spp; c.use_denoising = True; c.denoiser = 'OPENIMAGEDENOISE'; c.use_adaptive_sampling = True; c.adaptive_threshold = .1
    c.max_bounces = 3; c.diffuse_bounces = 1; c.glossy_bounces = 1; c.transmission_bounces = 3; c.transparent_max_bounces = 6
    c.caustics_reflective = False; c.caustics_refractive = False
    S.render.use_persistent_data = True
    S.render.resolution_x, S.render.resolution_y = res; S.render.resolution_percentage = 100
    S.render.fps = FPS; S.render.image_settings.file_format = 'JPEG'; S.render.image_settings.quality = 93
    S.view_settings.view_transform = 'AgX'; S.view_settings.look = 'AgX - Medium High Contrast'
