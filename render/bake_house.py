# One-time: turn assets/house.gltf into assets/house.blend (one joined mesh) so every render loads fast.
import bpy, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene
scene.load_house()
# leave interior doors out so doorways are open (characters can walk through rooms)
for root in [o for o in bpy.data.objects if o.name.split('.')[0] == 'Doors']:
    for o in list(root.children_recursive) + [root]: bpy.data.objects.remove(o, do_unlink=True)
ms = [o for o in bpy.data.objects if o.type == 'MESH']
for o in bpy.data.objects: o.select_set(False)
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active = ms[0]
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.join()
for o in list(bpy.data.objects):
    if o.type != 'MESH': bpy.data.objects.remove(o)
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(scene.ROOT, 'assets', 'house.blend'), compress=True)
print('baked', len(bpy.data.objects), len(bpy.context.view_layer.objects.active.data.polygons))
