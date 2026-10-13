"""Finalize documents from actual native v11 export and saved v7 verification."""
import hashlib, json, shutil
from datetime import datetime
from pathlib import Path
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PLANNING=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007')
def read(p): return json.loads((ROOT/p).read_text())
def write(p,d): (ROOT/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
v=read('out/figma-v11-color-final-validation.json')
ink=read('out/figma-v11-text-ink-mutation.json')
p=read('copy/color_system_v11.json')
assert v['problems']==[] and v['invalidAliases']==[]
assert v['textCount']==v['sourceTextCount']==v['boundTextCount']==95
assert v['variableCount']==76 and v['posterSize']==[1191,1684]
assert v['backgroundHash']==read('out/figma-v11-color-upload.json')['imageHash']
assert v['sourceBackgroundHash']=='941c6dfe8fff1e17567f2413cb93c420b93e8517'
p['overlayInkTokens']={k:a['hex'] for k,a in ink['variables'].items()}
p['styleGuide']['height']=v['guideSize'][1]
p['outputFrameId']=v['frameId'];p['outputBackgroundId']=v['backgroundId'];p['outputGuideId']=v['guideId']
write('copy/color_system_v11.json',p)
shutil.copy2(ROOT/'copy/color_system_v11.json',PLANNING/'color-design/approved-color-system.json')
tokens={**p['tokens'],**p['overlayInkTokens']}
foundation=read('out/figma-v11-color-foundation.json')
foundation['collectionId']=foundation['createdCollectionId']
semantic={**foundation['semanticIds'],**{k:a['semanticId'] for k,a in ink['variables'].items()}}
primitive={**foundation['primitiveIds'],**{k:a['rawId'] for k,a in ink['variables'].items()}}
design=ROOT/'design';design.mkdir(exist_ok=True)
write('design/design-tokens.json',{'name':p['name'],'colors':{k:{'value':h,'space':'sRGB','primitiveVariableId':primitive[k],'semanticVariableId':semantic[k],'scope':'TEXT_FILL' if k.startswith('type_') else 'poster'} for k,h in tokens.items()},'typography':{'display':p['title'],'core':{'family':'Noto Sans KR','style':'Bold','fontSize':21,'lineHeight':26},'body':{'family':'Noto Sans KR','style':'Regular','fontSize':11.5,'lineHeight':15.5},'caption':{'family':'Noto Sans KR','fontSize':'existing 9–12px','layout':'current bounds preserved'}},'figma':{'collectionId':foundation['collectionId'],'modeId':foundation['modeId'],'rawCount':38,'semanticCount':38,'textStyleIds':foundation['styleIds']}})
(design/'design-tokens.css').write_text(':root {\n'+''.join('  --rc-'+k.replace('_','-')+': '+h+';\n' for k,h in tokens.items())+'  --rc-font-display: "Noto Serif KR";\n  --rc-font-body: "Noto Sans KR";\n}\n')
previous=read('copy/narrative_v10.json');source_map=read('out/figma-v11-color-mutation.json')['idMap'];reverse={b:a for a,b in source_map.items()};old={t['id']:t for t in previous['texts']}
texts=[]
for id,t,x,y,w,h,fs,color,var in v['texts']:
    record={**old[reverse[id]],'sourceId':reverse[id],'id':id,'text':t,'x':x,'y':y,'width':w,'height':h,'fontSize':fs,'color':color,'colorVariableId':var}
    if id=='728:245':record.update(fontFamily='Noto Serif KR',fontStyle='Bold',lineHeight={'unit':'PIXELS','value':80},letterSpacing={'unit':'PERCENT','value':-1})
    texts.append(record)
write('copy/narrative_v11.json',{'frameId':v['frameId'],'question':previous['question'],'copy_source':'live v10 95 texts; all copy and bounds preserved','titleFont':'Noto Serif KR Bold 70/80','bodyFont':'Noto Sans KR','texts':texts})
# Rendered background contrast is a diagnostic of sampled rectangles, not a glyph certification.
base=ROOT/'out/figma_import/map_v7_color_without_text_2x_optimized.png'
original=Image.open(ROOT/'out/figma_import/map_v7_color_without_text_2x.png').convert('RGB')
im=Image.open(base).convert('RGB');assert im.size==(2382,3368) and im.tobytes()==original.tobytes()
a=np.array(im)/255;lin=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4);lum=lin@np.array([.2126,.7152,.0722]);rows=[]
for id,t,x,y,w,h,fs,color,var in v['texts']:
    rgb=np.array([int(color[i:i+2],16)/255 for i in (1,3,5)]);rgb=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);l=rgb@np.array([.2126,.7152,.0722]);bg=lum[max(0,round(y*2)):round((y+h)*2),max(0,round(x*2)):round((x+w)*2)]
    c=(np.maximum(bg,l)+.05)/(np.minimum(bg,l)+.05)
    rows.append({'id':id,'text':t,'color':color,'p10':round(float(np.quantile(c,.1)),2),'median':round(float(np.median(c)),2),'min':round(float(c.min()),2)})
write('out/contrast-v11-rendered-regions-final.json',{'method':'sRGB relative luminance of actual no-text base TEXT rectangles. Region p10/median reflect light/shadow variation; rotated labels, actual glyph masks and antialiasing excluded. Not a formal WCAG certification or reader study.','rows':rows})
accent_ids=set(ink['bindingChanges'])
print('FINAL_ACCENT_CONTRAST',json.dumps([r for r in rows if r['id'] in accent_ids],ensure_ascii=False))
scene_review=json.loads((PLANNING/'color-design/v7-saved-validation.json').read_text())
assert scene_review['pass']
shutil.copy2(PLANNING/'color-design/v11-final-color-qa.md',ROOT/'out/v11-final-color-qa.md')
for src,dst in [('v7-saved-validation.json','v7-color-saved-validation.json'),('v7-saved-validation.md','v7-color-saved-validation.md'),('palette-review.md','v11-palette-review.md'),('typography-review.md','v11-typography-review.md')]:shutil.copy2(PLANNING/'color-design'/src,ROOT/'out'/dst)
assert sha(ROOT/'out/roman_concrete_narrative_v6.blend')=='d71533920ebd305c41e92db718b527647c8b9655aee87cbb3b656c3afde257cd'
assert sha(ROOT/'out/roman_concrete_narrative_v7.blend')=='2c22462b8cd9f169f6eb12822befa415c9c42a256eca86ae4e5ead5820d1b4b8'
assert sha(ROOT.parent/'roman_concrete_map.blend')=='28d49f93c6edaf89bcbcc54ff1dfb94b0089cc2a0e43496032d46717c1a14cb3'
for file,size in [('figma_poster_v11_color_2x.png',(2382,3368)),('figma_poster_v11_color_1x.png',(1191,1684)),('figma_color_typography_guide_v11_2x.png',(1480,924))]:assert Image.open(ROOT/'out'/file).size==size
artifacts=['out/roman_concrete_narrative_v7.blend','out/figma_poster_v11_color_2x.png','out/figma_poster_v11_color_1x.png','out/figma_color_typography_guide_v11_2x.png','out/figma_import/map_v7_color_without_text_2x_optimized.png','out/poster-color-v7.json','out/figma-v11-color-final-validation.json','out/figma-v11-color-mutation.json','out/figma-v11-text-ink-mutation.json','out/figma-v11-color-foundation.json','out/v7-color-saved-validation.json','copy/narrative_v11.json','copy/color_system_v11.json','design/design-tokens.json','design/design-tokens.css']
receipt={'createdAtLocal':datetime.now().isoformat(timespec='seconds'),'figmaUrl':'https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=728-241','guideUrl':'https://www.figma.com/design/jQPriO85F6wtPy1NPo752p/?node-id=728-360','frameId':v['frameId'],'pageId':'19:4','backgroundId':v['backgroundId'],'backgroundHash':v['backgroundHash'],'editableTexts':95,'copyAndTextBoundsPreserved':True,'textSemanticBindings':95,'colorVariables':76,'textStyles':4,'visibleColoredObjects':227,'geometryTransformsCameraVisibilityPreservedObjects':317,'sourceV10BackgroundPreserved':True,'sourceV6AndCanonicalBlendBytesPreserved':True,'nativeExportSize':[2382,3368],'noTextUploadLosslessPixelsEqual':True,'originalRenderSettingsChanged':['view_settings.exposure: +0.35 to +0.7','shading.background_type: THEME to WORLD','World.color and World Background Color: cream palette'],'newMeshyJobs':0,'verificationScope':'Actual native export visual QA and live color/font/copy/bounds checks; fresh saved geometry/scene verification. No reader comprehension study.','artifacts':[{'path':f,'bytes':(ROOT/f).stat().st_size,'sha256':sha(ROOT/f)} for f in artifacts]}
write('out/delivery-receipt-v11.json',receipt)
print('V11_DOCUMENTS_COMPLETE',json.dumps({'artifacts':len(artifacts),'editable_texts':95,'variables':76,'receipt':'out/delivery-receipt-v11.json'}))
