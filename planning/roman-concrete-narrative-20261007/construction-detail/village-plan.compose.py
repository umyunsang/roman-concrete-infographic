from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
B=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/construction-detail')
R=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007')
M=np.load(B/'village-plan.masks.npz');H=np.load(B/'village-plan.hero.npz');I=json.loads((B/'village-plan.inventory.json').read_text())
N=json.loads((R/'out/figma-v14-road-native-validation.json').read_text())
source_sha='f58d958eee5db375a76779f337681be96f8b7b6f0f0d4ba562f7d9aa3f79f528'
assert I['sha256']==source_sha

def stats(r):
 x,y,u,v=map(int,r);mask=np.zeros((1684,1191),dtype=bool);mask[y:v+1,x:u+1]=True
 return {'road_pixels':int((mask&M['road']).sum()),'water_pixels':int((mask&M['water']).sum()),'outside_terrain_pixels':int((mask&~M['land']).sum()),'pass':not ((mask&M['road']).any() or (mask&M['water']).any() or (mask&~M['land']).any())}

def slot(id,quadrant,bbox,floors,assets,notes,anchor=None):
 return {'id':id,'quadrant':quadrant,'cluster_bbox':bbox,'land_floor_rectangles':floors,'floor_mask_audit':[stats(r) for r in floors],'anchor':anchor or [(bbox[0]+bbox[2])/2,bbox[3]],'assets':assets,'notes':notes}
slots=[
slot('NW_heritage_neighborhood','NW',[310,475,467,567],[[315,543,379,566],[410,526,464,548]],['L03_forum_vesta','L03_forum_temple'],'Existing two temples remain as northwestern neighborhood architecture. If needed uniformscale~.68–.78 within these smaller2pedestal slots; do not use the rejected floor[348,634,427,660], which crosses607road pixels.'),
slot('N_house','N',[544,538,635,615],[[555,590,625,615]],['new_meshy_roman_house'],'House actual height4–6world; footprint60–100px; top clear of CORE1 last line ending529.'),
slot('NE_market','NE',[813,646,901,728],[[824,699,898,728]],['new_meshy_roman_market','NB_worker_carrier(optional)'],'Market primary floor begins699, beyond aqueduct bottom672. Stall40–80px; a carrier is2.3–3.0world high,23–35px. Existing field patches may be moved or hidden.'),
slot('W_concrete_workspace','W',[54,845,207,945],[[68,902,206,945]],['C2_hot_mixing','D2_lime_kiln','material_stockpile'], '150px cluster comes from separate small maker/kiln/material stockpile. Maker whole model height~3.5world/fullbbox~80px; kiln4–5world. Keep prep on the west-bank land, entirely west of the core road; no common base crossing road or river.'),
slot('E_attached_construction','E',[772,839,838,924],[[798,891,827,923]],['NB_worker_builder','attached_scaffold','NB_build_stone_*','NB_build_form*'],'COL right facade construction. Human2.4world; scaffold beamwidth3–5world, platformlevels z3/z6. Body may project over facade; base is outside road. Real world attachment/penetration must be checked after placement.',anchor=[812,909]),
slot('SW_masonry_workyard','SW',[344,1135,468,1235],[[358,1201,464,1234]],['NB_vault_construction','NB_vault_timber_*','stone_brick_rubble','mortar_stockpile'],'Real incomplete arch, timber, stone/rubble and mortar pile replace giant cube/whiteball. Architectural height4–6world; human23–35px. Yard width110–124px comes from several natural parts, not a giant person.'),
slot('S_daily_life','S',[547,1133,612,1207],[[551,1182,608,1206]],['new_meshy_roman_lifeduo','small_jars_optional'],'Quiet central-south courtyard balances the active construction scenes; humans2.3–3world. Do not add a wide abstract platform.',anchor=[580,1194]),
slot('SE_repair_workyard','SE',[737,1135,839,1236],[[746,1208,835,1235]],['NB_vault_complete','masonry_wall_section_with_small_crack','NB_worker_pair(optional)'],'Natural finished vault and small wall section/repair seam replace floating triptych and microcubes. Width90–102px, architecture4–6world; paired humans each2.3–3world. Callout leader targets wall/stone material, not a freestanding diagram cube.'),
]
attachedWest={'id':'W_attached_scaffold','belongsTo':'NW_heritage_neighborhood / western construction','assembly_bbox':[360,836,415,923],'floor_rectangle':[370,895,396,922],'anchor':[383,909],'floor_mask_audit':stats([370,895,396,922]),'human_height_world':2.4,'scaffold_beamwidth_world':[3,5],'platform_levels_world':[3,6],'notes':'Second scaffold at left COL facade. Separate narrow base; do not connect it to west-bank preparation by a floor over the road/water. Source figure may be a standing carrier copy; final3D attachment is production QA.'}
retire=['NB_lime_clast_specimen']+[f'NB_lime_clast_specimen_LIME{i:02}' for i in range(6)]+['NB_detail_calcium_clast','NB_core4_sequence']+[f'NB_core4_sequence_GRAY{i:02}' for i in range(5)]+['NB_detail4_micro','NB_detail4_matrix','NB_detail4_crack','NB_detail4_crystal']
retireText=['749:108','749:177','749:178','749:180','749:181','749:184','749:186','749:187','749:188','749:189','749:204','749:200','749:201','749:202','749:203','755:78','755:79','749:198','749:199','749:197']
copyplan={
'CORE2':{'frame':[30,722,160,102],'preserveMainText':True,'nativeCaption':[54,952,153,14],'caption':'콘크리트 배합 마당'},
'CORE3':{'mainFrame':[330,1032,190,91],'sourceOrigin':[408.5,1028],'translation':[-78.5,4],'titleFont':21,'bodyFont':11.5,'bodyLines':2,'bodyText':'불량 혼합으로 여긴 흰 알갱이.\n연구가 찾은 건 ‘칼슘 공급원’.','detailFrame':[320,1250,170,57],'detailTitle':'벽·반죽 속 흰 석회','detailTitleFont':12,'detailBodyFont':9.5,'detailBodyLines':2,'detailBody':'벽·반죽에 남은 흰 알갱이.\n칼슘이 풍부해 물에 녹아 나온다.','leaderTarget':[398,1224],'replace3DAbstract':True},
'CORE4':{'mainFrame':[638.5,1032,178,91],'preserveMainText':True,'titleFont':21,'bodyFont':11.5,'bodyLines':2,'detailFrame':[673,1250,190,57],'detailTitle':'물에서 새 결정으로','detailTitleFont':12,'detailBodyFont':9.5,'detailBodyLines':2,'detailBody':'물에 녹은 칼슘이 틈으로 이동.\n새 결정이 자라 작은 금을 메운다.','leaderTarget':[790,1220],'limitationFrame':[650,1320,217,26],'limitationFont':9.5,'limitationText':'다른 유적·재현 시편에서 확인\n콜로세움에서 직접 입증 안 됨','replace3DAbstract':True},
}
# New informative frames clear all proposed village architecture rectangles;
# facade assemblies are judged by silhouette/glyph and 3D fit after production.
def ix(a,b):return min(a[2],b[2])>max(a[0],b[0]) and min(a[3],b[3])>max(a[1],b[1])
frames=[]
for k,c in copyplan.items():
 for key in ['mainFrame','detailFrame','limitationFrame']:
  if key in c:
   x,y,w,h=c[key];frames.append({'id':k+'.'+key,'bbox':[x,y,x+w,y+h]})
retained=[{'id':row[0],'text':row[1],'bbox':[row[2],row[3],row[2]+row[4],row[3]+row[5]]} for row in N['rows'] if row[0] not in retireText and row[0] not in ['749:110','749:158','749:159','749:160']]
textOverlaps=[]
for s in slots:
 for t in frames+retained:
  if ix(s['cluster_bbox'],t['bbox']):textOverlaps.append({'slot':s['id'],'frame':t['id'],'text':t.get('text'),'reason':'conservative projected rectangle indication; final real glyph/silhouette audit required'})
D={'status':'read_only_village_proposal_complete','source':I['source'],'source_sha256':source_sha,'canvas':[1191,1684],'direction':'CORE1NE→CORE2W→CORE3SW→CORE4S/SE→CORE5E counterclockwise narrative; village objects dispersed on land, no road procession','primaryNegativeConstraints':['all primary floor polygons on T_land','zero intersection with R_core_road/R_via_appia/R_via_ostiensis/B_pons1/B_pons2 projected union','zero L02_tiber projected intersection','source terrain/camera and existing COL center preserved','no abstract cubes/white balls/micro triptych as terrain objects'],'units':{'humanHeightWorld':[2.3,3.0],'humanNativeHeightPx':[23,35],'houseHeightWorld':[4,6],'houseFootprintPx':[60,100],'makerWholeHeightWorld':3.5,'makerWholeBBoxPxApprox':80,'COL_heightWorld_reference':15.29,'templeHeightWorld_reference':9},'slots':slots,'attachedWestScaffold':attachedWest,'retireAbstractObjects':retire,'sourceAlreadyHiddenAbstractObjects':['C3_arch_building','C4_crack_repair'],'nativeTextIdsToReplaceOrRelocate':retireText,'nativeCopyPlan':copyplan,'nativeRetainedRectangles':retained,'textRectangleIndications':textOverlaps,'floorMasksAllPass':all(a['pass'] for s in slots for a in s['floor_mask_audit']) and attachedWest['floor_mask_audit']['pass'],'evidence':{'inventory':str(B/'village-plan.inventory.json'),'roadWaterTerrainMasks':str(B/'village-plan.masks.npz'),'sourceProjectedGeometry':str(B/'counterclockwise-road-geometry.npz'),'currentCOLGeometry':str(B/'village-plan.hero.npz'),'nativeText':str(R/'out/figma-v14-road-native-validation.json')},'limitations':['Footprint rectangles reserve primary ground contact only; upper bodies/roofs may extend in projection. These are layout proposals, no transforms applied.','All source road/water/terrain meshes are unchanged since v9; actual polygon projections used, not handdrawn road shapes.','Lowest COL vertices are arena pit floor, so lowZ hull must not be used as exterior foundation footprint; final world BVH performs collision/attachment QA.','After placement sample actual model low vertices/base faces against road/water surfaces and check facade scaffold supports. Scale by actual world height before final projected fit; text-glyph/model-silhouette QA after native overlay export.','Village buildings are visual scene context, not an exact historical reconstruction of the Colosseum neighborhood.']}
(B/'village-plan.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
# Engineering diagram, polygon silhouettes and proposed land contacts only.
im=Image.new('RGB',(1191,1684),'#efe8d2');im.paste('#89c8d0',mask=Image.fromarray(M['water']).convert('L'));im.paste('#a49c83',mask=Image.fromarray(M['road']).convert('L'));dr=ImageDraw.Draw(im)
p=H['points'];loops=H['loops']
for start,count in zip(H['starts'],H['totals']):dr.polygon([tuple(v) for v in p[loops[start:start+count]]],fill='#ccb894')
for s in slots:
 dr.rectangle(s['cluster_bbox'],outline='#355967',width=2);dr.text((s['cluster_bbox'][0],s['cluster_bbox'][1]-13),s['id'],fill='#355967')
 for r in s['land_floor_rectangles']:dr.rectangle(r,fill='#8b9b7f')
dr.rectangle(attachedWest['assembly_bbox'],outline='#355967',width=2);dr.rectangle(attachedWest['floor_rectangle'],fill='#8b9b7f');dr.text((360,820),'west COL scaffold',fill='#355967')
for t in frames:dr.rectangle(t['bbox'],outline='#b97554',width=1);dr.text((t['bbox'][0],t['bbox'][1]),t['id'],fill='#b97554')
im.save(B/'village-plan.png')
lines=['# Village layout proposal','', 'Read-only plan for the latest user override. Source v11 SHA '+source_sha+'.','', 'Eight dominant neighborhood clusters, plus a second narrow scaffold base at the opposite COL facade. Every proposed primary floor rectangle has zero projected road/water intersection and is inside the terrain mask. The road is kept as circulation space.','', '| Cluster | Scene bbox | Land floor(s) |','|---|---|---|']
lines += [f"| {s['id']} | {s['cluster_bbox']} | {s['land_floor_rectangles']} |" for s in slots]
lines += ['', 'Physical scale is the first constraint: human2.3–3world≈23–35nativepx; house4–6world; maker wholeheight~3.5world/~80px. A150px prep group combines several small objects. Do not fit people to80px.','', 'Hide18 current abstract-object roots/children. Replace CORE3 clast/cube with SW mortar/rubble/actual masonry; replace CORE4 triptych/micro with SE cracked wall/finished vault. Main copy remains2body lines at11.5px. Detail callouts are2lines at9.5px in170/190px frames and point into real workyards. Retain the2line research limitation.','', 'CORE3 main frame moves from408.5,1028 to330,1032; shift its bakedbadge/rule by−78.5,+4. CORE2/4/5 main positions can remain. The main/details frames clear all new yard bboxes.','', 'West scaffold base[370,895,396,922], east base[798,891,827,923]. Human2.4world, beams3–5world wide, levels3/6world. Roof/head projection over facade is acceptable, but exact world contact/penetration needs final BVH QA.','', 'The NPZ COL low2percent hull corresponds to arena pit floor and is not a valid exterior foundation mask; it was not used as a hard placement condition. Final footprint/attachment checks must use full world geometry.','', f"Conservative text rectangle indications: {len(textOverlaps)}. See JSON for exact IDs; use glyph/silhouette review rather than failing on rectangles alone."]
(B/'village-plan.md').write_text('\n'.join(lines)+'\n')
print('VILLAGE_PLAN',json.dumps({'floors_all_pass':D['floorMasksAllPass'],'clusters':len(slots),'retire_objects':len(retire),'text_rectangle_indications':textOverlaps,'json_bytes':(B/'village-plan.json').stat().st_size},ensure_ascii=False))
