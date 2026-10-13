"""Build a local narrative text overlay; preserve baseline raster outside scoped text patches."""
import hashlib, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = Path('/Users/um-yunsang/Documents/로마콘크리트_3D')
OUT = ROOT / 'narrative_benchmark_20261007' / 'copy'
OUT.mkdir(parents=True, exist_ok=True)
BASE = ROOT / 'team' / 'text_overlay_rgba_2x.png'
FONT_R = Path('/Users/um-yunsang/Library/Fonts/NotoSansCJKkr-Regular.otf')
FONT_B = Path('/Users/um-yunsang/Library/Fonts/NotoSansCJKkr-Bold.otf')
SCALE = 2
W, H = 1191, 1684
base = Image.open(BASE).convert('RGBA')
assert base.size == (W*SCALE, H*SCALE)
overlay = base.copy()
original = json.loads((ROOT/'assets'/'figma_text_v6.json').read_text())
byid = {i['id']: dict(i) for i in original}

# Current canonical Figma/overlay transforms relative to the older JSON.
for i in byid.values():
    if i['id'].startswith('C3_'):
        i['y'] -= 8
    elif i['id'].startswith('C4_'):
        i['y'] -= 4
    elif i['id'].startswith('C5_'):
        i['x'] -= 8
    if i['id'].startswith('D4_'):
        i['y'] += 27.3

COPY = {
 'C1_t1': '현대와 로마,', 'C1_t2': '다른 결합재',
 'C1_b': '현대: 포틀랜드 시멘트\n로마: 석회·화산재 (대표 배합)',
 'C2_t1': '마른 채 섞고', 'C2_t2': '물로 뜨겁게',
 'C2_b': '생석회와 화산재를 먼저 섞고\n물을 부으면 발열하며 빨리 굳음',
 'C3_t1': '흰 알갱이가', 'C3_t2': '칼슘을 저장',
 'C3_b': '프리베르눔의 흰 석회 알갱이\n균열 충전에 쓰이는 칼슘 공급원',
 'C4_t1': '물과 칼슘이', 'C4_t2': '작은 금을 메움',
 'C4_b': '물이 칼슘을 옮기고\n새 결정이 작은 금을 메움',
 'C5_t1': '0.5mm 금,', 'C5_t2': '실험으로 확인',
 'C5_b': '현대 재현 실험에서\n수 주 내 누수 거의 멈춤',
 'D2_b': '생석회는 물을 만나면 열을 냄\n남은 석회 알갱이 = 칼슘 창고',
 'D3_h': '철근 없이 버틴 구조\n위는 가볍게, 아래는 두껍게',
 'D3_b': '아치·벽·기초가 무게를 나눠\n주로 누르는 힘을 받게 설계',
 'D4_h': '균열 원리 · 금이 메워지는 순서',
 'D4_b': '다른 유적·재현 시편에서 확인\n콜로세움에서 직접 입증 안 됨',
 'S1_d': '해양 콘크리트 안에서\n새로운 결정이 자람',
 'S2_d': '생석회를 섞어 둔 원료 더미',
 'S4_d': '재현 시편은 수 주 내 누수 감소,\n생석회 없는 시편은 계속 샘',
 'TL80_event': '콜로세움 개장',
 'C1_model_note': '철근은 당기는 힘을 보완',
 'S1_breakwater_note': '로마 방파제 · 개념 모형'
}
# Generous field widths remain inside the same current CORE module boxes.
byid['C1_t1']['w'] = 115
byid['C2_t1']['w'] = 120
byid['C2_t2']['w'] = 100
byid['C3_t2']['w'] = 100
byid['C3_b']['w'] = 150
byid['C4_t1']['w'] = 125
byid['C5_t2']['w'] = 150
byid['C5_b']['w'] = 150
byid['D4_h']['x'], byid['D4_h']['y'] = 650, 1237
byid['D4_b']['x'], byid['D4_b']['y'] = 650, 1257
question = '철근도 없는 로마 건축물이 어떻게 2천 년을 버텼을까?'
byid['Q'] = dict(id='Q',g='QUESTION',t=question,x=370,y=129.9,w=452,h=24,s=20,b=1,align='center')
byid['TL80_event'] = dict(id='TL80_event',g='TIMELINE',t='콜로세움 개장',x=283.4,y=1647.5,w=55,h=12,s=9.5,b=0)
byid['C1_model_note'] = dict(id='C1_model_note',g='SUPPORT',t=COPY['C1_model_note'],x=528,y=482,w=130,h=13,s=9.5,b=0)
byid['S1_breakwater_note'] = dict(id='S1_breakwater_note',g='SUPPORT',t=COPY['S1_breakwater_note'],x=385,y=1602,w=130,h=13,s=9.5,b=0)
for k,t in COPY.items():
    byid[k]['t'] = t

def pxrect(box):
    x0,y0,x1,y1 = box
    return (math.floor(x0*SCALE),math.floor(y0*SCALE),math.ceil(x1*SCALE),math.ceil(y1*SCALE))

# Clear whole CORE blocks, but restore original white number pixels (the discs/lines are Blender).
clear = [
 ('Q',[435,127,763,155]),
 ('C1',[527,385,670,476]),
 ('C2',[68.5,755,217,846]),
 ('C3',[407.5,1027,561,1118]),
 ('C4',[637.5,1031,818,1122]),
 ('C5',[981.5,815,1135,906]),
 ('D2_b',[35,1054,162,1084]),
 ('D3',[249,1344,394,1409]),
 ('D4_original_caption',[649,1306,805,1357]),
 ('D4_moved_caption',[649,1236,805,1287]),
 ('S1_d',[231,1568.5,340,1597]),
 ('S2_d',[717.5,1580,835,1596]),
 ('S4_d',[505.5,1469,641,1498]),
 ('TL80_event',[282.4,1646.5,340,1661]),
 ('C1_model_note_old',[687,495,819,511]),
 ('C1_model_note',[527,481,659,497]),
 ('S1_breakwater_note',[384,1601,516,1617]),
]
# Question expands horizontally within its existing architectural header band.
clear.append(('Q_new_extent',[369,127,824,155]))
mask = Image.new('1',base.size,0)
md = ImageDraw.Draw(mask)
for _,r in clear:
    pr=pxrect(r); overlay.paste((0,0,0,0),pr); md.rectangle(pr,fill=1)
for k in range(1,6):
    n=byid[f'C{k}_n']
    rect=pxrect([n['x']-2,n['y']-3,n['x']+n['w']+2,n['y']+n['h']+3])
    overlay.paste(base.crop(rect),rect[:2])

d = ImageDraw.Draw(overlay)
rendered=[]
new_boxes=[]
for k in list(COPY)+['Q']:
    n=byid[k]
    font=ImageFont.truetype(str(FONT_B if n['b'] else FONT_R),round(n['s']*SCALE))
    lines=n['t'].split('\n')
    # Figma export's ink starts slightly below node y. Preserve those ink offsets.
    if n['g']=='CORE':
        ink_offset = 3.5 if n['b'] else 2.5
        lh=25 if n['b'] else 14
    elif k=='D3_h':
        ink_offset=1.9; lh=15
    elif n['g'] in ('DETAIL','SUPPORT','TIMELINE'):
        ink_offset=2.1; lh=14 if n['g']=='DETAIL' else 13
    else:
        ink_offset=0; lh=24
    if k=='Q':
        ink_offset=0
    bxs=[]
    for row,line in enumerate(lines):
        line_width=font.getlength(line)/SCALE
        x=n['x'] + ((n['w']-line_width)/2 if n.get('align')=='center' else 0)
        y=n['y']+ink_offset+row*lh
        pos=(round(x*SCALE),round(y*SCALE))
        bbox=d.textbbox(pos,line,font=font,anchor='lt')
        d.text(pos,line,font=font,fill=(17,17,17,255),anchor='lt')
        bb=[v/SCALE for v in bbox]
        bxs.append(bb)
        new_boxes.append(dict(id=k,line=row,text=line,bbox=bb))
    rendered.append(dict(**n,lineHeight=lh,inkOffset=ink_offset,
                         measuredWidth=max(font.getlength(s)/SCALE for s in lines),inkBboxes=bxs))
    
# Preserve the entire number-digit patches verbatim again after drawing.
for k in range(1,6):
    n=byid[f'C{k}_n']; rect=pxrect([n['x']-2,n['y']-3,n['x']+n['w']+2,n['y']+n['h']+3])
    overlay.paste(base.crop(rect),rect[:2])

overflows=[]
for n in rendered:
    if n['measuredWidth']>n['w']+0.1:
        overflows.append(dict(id=n['id'],width=n['measuredWidth'],allowed=n['w']))
    for bb in n['inkBboxes']:
        if bb[0]<0 or bb[1]<0 or bb[2]>W or bb[3]>H:
            overflows.append(dict(id=n['id'],bbox=bb,reason='poster_bounds'))
def overlap(a,b):
    return max(a[0],b[0])<min(a[2],b[2]) and max(a[1],b[1])<min(a[3],b[3])
new_text_collisions=[]
for a_index,a in enumerate(new_boxes):
    for b in new_boxes[a_index+1:]:
        if overlap(a['bbox'],b['bbox']):
            new_text_collisions.append([a['id'],a['line'],b['id'],b['line']])
model_anchors={
 'modern_building_C1':[695.24,384.01,816.79,478.01],
 'new_clue_C3':[450.82,1127.99,555.23,1245.99],
 'new_breakwater':[398,1510,500,1600]
}
model_collisions=[]
for n in new_boxes:
    for name,bb in model_anchors.items():
        if overlap(n['bbox'],bb):
            model_collisions.append(dict(text=n['id'],line=n['line'],model=name,bbox=n['bbox']))
current=json.loads((ROOT/'loop'/'figma_texts.json').read_text())
changed_current={'634:720','634:722','CORE1','CORE2','CORE3','CORE4','CORE5','D2T','D3T','D4T','S1','S2','S4','TL'}
retained_collisions=[]
for n in new_boxes:
    for old in current:
        if old['id'] in changed_current: continue
        if overlap(n['bbox'],old['b']):
            retained_collisions.append(dict(text=n['id'],line=n['line'],retained=old['id']))
arr_old=np.array(base); arr_new=np.array(overlay); maskarr=np.array(mask)
outside_changed=int(np.any(arr_old!=arr_new,axis=2)[~maskarr].sum())
actual_model_collisions=[]
integration_reports=list((OUT.parent/'out').glob('integration-report-v[0-9]*.json'))
integration_report=max(integration_reports,key=lambda p:int(p.stem.rsplit('-v',1)[1])) if integration_reports else OUT.parent/'out'/'integration-report-v1.json'
if integration_report.exists():
    for asset in json.loads(integration_report.read_text()).get('assets',[]):
        for n in new_boxes:
            if overlap(n['bbox'],asset['projected_bbox']):
                actual_model_collisions.append(dict(text=n['id'],line=n['line'],model=asset['id'],bbox=n['bbox']))
# All non-text pixels of baseline render are untouched because the map is never opened/written here.
audit=dict(size=list(overlay.size),mode=overlay.mode,fonts=[str(FONT_B),str(FONT_R)],
           overflows=overflows,newTextCollisions=new_text_collisions,
           retainedTextCollisions=retained_collisions,provisionalModelCollisions=model_collisions,
           actualIntegratedModelCollisions=actual_model_collisions,
           integrationReportChecked=str(integration_report) if integration_report.exists() else None,
           provisionalModelAnchors=model_anchors,
           changedPixelsOutsidePatchMask=outside_changed,
           headerQuestionInkBbox=new_boxes[-1]['bbox'],
           scope='local copy and RGBA overlay only; no remote Figma or Blender mutations',
           sourceOverlaySha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),
           sourceCopySha256=hashlib.sha256((ROOT/'assets'/'figma_text_v6.json').read_bytes()).hexdigest())
manifest=dict(question=question,canvasPt=[W,H],pixelSize=list(overlay.size),
              baselineOverlay=str(BASE),patchNodes=rendered,clearRegions=clear,
              unchanged='All baseline RGBA pixels outside scoped patch regions; all SUPPORT/place/timeline positions. S1 marine crystal wording, S2 quicklime terminology, S4 experiment duration, and 80 CE opening receive the listed tiny guards. D4 headline and source guard move below the single larger CORE4 sequence by explicit request.',
              addedCaptions='C1 explains the steel bar role at the new building; the added seaside Roman breakwater is labeled as a concept model.',
              sourceScope='Core 5 is a modern recreated specimen experiment; C3 Privernum specimen clue; no claim of direct Colosseum self-healing.')
(OUT/'narrative_copy.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(OUT/'figma_text_narrative.json').write_text(json.dumps(list(byid.values()),ensure_ascii=False,indent=2)+'\n')
(OUT/'overlay_validation.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
# Keep accepted aggregated S1 and timeline zones, unioning the new ink safely.
removed_groups=changed_current-{'S1','TL'}
combined_zones=[dict(x) for x in current if x['id'] not in removed_groups]
for node_id,group_id in [('S1_d','S1'),('TL80_event','TL')]:
    zone=next(x for x in combined_zones if x['id']==group_id)
    inks=next(x['inkBboxes'] for x in rendered if x['id']==node_id)
    zone['b']=[min(zone['b'][0],*(b[0] for b in inks)),min(zone['b'][1],*(b[1] for b in inks)),
               max(zone['b'][2],*(b[2] for b in inks)),max(zone['b'][3],*(b[3] for b in inks))]
for node in rendered:
    if node['id'] in ('S1_d','TL80_event'): continue
    for row,bb in enumerate(node['inkBboxes']):
        combined_zones.append(dict(id=f"{node['id']}_{row}",c=node['t'],b=bb,kind=node['g'].lower()))
(OUT/'text_zones_narrative.json').write_text(json.dumps(combined_zones,ensure_ascii=False,indent=2)+'\n')
overlay.save(OUT/'text_overlay_narrative_rgba_2x.png')
overlay.resize((W,H),Image.Resampling.LANCZOS).save(OUT/'text_overlay_narrative_rgba_1x.png')
preview=Image.new('RGBA',overlay.size,(245,245,245,255)); preview.alpha_composite(overlay)
preview.convert('RGB').resize((W,H),Image.Resampling.LANCZOS).save(OUT/'overlay_preview_on_white_1x.png')
print(json.dumps(audit,ensure_ascii=False,indent=2))
print('overlay',OUT/'text_overlay_narrative_rgba_2x.png')
assert not overflows, overflows
assert not new_text_collisions,new_text_collisions
assert not retained_collisions,retained_collisions
assert not model_collisions,model_collisions
assert not actual_model_collisions,actual_model_collisions
assert outside_changed==0
