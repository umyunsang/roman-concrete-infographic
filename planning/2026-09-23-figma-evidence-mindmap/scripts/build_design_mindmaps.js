// Finite publication component family, on the existing Design "마인드맵" page only.
// Root executes with skillNames "figma-use,figma-generate-library" and owns upload_assets / screenshots.
// Adapted from the official createComponentWithVariants helper: variables first, per-variant Label properties,
// combineAsVariants, then explicitly place the variants. No library/demo pages or application UI.
const LABELS = {"ARC01":"오늘도 남아 있는 판테온","ARC02":"원통 위를 덮은 돔","ARC03":"원형 공간을 감싼 두꺼운 벽","ARC04":"돔의 무게를 받는 여덟 지지부","ARC05":"쓰임의 지속과 보존","ARC06":"일부를 잃고 남은 콜로세움","ARC07":"고리형 벽과 방사형 벽의 연결","ARC08":"기둥과 아치·볼트가 만든 회랑","ARC09":"석재·벽돌·콘크리트의 조합","ARC10":"계속되는 관리와 보수","ARC11":"용도에 따라 달라지는 배합","ARC12":"다른 유적 연구의 자가복원 단서","PRE02":"현재도 미사와 기도가 열림","PRE04":"현관 청동 덮개는 후대에 철거","PRE05":"대리석 바닥에도 균열·결손","PRE06":"19세기에도 바닥을 전면 복원","PRE07":"2023년 바닥 보존·복원 재개","PRE08":"오늘도 유지관리 책임이 존재","PRE09":"콜로세움 남측 회랑은 무너짐","PRE10":"19세기 버팀 구조로 외벽 보강","PRE11":"현대에도 통로 복원·방수","PRE12":"남아 있다 ≠ 무손상·무보수"};
const CLASS_GROUPS = [{"key":"cases","title":"남아 있는 건축물","side":"left","color":"#D29F2A","ids":["ARC01","ARC06"]},{"key":"structure","title":"하중을 버티는 구조","side":"left","color":"#E67845","ids":["ARC02","ARC03","ARC04","ARC07","ARC08"]},{"key":"material","title":"시간을 견디는 재료","side":"left","color":"#36A091","ids":["ARC09","ARC11","ARC12"]},{"key":"use","title":"쓰임이 이어진 역사","side":"right","color":"#9C79C1","ids":["ARC05","PRE02"]},{"key":"damage","title":"겪어온 손상과 상실","side":"right","color":"#BD687B","ids":["PRE04","PRE05","PRE09"]},{"key":"preservation","title":"후대의 보존과 보강","side":"right","color":"#4785C9","ids":["ARC10","PRE06","PRE07","PRE08","PRE10","PRE11","PRE12"]}];
const ROLE_GROUPS = [{"key":"basic","title":"01 기본\nBASIC","side":"left","color":"#4785C9","ids":["ARC01","ARC02","ARC06","ARC09"]},{"key":"detail","title":"03 세부\nDETAIL","side":"left","color":"#9C79C1","ids":["ARC03","ARC07","ARC08","ARC11","PRE04","PRE05","PRE09"]},{"key":"core","title":"02 핵심\nCORE","side":"right","color":"#36A091","ids":["ARC04","ARC05","ARC12","PRE10","PRE12"]},{"key":"support","title":"보조 근거\nSUPPORT","side":"right","color":"#D29F2A","ids":["ARC10","PRE02","PRE06","PRE07","PRE08","PRE11"]}];
const CONCEPTS = [{"id":"P","label":"판테온\n오늘도 남은 건축물","evidence_ids":["ARC01"],"kind":"primary_case","position":{"x":2080,"y":1080,"width":680}},{"id":"D","label":"원통형 몸체 위의\n반구형 돔","evidence_ids":["ARC02"],"kind":"structure","position":{"x":1210,"y":820,"width":490}},{"id":"W","label":"두꺼운 벽체\n여덟 큰 지지부","evidence_ids":["ARC03","ARC04"],"kind":"structure","position":{"x":190,"y":820,"width":590}},{"id":"PD","label":"청동 덮개의 상실\n바닥의 균열·결손","evidence_ids":["PRE04","PRE05"],"kind":"damage","position":{"x":1230,"y":370,"width":740}},{"id":"U","label":"609년 교회 전환\n지금도 이어지는 예배","evidence_ids":["ARC05","PRE02"],"kind":"use","position":{"x":3440,"y":380,"width":680}},{"id":"H","label":"지속된 쓰임\n보존에 일부 기여","evidence_ids":["ARC05"],"kind":"historical_interpretation","position":{"x":3210,"y":870,"width":780}},{"id":"PC","label":"바닥 복원과\n오늘의 유지관리","evidence_ids":["PRE06","PRE07","PRE08"],"kind":"conservation","position":{"x":3400,"y":1360,"width":760}},{"id":"S","label":"다른 유적·현대 시편 연구\n조건부 균열 충전 단서","evidence_ids":["ARC12"],"kind":"conditional_material_detail","position":{"x":130,"y":1460,"width":720}},{"id":"L","label":"남아 있음 ≠ 무손상\n타 유적 ≠ 직접 입증","evidence_ids":["PRE12","ARC12"],"kind":"interpretation_limit","position":{"x":1190,"y":1460,"width":740}},{"id":"C","label":"콜로세움\n일부를 잃고 남음","evidence_ids":["ARC06"],"kind":"comparison_case","position":{"x":2130,"y":2280,"width":750}},{"id":"CD","label":"지진과 철거\n남측 회랑의 붕괴","evidence_ids":["PRE09"],"kind":"damage","position":{"x":3500,"y":2220,"width":670}},{"id":"B","label":"19세기 버팀 구조\n남은 외벽의 후대 보강","evidence_ids":["PRE10"],"kind":"conservation","position":{"x":3500,"y":2740,"width":700}},{"id":"CC","label":"통로 복원·방수\n계속되는 계획적 유지관리","evidence_ids":["ARC10","PRE11"],"kind":"conservation","position":{"x":2140,"y":2990,"width":760}},{"id":"CS","label":"고리형·방사형 벽\n기둥과 볼트의 연결","evidence_ids":["ARC07","ARC08"],"kind":"structure","position":{"x":1190,"y":2360,"width":700}},{"id":"M","label":"석재·벽돌·콘크리트\n부위·용도별 재료와 배합","evidence_ids":["ARC09","ARC11"],"kind":"material","position":{"x":150,"y":2380,"width":740}}];
const RELATIONS = [{"id":"AR01","source":"P","target":"D","type":"whole_part","label":"전체–부분\n판테온의 돔","evidence_ids":["ARC01","ARC02"],"visual":{"color":"#D29F2A","start_magnet":"LEFT","end_magnet":"RIGHT","arrow":false,"dashed":false}},{"id":"AR02","source":"D","target":"W","type":"mechanical_load_path","label":"역학 원리\n돔 무게의 전달·분산","evidence_ids":["ARC02","ARC03","ARC04"],"visual":{"color":"#E67845","start_magnet":"LEFT","end_magnet":"RIGHT","arrow":true,"dashed":false}},{"id":"AR03","source":"PD","target":"P","type":"preservation_state_limit","label":"상태의 한계\n모든 부분이 원형은 아님","evidence_ids":["ARC01","PRE04","PRE05"],"visual":{"color":"#BD687B","start_magnet":"BOTTOM","end_magnet":"TOP","arrow":false,"dashed":true}},{"id":"AR04","source":"U","target":"H","type":"qualified_historical_interpretation","label":"역사 해석\n보존의 한 요인","evidence_ids":["ARC05","PRE02"],"visual":{"color":"#9C79C1","start_magnet":"BOTTOM","end_magnet":"TOP","arrow":true,"dashed":true}},{"id":"AR05","source":"H","target":"P","type":"qualified_contribution","label":"공동 설명\n보존에 일부 기여","evidence_ids":["ARC01","ARC05"],"visual":{"color":"#9C79C1","start_magnet":"LEFT","end_magnet":"RIGHT","arrow":true,"dashed":true}},{"id":"AR06","source":"PC","target":"P","type":"conservation_action","label":"보존 활동\n후대의 복원·관리","evidence_ids":["PRE06","PRE07","PRE08"],"visual":{"color":"#4785C9","start_magnet":"LEFT","end_magnet":"RIGHT","arrow":true,"dashed":false}},{"id":"AR07","source":"C","target":"P","type":"case_comparison","label":"사례 비교\n남아 있는 상태가 다름","evidence_ids":["ARC01","ARC06","PRE12"],"visual":{"color":"#D29F2A","start_magnet":"TOP","end_magnet":"BOTTOM","arrow":false,"dashed":false}},{"id":"AR08","source":"CD","target":"C","type":"recorded_damage_consequence","label":"손상 이력\n붕괴·철거 뒤 부분 잔존","evidence_ids":["ARC06","PRE09"],"visual":{"color":"#BD687B","start_magnet":"LEFT","end_magnet":"RIGHT","arrow":true,"dashed":false}},{"id":"AR09","source":"CD","target":"B","type":"temporal_sequence","label":"시간 관계\n손상 뒤의 후대 보강","evidence_ids":["PRE09","PRE10"],"visual":{"color":"#9C79C1","start_magnet":"BOTTOM","end_magnet":"TOP","arrow":true,"dashed":false}},{"id":"AR10","source":"B","target":"C","type":"later_structural_support","label":"후대 보강\n추가 붕괴를 막기 위한 지지","evidence_ids":["PRE10","ARC06"],"visual":{"color":"#4785C9","start_magnet":"LEFT","end_magnet":"RIGHT","arrow":true,"dashed":false}},{"id":"AR11","source":"CC","target":"C","type":"ongoing_conservation","label":"보존 활동\n복원·방수·유지관리","evidence_ids":["ARC10","PRE11"],"visual":{"color":"#4785C9","start_magnet":"TOP","end_magnet":"BOTTOM","arrow":true,"dashed":false}},{"id":"AR12","source":"C","target":"CS","type":"whole_part","label":"전체–부분\n회랑을 이루는 구조","evidence_ids":["ARC07","ARC08"],"visual":{"color":"#E67845","start_magnet":"LEFT","end_magnet":"RIGHT","arrow":false,"dashed":false}},{"id":"AR13","source":"M","target":"CS","type":"material_composition","label":"재료 구성\n부위별로 조합","evidence_ids":["ARC07","ARC08","ARC09","ARC11"],"visual":{"color":"#36A091","start_magnet":"RIGHT","end_magnet":"LEFT","arrow":false,"dashed":false}},{"id":"AR14","source":"S","target":"M","type":"conditional_supporting_detail","label":"재료 보조 단서\n조건부·다른 유적 연구","evidence_ids":["ARC11","ARC12"],"visual":{"color":"#36A091","start_magnet":"BOTTOM","end_magnet":"TOP","arrow":false,"dashed":true}},{"id":"AR15","source":"S","target":"L","type":"evidence_scope_limit","label":"근거의 범위\n타유적 관찰·현대 시편","evidence_ids":["ARC12"],"visual":{"color":"#BD687B","start_magnet":"RIGHT","end_magnet":"LEFT","arrow":false,"dashed":true}},{"id":"AR16","source":"L","target":"P","type":"application_limit","label":"적용의 한계\n자가치유의 직접 입증 아님","evidence_ids":["ARC12","PRE12"],"visual":{"color":"#BD687B","start_magnet":"RIGHT","end_magnet":"LEFT","arrow":false,"dashed":true}},{"id":"AR17","source":"C","target":"L","type":"survivorship_limit","label":"일반화 한계\n남아 있음 ≠ 무손상","evidence_ids":["ARC06","PRE09","PRE10","PRE12"],"visual":{"color":"#BD687B","start_magnet":"LEFT","end_magnet":"BOTTOM","arrow":false,"dashed":true}}];
const ASSETS = {"pantheon-exterior":{"path":"/Users/um-yunsang/.planning/2026-09-23-figma-evidence-mindmap/evidence/images/pantheon-exterior.jpg","caption":"중심 사례 · 판테온 / NikonZ7II · CC BY-SA 4.0"},"pantheon-interior":{"path":"/Users/um-yunsang/.planning/2026-09-23-figma-evidence-mindmap/evidence/images/pantheon-interior.jpg","caption":"판테온의 돔 내부 / Mariordo · CC BY-SA 4.0"},"colosseum-photo":{"path":"/Users/um-yunsang/.planning/2026-09-23-figma-evidence-mindmap/source-images/image8.jpg","caption":"비교 사례 · 콜로세움 / Kasa Fue · CC BY-SA 4.0"},"2023-mechanism":{"path":"/Users/um-yunsang/.planning/2026-09-23-figma-evidence-mindmap/evidence/images/2023-mechanism.jpg","caption":"다른 유적 연구의 제안 기작 · Seymour 외(2023), Fig. 6\nCC BY-NC 4.0 · 원본 비율 유지"}};
const RELATION_SOURCE_SHA256 = "5179a2897f9c25aaa677609a8ed32b88eb628dae46c6b84487bb4c8027ce534a";

if(figma.editorType!=='figma') throw new Error('This build targets Figma Design.');
if(figma.fileKey && figma.fileKey!=='jQPriO85F6wtPy1NPo752p') throw new Error('Unexpected Design file.');
const page=await figma.getNodeByIdAsync('19:2');
if(!page || page.type!=='PAGE' || page.name!=='마인드맵') throw new Error('Expected page 19:2 마인드맵.');
await figma.setCurrentPageAsync(page);
const frameNames=['01 · 분류 마인드맵','02 · 배열 마인드맵','03 · 관계 마인드맵'];
const familyName='로마 건축 / 주제 노드';
if(page.children.some(n=>frameNames.includes(n.name)||n.name==='주제 노드 · 컴포넌트 원본')) throw new Error('Mindmap content already exists; inspect before retrying.');
if(page.findAllWithCriteria({types:['COMPONENT_SET']}).some(n=>n.name===familyName)) throw new Error('Topic family already exists; inspect before retrying.');
const collectionName='로마 건축 / 마인드맵 색상';
const existingCollections=await figma.variables.getLocalVariableCollectionsAsync();
if(existingCollections.some(c=>c.name===collectionName)) throw new Error('Mindmap variables already exist; inspect before retrying.');
const baseX=Math.max(160,...page.children.map(n=>n.x+n.width+320));
const regular={family:'Noto Sans KR',style:'Regular'},bold={family:'Noto Sans KR',style:'Bold'};
await Promise.all([figma.loadFontAsync(regular),figma.loadFontAsync(bold),figma.loadFontAsync({family:'Inter',style:'Regular'})]);
const created=[],createdSet=new Set(),variableIds=[],collectionIds=[],instanceIds=[],imageTargets=[],maps=[],branchVectors=[],arrowheads=[],placementIssues=[];
function keep(n){if(!createdSet.has(n.id)){createdSet.add(n.id);created.push(n.id);}return n;}
function keepTree(n){keep(n);if('children' in n)for(const c of n.children)keepTree(c);return n;}
const rgb=h=>({r:parseInt(h.slice(1,3),16)/255,g:parseInt(h.slice(3,5),16)/255,b:parseInt(h.slice(5,7),16)/255});
// P1: exactly one mode, narrow scopes. Primitive values are hidden; semantic colors alias them.
const collection=figma.variables.createVariableCollection(collectionName);collectionIds.push(collection.id);
const modeId=collection.modes[0].modeId;collection.renameMode(modeId,'Print');
const palette={canvas:'#FFFFFF',text:'#1E1E1E',gold:'#D29F2A',terracotta:'#E67845',teal:'#36A091',violet:'#9C79C1',rose:'#BD687B',blue:'#4785C9'};
const colors={},byHex={};
for(const [key,hex] of Object.entries(palette)){
 const p=figma.variables.createVariable('primitive/'+key,collection,'COLOR');variableIds.push(p.id);
 p.scopes=[];p.setValueForMode(modeId,{...rgb(hex),a:1});p.setVariableCodeSyntax('WEB','var(--roman-map-raw-'+key+')');
 const v=figma.variables.createVariable('color/'+key,collection,'COLOR');variableIds.push(v.id);
 v.scopes=key==='text'?['TEXT_FILL']:(key==='canvas'?['FRAME_FILL','SHAPE_FILL']:['STROKE_COLOR','SHAPE_FILL']);
 v.setValueForMode(modeId,{type:'VARIABLE_ALIAS',id:p.id});v.setVariableCodeSyntax('WEB','var(--roman-map-'+key+')');
 colors[key]=v;byHex[hex.toUpperCase()]=v;
}
function bound(v){return [figma.variables.setBoundVariableForPaint({type:'SOLID',color:{r:0,g:0,b:0}},'color',v)];}
function colorFor(hex){const v=byHex[hex.toUpperCase()];if(!v)throw new Error('Unplanned branch color '+hex);return v;}
function auto(parent,name,width,gap=10){
 const n=keep(figma.createAutoLayout('VERTICAL'));parent.appendChild(n);n.name=name;n.resize(width,90);
 n.primaryAxisSizingMode='AUTO';n.counterAxisSizingMode='FIXED';n.itemSpacing=gap;n.fills=[];n.clipsContent=false;return n;
}
function tx(parent,name,value,width,size=24,strong=false,align='LEFT'){
 const n=keep(figma.createText());parent.appendChild(n);n.name=name;n.fontName=strong?bold:regular;n.fontSize=size;
 n.textAutoResize='HEIGHT';n.resize(width,Math.max(40,size*1.45));n.lineHeight={unit:'PERCENT',value:145};
 n.characters=value;n.textAlignHorizontal=align;n.fills=bound(colors.text);
 if(!(n.width>0))throw new Error('Collapsed text: '+name);return n;
}
// P2: five variants of one finite topic family. No visible boxes or dashboard cards.
const styles=[
 {role:'Center',width:700,size:50,bold:true,align:'CENTER',sample:'중심 주제\nLabel로 편집'},
 {role:'BranchLeft',width:400,size:36,bold:true,align:'RIGHT',sample:'왼쪽 가지'},
 {role:'BranchRight',width:400,size:36,bold:true,align:'LEFT',sample:'오른쪽 가지'},
 {role:'LeafLeft',width:670,size:26,bold:false,align:'RIGHT',sample:'왼쪽 근거 · Label로 편집'},
 {role:'LeafRight',width:670,size:26,bold:false,align:'LEFT',sample:'오른쪽 근거 · Label로 편집'}
];
const variants={},variantArray=[];
for(const s of styles){
 const c=keep(figma.createComponent());page.appendChild(c);c.name='Role='+s.role;c.resize(s.width,100);
 c.layoutMode='VERTICAL';c.primaryAxisSizingMode='AUTO';c.counterAxisSizingMode='FIXED';
 c.primaryAxisAlignItems='MIN';c.counterAxisAlignItems='MIN';c.paddingTop=8;c.paddingBottom=8;c.paddingLeft=8;c.paddingRight=8;c.itemSpacing=0;c.fills=[];c.strokes=[];c.clipsContent=false;
 c.description='출판용 마인드맵의 '+s.role+' 주제 노드. Label 텍스트 속성으로 편집합니다.';
 const key=c.addComponentProperty('Label','TEXT',s.sample);
 const label=tx(c,'Label',s.sample,s.width-16,s.size,s.bold,s.align);
 label.componentPropertyReferences={characters:key};
 // Explicit wrapping width is established before FILL on the fixed-width auto-layout master.
 label.layoutSizingHorizontal='FIXED';label.textAutoResize='HEIGHT';
 variants[s.role]={component:c,labelKey:key,labelNode:label,style:s};variantArray.push(c);
}
const componentSet=keep(figma.combineAsVariants(variantArray,page));componentSet.name=familyName;
componentSet.description='중심·좌우 가지·좌우 근거의 5종. 흰 캔버스와 글자·곡선만 사용하는 문서 전용 컴포넌트입니다.';
componentSet.layoutMode='NONE';componentSet.fills=[];
let variantX=40,variantMaxH=0;
for(const s of styles){const c=variants[s.role].component;c.x=variantX;c.y=40;variantX+=c.width+52;variantMaxH=Math.max(variantMaxH,c.height);}
componentSet.resizeWithoutConstraints(variantX-12,variantMaxH+80);
function topic(parent,role,value,x,y,width,name){
 const entry=variants[role],n=keepTree(entry.component.createInstance());parent.appendChild(n);instanceIds.push(n.id);n.name=name;
 const children=n.findAllWithCriteria({types:['TEXT']});const label=children.find(t=>t.name==='Label');
 if(!label)throw new Error('Topic instance missing Label child.');
 const refs=label.componentPropertyReferences;
 let key=refs&&refs.characters;
 if(!key||!n.componentProperties[key]){
  const candidates=Object.entries(n.componentProperties).filter(([k,v])=>v.type==='TEXT'&&k.split('#')[0]==='Label');
  if(candidates.length!==1)throw new Error('Ambiguous Label property on '+role);
  key=candidates[0][0];
 }
 n.setProperties({[key]:value});
 const w=width||entry.style.width;n.resize(w,Math.max(50,n.height));n.counterAxisSizingMode='FIXED';
 const liveLabel=n.findAllWithCriteria({types:['TEXT']}).find(t=>t.name==='Label');
 if(!liveLabel)throw new Error('Live Label missing after property change');
 liveLabel.layoutSizingHorizontal='FIXED';liveLabel.textAutoResize='HEIGHT';
 liveLabel.resize(w-n.paddingLeft-n.paddingRight,Math.max(40,liveLabel.height));liveLabel.textAutoResize='HEIGHT';
 n.primaryAxisSizingMode='AUTO';n.x=x;n.y=y;keepTree(n);
 if(liveLabel.textAutoResize!=='HEIGHT'||!(liveLabel.width>0))throw new Error('Topic geometry '+JSON.stringify({name,mode:liveLabel.textAutoResize,width:liveLabel.width,height:liveLabel.height}));
 return n;
}
function frame(name,x,y,w,h){const n=keep(figma.createFrame());page.appendChild(n);n.name=name;n.resize(w,h);n.x=x;n.y=y;n.fills=bound(colors.canvas);n.clipsContent=false;return n;}
function header(parent,title,subtitle,width){const a=auto(parent,'제목과 범위',width,14);a.x=90;a.y=60;tx(a,'단계 제목',title,width,51,true);tx(a,'단계 설명',subtitle,width,25);return a;}
function imageTarget(parent,key,x,y,w,h){
 const a=ASSETS[key];if(!a)throw new Error('Unknown image key '+key);
 const wrap=auto(parent,'도판 · '+key,w,14);wrap.x=x;wrap.y=y;
 const box=keep(figma.createRectangle());wrap.appendChild(box);box.name='IMAGE_FILL · '+key;box.resize(w,h);box.fills=bound(colors.canvas);box.strokes=[];
 tx(wrap,'사진·도판 출처 · '+key,a.caption,w,19);
 imageTargets.push({nodeId:box.id,key,path:a.path,scaleMode:'FIT',frameId:parent.id});return wrap;
}
function anchor(n,side){if(side==='LEFT')return{x:n.x,y:n.y+n.height/2};if(side==='RIGHT')return{x:n.x+n.width,y:n.y+n.height/2};if(side==='TOP')return{x:n.x+n.width/2,y:n.y};return{x:n.x+n.width/2,y:n.y+n.height};}
function normal(side){return side==='LEFT'?{x:-1,y:0}:side==='RIGHT'?{x:1,y:0}:side==='TOP'?{x:0,y:-1}:{x:0,y:1};}
function bez(p,t){const q=1-t;return{x:q*q*q*p[0].x+3*q*q*t*p[1].x+3*q*t*t*p[2].x+t*t*t*p[3].x,y:q*q*q*p[0].y+3*q*q*t*p[1].y+3*q*t*t*p[2].y+t*t*t*p[3].y};}
function tangent(p,t){const q=1-t;return{x:3*q*q*(p[1].x-p[0].x)+6*q*t*(p[2].x-p[1].x)+3*t*t*(p[3].x-p[2].x),y:3*q*q*(p[1].y-p[0].y)+6*q*t*(p[2].y-p[1].y)+3*t*t*(p[3].y-p[2].y)};}
function extrema(p,axis){
 const v=p.map(q=>q[axis]),a=-v[0]+3*v[1]-3*v[2]+v[3],b=2*(v[0]-2*v[1]+v[2]),c=v[1]-v[0],ts=[0,1];
 if(Math.abs(a)<1e-9){if(Math.abs(b)>1e-9){const t=-c/b;if(t>0&&t<1)ts.push(t);}}
 else{const d=b*b-4*a*c;if(d>=0)for(const t of [(-b+Math.sqrt(d))/(2*a),(-b-Math.sqrt(d))/(2*a)])if(t>0&&t<1)ts.push(t);}
 return ts.map(t=>bez(p,t)[axis]);
}
const number=x=>Math.round(x*1000)/1000;
function vectorPath(parent,name,points,color,isFill=false,weight=3,dashed=false){
 const n=keep(figma.createVector());parent.appendChild(n);n.name=name;
 const minX=Math.min(...points.map(p=>p.x)),minY=Math.min(...points.map(p=>p.y));
 n.vectorPaths=[{windingRule:'NONZERO',data:points.map((p,i)=>(i?'L ':'M ')+number(p.x-minX)+' '+number(p.y-minY)).join(' ')+(isFill?' Z':'')}];
 n.x=minX;n.y=minY;n.fills=isFill?bound(color):[];n.strokes=isFill?[]:bound(color);if(!isFill){n.strokeWeight=weight;n.dashPattern=dashed?[12,8]:[];}return n;
}
function curve(parent,a,b,color,start='RIGHT',end='LEFT',weight=3,arrow=false,dashed=false,name='가지'){
 const p0=anchor(a,start),p3=anchor(b,end),ns=normal(start),ne=normal(end);
 const distance=Math.hypot(p3.x-p0.x,p3.y-p0.y),reach=Math.max(64,Math.min(340,distance*.40));
 const ps=[p0,{x:p0.x+ns.x*reach,y:p0.y+ns.y*reach},{x:p3.x+ne.x*reach,y:p3.y+ne.y*reach},p3];
 const minX=Math.min(...extrema(ps,'x')),minY=Math.min(...extrema(ps,'y'));
 const local=ps.map(p=>({x:number(p.x-minX),y:number(p.y-minY)}));
 const n=keep(figma.createVector());parent.appendChild(n);n.name=name;n.fills=[];n.strokes=bound(color);n.strokeWeight=weight;n.strokeCap='ROUND';n.strokeJoin='ROUND';n.dashPattern=dashed?[12,8]:[];
 n.vectorPaths=[{windingRule:'NONZERO',data:'M '+local[0].x+' '+local[0].y+' C '+local[1].x+' '+local[1].y+' '+local[2].x+' '+local[2].y+' '+local[3].x+' '+local[3].y}];
 n.x=minX;n.y=minY;branchVectors.push(n.id);
 let arrowId=null;
 if(arrow){const d=tangent(ps,1),length=Math.hypot(d.x,d.y)||1,u={x:d.x/length,y:d.y/length},perp={x:-u.y,y:u.x};
  const tip=ps[3],q={x:tip.x-u.x*18,y:tip.y-u.y*18};
  const h=vectorPath(parent,name+' · 화살표',[tip,{x:q.x+perp.x*8,y:q.y+perp.y*8},{x:q.x-perp.x*8,y:q.y-perp.y*8}],color,true);
  arrowId=h.id;arrowheads.push(h.id);
 }
 return{node:n,points:ps,arrowId};
}
function footer(parent,y,width,scope){const a=auto(parent,'범위와 출처',width,12);a.x=90;a.y=y;tx(a,'핵심 질문','로마 건축물은 어떻게 약 2천 년을 버텼을까? · 판테온 중심 + 콜로세움 비교',width,24,true);tx(a,'근거 식별자','[ARC·PRE]는 통합 근거 22개의 식별자입니다. 주요 근거: 로마시·판테온 운영기관·콜로세움 고고학공원·구조 및 재료 원논문',width,20);tx(a,'해석 범위',scope,width,20);return a;}
function fitFrame(n,minH){let right=0,bottom=0;for(const c of n.children){right=Math.max(right,c.x+c.width);bottom=Math.max(bottom,c.y+c.height);}n.resize(Math.max(n.width,Math.ceil(right+90)),Math.max(minH,Math.ceil(bottom+90)));}
// P3: two accepted spatial trees. Each leaf remains an editable Label-property instance.
function buildTree(stage,x,groups,centerText){
 const f=frame(frameNames[stage-1],x,160,3700,2600);
 header(f,stage===1?'1단계 · 건축물의 생존을 분류하다':'2단계 · 건축물에서 작동 원리와 보존으로',stage===1?'판테온 중심 + 콜로세움 비교 · 유사한 정보끼리 묶기 · 읽는 순서와 중요도는 아직 정하지 않음':'기본 → 핵심 → 세부 · 보조 근거 / 자가치유는 다른 유적 연구의 재료 확대 가지',3520);
 const root=topic(f,'Center',centerText,1480,0,700,'중심 주제');root.y=1130-root.height/2;
 const branches={},leaves={},connections=[];let bottom=1900;
 for(const side of ['left','right']){
  const prep=groups.filter(g=>g.side===side).map(g=>{const list=g.ids.map(id=>topic(f,side==='left'?'LeafLeft':'LeafRight',LABELS[id]+'  ['+id+']',side==='left'?90:2930,0,670,id+' · '+LABELS[id]));return{g,list,height:Math.max(170,list.reduce((s,n)=>s+n.height,0)+38*(list.length-1))};});
  const total=prep.reduce((s,p)=>s+p.height,0)+140*(prep.length-1);let y=330+(1600-total)/2;
  for(const {g,list,height} of prep){
   const category=topic(f,side==='left'?'BranchLeft':'BranchRight',g.title,side==='left'?930:2360,0,400,'분류 가지 · '+g.title);category.y=y+height/2-category.height/2;branches[g.key]=category.id;
   connections.push(curve(f,root,category,colorFor(g.color),side==='left'?'LEFT':'RIGHT',side==='left'?'RIGHT':'LEFT',6,false,false,'중심 → '+g.title).node.id);
   let ly=y+(height-(list.reduce((s,n)=>s+n.height,0)+38*(list.length-1)))/2;
   for(let j=0;j<list.length;j++){const leaf=list[j];leaf.y=ly;ly+=leaf.height+38;leaves[g.ids[j]]=leaf.id;connections.push(curve(f,category,leaf,colorFor(g.color),side==='left'?'LEFT':'RIGHT',side==='left'?'RIGHT':'LEFT',3,false,false,g.title+' → '+g.ids[j]).node.id);}
   y+=height+140;bottom=Math.max(bottom,ly);
  }
 }
 imageTarget(f,stage===1?'pantheon-exterior':'pantheon-interior',1515,300,630,350);
 imageTarget(f,stage===1?'colosseum-photo':'2023-mechanism',1515,1550,630,stage===1?420:293);
 footer(f,Math.max(2230,bottom+110),3520,'건축물의 잔존은 무손상과 다릅니다. 자가치유는 재료의 하위 단서이며 판테온·콜로세움에서 직접 검증된 성능으로 단정하지 않습니다.');
 fitFrame(f,2600);
 maps.push({stage,frameId:f.id,rootNodeId:root.id,branchNodeIds:branches,leafNodeIds:leaves,leafCount:Object.keys(leaves).length,branchVectorIds:connections,branchCount:connections.length,bounds:{x:f.x,y:f.y,width:f.width,height:f.height}});
 return f;
}
buildTree(1,baseX,CLASS_GROUPS,'로마 건축물은\n어떻게 약 2천 년을\n버텼을까?');
buildTree(2,baseX+4080,ROLE_GROUPS,'구조·재료·계속된 사용과\n보존의 역사를 함께 읽는다');
// P4: typed relation graph, using the same topic family and native curved vectors.
const graph=frame(frameNames[2],baseX+8160,160,4380,3580);
header(graph,'3단계 · 관계맺기','판테온의 구조·쓰임·보존을 연결하고, 콜로세움의 결손·후대 보강을 비교합니다.',4200);
const graphNodes={},graphMeta=[],edgeMeta=[],obstacles=[];
for(const item of CONCEPTS){
 const p=item.position,role=item.kind==='primary_case'?'Center':(['comparison_case','interpretation_limit'].includes(item.kind)?'BranchRight':'LeafRight');
 const value=item.label+'\n['+item.evidence_ids.join(' · ')+']';
 const n=topic(graph,role,value,p.x,p.y,p.width,item.id+' · '+item.label.replace(/\n/g,' '));graphNodes[item.id]=n;
 graphMeta.push({id:item.id,nodeId:n.id,evidenceIds:item.evidence_ids});obstacles.push({x:n.x-16,y:n.y-16,width:n.width+32,height:n.height+32});
}
const gi1=imageTarget(graph,'pantheon-exterior',2210,410,690,420),gi2=imageTarget(graph,'colosseum-photo',3360,1700,700,390);
obstacles.push({x:gi1.x,y:gi1.y,width:gi1.width,height:gi1.height},{x:gi2.x,y:gi2.y,width:gi2.width,height:gi2.height},{x:0,y:0,width:4380,height:270});
const labelBoxes=[];
const intersects=(a,b)=>a.x<b.x+b.width&&a.x+a.width>b.x&&a.y<b.y+b.height&&a.y+a.height>b.y;
for(const r of RELATIONS){
 const line=curve(graph,graphNodes[r.source],graphNodes[r.target],colorFor(r.visual.color),r.visual.start_magnet,r.visual.end_magnet,r.type==='mechanical_load_path'?5:3,r.visual.arrow,r.visual.dashed,r.id+' · '+r.type);
 const label=auto(graph,r.id+' · 관계명',360,0);label.paddingTop=7;label.paddingBottom=7;label.paddingLeft=8;label.paddingRight=8;label.fills=bound(colors.canvas);
 tx(label,r.id+' · 가시 라벨',r.label,344,22,false,'CENTER');
 let chosen=null;
 for(const t of [.5,.42,.58,.33,.67]){if(chosen)break;const p=bez(line.points,t),d=tangent(line.points,t),len=Math.hypot(d.x,d.y)||1;
  for(const distance of [0,55,-55,90,-90]){const box={x:p.x-d.y/len*distance-label.width/2,y:p.y+d.x/len*distance-label.height/2,width:label.width,height:label.height};
   if(box.x>40&&box.y>270&&box.x+box.width<4340&&!obstacles.some(o=>intersects(box,o))&&!labelBoxes.some(o=>intersects(box,o))){chosen=box;break;}
  }
 }
 if(!chosen){const p=bez(line.points,.5);chosen={x:p.x-label.width/2,y:p.y-label.height/2,width:label.width,height:label.height};placementIssues.push({edge:r.id,reason:'Review relation label placement visually.'});}
 label.x=chosen.x;label.y=chosen.y;labelBoxes.push(chosen);
 edgeMeta.push({id:r.id,source:r.source,target:r.target,type:r.type,label:r.label,evidenceIds:r.evidence_ids,vectorId:line.node.id,arrowheadId:line.arrowId,labelId:label.id});
}
footer(graph,3260,4200,'선 위의 관계명을 함께 읽습니다. 부분·사례 비교는 인과관계가 아니며, 제안 기작·역사 해석·적용 한계의 구분을 유지했습니다.');
fitFrame(graph,3580);
maps.push({stage:3,frameId:graph.id,rootNodeId:graphNodes.P.id,conceptCount:CONCEPTS.length,relationCount:RELATIONS.length,nodes:graphMeta,edges:edgeMeta,bounds:{x:graph.x,y:graph.y,width:graph.width,height:graph.height},limitsMetadata:'evidence/architecture-relationships.json',relationSourceSha256:RELATION_SOURCE_SHA256});
// Compact source family below the three working frames, on this same page.
const familyY=Math.max(...maps.map(m=>m.bounds.y+m.bounds.height))+260;
const holder=frame('주제 노드 · 컴포넌트 원본',baseX,familyY,Math.max(3380,componentSet.width+120),500);
const familyHeader=auto(holder,'컴포넌트 안내',holder.width-120,10);familyHeader.x=60;familyHeader.y=36;
tx(familyHeader,'컴포넌트 제목','주제 노드 · 중심 / 좌우 가지 / 좌우 근거',holder.width-120,32,true);
tx(familyHeader,'컴포넌트 사용법','각 인스턴스의 Label 속성으로 문구를 편집할 수 있습니다. 연결선은 개별 편집 가능한 곡선 벡터입니다.',holder.width-120,22);
holder.appendChild(componentSet);componentSet.x=60;componentSet.y=familyHeader.y+familyHeader.height+36;fitFrame(holder,500);
const variantMetadata=styles.map(s=>{const v=variants[s.role];return{role:s.role,componentId:v.component.id,labelNodeId:v.labelNode.id,labelPropertyKey:v.labelNode.componentPropertyReferences.characters,width:v.component.width,height:v.component.height,layoutMode:v.component.layoutMode};});
const definitions=componentSet.componentPropertyDefinitions;
const labelKeys=Object.entries(definitions).filter(([key,value])=>value.type==='TEXT'&&key.split('#')[0]==='Label').map(([key])=>key);
if(styles.length!==5||maps[0].leafCount!==22||maps[1].leafCount!==22||maps[2].conceptCount!==15||maps[2].relationCount!==17)throw new Error('Final count contract failed.');
return{pageId:page.id,createdNodeIds:created,mutatedNodeIds:[],createdVariableIds:variableIds,createdCollectionIds:collectionIds,componentSetId:componentSet.id,componentSourceFrameId:holder.id,variantCount:styles.length,variants:variantMetadata,labelPropertyKeys:labelKeys,instanceCount:instanceIds.length,instanceIds,branchVectorCount:branchVectors.length,arrowheadCount:arrowheads.length,maps,imageTargets,layoutIssues:placementIssues,fonts:['Noto Sans KR Regular','Noto Sans KR Bold'],nativeNodeTypes:['FRAME','COMPONENT_SET','COMPONENT','INSTANCE','TEXT','VECTOR','RECTANGLE'],imageUploadPending:true,branchBehavior:'Editable cubic vectors; moving an instance does not auto-reroute them as a FigJam connector would.'};
