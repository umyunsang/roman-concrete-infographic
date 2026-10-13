const page=await figma.getNodeByIdAsync('19:4');await figma.setCurrentPageAsync(page);
const f=await figma.getNodeByIdAsync('749:78');const dfs=n=>[n,...('children'in n?n.children.flatMap(dfs):[])];
const fonts=new Map();for(const t of dfs(f).filter(n=>n.type==='TEXT'))for(const s of t.getStyledTextSegments(['fontName']))fonts.set(JSON.stringify(s.fontName),s.fontName);
await Promise.all([...fonts.values()].map(v=>figma.loadFontAsync(v)));
const removed=[];const changed=[];const created=[];
const N=async id=>await figma.getNodeByIdAsync(id);
function move(n,x,y){n.x=x;n.y=y;changed.push(n.id);}
function rewrite(n,text,x,y,w,fs,lh){n.characters=text;n.fontSize=fs;n.lineHeight={unit:'PIXELS',value:lh};n.textAutoResize='HEIGHT';n.resize(w,n.height);move(n,x,y);}
f.name='v14 · 반시계 도로 서사 — 배합·운반·시공·콜로세움';
const c2=await N('749:149');move(c2,30,722);move(await N('749:105'),36,728.5);
for(const id of ['751:80','751:81','749:205']){const n=await N(id);if(n){removed.push(...dfs(n).map(n=>n.id));n.remove();}}
const card2=await N('751:79');move(card2,23,716);card2.resize(178,114);
const cardcopy=await N('751:78');move(cardcopy,18,829);cardcopy.resize(152,56);
rewrite(await N('749:197'),'석회를 굽는 가마',90,560,126,10,14);
rewrite(await N('749:198'),'배합부터 콜로세움까지',24,835,143,10,14);
rewrite(await N('749:199'),'돌·벽돌·콘크리트로\n기초·회랑·볼트를 시공',24,853,143,9.5,14);
rewrite(await N('749:200'),'목재 틀 위에 타설',353,1012,112,9.5,13);
rewrite(await N('749:201'),'굳은 회랑 볼트',806,976,120,9.5,13);
rewrite(await N('749:202'),'콘크리트 배합',187,944,102,9.5,13);
rewrite(await N('749:203'),'재료 운반',280,1012,75,9.5,13);
const template=await N('749:200');function label(name,text,x,y,w){const t=template.clone();f.appendChild(t);t.name=name;rewrite(t,text,x,y,w,9.5,13);created.push(t.id);return t;}
label('시공 · 실제 작업자와 벽','돌·모르타르 시공',466,1012,91);
label('시공 · 콜로세움으로 향하는 작업자','중앙으로 운반',563,1012,100);
const svg='<svg xmlns="http://www.w3.org/2000/svg" width="1191" height="1684" viewBox="0 0 1191 1684"><g fill="none" stroke="#784C26" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M265 954 C273 976 280 987 294 998"/><path d="M339 1003 L356 1008"/><path d="M451 1007 L465 1007"/><path d="M538 1005 L556 1005"/><path d="M637 959 L648 941"/><path d="M400 1215 L435 1200"/></g><g fill="#784C26"><path d="M294 998 L286 997 L291 991 Z"/><path d="M356 1008 L348 1010 L350 1002 Z"/><path d="M465 1007 L458 1003 L458 1011 Z"/><path d="M556 1005 L549 1001 L549 1009 Z"/><path d="M648 941 L641 945 L648 949 Z"/></g></svg>';
const arrows=figma.createNodeFromSvg(svg);f.appendChild(arrows);arrows.name='반시계 도로 · 배합→운반→시공→중앙';arrows.x=0;arrows.y=0;created.push(...dfs(arrows).map(n=>n.id));
const bg=await N('749:79');bg.name='Blender v11 · 반시계 도로의 실제 작업자와 시공 장면';changed.push(bg.id);
const texts=dfs(f).filter(n=>n.type==='TEXT');const problems=texts.filter(t=>t.hasMissingFont||t.absoluteTransform[0][2]<f.x||t.absoluteTransform[1][2]<f.y||t.absoluteTransform[0][2]+t.width>f.x+f.width+.01||t.absoluteTransform[1][2]+t.height>f.y+f.height+.01).map(t=>t.id);
if(problems.length)throw new Error(JSON.stringify(problems));
const bodies=[];for(const id of ['749:148','749:154','749:160','749:166','749:172']){const t=await N(id);bodies.push([id,t.width,t.height,t.fontSize,t.lineHeight.value,Math.round(t.height/t.lineHeight.value)]);}
if(JSON.stringify(bodies.map(v=>v[5]))!=='[2,3,2,2,3]')throw new Error('Core reflow');
figma.currentPage.selection=[f];figma.viewport.scrollAndZoomIntoView([f]);
return {frameId:f.id,backgroundId:bg.id,created,changed,removed,nativeTextCount:texts.length,bodies,problems};
