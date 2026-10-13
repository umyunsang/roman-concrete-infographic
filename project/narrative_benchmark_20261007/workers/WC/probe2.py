import bpy, sys, json
import numpy as np
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/layout')
from common import Screen, world_verts
S = Screen()
print('blender', bpy.app.version_string)
np.set_printoptions(precision=3, suppress=True, linewidth=200)
O = bpy.data.objects
g3 = O['NB_core4_sequence_GRAY03']; Wv = world_verts(g3)
print('GRAY03 parent', g3.parent.name, list(g3.parent.location), list(g3.parent.rotation_euler), list(g3.parent.scale), g3.parent.type)
# split cubes by x clusters
import numpy as np
lab = np.argsort(Wv[:,0])
xs = Wv[:,0]
order = np.argsort(xs)
# group by connectivity
me = g3.data
import bmesh
bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table()
comp = [-1]*len(bm.verts); c=0
for v in bm.verts:
    if comp[v.index]>=0: continue
    st=[v]; comp[v.index]=c
    while st:
        u=st.pop()
        for e in u.link_edges:
            w=e.other_vert(u)
            if comp[w.index]<0: comp[w.index]=c; st.append(w)
    c+=1
comp=np.array(comp)
for k in range(c):
    P = Wv[comp==k]
    mn, mx = P.min(0), P.max(0)
    print('cube',k,'min',mn,'max',mx,'size',mx-mn,'center',(mn+mx)/2)
    corners = np.array([[x,y,z] for x in (mn[0],mx[0]) for y in (mn[1],mx[1]) for z in (mn[2],mx[2])])
    print('  corners pt', [tuple(np.round(p,1)) for p in S.project(corners)])
    print('  corner order: (x,y,z) min/max combos')
# bevel? faces normals
for n in ['NB_core4_sequence_GRAY00','NB_core4_sequence_GRAY02','NB_core4_sequence_GRAY04','R8_water_step1','R8_crack_step1','R8_crack_step2','R8_calcium_step2','R8_healed_step3','R1_water_in_crack1']:
    o=O[n]; Wv=world_verts(o)
    print(n, 'parent', o.parent.name if o.parent else None, 'nv', len(Wv), 'min', Wv.min(0), 'max', Wv.max(0))
    if len(Wv)<=30:
        print('   verts', Wv)
        print('   pt', S.project(Wv))
o=O['NB_core4_sequence_GRAY02']
me=o.data
print('GRAY02 polys', len(me.polygons), 'smooth', me.polygons[0].use_smooth)
o=O['NB_core4_sequence_GRAY04']; print('GRAY04 local loc', list(o.location), 'nv', len(o.data.vertices))
# lime specimen
sp=O['NB_lime_clast_specimen']; Wv=world_verts(sp)
print('specimen world min', Wv.min(0), 'max', Wv.max(0), 'dims', Wv.max(0)-Wv.min(0), 'dimensions', list(sp.dimensions))
for i in range(6):
    o=O[f'NB_lime_clast_specimen_LIME{i:02d}']; w=o.matrix_world.translation
    print(o.name, 'world', np.array(w), 'world radius', o.scale[0]*sp.scale[0], 'pt', S.to_pt(w), 'mesh', o.data.name, len(o.data.vertices))
    print('   bbox local', np.array([v.co for v in o.data.vertices]).min(0), np.array([v.co for v in o.data.vertices]).max(0))
for n in ['R1_healed_clast0','R1_healed_clast1','R1_healed_clast2','R1_specimen_healed','R1_specimen_leaking','R3_healed_fill','R3_leak_crack','R1_leak_drop0','R1_leak_puddle','R1_lab_bench']:
    o=O[n]; Wv=world_verts(o); lv=np.array([v.co for v in o.data.vertices])
    print(n, 'nv', len(Wv), 'local bbox', lv.min(0), lv.max(0), 'world min', Wv.min(0), 'max', Wv.max(0), 'smooth', o.data.polygons[0].use_smooth if len(o.data.polygons) else None)
    if len(Wv)<=12: print('   verts', Wv)
sc=bpy.context.scene
print('shading', sc.display.shading.light, sc.display.shading.studio_light, 'wsl', sc.display.shading.use_world_space_lighting, 'rot', sc.display.shading.studiolight_rotate_z, 'cavity', sc.display.shading.cavity_type, sc.display.shading.cavity_ridge_factor, sc.display.shading.cavity_valley_factor, sc.display.shading.curvature_ridge_factor, sc.display.shading.curvature_valley_factor)
print('specular', sc.display.shading.show_specular_highlight, 'xray', sc.display.shading.show_xray, 'outline', sc.display.shading.show_object_outline, 'shadow intensity', sc.display.shading.shadow_intensity)
cam=sc.camera; print('cam loc', list(cam.location), 'rot', list(cam.rotation_euler), 'lens', cam.data.lens, 'sensor', cam.data.sensor_width)
