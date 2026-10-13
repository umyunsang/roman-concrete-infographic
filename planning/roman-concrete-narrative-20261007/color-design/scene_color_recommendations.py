"""Add proposed roles to read-only evidence JSON; no Blender imports or edits."""
import json
from pathlib import Path
P=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/color-design/scene-color-inventory.json')
d=json.loads(P.read_text())
palette={
 'paper':'#F5F1E8','terrain':'#ECE7DA','terrain_mountain':'#D3CDBF',
 'hero_travertine':'#D1B498','support_stone':'#C4B39C','support_arch_shadow':'#9C8873',
 'road':'#D1C4B0','farm':'#C4C4A8','foliage':'#96A187','sea':'#B7CFCE','river':'#A9C7C7','water_marks':'#DAE6DF',
 'modern_cool_concrete':'#93A5AC','lab_cool_concrete':'#B1BDBC',
 'roman_matrix':'#9B7A5F','lime_chalk':'#FFF8E7','hot_mixing_scene':'#CAB08E',
 'heat':'#B95E3B','accent_narrative':'#A54F36','water_action':'#43858D',
 'process_arrow':'#536B68','open_crack':'#403D38','deep_foundation':'#796B5C',
 'medium_aggregate':'#B7A48B','light_aggregate':'#E2D5BD','heavy_aggregate':'#967E63',
 'brick':'#BA8466','ink':'#30423F','line':'#7B8D85','volcanic_stone':'#B5ABA0',
 'marine_concrete':'#AAA28F','marine_crystal':'#F8F4E5','tank':'#D5DDD4',
 'timber':'#B79573','ash':'#A6A39A','book_cover':'#80948A','book_pages':'#F5EDD9'}

def role(x):
 n,c=x['name'],x['category']
 if not x['render_visible_in_saved_scene'] or x['type']!='MESH':return None
 if c=='terrain_plain':return 'terrain'
 if c=='mountains':return 'terrain_mountain'
 if c=='vegetation_tree':return 'foliage'
 if c=='agricultural_fields':return 'farm'
 if c=='roads':return 'road'
 if c=='hero_colosseum':return 'hero_travertine'
 if c=='water':return 'sea' if n=='L10_sea' else 'river'
 if c=='water_surface_marks':return 'water_marks'
 if c=='core1_modern_reinforced_building':return 'modern_cool_concrete'
 if c=='core2_hot_mixing':return 'hot_mixing_scene'
 if c=='core5_modern_experiment_laboratory':return 'lab_cool_concrete'
 if c=='core3_lime_clast_specimen':return 'lime_chalk' if '_LIME' in n else 'roman_matrix'
 if c=='core4_crack_sequence':
  return {'00':'process_arrow','01':'open_crack','02':'lime_chalk','03':'roman_matrix','04':'water_action'}.get(n[-2:])
 if c=='detail1_marine_chemistry':
  if n=='D1_concrete':return 'marine_concrete'
  if n=='D1_seawater':return 'sea'
  if n.startswith('D1_crystal'):return 'marine_crystal'
  return 'tank'
 if c=='detail2_hot_mixing':
  if n.startswith('D2_heat'):return 'heat'
  if n.startswith('D2_lime') and n!='D2_lime_kiln':return 'lime_chalk'
  if n=='D2_cube':return 'roman_matrix'
  return 'support_stone'
 if c=='detail3_structure':
  if n.startswith('D3_press'):return 'ink'
  if n.startswith('D3_brick'):return 'brick'
  return {'D3_foundation':'deep_foundation','D3_heavy':'heavy_aggregate','D3_middle':'medium_aggregate','D3_light':'light_aggregate'}.get(n,'support_stone')
 if c=='legacy_crack_sequence_hidden':return 'support_stone'
 if c=='core_detail_badge_or_underline':return 'accent_narrative'
 if c=='support_leader':return 'line'
 if c=='overlay_other':
  if n in {'S_sect0','S_sect1','S_sect2','S_sect3'}:return {'S_sect0':'light_aggregate','S_sect1':'medium_aggregate','S_sect2':'heavy_aggregate','S_sect3':'deep_foundation'}[n]
  if n.startswith('S_sect_brick'):return 'brick'
  return 'line' if n.startswith(('S_lead','S_sect')) else 'ink'
 if c=='header_graphic':
  if 'lime' in n or n.endswith('pages'):return 'lime_chalk'
  if 'ash' in n:return 'ash'
  if 'book' in n:return 'book_cover'
  if 'lens' in n or 'core_band' in n:return 'ink'
  if 'mold' in n:return 'timber' if 'plank' in n else 'roman_matrix'
  if 'stone' in n:return 'support_stone'
  return 'hero_travertine' if 'colosseum' in n else 'support_stone'
 if c=='support_vesuvius':return 'volcanic_stone'
 if c=='support_roman_breakwater':return 'marine_concrete'
 if c=='support_palatine' and n.endswith('_arch'):return 'support_arch_shadow'
 if c.startswith('support_') or c=='bridge':return 'support_stone'
 return 'support_stone'

recommended={}
for x in d['inventory']:
 r=role(x)
 x['suggested_color_role']=r
 x['suggested_srgb_hex']=palette[r] if r else None
 if r:recommended[x['name']]={'role':r,'srgb_hex':palette[r]}
d['suggested_palette']=palette
d['suggested_object_color_dictionary']=recommended
d['recommendation_status']='Proposed role map only; parent root selects final palette and performs all Blender/Figma writes.'
d['source_authority']={
 'live_saved_scene':str(P),
 'workbench_object_color_documentation':'https://docs.blender.org/manual/en/5.1/render/workbench/color.html',
 'linear_color_pipeline_documentation':'https://developer.blender.org/docs/features/gpu/color_management/'}
P.write_text(json.dumps(d,ensure_ascii=False,indent=2))
print(json.dumps({'proposed_render_mesh_colors':len(recommended),'all_objects':len(d['inventory'])}))
