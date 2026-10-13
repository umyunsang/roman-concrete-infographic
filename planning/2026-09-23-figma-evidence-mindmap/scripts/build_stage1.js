// Native Figma working board. Run as the body of use_figma with skillNames: "figma-use".
// Root owns execution, screenshots, and upload_assets. Image rectangles intentionally receive fills later.
const CREATED = [];
const IMAGE_TARGETS = [];
const TEXT_NODES = [];
const COLORS = { ivory: '#F5F1E8', paper: '#FFFCF6', ink: '#272C2B', muted: '#68716B', line: '#D7D2C6', terracotta: '#A8563E', teal: '#286F69', sand: '#E8DECA', paleTeal: '#E4EEEA' };
const FONTS = { regular: { family: 'Noto Sans KR', style: 'Regular' }, medium: { family: 'Noto Sans KR', style: 'Medium' }, bold: { family: 'Noto Sans KR', style: 'Bold' }, serif: { family: 'Noto Serif KR', style: 'Bold' }, inter: { family: 'Inter', style: 'Regular' } };
await Promise.all(Object.values(FONTS).map(font => figma.loadFontAsync(font)));
function rgb(hex) { const h = hex.replace('#', ''); return { r: parseInt(h.slice(0,2),16)/255, g: parseInt(h.slice(2,4),16)/255, b: parseInt(h.slice(4,6),16)/255 }; }
function solid(hex) { return [{ type: 'SOLID', color: rgb(hex) }]; }
function track(node) { CREATED.push(node.id); return node; }
function stack(parent, name, width, gap=12, direction='VERTICAL') {
  const node = track(figma.createAutoLayout(direction)); node.name = name;
  parent.appendChild(node); node.resize(width, 80);
  node.layoutSizingHorizontal = 'FIXED'; node.layoutSizingVertical = 'HUG';
  node.primaryAxisSizingMode = direction === 'VERTICAL' ? 'AUTO' : 'FIXED'; node.counterAxisSizingMode = direction === 'VERTICAL' ? 'FIXED' : 'AUTO';
  node.primaryAxisAlignItems = 'MIN'; node.counterAxisAlignItems = 'MIN';
  node.itemSpacing = gap; node.fills = []; node.clipsContent = false;
  return node;
}
function text(parent, name, value, width, size=22, face='regular', color=COLORS.ink, line=1.55) {
  const node = track(figma.createText()); node.name = name;
  node.fontName = FONTS[face]; node.fontSize = size;
  node.textAutoResize = 'HEIGHT'; node.resize(width, Math.ceil(size*line));
  node.layoutSizingHorizontal = 'FIXED'; node.lineHeight = { unit:'PERCENT', value:line*100 };
  node.fills = solid(color); node.characters = value;
  parent.appendChild(node); TEXT_NODES.push(node);
  if (!(node.width > 0)) throw new Error('Text width failed: ' + name);
  return node;
}
function rule(parent, name, width, color=COLORS.line, height=1) {
  const node=track(figma.createRectangle()); node.name=name; parent.appendChild(node);
  node.resize(width,height); node.fills=solid(color); node.strokes=[]; return node;
}
function image(parent, key, width, height, attribution, caption, path) {
  const box=stack(parent, '도판 · '+key, width, 10);
  const target=track(figma.createRectangle()); target.name='IMAGE_FILL · '+key;
  box.appendChild(target); target.resize(width,height); target.fills=solid(COLORS.sand);
  target.strokes=solid(COLORS.line); target.strokeWeight=1;
  text(box, '도판 설명 · '+key, caption, width, 18, 'medium', COLORS.ink,1.5);
  text(box, '도판 출처 · '+key, attribution, width, 15, 'regular',COLORS.muted,1.5);
  IMAGE_TARGETS.push({ nodeId:target.id, key, path, width, height, scaleMode:'FIT', attribution });
  return box;
}
function evidenceEntry(parent, item, width) {
  const e=stack(parent, '근거 · '+item.id, width, 6);
  const state=item.state || '관찰';
  text(e, item.id+' · 표지', item.id+'  /  '+state+'  /  '+item.source, width,15,'medium',COLORS.teal,1.35);
  text(e, item.id+' · 사실', item.claim, width,21,'regular',COLORS.ink,1.5);
  if (item.limit) text(e,item.id+' · 범위',item.limit,width,17,'regular',COLORS.muted,1.5);
  rule(e,item.id+' · 구분',width);
  return e;
}
function evidenceDigest(items) { return items.map(item=>({id:item.id, source:item.source, state:item.state})); }
function returnEvidence(root, page, stage, extra={}) {
  let maxBottom = 0; for (const child of root.children) maxBottom=Math.max(maxBottom,child.y+child.height);
  root.resize(root.width, Math.max(1320, Math.ceil(maxBottom+64)));
  const badText=TEXT_NODES.filter(n=>!(n.width>0)||n.height>1200).map(n=>({id:n.id,name:n.name,width:n.width,height:n.height}));
  return { stage, pageId:page.id, pageName:page.name, rootId:root.id, createdNodeIds:CREATED, mutatedNodeIds:[], allNodeIds:CREATED, imageTargets:IMAGE_TARGETS, bounds:{x:root.x,y:root.y,width:root.width,height:root.height}, textCount:TEXT_NODES.length, layoutIssues:badText, imageUploadPending:IMAGE_TARGETS.length>0, ...extra };
}

const EVIDENCE = [
  {
    "id": "MAT-01",
    "claim": "로마 콘크리트는 굵은 골재와 이를 결합하는 모르타르로 구성된다.",
    "source": "S2023",
    "state": "재료 정의",
    "limit": "논문의 재료 정의; 직접시험 결과와 구분.",
    "group": "G-COMPOSITION",
    "role": "basic"
  },
  {
    "id": "MAT-02",
    "claim": "석회석을 가열하면 생석회가 만들어진다.",
    "source": "S2023",
    "state": "기초 화학",
    "limit": "기초 화학 설명; 유적별 공정은 별도 확인.",
    "group": "G-FORMATION",
    "role": "basic"
  },
  {
    "id": "MAT-03",
    "claim": "폼페이 자료는 생석회·포졸란의 건식 혼합 후 물 첨가를 뒷받침한다.",
    "source": "S2025",
    "state": "현장 자료 해석",
    "limit": "Domus IX 10, 1의 제조법 복원.",
    "group": "G-FORMATION",
    "role": "core"
  },
  {
    "id": "MAT-04",
    "claim": "생석회가 물과 반응해 소석회가 될 때 열이 발생한다.",
    "source": "S2025",
    "state": "기초 화학",
    "limit": "발열 반응이지 균열 치유 자체는 아니다.",
    "group": "G-FORMATION",
    "role": "basic"
  },
  {
    "id": "MAT-05",
    "claim": "석회·포졸란 반응은 재료를 결합하는 수화물을 만든다.",
    "source": "S2023",
    "state": "기초 화학",
    "limit": "초기 경화와 이후 충전을 구별.",
    "group": "G-FORMATION",
    "role": "detail"
  },
  {
    "id": "MAT-06",
    "claim": "프리베르눔의 석회 덩어리에서는 방해석이 주성분으로 확인됐다.",
    "source": "S2023",
    "state": "고대 시료 관찰",
    "limit": "덩어리 전체를 미반응 생석회로 표시하지 않는다.",
    "group": "G-ANCIENT",
    "role": "basic"
  },
  {
    "id": "MAT-07",
    "claim": "2023년 고대 분석 대상은 프리베르눔 성벽 모르타르 시료 10개다.",
    "source": "S2023",
    "state": "고대 시료 관찰",
    "limit": "콜로세움 시료가 아니다.",
    "group": "G-ANCIENT",
    "role": "support"
  },
  {
    "id": "MAT-08",
    "claim": "2025년 연구는 폼페이 공사 현장의 원료와 벽체를 비교했다.",
    "source": "S2025",
    "state": "고대 시료 관찰",
    "limit": "현장별 배합 차이를 남겨둔다.",
    "group": "G-ANCIENT",
    "role": "support"
  },
  {
    "id": "MAT-09",
    "claim": "폼페이에는 소석회를 사용한 보수·마감의 단서도 있다.",
    "source": "S2025",
    "state": "현장 자료 해석",
    "limit": "저자 해석이며 용도별 제조법이 다를 수 있다.",
    "group": "G-ANCIENT",
    "role": "detail"
  },
  {
    "id": "MAT-10",
    "claim": "균열이 생긴 뒤 물이 틈과 연결된 공극으로 들어올 수 있다.",
    "source": "S2023",
    "state": "제안된 기작",
    "limit": "물의 접근이 필요한 조건.",
    "group": "G-HEALING",
    "role": "core"
  },
  {
    "id": "MAT-11",
    "claim": "석회 덩어리 일부가 녹으면 칼슘을 공급할 수 있다.",
    "source": "S2025",
    "state": "제안된 기작",
    "limit": "용해·재광물화 해석; 속도는 현장마다 다를 수 있다.",
    "group": "G-HEALING",
    "role": "core"
  },
  {
    "id": "MAT-12",
    "claim": "칼슘이 풍부한 용액은 연결된 틈으로 이동할 수 있다.",
    "source": "S2023",
    "state": "제안된 기작",
    "limit": "연결된 물길과 화학 조건이 필요하다.",
    "group": "G-HEALING",
    "role": "core"
  },
  {
    "id": "MAT-13",
    "claim": "탄산칼슘이 다시 석출되면 작은 틈을 메울 수 있다.",
    "source": "S2023",
    "state": "제안된 기작",
    "limit": "일부 조건의 충전 가능성.",
    "group": "G-HEALING",
    "role": "core"
  },
  {
    "id": "MAT-14",
    "claim": "칼슘은 남은 포졸란과 반응해 추가 결합 물질을 만들 수도 있다.",
    "source": "S2025",
    "state": "제안된 기작",
    "limit": "주 경로와 병렬인 추가 반응.",
    "group": "G-HEALING",
    "role": "detail"
  },
  {
    "id": "MAT-15",
    "claim": "균열 치유 시험은 로마 재료에서 착안한 현대 모르타르로 했다.",
    "source": "S2023",
    "state": "현대 시편 시험",
    "limit": "OPC·플라이애시·모래·물·생석회; 굵은 골재 없음.",
    "group": "G-EXPERIMENT",
    "role": "basic"
  },
  {
    "id": "MAT-16",
    "claim": "시험 시편의 인위적 틈은 0.5 ± 0.1 mm였다.",
    "source": "S2023",
    "state": "현대 시편 시험",
    "limit": "보편적인 치유 한계값이 아니다.",
    "group": "G-EXPERIMENT",
    "role": "detail"
  },
  {
    "id": "MAT-17",
    "claim": "시편은 균열을 내기 전 28일간 수중 양생했다.",
    "source": "S2023",
    "state": "현대 시편 시험",
    "limit": "현대 시편의 사전 준비 조건.",
    "group": "G-EXPERIMENT",
    "role": "support"
  },
  {
    "id": "MAT-18",
    "claim": "본시험 전 두 달간 습윤·건조 전처리를 했다.",
    "source": "S2023",
    "state": "현대 시편 시험",
    "limit": "현장 자연노출 시간과 다르다.",
    "group": "G-EXPERIMENT",
    "role": "support"
  },
  {
    "id": "MAT-19",
    "claim": "물 공급에 따른 유량 변화를 30일 범위에서 관찰했다.",
    "source": "S2023",
    "state": "현대 시편 시험",
    "limit": "유량이 멈추거나 미미해지면 종료.",
    "group": "G-EXPERIMENT",
    "role": "detail"
  },
  {
    "id": "MAT-20",
    "claim": "유량은 균열 형상에 따라 약 1–3주에 거의 0으로 줄었다.",
    "source": "S2023",
    "state": "현대 시편 시험",
    "limit": "해당 석회 덩어리 포함 시편의 결과.",
    "group": "G-EXPERIMENT",
    "role": "core"
  },
  {
    "id": "MAT-21",
    "claim": "새로 생긴 균열 충전물은 방해석으로 확인됐다.",
    "source": "S2023",
    "state": "현대 시편 시험",
    "limit": "현대 시험의 충전물 분석.",
    "group": "G-EXPERIMENT",
    "role": "basic"
  },
  {
    "id": "MAT-22",
    "claim": "유량 감소만으로 원래의 하중 지지 능력 회복을 입증하지는 못한다.",
    "source": "S2023",
    "state": "해석의 한계",
    "limit": "측정 지표와 구조 안전을 구분.",
    "group": "G-LIMITS",
    "role": "core"
  },
  {
    "id": "MAT-23",
    "claim": "두 현장 연구를 모든 로마 콘크리트에 일반화할 수는 없다.",
    "source": "S2025",
    "state": "해석의 한계",
    "limit": "콜로세움·제국 전체의 동일 성능 미검증.",
    "group": "G-LIMITS",
    "role": "core"
  },
  {
    "id": "MAT-24",
    "claim": "고대 건축가가 자가치유를 의도했는지는 확인되지 않았다.",
    "source": "S2025",
    "state": "해석의 한계",
    "limit": "제조 행위와 설계 의도를 구분.",
    "group": "G-LIMITS",
    "role": "support"
  }
];

function createWorkingBoard(pageName, boardName, width=1860) {
  const page = figma.root.children.find(p => p.name === pageName);
  if (!page) throw new Error('Target page missing: ' + pageName);
  return page;
}
function makeRoot(page, name, width=1860) {
  if (page.children.some(node => node.name === name)) throw new Error('Working board already exists; inspect its current state before retrying: ' + name);
  const clearX = Math.max(120, ...page.children.map(n=>n.x+n.width+160));
  const root=track(figma.createFrame()); root.name=name; page.appendChild(root);
  root.x=clearX; root.y=120; root.resize(width,1500); root.fills=solid(COLORS.ivory); root.clipsContent=false;
  return root;
}
function heading(root, step, title, scope) {
  const h=stack(root,'제목과 핵심 질문',1700,14); h.x=80; h.y=68;
  text(h,'단계 표제','ROMAN CONCRETE  /  '+step,1700,17,'inter',COLORS.terracotta,1.3);
  text(h,'작업판 제목',title,1700,48,'serif',COLORS.ink,1.28);
  text(h,'핵심 질문','로마 콘크리트는 어떻게 작은 균열을 스스로 메우며,\n이 반응은 오래 버티는 데 어떻게 기여할까?',1700,27,'medium',COLORS.ink,1.52);
  text(h,'단계의 범위',scope,1700,19,'regular',COLORS.muted,1.5);
  rule(h,'머리말 하단선',1700,COLORS.ink,2);
  return h;
}
function sourceNotes(parent,width) {
  text(parent,'자료의 범위','자료 범위: 자기치유 질문에 맞춰 선택한 원자 단위 근거 24개. 두 논문 전체의 모든 주장을 추출한 목록은 아닙니다.',width,16,'regular',COLORS.muted,1.5);
  text(parent,'S2023 출처','S2023 · Seymour et al. (2023), Science Advances · doi.org/10.1126/sciadv.add1602',width,16,'regular',COLORS.muted,1.5);
  text(parent,'S2025 출처','S2025 · Vaserman et al. (2025), Nature Communications · doi.org/10.1038/s41467-025-66634-7',width,16,'regular',COLORS.muted,1.5);
}

const page=createWorkingBoard('01 · 분류하기','분류하기');
await figma.setCurrentPageAsync(page);
const root=makeRoot(page,'01 · 분류하기 — 근거를 성격별로 모으기');
const header=heading(root,'01  분류하기','무엇을 알고 있는가','자료를 성격별로 묶습니다. 항목 번호는 식별자이며, 읽는 순서나 중요도를 뜻하지 않습니다.');
const columns=stack(root,'동일한 비중의 근거 묶음',1700,40,'HORIZONTAL');
columns.x=80; columns.y=header.y+header.height+38;
const groupNames={ 'G-COMPOSITION':'무엇으로 이루어졌나', 'G-FORMATION':'만들어질 때의 반응', 'G-ANCIENT':'고대 현장에서 발견한 단서', 'G-HEALING':'균열 이후의 반응', 'G-EXPERIMENT':'현대 시편에서 확인한 결과', 'G-LIMITS':'설명할 수 있는 범위' };
const layout=[['G-COMPOSITION','G-EXPERIMENT'],['G-FORMATION','G-LIMITS'],['G-ANCIENT','G-HEALING']];
const groupNodeIds={};
for (let i=0;i<layout.length;i++) {
  const column=stack(columns,'분류 열 '+(i+1),540,40);
  for (const key of layout[i]) {
    const group=stack(column,'분류 · '+groupNames[key],540,16); groupNodeIds[key]=group.id;
    rule(group,'분류 머리선 · '+key,540,COLORS.teal,3);
    text(group,'분류명 · '+key,groupNames[key],540,29,'bold',COLORS.ink,1.35);
    for (const item of EVIDENCE.filter(e=>e.group===key)) evidenceEntry(group,item,540);
  }
}
const evidenceImages=stack(root,'원문 도판과 출처',1700,24);
evidenceImages.x=80; evidenceImages.y=columns.y+columns.height+50;
rule(evidenceImages,'도판 상단선',1700,COLORS.ink,2);
text(evidenceImages,'원문 도판 표제','원문 도판도 관찰과 해석을 구분해 둡니다',1700,27,'medium',COLORS.ink,1.4);
const imageRow=stack(evidenceImages,'원문 도판 두 장',1700,44,'HORIZONTAL');
image(imageRow,'2023-experiment',828,418,'Seymour et al. 2023 · Fig. 5 · CC BY-NC 4.0 · 원본 비율 유지','현대 모르타르 시편의 균열·유량 시험과 충전물 분석','/Users/um-yunsang/.planning/2026-09-23-figma-evidence-mindmap/evidence/images/2023-experiment.jpg');
image(imageRow,'2025-production',828,240,'Vaserman 외(2025), Fig. 7 · CC BY-NC-ND 4.0 · 원형 유지','폼페이 건설 공정의 재구성','/Users/um-yunsang/.planning/2026-09-23-figma-evidence-mindmap/evidence/images/2025-production.png');
const notes=stack(evidenceImages,'누락과 중복 확인',1700,9);
text(notes,'중복 원칙','같은 시험에서 나온 조건·유량·충전물은 서로 다른 사실이지만, 독립된 재현 실험으로 세지 않습니다.',1700,18,'medium',COLORS.ink,1.5);
text(notes,'미확인 범위','아직 확인되지 않은 것: 원래 하중 지지 능력의 회복, 모든 로마 콘크리트의 동일 성능, 고대 건축가의 자기치유 설계 의도.',1700,18,'regular',COLORS.muted,1.5);
sourceNotes(notes,1700);
return returnEvidence(root,page,'classification',{evidenceCount:EVIDENCE.length,evidenceIds:EVIDENCE.map(e=>e.id),evidence:evidenceDigest(EVIDENCE),groupNodeIds,stageBoundary:'Classification only; no priority or final-artifact sequence assigned.'});
