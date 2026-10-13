const page=await figma.getNodeByIdAsync('19:4');await figma.setCurrentPageAsync(page);
const source=await figma.getNodeByIdAsync('743:78');const dfs=n=>[n,...('children'in n?n.children.flatMap(dfs):[])];const old=dfs(source),texts=old.filter(n=>n.type==='TEXT');
if(texts.length!==95)throw new Error('Live source changed');
if(page.children.some(n=>n.name==='v14 · 배합에서 콜로세움 시공까지 — CORE3·4 DETAIL'))throw new Error('v14 already exists');
const sourceSnapshot=()=>JSON.stringify(dfs(source).map(n=>[n.id,n.x,n.y,n.width,n.height,...(n.type==='TEXT'?[n.characters]:[]),...('fills'in n?[n.fills]:[])]));const before=sourceSnapshot();
const fonts=new Map();for(const t of texts)for(const s of t.getStyledTextSegments(['fontName']))fonts.set(JSON.stringify(s.fontName),s.fontName);
fonts.set('newRegular',{family:'Noto Sans KR',style:'Regular'});fonts.set('newBold',{family:'Noto Sans KR',style:'Bold'});await Promise.all([...fonts.values()].map(f=>figma.loadFontAsync(f)));
const f=source.clone();page.appendChild(f);f.name='v14 · 배합에서 콜로세움 시공까지 — CORE3·4 DETAIL';f.x=source.x-1411;f.y=source.y;f.exportSettings=[{format:'PNG',constraint:{type:'SCALE',value:2}}];
const copied=dfs(f);const idMap=Object.fromEntries(old.map((n,i)=>[n.id,copied[i].id]));const N=id=>copied[old.findIndex(n=>n.id===id)];
const created=copied.map(n=>n.id),modified=new Set([f.id]);const removed=[];const edited=new Set();const deletedSourceIds=new Set();
const touch=n=>modified.add(n.id);
const erase=id=>{const n=N(id);for(const o of dfs(n)){removed.push(o.id);if(o.type==='TEXT'){const oldId=Object.keys(idMap).find(k=>idMap[k]===o.id);deletedSourceIds.add(oldId);}}n.remove();};
const bg=N('743:79');bg.name='Blender v10 · 가마 배색·시공 단계·알갱이와 결정 DETAIL';touch(bg);
const c2=N('743:149');c2.x=36;c2.y=510;touch(c2);const num2=N('743:105');num2.x-=33.5;num2.y-=234;touch(num2);
erase('743:173');for(const id of ['743:100','743:101','743:114','743:116','743:117','743:118'])erase(id);
const ink3=N('743:159').fills,ink4=N('743:165').fills,muted=N('743:184').fills;
function setText(id,text,w,fs,lh,fills){const n=N(id);n.characters=text;if(fs)n.fontSize=fs;if(lh)n.lineHeight={unit:'PIXELS',value:lh};if(fills)n.fills=fills;n.textAutoResize='HEIGHT';n.resize(w,n.height);edited.add(id);touch(n);return n;}
const d3=N('743:176');d3.name='DETAIL CORE3 · 알갱이 속 칼슘';d3.x=270;d3.y=1277;d3.resize(155,d3.height);touch(d3);
setText('743:177','확대 · 알갱이 속 칼슘',155,12,15,ink3);
setText('743:178','굳은 모재 속 흰 석회 알갱이.\n칼슘이 풍부하고 물에 녹아 나온다.',155,9.5,14,muted);
const d4=N('743:179');d4.name='DETAIL CORE4 · 물에서 새 결정으로';d4.x=631;d4.y=1281;d4.resize(190,d4.height);touch(d4);
setText('743:180','확대 · 물에서 새 결정으로',190,12,15,ink4);
setText('743:181','칼슘 성분이 물에 녹아 틈으로 이동.\n탄산칼슘 결정이 작은 금을 메운다.',190,10,14,muted);
const guard=N('743:182');guard.name='CORE4 · 근거가 확인된 범위';erase('743:183');guard.x=631;guard.y=1334;touch(guard);setText('743:184',N('743:184').characters,190,9.5,13,muted);
const pin=setText('743:108','석회 알갱이',84,9.5,13,ink3);pin.x=300;pin.y=1151;
setText('743:189','흰 알갱이가 남은 콘크리트',184,10,14,muted);
const mountain=N('743:103');mountain.rotation=0;mountain.x=445;mountain.y=250;touch(mountain);
const rgb=h=>({r:parseInt(h.slice(1,3),16)/255,g:parseInt(h.slice(3,5),16)/255,b:parseInt(h.slice(5,7),16)/255});
function label(name,text,x,y,w,fs=10,bold=false,fill=muted){const t=figma.createText();f.appendChild(t);created.push(t.id);t.name=name;t.fontName={family:'Noto Sans KR',style:bold?'Bold':'Regular'};t.fontSize=fs;t.lineHeight={unit:'PIXELS',value:fs+4};t.characters=text;t.textAutoResize='HEIGHT';t.resize(w,t.height);t.x=x;t.y=y;t.fills=fill;return t;}
label('가마 · 기존 모형의 부위별 재질','석회를 굽는 가마',40,341,126,10,true);
label('시공 · 읽는 순서','배합에서 콜로세움 시공으로',282,406,233,12,true,ink3);
label('시공 · 재료와 구조','돌·벽돌·콘크리트를 함께 사용.\n기초와 내부 회랑·볼트를 만든다.',282,425,230,10,false,muted);
label('시공 · 목재 틀','목재 틀 위에 시공',292,454,124,10,true,ink3);
label('시공 · 굳은 볼트','굳은 회랑 볼트',422,454,93,10,true,ink3);
label('시공 · 배합과 운반','배합·운반',61,749,122,10,true,ink3);
label('시공 · 운반 연결','운반',213,643,36,9,false,muted);
label('CORE4 · 결정 단면','틈 속 탄산칼슘 결정',776,1382,130,9.5,false,ink4);
// Native vector connections keep the map's terrain and camera unchanged.
const svg='<svg xmlns="http://www.w3.org/2000/svg" width="1191" height="1684" viewBox="0 0 1191 1684"><g fill="none" stroke="#784C26" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M185 686 L244 667 L281 592 L302 560"/><path d="M409 517 L420 517"/><path d="M478 564 L531 605"/><path d="M400 1215 L435 1200"/></g><g fill="#784C26"><path d="M302 560 L295 564 L301 568 Z"/><path d="M420 517 L414 513 L414 521 Z"/><path d="M531 605 L523 603 L528 597 Z"/></g></svg>';
const arrows=figma.createNodeFromSvg(svg);f.appendChild(arrows);arrows.name='배합→시공→콜로세움 / CORE3·4 확대 연결';arrows.x=0;arrows.y=0;created.push(...dfs(arrows).map(n=>n.id));
const bodyMeasurements=[];for(const id of ['743:148','743:154','743:160','743:166','743:172']){const t=N(id);bodyMeasurements.push([t.id,t.width,t.height,t.fontSize,t.lineHeight.value,Math.round(t.height/t.lineHeight.value)]);}
const problems=[];for(const t of dfs(f).filter(n=>n.type==='TEXT')){const x=t.absoluteTransform[0][2]-f.x,y=t.absoluteTransform[1][2]-f.y;if(t.hasMissingFont||x<0||y<0||x+t.width>f.width+.01||y+t.height>f.height+.01)problems.push([t.id,'font/bounds']);}
for(const t of texts){if(deletedSourceIds.has(t.id)||edited.has(t.id)||['743:105','743:152','743:153','743:154','743:103','743:184'].includes(t.id))continue;const n=N(t.id);if(n.characters!==t.characters||n.fontSize!==t.fontSize||n.width!==t.width||n.height!==t.height)problems.push([n.id,'unintended text change']);}
if(sourceSnapshot()!==before||problems.length)throw new Error('v14 validation '+JSON.stringify(problems));
for(const id of ['743:178','743:181','743:184']){const t=N(id);if(Math.round(t.height/t.lineHeight.value)!==2)throw new Error('Detail wrapping '+t.id);}
if(JSON.stringify(bodyMeasurements.map(r=>r[5]))!=='[2,3,2,2,3]')throw new Error('Core body reflow');
figma.currentPage.selection=[f];figma.viewport.scrollAndZoomIntoView([f]);
return {frameId:f.id,backgroundId:bg.id,pageId:page.id,createdNodeIds:created.filter(id=>!removed.includes(id)),modifiedNodeIds:[...modified],removedNodeIds:removed,idMap,nativeTextCount:dfs(f).filter(n=>n.type==='TEXT').length,bodyMeasurements,editedSourceTextIds:[...edited],deletedSourceTextIds:[...deletedSourceIds],sourceV13Unchanged:true,problems};
