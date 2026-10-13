const page=await figma.getNodeByIdAsync('19:4');await figma.setCurrentPageAsync(page);
const frame=await figma.getNodeByIdAsync('743:78');
await Promise.all([{family:'Noto Sans KR',style:'Regular'},{family:'Noto Sans KR',style:'Bold'}].map(f=>figma.loadFontAsync(f)));
const color=h=>({r:parseInt(h.slice(1,3),16)/255,g:parseInt(h.slice(3,5),16)/255,b:parseInt(h.slice(5,7),16)/255});
const collection=figma.variables.createVariableCollection('로마 콘크리트 / 바다·화산 재질 v13');collection.renameMode(collection.defaultModeId,'저채도 석재·흙색');
const variables={},createdVariableIds=[];
for(const [role,info]of Object.entries(MATERIALS)){
 const raw=figma.variables.createVariable('primitive/'+role,collection,'COLOR');raw.scopes=[];raw.setValueForMode(collection.defaultModeId,color(info.hex));
 const alias=figma.variables.createVariable('material/'+role,collection,'COLOR');alias.scopes=['SHAPE_FILL'];alias.setValueForMode(collection.defaultModeId,figma.variables.createVariableAlias(raw));alias.description=info.name+' · sRGB '+info.hex;variables[role]=alias;createdVariableIds.push(raw.id,alias.id);
}
const guide=figma.createAutoLayout('VERTICAL');page.appendChild(guide);guide.name='v13 · 바다·화산 부위별 재질 가이드';guide.x=frame.x;guide.y=frame.y+frame.height+100;guide.resize(800,400);guide.counterAxisSizingMode='FIXED';guide.primaryAxisSizingMode='AUTO';guide.paddingLeft=24;guide.paddingRight=24;guide.paddingTop=24;guide.paddingBottom=24;guide.itemSpacing=16;guide.fills=[{type:'SOLID',color:color('#F3E8D4')}];
const created=[guide.id];
const label=(parent,text,size=12,bold=false,w=752)=>{const n=figma.createText();parent.appendChild(n);created.push(n.id);n.fontName={family:'Noto Sans KR',style:bold?'Bold':'Regular'};n.fontSize=size;n.lineHeight={unit:'PIXELS',value:size+5};n.characters=text;n.textAutoResize='HEIGHT';n.resize(w,size+5);n.fills=[{type:'SOLID',color:color('#3E3A31')}];n.name=text;return n;};
label(guide,'로마 콘크리트 · 바다와 화산의 부위별 배색',24,true);
label(guide,'항구 4개 모델의 기존 부위와 베수비오의 분화구·테두리·사면을 구분',12);
const names={sea_stone:'벽체·교각 석재',sea_base:'해양 기단',sea_deck:'상판·보행면',sea_cap:'정상부·벽체 상면',sea_recess:'창·오목면',sea_concrete:'방파제 블록',sea_aggregate:'드러난 골재',volcano_body:'화산 주 사면',volcano_crater:'분화구 안쪽',volcano_rock:'정상 테두리',volcano_low_slope:'낮은 사면'};
const entries=Object.entries(MATERIALS);
for(let i=0;i<entries.length;i+=4){
 const row=figma.createAutoLayout('HORIZONTAL');guide.appendChild(row);created.push(row.id);row.fills=[];row.itemSpacing=16;
 for(const [role,info]of entries.slice(i,i+4)){
  const chip=figma.createAutoLayout('VERTICAL');row.appendChild(chip);created.push(chip.id);chip.fills=[];chip.itemSpacing=5;chip.name=role;
  const rect=figma.createRectangle();chip.appendChild(rect);created.push(rect.id);rect.resize(176,28);rect.name=info.name;rect.fills=[figma.variables.setBoundVariableForPaint({type:'SOLID',color:color(info.hex)},'color',variables[role])];
  label(chip,(names[role]??role)+' '+info.hex,10,false,176);
 }
}
label(guide,'Workbench MATERIAL · 5개 객체의 면별 재질만 변경 / 지형·배치·바다색 유지',11);
label(guide,'코어 본문 ①2줄 ②3줄 ③2줄 ④2줄 ⑤3줄 · 기존 글자 크기와 폭 유지',11);
guide.exportSettings=[{format:'PNG',constraint:{type:'SCALE',value:2}}];
return {guideId:guide.id,createdNodeIds:created,modifiedNodeIds:[],createdCollectionId:collection.id,createdVariableIds,materialSemanticIds:Object.fromEntries(Object.entries(variables).map(([r,v])=>[r,v.id])),size:[guide.width,guide.height]};
