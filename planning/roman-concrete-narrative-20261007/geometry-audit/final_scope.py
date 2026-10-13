"""Read-only exact component selection and refined final slot recommendations."""
exec((__import__('pathlib').Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/geometry-audit/evaluate_slots.py')).read_text())

all_components=[]
field=cache['F_centuriatio']
for idx,indices in enumerate(groups.values()):
    p=field['pts'][indices];uv=helper.project_pts(p)
    bb=[float(uv[:,0].min()),float(uv[:,1].min()),float(uv[:,0].max()),float(uv[:,1].max())]
    all_components.append({'component_id':idx,'vertex_indices':indices,'world_min':p.min(0).tolist(),
                           'world_max':p.max(0).tolist(),'projected_bbox':bb})

pad=1.5
modern=cache['NB_modern_building']['info']
lo=np.array(modern['world_min'][:2])-pad;hi=np.array(modern['world_max'][:2])+pad
plaza=[c for c in all_components if np.all(np.array(c['world_min'][:2])<hi) and np.all(np.array(c['world_max'][:2])>lo)]
caption_zone=[515,478,710,569]
caption=[c for c in all_components if bbox_overlap(c['projected_bbox'],caption_zone)]
def aggregate(xs):
    return {'component_count':len(xs),'vertex_count':sum(len(c['vertex_indices']) for c in xs),
            'component_ids':[c['component_id'] for c in xs],
            'projected_bbox':[min(c['projected_bbox'][0] for c in xs),min(c['projected_bbox'][1] for c in xs),max(c['projected_bbox'][2] for c in xs),max(c['projected_bbox'][3] for c in xs)],
            'world_xy_min':[min(c['world_min'][j] for c in xs) for j in range(2)],
            'world_xy_max':[max(c['world_max'][j] for c in xs) for j in range(2)],
            'components':xs}

# Full bottom-vertex terrain requirement, avoiding sparse ray sampling.
ground_moves=[]
for name in ['NB_modern_building','NB_lime_clast_specimen']:
    p=cache[name]['pts'];zmin=p[:,2].min();zmax=p[:,2].max()
    foot=p[p[:,2]<=zmin+max(.02,(zmax-zmin)*.005)]
    deficits=[ground_z(v[0],v[1])-v[2] for v in foot if ground_z(v[0],v[1]) is not None]
    minimum_dz=max(deficits)+.02
    ground_moves.append({'name':name,'bottom_vertices_tested':len(foot),'required_dz_to_clear_all_tested_bottom_vertices':minimum_dz,
                         'candidate':displaced(name,dz=minimum_dz)})

marine=[displaced('NB_marine_breakwater',0,dv,-.85) for dv in [-11,-24,-28,-30]]
final={'component_id_method':'deterministic insertion order of connected components via vertex-index union-find on evaluated F_centuriatio mesh. IDs are audit IDs, not Blender datablock IDs; exact vertex_indices are authoritative.',
       'plaza_world_xy_boundary':[lo.tolist(),hi.tolist()],'modern_plaza':aggregate(plaza),
       'core1_caption_screen_zone':caption_zone,'caption_field_components':aggregate(caption),
       'ground_moves':ground_moves,'marine_slots':marine}
(ROOT/'placement_scope.json').write_text(json.dumps(final,ensure_ascii=False,indent=2))
print('PLAZA',final['modern_plaza']['component_count'],final['modern_plaza']['vertex_count'],final['modern_plaza']['projected_bbox'])
print('CAPTION',final['caption_field_components']['component_count'],final['caption_field_components']['vertex_count'],final['caption_field_components']['projected_bbox'])
for x in ground_moves:print('FINALGROUND',x['name'],x['bottom_vertices_tested'],x['required_dz_to_clear_all_tested_bottom_vertices'],x['candidate']['new_bbox'])
for x in marine:print('FINALMARINE',x['du_dv_dz'],x['delta_world'],x['new_bbox'],x['bottom_sample_land_count'],x['bottom_sample_sea_count'])
