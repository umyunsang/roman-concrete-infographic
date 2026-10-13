const page=await figma.getNodeByIdAsync('19:4');await figma.setCurrentPageAsync(page);
const W=420*72/25.4,H=594*72/25.4,created=[],images=[],texts=[];
const F={r:{family:'Noto Sans KR',style:'Regular'},b:{family:'Noto Sans KR',style:'Bold'},s:{family:'Noto Serif KR',style:'Bold'},en:{family:'Inter',style:'Regular'}};
await Promise.all(Object.values(F).map(f=>figma.loadFontAsync(f)));
const C={paper:'#FAF4E5',ink:'#393D34',muted:'#63665A',rust:'#A5653F',teal:'#45877F',ochre:'#B59C62'};
const rgb=h=>({r:parseInt(h.slice(1,3),16)/255,g:parseInt(h.slice(3,5),16)/255,b:parseInt(h.slice(5,7),16)/255});
const fill=h=>[{type:'SOLID',color:rgb(h)}],keep=n=>(created.push(n.id),n);
if(page.children.some(n=>n.name==='A2 · 건축물을 따라 읽는 자유 구도'))throw new Error('Free composition already exists; inspect before rerun');
const root=keep(figma.createFrame());root.name='A2 · 건축물을 따라 읽는 자유 구도';root.resize(W,H);root.x=100;root.y=100;root.fills=fill(C.paper);root.clipsContent=true;root.exportSettings=[{format:'PDF'}];
function tx(parent,s,x,y,w,size=16,face='r',color=C.ink,line=1.5,name=s){const n=keep(figma.createText());parent.appendChild(n);n.name=name;n.fontName=F[face];n.fontSize=size;n.lineHeight={unit:'PERCENT',value:line*100};n.characters=s;n.textAutoResize='HEIGHT';n.resize(w,Math.max(20,n.height));n.x=x;n.y=y;n.fills=fill(color);texts.push(n);return n;}
function vpath(parent,name,d,color,width=1.4,dash=[]){const n=keep(figma.createVector());parent.appendChild(n);n.name=name;n.vectorPaths=[{windingRule:'NONZERO',data:d}];n.fills=[];n.strokes=fill(color);n.strokeWeight=width;n.dashPattern=dash;return n;}
function dot(x,y,r=3,color=C.teal){const n=keep(figma.createEllipse());root.appendChild(n);n.resize(r*2,r*2);n.x=x-r;n.y=y-r;n.fills=fill(color);return n;}
function callout(name,title,body,x,y,w,accent=C.rust){const n=keep(figma.createAutoLayout('VERTICAL',{name,itemSpacing:10}));root.appendChild(n);n.resize(w,50);n.primaryAxisSizingMode='AUTO';n.counterAxisSizingMode='FIXED';n.fills=[];n.x=x;n.y=y;n.clipsContent=false;tx(n,title,0,0,w,22,'b',accent,1.4,title);tx(n,body,0,0,w,14.5,'r',C.ink,1.6,body);return n;}
function image(key,x,y,w,h,ellipse=false){const n=keep(ellipse?figma.createEllipse():figma.createRectangle());root.appendChild(n);n.name='그림 · '+key;n.resize(w,h);n.x=x;n.y=y;n.fills=fill(C.paper);images.push({nodeId:n.id,key,scaleMode:ellipse?'FILL':'FIT'});return n;}
// The illustration establishes the field; the native labels remain separately editable.
const hero=image('pantheon-cutaway',245,247,895,1267);hero.blendMode='MULTIPLY';
tx(root,'FOREIGN ARCHITECTURE  /  ROME',64,45,720,12,'en',C.rust,1.2,'분야 표제');
tx(root,'로마 건축물은 어떻게\n약 2천 년을 버텼을까?',62,81,1015,45,'s',C.ink,1.28,'중심 질문');
tx(root,'판테온의 돔에서 시작해,\n벽체와 재료, 이어진 쓰임과 보존의 흔적을 따라간다.',66,218,635,18,'r',C.muted,1.55,'독해의 출발');
callout('공간의 규모','하나의 큰 공간','내부 높이와 돔 지름은 약 43m.\n원통형 몸체 위에 반구형 돔이 놓인다.',858,305,265,C.rust);
vpath(root,'공간 설명선','M 855 413 C 825 416 819 437 811 469',C.rust,1.2);dot(811,469,3,C.rust);
callout('구조의 작동','무게를 나누는 구조','두꺼운 벽체와 여덟 큰 지지부가\n돔의 무게를 받는다.\n큰 빈 공간을 지키는 구조의 연결.',66,458,275,C.teal);
vpath(root,'구조 설명선','M 343 544 C 428 540 434 665 640 769',C.teal,1.5);dot(640,769);
callout('쓰임과 보존','쓰임이 이어진 건축','609년 성당으로 전환된 뒤\n오늘도 예배가 이어진다.\n용도의 지속은 보존에 기여한 한 요인이다.',65,729,257,C.rust);
vpath(root,'사용 설명선','M 324 817 C 386 815 392 893 558 1000',C.rust,1.2);dot(558,1000,3,C.rust);
// A small material magnifier, clearly presented as evidence from other sites.
const disc=keep(figma.createEllipse());root.appendChild(disc);disc.name='재료 확대의 바탕';disc.resize(180,180);disc.x=976;disc.y=1172;disc.fills=fill('#F5EBD3');disc.strokes=fill(C.ochre);disc.strokeWeight=1.4;
const diagram=figma.createNodeFromSvg('<svg xmlns="http://www.w3.org/2000/svg" width="150" height="150"><defs><clipPath id="crop"><circle cx="75" cy="75" r="73"/></clipPath></defs><g clip-path="url(#crop)"><rect width="150" height="150" fill="#DCCFB7"/><path d="M2 14L36 9L49 41L20 60L0 40 M108 81L145 69L158 119L121 144L98 119" fill="#96998E"/><ellipse cx="79" cy="71" rx="28" ry="22" fill="#FAF4E4" stroke="#B6A788"/><path d="M73 -3L87 31L65 58L91 81L76 111L90 155" fill="none" stroke="#FCF7E9" stroke-width="10"/><path d="M73 -3L87 31L65 58L91 81" fill="none" stroke="#45877F" stroke-width="3"/><path d="M91 81L76 111L90 155" fill="none" stroke="#B99141" stroke-width="6"/><circle cx="78" cy="77" r="4" fill="#B99141"/><circle cx="87" cy="94" r="4" fill="#B99141"/></g></svg>');root.appendChild(diagram);diagram.name='균열 충전 개념 확대';diagram.x=991;diagram.y=1187;created.push(diagram.id,...diagram.findAll().map(n=>n.id));
vpath(root,'재료 확대 연결','M 1010 1090 C 1030 1120 1043 1146 1056 1172',C.ochre,1.1,[5,5]);dot(1010,1090,3,C.ochre);
callout('재료의 단서','재료 속 작은 단서','물과 칼슘의 반응이 작은 균열을\n메울 가능성을 보여 준 연구가 있다.',809,1374,333,C.teal);
tx(root,'다른 로마 유적·현대 시편의 연구.\n판테온에서 직접 검증된 성능은 아니다.',811,1498,326,10.5,'r',C.muted,1.55,'재료 연구의 적용 범위');
// Comparison floats at the edge instead of becoming a second equal-size panel.
tx(root,'다른 모습으로 남다',66,1288,385,21,'b',C.rust,1.4,'비교 표제');
const compare=image('colosseum-photo',66,1331,309,196,true);
tx(root,'콜로세움은 일부 회랑을 잃었고,\n19세기의 버팀 구조와 이후 보존을 거쳤다.',66,1542,402,13,'r',C.ink,1.5,'콜로세움 비교');
tx(root,'Kasa Fue · CC BY-SA 4.0 · 타원형 표시',69,1514,385,9,'r',C.muted,1.3,'사진 출처');
// A meandering preservation trace; positions do not encode chronological distance.
vpath(root,'보존의 흔적','M 471 1289 C 437 1356 427 1397 492 1417 C 562 1436 674 1456 719 1512',C.ochre,1.3,[4,5]);
dot(486,1414,3,C.ochre);dot(715,1508,3,C.ochre);
tx(root,'1872–1873',477,1430,250,16,'b',C.rust,1.25,'복원 시점');tx(root,'대리석 바닥의 전면 복원',477,1459,270,12,'r',C.muted,1.3,'복원 내용');
tx(root,'2023',553,1532,175,16,'b',C.rust,1.25,'현대 보존 시점');tx(root,'바닥 보존·복원 착수',553,1561,225,12,'r',C.muted,1.3,'현대 보존 내용');
tx(root,'건축물의 잔존은 무손상·무보수를 뜻하지 않는다.',65,1610,1060,13,'b',C.ink,1.35,'핵심 해석');
tx(root,'근거: 로마시 Turismo Roma · 판테온 운영기관 · 문화부 바닥 복원 보고(2024) · 콜로세움 고고학공원 · Seymour 외(2023), Vaserman 외(2025)',66,1640,1070,8.5,'r',C.muted,1.4,'정보 출처');
tx(root,'개념 절개도·확대도 / 실측 복원·응력 해석이 아님 · 시간선 간격은 실제 기간과 비례하지 않음',66,1660,1070,8.5,'r',C.muted,1.3,'표현 범위');
const labels=texts.map(n=>({id:n.id,name:n.name,x:n.x,y:n.y,width:n.width,height:n.height}));
return {createdNodeIds:created,frameId:root.id,pageId:page.id,imageTargets:images,dimensions:{width:W,height:H,width_mm:420,height_mm:594},textNodes:labels,referencePrinciples:['architectural cutaway as composition','local labels instead of rectangular sections','light preservation trace','small comparison at the edge'],originalIllustration:'outputs/pantheon-cutaway-concept.png'};
