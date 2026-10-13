const page=await figma.getNodeByIdAsync('19:4');await figma.setCurrentPageAsync(page);
const source=await figma.getNodeByIdAsync('737:78');
const dfs=n=>[n,...('children'in n?n.children.flatMap(dfs):[])];
const old=dfs(source),texts=old.filter(n=>n.type==='TEXT');
if(texts.length!==95)throw new Error('Live text count changed');
if(page.children.some(n=>n.name==='v13 · 바다·화산 배색 — 코어 본문 압축'))throw new Error('v13 already exists');
const snapshot=()=>JSON.stringify(dfs(source).map(n=>({id:n.id,x:n.x,y:n.y,w:n.width,h:n.height,...(n.type==='TEXT'?{t:n.characters}:{}),...('fills'in n?{fills:n.fills}:{})})));
const before=snapshot();
const fonts=new Map();for(const t of texts)for(const s of t.getStyledTextSegments(['fontName']))fonts.set(JSON.stringify(s.fontName),s.fontName);
await Promise.all([...fonts.values()].map(f=>figma.loadFontAsync(f)));
const f=source.clone();page.appendChild(f);f.name='v13 · 바다·화산 배색 — 코어 본문 압축';f.x=source.x-1411;f.y=source.y;
f.exportSettings=[{format:'PNG',constraint:{type:'SCALE',value:2}}];
const copied=dfs(f);if(copied.length!==old.length)throw new Error('Clone topology mismatch');
const map=Object.fromEntries(old.map((n,i)=>[n.id,copied[i].id]));
const bg=await figma.getNodeByIdAsync(map['737:79']);bg.name='Blender v9 · 바다·화산 부위별 배색 · 글 없는 지도';
const body={
 '737:148':'로마에는 2천 년 전 유구가 남았다.\n철근 없이, 어떤 재료로 굳혔을까?',
 '737:154':'생석회·화산재를 마른 채 섞고,\n물을 붓자 열이 났다.\n굳은 반죽엔 흰 알갱이가 남았다.',
 '737:160':'불량 혼합으로 여긴 흰 알갱이.\n연구가 찾은 건 ‘칼슘 공급원’.',
 '737:166':'물이 칼슘을 녹여 틈으로 옮긴다.\n새 결정이 자라 작은 금을 메운다.',
 '737:172':'현대 재현 시편에 약 0.5mm 금.\n생석회 든 쪽은 수 주 뒤 거의 안 샜다.\n없는 쪽은 계속 샜다.',
 '737:191':'현대: 포틀랜드 시멘트 · 철근 보강\n로마: 석회·화산재'
};
const measurements=[];const errors=[];
for(const [id,text]of Object.entries(body)){
 const n=await figma.getNodeByIdAsync(map[id]);n.characters=text;
 const lh=n.lineHeight.value;const actualLines=Math.round(n.height/lh),expectedLines=text.split('\n').length;
 measurements.push({sourceId:id,nodeId:n.id,text,width:n.width,height:n.height,fontSize:n.fontSize,lineHeight:lh,actualLines,expectedLines});
 if(n.textAutoResize!=='HEIGHT'||actualLines!==expectedLines||actualLines<2||actualLines>3)errors.push([id,'line count',actualLines,expectedLines]);
}
for(const oldText of texts){
 const n=await figma.getNodeByIdAsync(map[oldText.id]);
 if(n.characters!==(body[oldText.id]??oldText.characters)||Math.abs(n.absoluteTransform[0][2]-f.x-(oldText.absoluteTransform[0][2]-source.x))>.01||Math.abs(n.absoluteTransform[1][2]-f.y-(oldText.absoluteTransform[1][2]-source.y))>.01||n.width!==oldText.width||(!(oldText.id in body)&&n.height!==oldText.height))errors.push([oldText.id,'copy/bounds']);
}
if(errors.length||snapshot()!==before)throw new Error('Copy/layout/source validation failed '+JSON.stringify(errors));
figma.currentPage.selection=[f];figma.viewport.scrollAndZoomIntoView([f]);
return {frameId:f.id,backgroundId:bg.id,pageId:page.id,createdNodeIds:copied.map(n=>n.id),modifiedNodeIds:[f.id,bg.id,...measurements.map(r=>r.nodeId)],idMap:map,nativeTextCount:texts.length,bodyMeasurements:measurements,sourceV12Unchanged:true,allOtherTextCopyFontBoundsPreserved:true,size:[f.width,f.height]};
