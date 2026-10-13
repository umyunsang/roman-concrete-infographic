const page=await figma.getNodeByIdAsync('19:4');await figma.setCurrentPageAsync(page);
const source=await figma.getNodeByIdAsync('728:241');
const dfs=n=>[n,...('children'in n?n.children.flatMap(dfs):[])];
const old=dfs(source),texts=old.filter(n=>n.type==='TEXT');
if(texts.length!==BASE.textCount)throw new Error('Live text count changed since baseline');
if(page.children.some(n=>n.name==='v12 · 부위별 재질 배색 — 철근·제작·유적'))throw new Error('v12 exists; inspect instead of duplicate');
const snapshot=()=>JSON.stringify(dfs(source).map(n=>({id:n.id,x:n.x,y:n.y,w:n.width,h:n.height,...(n.type==='TEXT'?{t:n.characters}:{}),...('fills'in n?{fills:n.fills}:{})})));
const before=snapshot();
const fonts=new Map();for(const t of texts)for(const s of t.getStyledTextSegments(['fontName']))fonts.set(JSON.stringify(s.fontName),s.fontName);
fonts.set('guide',{family:'Noto Sans KR',style:'Regular'});fonts.set('guideBold',{family:'Noto Sans KR',style:'Bold'});
await Promise.all([...fonts.values()].map(f=>figma.loadFontAsync(f)));
const f=source.clone();page.appendChild(f);f.name='v12 · 부위별 재질 배색 — 철근·제작·유적';f.x=source.x-1411;f.y=source.y;
f.exportSettings=[{format:'PNG',constraint:{type:'SCALE',value:2}}];
const copied=dfs(f);if(copied.length!==old.length)throw new Error('Clone topology mismatch');
const map=Object.fromEntries(old.map((n,i)=>[n.id,copied[i].id]));
const bg=await figma.getNodeByIdAsync(map['728:242']);bg.name='Blender v8 · 부위별 MATERIAL 배색 · 글 없는 지도';
const errors=[];
for(const oldText of texts){const n=await figma.getNodeByIdAsync(map[oldText.id]);if(n.characters!==oldText.characters||Math.abs(n.absoluteTransform[0][2]-f.x-(oldText.absoluteTransform[0][2]-source.x))>.01||Math.abs(n.absoluteTransform[1][2]-f.y-(oldText.absoluteTransform[1][2]-source.y))>.01||n.width!==oldText.width||n.height!==oldText.height)errors.push(n.id);}
if(errors.length||snapshot()!==before)throw new Error('Source/copy/layout changed '+JSON.stringify(errors));
// Material palette is a distinct production foundation; no poster text is added.
const col=figma.variables.createVariableCollection('로마 콘크리트 / 부위별 재질 v12');col.renameMode(col.defaultModeId,'따뜻한 지도 · 재료 구분');
const color=h=>({r:parseInt(h.slice(1,3),16)/255,g:parseInt(h.slice(3,5),16)/255,b:parseInt(h.slice(5,7),16)/255});
const vars={},createdVariableIds=[];
for(const [key,h]of Object.entries(PARTS)){
 const raw=figma.variables.createVariable('primitive/'+key,col,'COLOR');raw.scopes=[];raw.setValueForMode(col.defaultModeId,color(h));
 const v=figma.variables.createVariable('material/'+key,col,'COLOR');v.scopes=['SHAPE_FILL'];v.setValueForMode(col.defaultModeId,figma.variables.createVariableAlias(raw));v.description='Blender RC.v12.'+key+' · sRGB '+h;
 vars[key]=v;createdVariableIds.push(raw.id,v.id);
}
const guide=figma.createAutoLayout('VERTICAL');page.appendChild(guide);guide.name='부위별 배색 v12 · Blender 재질 가이드';guide.x=f.x;guide.y=f.y+f.height+100;guide.paddingLeft=24;guide.paddingRight=24;guide.paddingTop=24;guide.paddingBottom=24;guide.itemSpacing=16;guide.resize(800,400);guide.counterAxisSizingMode='FIXED';guide.primaryAxisSizingMode='AUTO';guide.fills=[{type:'SOLID',color:color('#F3E8D4')}];
const extra=[guide.id];
const label=(parent,text,size=12,bold=false,width=752)=>{const n=figma.createText();parent.appendChild(n);extra.push(n.id);n.fontName={family:'Noto Sans KR',style:bold?'Bold':'Regular'};n.fontSize=size;n.lineHeight={unit:'PIXELS',value:size+5};n.characters=text;n.textAutoResize='HEIGHT';n.resize(width,size+5);n.fills=[{type:'SOLID',color:color('#3E3A31')}];n.name=text;return n;};
label(guide,'로마 콘크리트 · 부위별 재질 배색',24,true);
label(guide,'콘크리트와 철근 / 피부·의복·도구·반죽 / 잎과 줄기 / 유적의 벽·내부·지면',12);
const chips=[['concrete','콘크리트'],['steel','노출 철근'],['labstone','실험실 벽체'],['roof','지붕·현대 장치'],['skin','피부'],['linen','밝은 의복'],['cloth','적갈색 의복'],['toolwood','목제 도구'],['toolmetal','금속 도구'],['basin','배합 용기'],['mixture','반죽·모재'],['raw_lime','석회·결정'],['colosseum_wall','콜로세움 외벽'],['colosseum_interior','내부 좌석·벽'],['arena_earth','아레나 지면'],['roman_plinth','석재 기단'],['roman_stone','유적 석재'],['roman_roof','유적 지붕'],['foliage','나무 잎'],['trunk','줄기']];
for(let r=0;r<Math.ceil(chips.length/4);r++){
 const row=figma.createAutoLayout('HORIZONTAL');guide.appendChild(row);extra.push(row.id);row.fills=[];row.itemSpacing=16;row.name='부위 재질 '+(r+1);
 for(const [key,name]of chips.slice(r*4,r*4+4)){
  const chip=figma.createAutoLayout('VERTICAL');row.appendChild(chip);extra.push(chip.id);chip.fills=[];chip.itemSpacing=5;chip.name=name;
  const rect=figma.createRectangle();chip.appendChild(rect);extra.push(rect.id);rect.resize(176,28);rect.name='RC.v12.'+key;rect.fills=[figma.variables.setBoundVariableForPaint({type:'SOLID',color:color(PARTS[key])},'color',vars[key])];
  label(chip,name+' '+PARTS[key],10,false,176);
 }
}
label(guide,'Workbench MATERIAL · 같은 메시 안의 면별 재질 / 기존 맵 형상·배치와 현재 문구 유지',11);
guide.exportSettings=[{format:'PNG',constraint:{type:'SCALE',value:2}}];
figma.currentPage.selection=[f];figma.viewport.scrollAndZoomIntoView([f]);
return {frameId:f.id,backgroundId:bg.id,guideId:guide.id,pageId:page.id,createdNodeIds:copied.map(n=>n.id).concat(extra),modifiedNodeIds:[f.id,bg.id],createdCollectionId:col.id,createdVariableIds,materialSemanticIds:Object.fromEntries(Object.entries(vars).map(([k,v])=>[k,v.id])),idMap:map,nativeTextCount:texts.length,copyAndBoundsPreserved:true,sourceV11Unchanged:true,size:[f.width,f.height],guideSize:[guide.width,guide.height]};
