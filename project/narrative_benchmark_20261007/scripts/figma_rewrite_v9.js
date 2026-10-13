const copy={"centralQuestion": "철근도 없는 로마 건축물이 어떻게 2천 년을 버텼을까?", "sourceFrame": "688:78", "purpose": "Replace itemized v8 explanations with the Reel's rhetorical progression while preserving the map and Colosseum.", "cores": [{"core": 1, "t1": "철근이 있어도", "t2": "금은 생기는데", "body": "그런데 로마는 철근 없이도\n약 2천 년 전 유구가 남아 있다.\n굳히는 재료는 무엇이 달랐을까?", "width": 174, "titleWidths": [145, 160], "bodyWidth": 174, "bodyHeight": 42, "gap": 10}, {"core": 2, "t1": "물을 넣자,", "t2": "열이 났다", "body": "생석회·화산재를 마른 채 섞는다.\n물을 붓자, 열을 내며 굳는다.\n그 반죽에 흰 알갱이가 남았다.", "width": 155, "titleWidths": [125, 130], "bodyWidth": 155, "bodyHeight": 39, "gap": 5, "lineHeight": 13}, {"core": 3, "t1": "잘못 섞인 걸까?", "t2": "흰 알갱이의 반전", "body": "불량 혼합의 흔적으로 여겼던 알갱이.\n연구가 찾은 역할은 ‘칼슘 공급원’.", "width": 190, "titleWidths": [160, 185], "bodyWidth": 190, "bodyHeight": 28, "gap": 10}, {"core": 4, "t1": "금에 스민 물,", "t2": "칼슘을 옮기다", "body": "금으로 들어온 물이 칼슘을 녹이고,\n그 칼슘이 틈 안으로 이동한다.\n새 결정이 자라 작은 금을 메운다.", "width": 178, "titleWidths": [145, 170], "bodyWidth": 178, "bodyHeight": 42, "gap": 10}, {"core": 5, "t1": "정말 메워질까?", "t2": "금을 내어 봤더니", "body": "약 0.5mm 금을 낸 현대 재현 시편.\n생석회가 든 쪽은 수 주가 지나자\n누수가 거의 멈췄다.\n없는 쪽은 계속 샜다.", "width": 180, "titleWidths": [153, 178], "bodyWidth": 180, "bodyHeight": 56, "gap": 10}], "comparison": {"text": "대표 결합재 — 현대: 포틀랜드 시멘트\n로마: 석회·화산재\n철근은 당기는 힘을 보완", "x": 528, "y": 496, "width": 174, "fontSize": 9.5, "lineHeight": 13}, "clastCaption": {"text": "석회 알갱이를 확대한 개념 모형", "x": 444, "y": 1269, "width": 181, "fontSize": 9.5, "lineHeight": 13}, "states": [{"text": "물이 스밈", "x": 642, "y": 1234, "width": 56}, {"text": "칼슘 이동", "x": 700, "y": 1234, "width": 56}, {"text": "결정 충전", "x": 758, "y": 1234, "width": 56}], "closing": {"x": 462, "y": 1320, "width": 334, "cue": "그래서 오늘, 로마의 배합을 다시 본다.", "title": "2천 년의 비결은 하나가 아니었다.", "body": "재료의 반응과 압축에 유리한 구조,\n그리고 이어진 보수를 함께 봐야 한다."}, "proofBoundary": "The controlled modern specimens test crack filling and reduced leakage; this does not prove direct Colosseum healing or restored structural strength.", "benchmarkFunctions": ["familiar modern vulnerability to Roman surviving surprise", "manufacture leaves the grains introduced next", "apparent mixing defect becomes calcium-supply clue", "same calcium moves and precipitates in the crack", "controlled reconstructed specimens with comparator", "return to present research and the opening question"]};
const page=await figma.getNodeByIdAsync('19:4');await figma.setCurrentPageAsync(page);
const name='v9 · 릴스 서사 이식 — 대비, 알갱이의 반전, 실험';
const existing=page.children.find(n=>n.name===name);
if(existing)return {alreadyExists:true,frameId:existing.id,createdNodeIds:[],mutatedNodeIds:[]};
const v8=await figma.getNodeByIdAsync('688:78'),v7=await figma.getNodeByIdAsync('634:78');
const snapshot=f=>JSON.stringify([f,...f.findAll()].map(n=>({id:n.id,type:n.type,name:n.name,m:n.absoluteTransform,w:n.width,h:n.height,children:'children'in n?n.children.map(c=>c.id):undefined,text:n.type==='TEXT'?n.characters:undefined,fills:'fills'in n?n.fills:undefined})));
const before8=snapshot(v8),before7=snapshot(v7);
const fontMap=new Map();for(const n of v8.findAllWithCriteria({types:['TEXT']}))for(const s of n.getStyledTextSegments(['fontName']))fontMap.set(JSON.stringify(s.fontName),s.fontName);
await Promise.all([...fontMap.values()].map(f=>figma.loadFontAsync(f)));
const frame=v8.clone();page.appendChild(frame);frame.name=name;frame.x=226;frame.y=56;frame.placeholder=true;
const created=[frame.id,...frame.findAll().map(n=>n.id)],mutated=new Set([frame.id]);
const texts=frame.findAllWithCriteria({types:['TEXT']});
const get=id=>{const n=texts.find(t=>t.name.startsWith('개정 · '+id+' · '));if(!n)throw new Error('Missing '+id);return n;};
const edit=(n,id,text,width,height,lineHeight)=>{n.textAutoResize='HEIGHT';n.resize(width,height);if(lineHeight)n.lineHeight={unit:'PIXELS',value:lineHeight};n.characters=text;n.name='서사 v9 · '+id+' · '+text.replace(/\n/g,' / ');mutated.add(n.id);return n;};
const patched=[];
for(const c of copy.cores){
 const id='C'+c.core,n1=get(id+'_t1'),n2=get(id+'_t2'),b=get(id+'_b');
 const main=b.parent,head=n2.parent,row=n1.parent;
 edit(n1,id+'_t1',c.t1,c.titleWidths[0],25,25);edit(n2,id+'_t2',c.t2,c.titleWidths[1],25,25);edit(b,id+'_b',c.body,c.bodyWidth,c.bodyHeight,c.lineHeight||14);
 for(const n of[n1,n2,b]){n.layoutSizingHorizontal='FIXED';n.layoutSizingVertical='FIXED';}
 main.resize(c.width,50+c.gap+c.bodyHeight);main.itemSpacing=c.gap;main.name='CORE '+c.core+' · '+c.t1+' '+c.t2;head.resize(c.width,50);row.resize(c.width,25);
 for(const n of[main,head,row])mutated.add(n.id);
 patched.push({core:c.core,titleIds:[n1.id,n2.id],bodyId:b.id,layoutId:main.id,bodyHeight:b.height,expectedHeight:c.bodyHeight,bodyPosition:[b.absoluteTransform[0][2]-frame.x,b.absoluteTransform[1][2]-frame.y]});
}
const comparison=get('C1_model_note'),cmp=copy.comparison;edit(comparison,'C1_comparison',cmp.text,cmp.width,cmp.lineHeight*3,cmp.lineHeight);comparison.x=cmp.x;comparison.y=cmp.y;
const d4=get('D4_h').parent;d4.y=1253;mutated.add(d4.id);
const solid=[{type:'SOLID',color:{r:17/255,g:17/255,b:17/255}}];
const newText=(parent,id,text,w,size,lh,bold=false)=>{const n=figma.createText();created.push(n.id);parent.appendChild(n);n.name='서사 v9 · '+id+' · '+text.replace(/\n/g,' / ');n.fontName={family:'Noto Sans KR',style:bold?'Bold':'Regular'};n.fontSize=size;n.lineHeight={unit:'PIXELS',value:lh};n.fills=solid;n.textAutoResize='HEIGHT';n.resize(w,lh*text.split('\n').length);n.characters=text;return n;};
const states=figma.createAutoLayout('HORIZONTAL');created.push(states.id);frame.appendChild(states);states.name='균열의 연속 동작 · 물 → 칼슘 → 결정';states.resize(172,13);states.x=642;states.y=1234;states.primaryAxisSizingMode='FIXED';states.counterAxisSizingMode='AUTO';states.itemSpacing=2;states.fills=[];states.strokes=[];states.clipsContent=false;
for(const [i,s]of copy.states.entries()){const n=newText(states,'crack_state_'+(i+1),s.text,s.width,9.5,13);n.layoutSizingHorizontal='FIXED';n.layoutSizingVertical='FIXED';}
const cc=copy.clastCaption,caption=newText(frame,'clast_model_scope',cc.text,cc.width,cc.fontSize,cc.lineHeight);caption.x=cc.x;caption.y=cc.y;
const close=figma.createAutoLayout('VERTICAL');created.push(close.id);frame.appendChild(close);close.name='처음 질문으로 돌아오기 · 현재 연구와 재료·구조·보수';close.resize(copy.closing.width,75);close.x=copy.closing.x;close.y=copy.closing.y;close.primaryAxisSizingMode='AUTO';close.counterAxisSizingMode='FIXED';close.itemSpacing=6;close.fills=[];close.strokes=[];close.clipsContent=false;
for(const [id,text,size,lh,bold] of [['return',copy.closing.cue,11.5,14.5,true],['answer',copy.closing.title,16,20,true],['multiple_causes',copy.closing.body,10.5,14,false]]){const n=newText(close,id,text,copy.closing.width,size,lh,bold);n.layoutSizingHorizontal='FIXED';n.layoutSizingVertical='FIXED';}
frame.placeholder=false;frame.exportSettings=[{format:'PNG',constraint:{type:'SCALE',value:2}}];
page.selection=[frame];figma.viewport.scrollAndZoomIntoView([frame]);
const allTexts=frame.findAllWithCriteria({types:['TEXT']});
const nativeTexts=allTexts.map(n=>({id:n.id,t:n.characters,x:Math.round((n.absoluteTransform[0][2]-frame.x)*100)/100,y:Math.round((n.absoluteTransform[1][2]-frame.y)*100)/100,w:n.width,h:n.height}));
const outOfBounds=allTexts.filter(n=>{const b=n.absoluteBoundingBox;return b&&(b.x<frame.x-.1||b.y<frame.y-.1||b.x+b.width>frame.x+frame.width+.1||b.y+b.height>frame.y+frame.height+.1);}).map(n=>({id:n.id,name:n.name,bounds:n.absoluteBoundingBox}));
return {frameId:frame.id,backgroundId:frame.findAll(n=>n.type==='RECTANGLE')[0].id,pageId:page.id,name:frame.name,bounds:{x:frame.x,y:frame.y,w:frame.width,h:frame.height},createdNodeIds:created,mutatedNodeIds:[...mutated],patches:patched,textCount:allTexts.length,originalV7Unchanged:before7===snapshot(v7),previousV8Unchanged:before8===snapshot(v8),backgroundHash:frame.findAll(n=>n.type==='RECTANGLE')[0].fills[0].imageHash,outOfBounds,nativeTexts};
