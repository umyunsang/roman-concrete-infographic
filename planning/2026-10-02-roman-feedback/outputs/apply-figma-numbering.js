const page=await figma.getNodeByIdAsync('19:4');
await figma.setCurrentPageAsync(page);
const frame=await figma.getNodeByIdAsync('179:78');
if(!frame||frame.parent.id!==page.id) throw new Error('W3/page mismatch');
const changes=[["211:1874","① 원리 · 왜 굳고,\n더 단단해지나","재료 원리 · 해수 속\n새 결정"],["211:1880","② 원리 · 왜 빨리 굳나","제작 원리 · 열과 석회"],["211:1886","③ 원리 · 잘라 본 벽 —\n위는 가볍게,\n아래는 두껍게","구조 원리 · 벽과 기초\n위는 가볍게,\n아래는 두껍게"],["211:1892","④ 원리 · 금이\n메워지는 순서","균열 원리 · 금이\n메워지는 순서"],["227:26096","확인","결정 관찰"],["227:26105","확인","배합 흔적"],["227:26116","확인","석회·결정 관찰"],["227:26125","확인","균열 충전 실험"],["204:8772","재료①·만들기②·짓기③·\n고치기④가 함께 맞물려\n2천 년을 버텼다","재료·만들기·짓기·\n고치기가 함께 맞물려\n2천 년을 버텼다"],["231:21383","굵은 점선 ① 출발 → ⑤ = 재료가\n콜로세움이 되기까지의 길","굵은 점선 = 코어를 읽는 순서\n재료에서 보수까지 이어지는 길"],["231:21386","검은 원 번호 옆의 굵은 기울인 글 =\n그 단계의 설명","검은 원 번호 · +30° 글 =\n코어의 핵심 설명"],["231:21389","같은 번호 배지의 확대 모형 = 원리","−30° 글 · 무번호 확대 모형 = 원리"],["231:21395","점선 핀과 번호 확인 = 증거가 나온 곳","점선 핀 · 지명·관찰명 = 확인 근거"],["397:79","3","절개 단면"],["397:81","4","버팀벽 보강"]];
const prefixRemovals=[["200:103","전제 1 · 로마 콘크리트란?",3,5],["200:107","전제 2 · 어떻게 알았나",3,5],["211:1926","1 금이 흰\n석회 알갱이를\n지나감",0,2],["211:1939","2 스민 물이\n칼슘을 녹임",0,2],["211:1949","3 다시 굳어\n금을 메움",0,2]];
const hideIds=["209:1861","208:122","208:145","208:156","227:26094","227:26103","227:26112","227:26114","227:26123","228:87","228:95","228:100","228:108","231:21387","231:21390"];
const renames=[["211:1873","DETAIL · 재료 원리 (해수 속 새 결정)"],["211:1879","DETAIL · 제작 원리 (열과 석회)"],["211:1885","DETAIL · 구조 원리 (벽과 기초)"],["211:1891","DETAIL · 균열 원리 (금이 메워지는 순서)"],["209:1834","DETAIL · 재료 확대 모형 (바닷물 속 새 결정)"],["208:105","DETAIL · 제작 확대 모형 (흰 석회 알갱이)"],["208:124","DETAIL · 구조 확대 모형 (벽과 기초)"],["211:1918","DETAIL · 균열 과정 모형"],["397:78","부위 이름 · 절개 단면"],["397:80","행위 이름 · 버팀벽 보강"]];
const ids=[...new Set([...changes.map(x=>x[0]),...prefixRemovals.map(x=>x[0]),...hideIds,...renames.map(x=>x[0])])];
const nodes=await Promise.all(ids.map(id=>figma.getNodeByIdAsync(id)));
const byId=new Map(nodes.map(n=>[n.id,n]));
for(const n of nodes){ let a=n; while(a&&a!==frame)a=a.parent; if(!a) throw new Error('Out-of-scope node '+n.id); }
for(const [id,old,next] of changes){const n=byId.get(id);if(n.type!=='TEXT'||(n.characters!==old&&n.characters!==next))throw new Error('Text changed unexpectedly: '+id);}
for(const [id,old,start,end] of prefixRemovals){const n=byId.get(id);const next=old.slice(0,start)+old.slice(end);if(n.type!=='TEXT'||(n.characters!==old&&n.characters!==next))throw new Error('Text changed unexpectedly: '+id);}
const all=frame.findAll(()=>true);
const textNodes=frame.findAllWithCriteria({types:['TEXT']});
const fonts=new Map(); for(const t of textNodes) for(const s of t.getStyledTextSegments(['fontName']))fonts.set(JSON.stringify(s.fontName),s.fontName);
await Promise.all([...fonts.values()].map(f=>figma.loadFontAsync(f)));
function state(n){const v={id:n.id,p:n.parent.id,x:n.x,y:n.y,w:n.width,h:n.height,r:n.rotation,visible:n.visible,transform:n.absoluteTransform}; if('fills'in n)v.fills=n.fills; if('strokes'in n)v.strokes=n.strokes; if(n.type==='VECTOR')v.paths=n.vectorPaths; return v;}
const primitives=all.filter(n=>['VECTOR','RECTANGLE','ELLIPSE','LINE','POLYGON','STAR','BOOLEAN_OPERATION'].includes(n.type));
const primitiveBefore=primitives.map(state);
const otherBefore=page.children.filter(n=>n.id!==frame.id).map(n=>({id:n.id,name:n.name,x:n.x,y:n.y,w:n.width,h:n.height}));
const coreIds=['204:8726','204:8736','204:8748','204:8758','204:8775'];
const detailIds=['211:1873','211:1879','211:1885','211:1891'];
const roleNodes=await Promise.all([...coreIds,...detailIds].map(id=>figma.getNodeByIdAsync(id)));
const rolesBefore=roleNodes.map(n=>({id:n.id,x:n.x,y:n.y,r:n.rotation}));
const beforeTargets=nodes.map(n=>({id:n.id,name:n.name,visible:n.visible,x:n.x,y:n.y,w:n.width,h:n.height,...(n.type==='TEXT'?{text:n.characters}: {})}));
const mutated=new Set();
for(const [id,old,next] of changes){const n=byId.get(id);if(n.characters!==next){n.characters=next;mutated.add(id);}}
for(const [id,old,start,end] of prefixRemovals){const n=byId.get(id);if(n.characters===old){n.deleteCharacters(start,end);mutated.add(id);}}
for(const id of hideIds){const n=byId.get(id);if(n.visible){n.visible=false;mutated.add(id);}}
for(const [id,name]of renames){const n=byId.get(id);if(n.name!==name){n.name=name;mutated.add(id);}}
for(const id of ['397:78','397:80']){
const n=byId.get(id);n.fills=[];n.strokes=[];n.primaryAxisAlignItems='MIN';n.counterAxisAlignItems='CENTER';n.primaryAxisSizingMode='AUTO';n.counterAxisSizingMode='AUTO';mutated.add(id);
const t=n.children.find(c=>c.type==='TEXT');t.fontSize=9;t.fills=[{type:'SOLID',color:{r:0.13,g:0.13,b:0.13}}];mutated.add(t.id);
}
const geomSame=JSON.stringify(primitiveBefore)===JSON.stringify(primitives.map(state));
const roles=roleNodes.map(n=>({id:n.id,x:n.x,y:n.y,r:n.rotation,w:n.width,h:n.height}));
const anchorsSame=roles.every((n,i)=>n.x===rolesBefore[i].x&&n.y===rolesBefore[i].y&&n.r===rolesBefore[i].r);
const outsideSame=JSON.stringify(otherBefore)===JSON.stringify(page.children.filter(n=>n.id!==frame.id).map(n=>({id:n.id,name:n.name,x:n.x,y:n.y,w:n.width,h:n.height})));
const visible=n=>{let a=n;while(a&&a.type!=='PAGE'){if(a.visible===false)return false;a=a.parent;}return true;};
const allText=textNodes.filter(visible).map(n=>({id:n.id,t:n.characters}));
const sequenceLabels=allText.filter(n=>/^[1-5]$/.test(n.t));
const visibleReferenceLabels=allText.filter(n=>/[①②③④⑤]/.test(n.t));
const targets=changes.map(([id])=>{const n=byId.get(id);return{id,text:n.characters,w:n.width,h:n.height,pw:n.parent.width,ph:n.parent.height};});
const hiddenOk=hideIds.every(id=>!byId.get(id).visible);
const coreAngles=roles.slice(0,5).every(n=>Math.abs(n.r-30)<0.001);
const detailAngles=roles.slice(5).every(n=>Math.abs(n.r+30)<0.001);
return{pageId:page.id,frameId:frame.id,mutatedNodeIds:[...mutated],createdNodeIds:[],removedNodeIds:[],beforeTargets,checks:{geomSame,primitiveCount:primitives.length,anchorsSame,outsideSame,hiddenOk,coreAngles,detailAngles,hiddenBadgeCount:hideIds.length},roles,targets,sequenceLabels,visibleReferenceLabels,prefixTexts:prefixRemovals.map(([id])=>({id,text:byId.get(id).characters})),allVisibleText:allText};

