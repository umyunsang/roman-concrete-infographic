const page=await figma.getNodeByIdAsync('19:4');await figma.setCurrentPageAsync(page);
const source=await figma.getNodeByIdAsync(P.sourceFrameId);
if(page.children.some(n=>n.name===P.name))throw new Error('v11 already exists; inspect before retry');
const dfs=n=>[n,...(('children'in n)?n.children.flatMap(dfs):[])];
const baseline=dfs(source),oldTexts=baseline.filter(n=>n.type==='TEXT');
if(oldTexts.length!==95)throw new Error('Live95text baseline changed');
const snap=()=>JSON.stringify(dfs(source).map(n=>({id:n.id,x:n.x,y:n.y,w:n.width,h:n.height,...(n.type==='TEXT'?{t:n.characters}:{}),...('fills'in n?{fills:n.fills}:{})})));
const sourceSnapshot=snap();
const fonts=new Map();for(const t of oldTexts)for(const s of t.getStyledTextSegments(['fontName']))fonts.set(JSON.stringify(s.fontName),s.fontName);
for(const f of [{family:'Noto Serif KR',style:'Bold'},{family:'Noto Sans KR',style:'Bold'},{family:'Noto Sans KR',style:'Regular'},{family:'Noto Sans KR',style:'Medium'}])fonts.set(JSON.stringify(f),f);
await Promise.all([...fonts.values()].map(f=>figma.loadFontAsync(f)));
const vars={};for(const[key,id]of Object.entries(S.semanticIds))vars[key]=await figma.variables.getVariableByIdAsync(id);
const color=hex=>({r:parseInt(hex.slice(1,3),16)/255,g:parseInt(hex.slice(3,5),16)/255,b:parseInt(hex.slice(5,7),16)/255});
const paint=key=>figma.variables.setBoundVariableForPaint({type:'SOLID',color:color(P.tokens[key])},'color',vars[key]);
const f=source.clone();page.appendChild(f);f.name=P.name;f.x=P.poster.x;f.y=P.poster.y;f.fills=[paint('background')];
f.exportSettings=[{format:'PNG',constraint:{type:'SCALE',value:2}}];
const copied=dfs(f);if(copied.length!==baseline.length)throw new Error('Unexpected clone topology');
const map=new Map(baseline.map((n,i)=>[n.id,copied[i]]));const node=id=>{const n=map.get(id);if(!n)throw new Error('Missing source '+id);return n;};
const modified=new Set([f.id]),bindings={};
const bind=(n,key)=>{n.fills=[paint(key)];modified.add(n.id);bindings[n.id]=key;};
for(const t of copied.filter(n=>n.type==='TEXT')){
 const y=t.absoluteTransform[1][2]-f.y;
 bind(t,y>=1520?'type_body':'type_secondary_on_light_ground');
}
for(const id of P.numeralIds)bind(node(id),'badge_numeral');
for(const [i,ids]of P.coreTitles.entries()){
 for(const id of ids)await node(id).setTextStyleIdAsync(S.styleIds.Core);
 bind(node(ids[0]),'type_heading');bind(node(ids[1]),['badge_1_5','badge_2','badge_3','badge_4','badge_1_5'][i]);
}
for(const id of P.coreBodyIds){await node(id).setTextStyleIdAsync(S.styleIds.Body);bind(node(id),'type_body');}
for(const id of ['718:80','718:81','718:86'])bind(node(id),'type_heading');
for(const id of ['718:83','718:84','718:85'])bind(node(id),'type_body');
for(const id of ['718:194','718:187','718:195','718:123','718:122'])bind(node(id),'type_body');
bind(node('718:177'),'badge_4');bind(node('718:180'),'badge_2');bind(node('718:183'),'type_heading');
bind(node('718:186'),'badge_4');bind(node('718:120'),'badge_1_5');
bind(node('718:189'),'badge_4');bind(node('718:190'),'badge_3');bind(node('718:191'),'badge_3');
for(const id of ['718:178','718:181','718:184'])bind(node(id),'type_body');
const title=node(P.title.sourceId);await title.setTextStyleIdAsync(S.styleIds.Display);
title.textAutoResize='WIDTH_AND_HEIGHT';const naturalTitleWidth=title.width;
if(naturalTitleWidth>P.title.width)throw new Error('Serif title exceeds fixed width '+naturalTitleWidth);
title.textAutoResize='HEIGHT';title.resize(P.title.width,P.title.lineHeight);bind(title,'type_heading');
// CENTER auto-resize moved x while measuring the serif's natural width. Restore its fixed poster anchor.
title.x=baseline.find(n=>n.id===P.title.sourceId).x;title.y=baseline.find(n=>n.id===P.title.sourceId).y;
const bg=node(P.backgroundSourceId);bg.name='Blender v7 · 석회·트래버틴·청록 배색 · 글 없는 지도';modified.add(bg.id);

// Editable palette board outside the poster, with no extra poster text.
const extra=[];const register=n=>{extra.push(n.id);return n;};
const guide=register(figma.createAutoLayout('VERTICAL'));
page.appendChild(guide);guide.name='로마 콘크리트 · 배색과 타이포 가이드';guide.x=P.styleGuide.x;guide.y=P.styleGuide.y;
guide.fills=[paint('background')];guide.paddingLeft=28;guide.paddingRight=28;guide.paddingTop=28;guide.paddingBottom=28;guide.itemSpacing=16;guide.clipsContent=false;
guide.resize(P.styleGuide.width,490);guide.primaryAxisSizingMode='AUTO';guide.counterAxisSizingMode='FIXED';
const gt=(parent,t,size,lh,font='Regular',key='type_body',width=684)=>{
 const n=register(figma.createText());parent.appendChild(n);n.name=t.replaceAll('\n',' · ');n.fontName={family:'Noto Sans KR',style:font};n.fontSize=size;n.lineHeight={unit:'PIXELS',value:lh};n.characters=t;n.textAutoResize='HEIGHT';n.resize(width,lh);n.fills=[paint(key)];return n;};
const gtTitle=gt(guide,'로마 콘크리트 · 색과 글의 기준',25,34,'Bold','type_heading');
gt(guide,'따뜻한 석재 / 적갈색 발열 / 청록의 물과 현대 실험',13,18,'Medium');
const chips=[['background','크림 바탕'],['colosseum','중앙 콜로세움'],['roman_support_stone','유적과 보조 장면'],['modern_concrete','현대 골조'],['hot_mixing','배합과 발열'],['lime_specimen_matrix','시편의 모재'],['lime_calcium_crystal','석회·칼슘·충전 결정'],['water_process','물의 작용'],['sea_river','바다와 강'],['foliage','수목'],['type_heading','주요 제목'],['type_body','본문']];
for(let r=0;r<4;r++){
 const row=register(figma.createAutoLayout('HORIZONTAL'));guide.appendChild(row);row.name='배색 '+(r+1);row.fills=[];row.itemSpacing=16;
 for(const [key,label]of chips.slice(r*3,r*3+3)){
  const chip=register(figma.createAutoLayout('VERTICAL'));row.appendChild(chip);chip.name=label;chip.fills=[];chip.itemSpacing=5;
  const swatch=register(figma.createRectangle());chip.appendChild(swatch);swatch.name=label+' · '+P.tokens[key];swatch.resize(212,32);swatch.fills=[paint(key)];
  gt(chip,label+'  '+P.tokens[key],11,15,'Medium','type_body',212);
 }
}
gt(guide,'제목  Noto Serif KR Bold 70 / 80\n코어·본문  Noto Sans KR Bold / Regular',13,19,'Regular');
guide.exportSettings=[{format:'PNG',constraint:{type:'SCALE',value:2}}];

const texts=dfs(f).filter(n=>n.type==='TEXT');
const copyPreserved=oldTexts.every(t=>node(t.id).characters===t.characters)&&texts.length===95;
const geometryPreserved=oldTexts.every(t=>{const c=node(t.id);return Math.abs(c.absoluteTransform[0][2]-f.x-(t.absoluteTransform[0][2]-source.x))<.01&&Math.abs(c.absoluteTransform[1][2]-f.y-(t.absoluteTransform[1][2]-source.y))<.01&&Math.abs(c.width-t.width)<.01&&Math.abs(c.height-t.height)<.01;});
if(!copyPreserved||!geometryPreserved||snap()!==sourceSnapshot){
 const diffs=oldTexts.map(t=>{const c=node(t.id);return {id:t.id,old:[t.absoluteTransform[0][2]-source.x,t.absoluteTransform[1][2]-source.y,t.width,t.height],new:[c.absoluteTransform[0][2]-f.x,c.absoluteTransform[1][2]-f.y,c.width,c.height]};}).filter(d=>d.old.some((v,i)=>Math.abs(v-d.new[i])>.01));
 throw new Error('Layout diagnostic '+JSON.stringify({copyPreserved,sourceUnchanged:snap()===sourceSnapshot,diffs}));
}
figma.currentPage.selection=[f];figma.viewport.scrollAndZoomIntoView([f]);
return {frameId:f.id,backgroundId:bg.id,guideId:guide.id,createdNodeIds:copied.map(n=>n.id).concat(extra),modifiedNodeIds:[...modified],
 current95CopyPreserved:copyPreserved,allTextBoundsPreserved:geometryPreserved,sourceV10Unchanged:true,naturalSerifTitleWidth:naturalTitleWidth,
 title:{id:title.id,w:title.width,h:title.height,font:title.fontName,fs:title.fontSize},
 guideBounds:{x:guide.x,y:guide.y,w:guide.width,h:guide.height},bindingCount:Object.keys(bindings).length,bindings,
 idMap:Object.fromEntries([...map].filter(([id,n])=>n.type==='TEXT'||id===P.backgroundSourceId).map(([id,n])=>[id,n.id]))};
