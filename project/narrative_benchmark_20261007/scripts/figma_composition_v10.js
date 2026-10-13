const page = await figma.getNodeByIdAsync('19:4');
await figma.setCurrentPageAsync(page);
const source = await figma.getNodeByIdAsync(P.sourceFrameId);
if (!source || source.type !== 'FRAME') throw new Error('Current poster missing');
if (page.children.some(n=>n.name === P.name)) throw new Error('v10 already exists; read it before retrying');
const dfs = n => [n,...(('children' in n)?n.children.flatMap(dfs):[])];
const srcNodes = dfs(source);
const srcTexts = srcNodes.filter(n=>n.type==='TEXT');
if(srcTexts.length!==95) throw new Error('Current text baseline changed');
const sourceSnapshot = () => JSON.stringify(dfs(source).map(n=>({id:n.id,x:n.x,y:n.y,w:n.width,h:n.height,name:n.name,...(n.type==='TEXT'?{t:n.characters}:{}),...('fills' in n?{fills:n.fills}:{})})));
const original = sourceSnapshot();
const fontMap = new Map();
for(const n of srcTexts) for(const s of n.getStyledTextSegments(['fontName'])) fontMap.set(JSON.stringify(s.fontName),s.fontName);
await Promise.all([...fontMap.values()].map(f=>figma.loadFontAsync(f)));
const frame = source.clone(); page.appendChild(frame);
frame.name=P.name; frame.x=P.poster.x; frame.y=P.poster.y;
frame.exportSettings=[{format:'PNG',constraint:{type:'SCALE',value:2}}];
const cloneNodes=dfs(frame);
if(cloneNodes.length!==srcNodes.length) throw new Error('Clone topology changed');
const map=new Map(srcNodes.map((n,i)=>[n.id,cloneNodes[i]]));
const n=id=>{const v=map.get(id); if(!v)throw new Error('Missing baseline node '+id);return v;};
const modified=new Set([frame.id]);
const added=[];
const gray=v=>[{type:'SOLID',color:{r:v,g:v,b:v}}];
const paint=(node,v)=>{node.fills=gray(v);modified.add(node.id);};
const setText=(node,size,lh,w,shade,align)=>{
  if(node.type!=='TEXT')throw new Error('Expected TEXT '+node.id);
  node.fontSize=size;node.lineHeight={unit:'PIXELS',value:lh};
  node.textAutoResize='HEIGHT';node.resize(w,Math.max(1,node.height));
  if(align)node.textAlignHorizontal=align;
  paint(node,shade);modified.add(node.id);
};
const position=(node,x,y)=>{node.x=x;node.y=y;modified.add(node.id);};
const ty=P.typography;
const whiteNumbers=new Set(['691:222','691:226','691:231','691:232','691:227'].map(id=>n(id).id));
for(const node of cloneNodes.filter(n=>n.type==='TEXT')){
 if(!whiteNumbers.has(node.id))paint(node,Math.abs(node.rotation)>5?ty.placeGray:ty.secondaryGray);
}
const title=n('691:202');setText(title,ty.title,80,455,ty.primaryGray,'CENTER');position(title,368.5,27);
paint(n('691:206'),ty.primaryGray);
const coreIds=[['691:267','691:268','691:269','691:270','691:271','691:272'],
 ['691:273','691:274','691:275','691:276','691:277','691:278'],
 ['691:279','691:280','691:281','691:282','691:283','691:284'],
 ['691:285','691:286','691:287','691:288','691:289','691:290'],
 ['691:291','691:292','691:293','691:294','691:295','691:296']];
for(let i=0;i<5;i++){
 const [block,head,row,t1,t2,body]=coreIds[i].map(n),c=P.cores[i];
 block.layoutMode='VERTICAL';block.primaryAxisSizingMode='AUTO';block.counterAxisSizingMode='FIXED';block.itemSpacing=c.gap;block.resize(c.width,block.height);
 head.primaryAxisSizingMode='FIXED';head.counterAxisSizingMode='FIXED';head.itemSpacing=0;head.resize(c.width,52);
 row.primaryAxisSizingMode='FIXED';row.counterAxisSizingMode='FIXED';row.paddingLeft=25;row.paddingTop=0;row.paddingBottom=0;row.paddingRight=0;row.resize(c.width,26);
 setText(t1,ty.coreTitle,ty.coreTitleLineHeight,c.width-25,ty.primaryGray);
 t1.textAutoResize='NONE';t1.resize(c.width-25,26);
 setText(t2,ty.coreTitle,ty.coreTitleLineHeight,c.width,ty.primaryGray);
 t2.textAutoResize='NONE';t2.resize(c.width,26);
 setText(body,ty.coreBody,ty.coreBodyLineHeight,c.bodyWidth,ty.bodyGray);
 position(block,c.x,c.y);
 for(const item of [block,head,row])modified.add(item.id);
}
position(n('691:226'),n('691:226').x,n('691:226').y-12);
const comp=n('692:78');comp.fills=[];comp.strokes=[];comp.cornerRadius=0;
comp.paddingLeft=0;comp.paddingRight=0;comp.paddingTop=0;comp.paddingBottom=0;
comp.primaryAxisSizingMode='AUTO';comp.counterAxisSizingMode='FIXED';comp.resize(P.comparison.width,comp.height);
setText(n('691:224'),P.comparison.fontSize,P.comparison.lineHeight,P.comparison.width,ty.bodyGray);
position(comp,P.comparison.x,P.comparison.y);
const states=n('691:309');states.itemSpacing=P.crackStates.gap;states.primaryAxisSizingMode='FIXED';states.counterAxisSizingMode='AUTO';states.resize(P.crackStates.width,14);
for(const id of ['691:310','691:311','691:312'])setText(n(id),P.crackStates.fontSize,P.crackStates.lineHeight,P.crackStates.labelWidth,ty.bodyGray,'CENTER');
position(states,P.crackStates.x,P.crackStates.y);
const guard=n('691:306');guard.itemSpacing=5;guard.primaryAxisSizingMode='AUTO';guard.counterAxisSizingMode='FIXED';guard.resize(P.crackEvidence.width,guard.height);
setText(n('691:307'),12,15,P.crackEvidence.width,ty.bodyGray);
setText(n('691:308'),P.crackEvidence.bodySize,P.crackEvidence.bodyLineHeight,P.crackEvidence.width,ty.secondaryGray);
position(guard,P.crackEvidence.x,P.crackEvidence.y);
for(const [id,c] of [['691:313',P.clastCaption],['692:79',P.observationCaption],['691:252',P.marine.caption]]){
 const node=n(id);setText(node,c.fontSize,c.lineHeight,c.width,ty.secondaryGray);position(node,c.x,c.y);
}
const lab=figma.createFrame();frame.appendChild(lab);lab.name='오늘의 실험실 · 코어 5의 검증 장면';
lab.layoutMode='VERTICAL';lab.primaryAxisSizingMode='AUTO';lab.counterAxisSizingMode='FIXED';
lab.paddingLeft=0;lab.paddingRight=0;lab.paddingTop=0;lab.paddingBottom=0;lab.itemSpacing=4;lab.fills=[];lab.strokes=[];lab.clipsContent=false;lab.resize(P.laboratoryCaption.width,64);
added.push(lab.id);
for(const [id,size,lh,shade]of [['691:241',12,15,ty.bodyGray],['691:243',9.5,13,ty.secondaryGray],['691:244',10,14,ty.secondaryGray]]){
 const node=n(id);lab.appendChild(node);setText(node,size,lh,P.laboratoryCaption.width,shade);
}
position(lab,P.laboratoryCaption.x,P.laboratoryCaption.y);
const currentTexts=dfs(frame).filter(n=>n.type==='TEXT');
const copyPreserved=srcTexts.every(t=>n(t.id).characters===t.characters)&&currentTexts.length===95;
if(!copyPreserved)throw new Error('Current copy changed');
if(sourceSnapshot()!==original)throw new Error('Original poster was mutated');
const rel=node=>({id:node.id,x:node.absoluteTransform[0][2]-frame.x,y:node.absoluteTransform[1][2]-frame.y,w:node.width,h:node.height});
return {frameId:frame.id,backgroundId:n('691:199').id,name:frame.name,createdIds:cloneNodes.map(n=>n.id).concat(added),modifiedIds:[...modified],
 sourceId:source.id,sourceUnchanged:true,current95TextContentsPreserved:copyPreserved,fontFamilies:[...fontMap.values()],
 coreMetrics:coreIds.map(ids=>({block:rel(n(ids[0])),body:rel(n(ids[5])),title1:rel(n(ids[3])),title2:rel(n(ids[4]))})),
 lab:rel(lab),states:rel(states),guard:rel(guard),comparison:rel(comp),
 idMap:Object.fromEntries([...map].filter(([id,node])=>node.type==='TEXT'||['691:199','691:267','691:273','691:279','691:285','691:291','692:78','691:309','691:306'].includes(id)).map(([id,node])=>[id,node.id]))};
