import bpy, sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'layout'))
from common import Screen, world_verts, map_visible_objects
S = Screen()
sc = bpy.context.scene
print('SCENE KEYS', list(sc.keys()))
cam = sc.camera
print('CAM', cam.data.type, tuple(round(v,3) for v in cam.location), tuple(round(v,4) for v in cam.rotation_euler), cam.data.lens if cam.data.type!='ORTHO' else cam.data.ortho_scale, sc.render.resolution_x, sc.render.resolution_y)
OWN = ['T_land','R_core_road','R_via_appia','R1_road_landing1','R1_road_landing5','R1_road5_bed','B_pons1','B_pons1_parapet0','B_pons1_parapet1','B_pons2','B_pons2_parapet0','B_pons2_parapet1','R4_bridge_west_bed','F_centuriatio','L02_tiber','L10_sea','W_water_marks']
REF = ['L05_aqua_claudia','R1_lab_bench','C5_researchers','D2_heat','L11_privernum_wall','R_roadgeo_ostiensis_junction_fill','R_via_ostiensis','R3_colosseum_podium']
for n in OWN+REF:
    o = bpy.data.objects.get(n)
    if o is None:
        print('MISSING', n); continue
    if o.type != 'MESH':
        print(n, o.type); continue
    me = o.data
    Wv = world_verts(o)
    P = S.project(Wv) if len(Wv) else np.zeros((0,2))
    sm = np.empty(len(me.polygons), bool); me.polygons.foreach_get('use_smooth', sm)
    print(n, 'v', len(me.vertices), 'f', len(me.polygons), 'users', me.users,
          'mats', [s.material.name if s.material else None for s in o.material_slots],
          'mods', [(m.type, m.name) for m in o.modifiers],
          'wmin', np.round(Wv.min(0),3).tolist(), 'wmax', np.round(Wv.max(0),3).tolist(),
          'pt', np.round([P[:,0].min(),P[:,0].max(),P[:,1].min(),P[:,1].max()],1).tolist(),
          'smooth', round(float(sm.mean()),3), 'colls', [c.name for c in o.users_collection],
          'attrs', [a.name for a in me.attributes if not a.name.startswith('.')],
          'loc', np.round(o.location[:],3).tolist(), 'rot', np.round(o.rotation_euler[:],4).tolist(), 'scale', np.round(o.scale[:],4).tolist())
# objects whose names start with R8 / cube
names = sorted(o.name for o in bpy.data.objects if o.type=='MESH')
print('ALL MESH', len(names))
print([n for n in names if n.startswith(('R8','R3_','R1_','C4','C5','S_','D2','D4','L0','L1'))])
