// Native FigJam mindmaps: editable TEXT nodes joined by attached CURVED CONNECTOR nodes.
// Native spatial tree, with diagram images associated with its branches.
const created = [], maps = [], imageTargets = [];
const regular = {family:'Noto Sans KR',style:'Regular'};
const bold = {family:'Noto Sans KR',style:'Bold'};
await Promise.all([figma.loadFontAsync(regular),figma.loadFontAsync(bold),figma.loadFontAsync({family:'Inter',style:'Medium'})]);
const ink='#1E1E1E';
const rgb=h=>({r:parseInt(h.slice(1,3),16)/255,g:parseInt(h.slice(3,5),16)/255,b:parseInt(h.slice(5,7),16)/255});
const paint=h=>[{type:'SOLID',color:rgb(h)}];
function keep(n){created.push(n.id);return n;}
function text(parent,s,x,y,w=650,size=26,strong=false,name=s){
 const n=keep(figma.createText());parent.appendChild(n);n.fontName=strong?bold:regular;n.fontSize=size;n.lineHeight={unit:'PERCENT',value:145};n.characters=s;n.textAutoResize='HEIGHT';n.resize(w,Math.max(40,n.height));n.x=x;n.y=y;n.fills=paint(ink);n.name=name;return n;
}
function link(parent,a,b,color,left=false,weight=3){
 const n=keep(figma.createConnector());parent.appendChild(n);n.name='가지 · '+a.name+' → '+b.name;
 n.connectorLineType='CURVED';n.connectorStart={endpointNodeId:a.id,magnet:left?'LEFT':'RIGHT'};n.connectorEnd={endpointNodeId:b.id,magnet:left?'RIGHT':'LEFT'};
 n.connectorStartStrokeCap='NONE';n.connectorEndStrokeCap='NONE';n.strokes=paint(color);n.strokeWeight=weight;return n;
}
const labels={
 'MAT-01':'골재 + 결합재 모르타르',
 'MAT-02':'석회석 가열 → 생석회',
 'MAT-03':'생석회·포졸란을 건식 혼합',
 'MAT-04':'물 첨가 → 발열 반응',
 'MAT-05':'포졸란 반응 → 결합 물질 생성',
 'MAT-06':'석회 덩어리의 주성분: 방해석',
 'MAT-07':'프리베르눔 성벽 시료 10개',
 'MAT-08':'폼페이 원료 더미·벽체 분석',
 'MAT-09':'보수·마감에는 다른 석회 사용 단서',
 'MAT-10':'작은 균열 → 물의 유입',
 'MAT-11':'석회 덩어리 용해 → 칼슘 공급',
 'MAT-12':'칼슘이 풍부한 용액의 이동',
 'MAT-13':'탄산칼슘 석출 → 틈 메움 가능',
 'MAT-14':'추가 포졸란 반응도 가능',
 'MAT-15':'로마 재료에서 착안한 현대 모르타르',
 'MAT-16':'시험 틈: 0.5 ± 0.1 mm',
 'MAT-17':'시험 준비: 28일 수중 양생',
 'MAT-18':'시험 준비: 2개월 습윤·건조',
 'MAT-19':'30일 범위에서 유량 관찰',
 'MAT-20':'조건별 1–3주에 유량 거의 0',
 'MAT-21':'새 충전물: 방해석 확인',
 'MAT-22':'틈 메움 ≠ 원래 강도 회복의 입증',
 'MAT-23':'모든 로마 콘크리트로 일반화 불가',
 'MAT-24':'고대인의 자가복원 설계 의도 미확인'
};
function leaf(parent,id,x,y,side,color){
 const n=text(parent,labels[id]+'  ['+id.slice(4)+']',x,y,670,26,false,id+' · '+labels[id]);
 n.textAlignHorizontal=side==='left'?'RIGHT':'LEFT';return n;
}
function imageTarget(parent,key,x,y,w,h,caption){
 const n=keep(figma.createShapeWithText());parent.appendChild(n);n.shapeType='SQUARE';n.text.fontName=regular;n.text.characters='';n.resize(w,h);n.x=x;n.y=y;n.name='도판 · '+key;n.fills=paint('#FFFFFF');n.strokes=[];
 text(parent,caption,x,y+h+14,w,18,false,'출처 · '+key);
 imageTargets.push({nodeId:n.id,key,scaleMode:'FIT'});return n;
}
function createMap(name,title,subtitle,x,groups,centerText,ordered){
 if(figma.currentPage.children.some(n=>n.name===name))throw new Error('Existing mindmap: inspect before retrying');
 const section=keep(figma.createSection());section.name=name;section.resize(3600,2650);section.x=x;section.y=120;section.fills=paint('#FFFFFF');
 text(section,title,90,65,3100,52,true,'마인드맵 단계');
 text(section,subtitle,90,158,3100,25,false,'단계 설명');
 const root=text(section,centerText,1460,1040,670,52,true,'중심 주제');root.textAlignHorizontal='CENTER';
 const roots={},leafIds={},connectors=[];let maxBottom=1800;
 for(const side of ['left','right']){
  const these=groups.filter(g=>g.side===side);const prepared=[];
  for(const g of these){
   const ls=g.ids.map(id=>leaf(section,id,side==='left'?90:2810,0,side,g.color));
   const natural=ls.reduce((s,n)=>s+n.height,0)+38*(ls.length-1);
   prepared.push({g,ls,height:Math.max(170,natural)});
  }
  const total=prepared.reduce((s,z)=>s+z.height,0)+140*(prepared.length-1);let y=330+(1600-total)/2;
  for(const {g,ls,height} of prepared){
   const mid=y+height/2;const category=text(section,g.title,side==='left'?960:2330,mid-28,310,36,true,'분류 가지 · '+g.title);category.textAlignHorizontal=side==='left'?'RIGHT':'LEFT';roots[g.key]=category.id;
   connectors.push(link(section,root,category,g.color,side==='left',6).id);
   let ly=y+(height-(ls.reduce((s,n)=>s+n.height,0)+38*(ls.length-1)))/2;
   for(let j=0;j<ls.length;j++){const n=ls[j];n.y=ly;ly+=n.height+38;leafIds[g.ids[j]]=n.id;connectors.push(link(section,category,n,g.color,side==='left',3).id);}
   y+=height+140;maxBottom=Math.max(maxBottom,ly);
  }
 }
 const imageA=imageTarget(section,ordered?'2023-mechanism':'2025-production',1480,300,630,ordered?293:182,ordered?'제안된 자가복원 기작 · Seymour 외(2023), Fig.6\nCC BY-NC 4.0':'폼페이 공정 재구성 · Vaserman 외(2025), Fig.7\nCC BY-NC-ND 4.0 · 원형 유지');
 const imageB=imageTarget(section,'2023-experiment',1480,1370,630,382,'현대 모르타르 시험 · Seymour 외(2023), Fig.5\nCC BY-NC 4.0 · 시험 조건과 함께 해석');
 const noteY=Math.max(2110,maxBottom+100);
 text(section,'핵심 질문  로마 콘크리트는 어떻게 작은 균열을 스스로 메우며, 오래 버티는 데 어떻게 기여할까?',90,noteY,3350,24,true);
 text(section,'[01–24]는 근거 식별자입니다.  S2023  doi.org/10.1126/sciadv.add1602   ·   S2025  doi.org/10.1038/s41467-025-66634-7',90,noteY+62,3350,20);
 text(section,'색은 가지를 구분합니다. 제안된 반응·현대 시편 실험·고대 현장 관찰을 구별하며, 건물 전체의 영구 안전을 뜻하지 않습니다.',90,noteY+112,3350,20);
 section.resize(3600,noteY+200);
 maps.push({stage:ordered?2:1,sectionId:section.id,rootNodeId:root.id,branchNodeIds:roots,leafNodeIds:leafIds,connectorIds:connectors,leafCount:Object.keys(leafIds).length,connectorCount:connectors.length,bounds:{width:section.width,height:section.height},imageNodeIds:[imageA.id,imageB.id]});
}
createMap('01 · 분류 마인드맵','1단계 · 분류하기','유사한 정보끼리 묶기 · 순서와 중요도는 아직 정하지 않음',120,[
 {key:'composition',title:'재료 구성',side:'left',color:'#D29F2A',ids:['MAT-01']},
 {key:'formation',title:'고온혼합·제조',side:'left',color:'#E67845',ids:['MAT-02','MAT-03','MAT-04','MAT-05']},
 {key:'experiment',title:'현대 시편 실험',side:'left',color:'#4785C9',ids:['MAT-15','MAT-16','MAT-17','MAT-18','MAT-19','MAT-20','MAT-21']},
 {key:'ancient',title:'고대 현장 단서',side:'right',color:'#9C79C1',ids:['MAT-06','MAT-07','MAT-08','MAT-09']},
 {key:'healing',title:'균열 이후 반응',side:'right',color:'#36A091',ids:['MAT-10','MAT-11','MAT-12','MAT-13','MAT-14']},
 {key:'limits',title:'설명 가능한 범위',side:'right',color:'#BD687B',ids:['MAT-22','MAT-23','MAT-24']}
],'로마 콘크리트\n자가복원',false);
createMap('02 · 배열 마인드맵','2단계 · 배열하기','기본 → 핵심 → 세부 · 보조 근거는 각 설명을 뒷받침',4160,[
 {key:'basic',title:'01 기본\nBASIC',side:'left',color:'#4785C9',ids:['MAT-01','MAT-02','MAT-04','MAT-06','MAT-15','MAT-21']},
 {key:'detail',title:'03 세부\nDETAIL',side:'left',color:'#9C79C1',ids:['MAT-05','MAT-09','MAT-14','MAT-16','MAT-19']},
 {key:'core',title:'02 핵심\nCORE',side:'right',color:'#36A091',ids:['MAT-03','MAT-10','MAT-11','MAT-12','MAT-13','MAT-20','MAT-22','MAT-23']},
 {key:'support',title:'보조 근거\nSUPPORT',side:'right',color:'#D29F2A',ids:['MAT-07','MAT-08','MAT-17','MAT-18','MAT-24']}
],'물이 칼슘을 옮기고\n새 광물이 틈을 메울 수 있다',true);
return {createdNodeIds:created,maps,imageTargets,nativeNodeTypes:['TEXT','CONNECTOR','SECTION','SHAPE_WITH_TEXT'],noHtmlCapture:true};
