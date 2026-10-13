const page=await figma.getNodeByIdAsync('19:4');await figma.setCurrentPageAsync(page);
const source=await figma.getNodeByIdAsync('749:78');const dfs=n=>[n,...('children'in n?n.children.flatMap(dfs):[])];const before=dfs(source);
if(before.filter(n=>n.type==='TEXT').length!==96)throw new Error('v14 text count changed');
const fonts=new Map();for(const t of before.filter(n=>n.type==='TEXT'))for(const s of t.getStyledTextSegments(['fontName']))fonts.set(JSON.stringify(s.fontName),s.fontName);await Promise.all([...fonts.values()].map(x=>figma.loadFontAsync(x)));
if(page.children.some(n=>n.name==='v15 · 로마 마을 — 건축·생활·실제 시공'))throw new Error('v15 already created');
const f=source.clone();page.appendChild(f);f.name='v15 · 로마 마을 — 건축·생활·실제 시공';f.x=source.x-1411;f.y=source.y;f.exportSettings=[{format:'PNG',constraint:{type:'SCALE',value:2}}];
const cloned=dfs(f);const byId=new Map(before.map((n,i)=>[n.id,cloned[i]]));const idMap=Object.fromEntries(before.map((n,i)=>[n.id,cloned[i].id]));const created=cloned.map(n=>n.id);const removed=[];const changed=[];const N=id=>byId.get(id);
function erase(id){const n=N(id);if(n){removed.push(...dfs(n).map(x=>x.id));n.remove();}}
function move(n,x,y){n.x=x;n.y=y;changed.push(n.id);}
function text(id,value,x,y,w,fs=9.5,lh=13.5){const n=N(id);n.characters=value;n.fontSize=fs;n.lineHeight={unit:'PIXELS',value:lh};n.textAutoResize='HEIGHT';n.resize(w,n.height);move(n,x,y);return n;}
N('749:79').name='Blender v12 · 실제 주택·장터·사람·콜로세움 비계';
move(N('749:155'),370,1032);move(N('749:110'),376,1038.5);
for(const id of ['751:78','755:80','749:108','749:189','749:185','749:204','749:203','749:177','749:180','755:79','749:195','749:196'])erase(id);
const d3=N('749:176');move(d3,320,1250);d3.resize(170,27);text('749:178','굳은 반죽 속 흰 석회 알갱이.\n칼슘이 풍부하고 물에 녹아 나온다.',0,0,170);
const d4=N('749:179');move(d4,673,1290);d4.resize(190,27);text('749:181','물에 녹은 칼슘이 틈으로 이동.\n탄산칼슘 결정이 작은 금을 메운다.',0,0,190);
move(N('749:182'),673,1323);
text('749:197','석회 가마',54,845,110,9.5,13.5);
text('749:198','주거와 골목',552,1242,120,9.5,13.5);
text('749:199','돌·벽돌·콘크리트를 함께 써\n기초와 회랑의 볼트를 만든다.',842,924,192,9.5,14);
text('749:200','콜로세움 회랑 시공',842,905,170,10,14);
text('749:201','장터와 사람들',813,744,125,9.5,13.5);
text('749:202','콘크리트 작업장',54,948,136,9.5,13.5);
text('755:78','건축·생활 장면 재구성',1010,985,160,9,13);
text('749:194','오늘의 재현 실험',995,686,160,11,15);
text('749:128','로마 방파제',385,1587,145,10,14);
const svg='<svg xmlns="http://www.w3.org/2000/svg" width="1191" height="1684" viewBox="0 0 1191 1684"><g fill="none" stroke="#86775F" stroke-width="1" stroke-linecap="round"><path d="M452 1244 L454 1213"/><path d="M823 1285 L849 1258"/><path d="M836 916 L772 883"/></g></svg>';
const leaders=figma.createNodeFromSvg(svg);f.appendChild(leaders);leaders.name='실제 벽·시공 부위에 붙는 짧은 정보 연결';leaders.x=0;leaders.y=0;created.push(...dfs(leaders).map(n=>n.id));
const bodies=[];for(const id of ['749:148','749:154','749:160','749:166','749:172']){const t=N(id);bodies.push([t.id,t.width,t.height,t.fontSize,t.lineHeight.value,Math.round(t.height/t.lineHeight.value)]);}
if(JSON.stringify(bodies.map(b=>b[5]))!=='[2,3,2,2,3]')throw new Error('CORE wrapping changed');
for(const id of ['749:178','749:181','749:184']){const t=N(id);if(Math.round(t.height/t.lineHeight.value)!==2)throw new Error('detail lines');}
const texts=dfs(f).filter(n=>n.type==='TEXT');const problems=[];for(const t of texts){const x=t.absoluteTransform[0][2]-f.x,y=t.absoluteTransform[1][2]-f.y;if(t.hasMissingFont||x<0||y<0||x+t.width>1191+.01||y+t.height>1684+.01)problems.push(t.id);}
if(problems.length)throw new Error(JSON.stringify(problems));figma.currentPage.selection=[f];figma.viewport.scrollAndZoomIntoView([f]);
return {frameId:f.id,backgroundId:N('749:79').id,pageId:page.id,createdNodeIds:created.filter(x=>!removed.includes(x)),removedNodeIds:removed,changedNodeIds:changed,idMap,nativeTextCount:texts.length,bodies,problems};
