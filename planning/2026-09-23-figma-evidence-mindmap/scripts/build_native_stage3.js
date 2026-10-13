// Source-only deliverable; root owns use_figma execution and image uploads.
// Native FigJam relation graph: no HTML capture, Design frames, or editorial cards.
// Load figma-use + figma-use-figjam before execution. Do not add an IIFE or closePlugin().
const PROPOSAL_SHA256 = "25d235086f228caaf08272c1ae5ec2cb7fcecc2550e32e3ef3a02bb61216e002";
const CONCEPTS = [
  {
    "id": "A1",
    "label": "폼페이 현장 단서\n제조·보수법의 차이",
    "evidence_ids": [
      "MAT-03",
      "MAT-08",
      "MAT-09"
    ],
    "kind": "ancient_observation",
    "era": "ancient_evidence",
    "position": {
      "x": 120,
      "y": 310,
      "width": 500
    }
  },
  {
    "id": "L3",
    "label": "고대의 자기치유\n설계 의도는 미확인",
    "evidence_ids": [
      "MAT-24"
    ],
    "kind": "limitation",
    "era": "cross_era",
    "position": {
      "x": 800,
      "y": 280,
      "width": 490
    }
  },
  {
    "id": "M1",
    "label": "로마 콘크리트\n골재 + 모르타르",
    "evidence_ids": [
      "MAT-01"
    ],
    "kind": "material_definition",
    "era": "material",
    "position": {
      "x": 1480,
      "y": 310,
      "width": 440
    }
  },
  {
    "id": "A2",
    "label": "프리베르눔 성벽\n모르타르 시료 10개",
    "evidence_ids": [
      "MAT-06",
      "MAT-07"
    ],
    "kind": "ancient_observation",
    "era": "ancient_evidence",
    "position": {
      "x": 2180,
      "y": 350,
      "width": 570
    }
  },
  {
    "id": "F1",
    "label": "석회석 가열 → 생석회\n생석회·포졸란 건식 혼합",
    "evidence_ids": [
      "MAT-02",
      "MAT-03"
    ],
    "kind": "manufacture",
    "era": "formation",
    "position": {
      "x": 120,
      "y": 660,
      "width": 500
    }
  },
  {
    "id": "F2",
    "label": "물 첨가\n발열·경화",
    "evidence_ids": [
      "MAT-04",
      "MAT-05"
    ],
    "kind": "manufacture",
    "era": "formation",
    "position": {
      "x": 800,
      "y": 660,
      "width": 440
    }
  },
  {
    "id": "M2",
    "label": "시료 속 석회 덩어리\n방해석이 주성분",
    "evidence_ids": [
      "MAT-06"
    ],
    "kind": "material_part",
    "era": "material",
    "position": {
      "x": 1480,
      "y": 720,
      "width": 490
    }
  },
  {
    "id": "C1",
    "label": "시간이 흐른 뒤\n균열 발생",
    "evidence_ids": [
      "MAT-10"
    ],
    "kind": "event",
    "era": "after_crack",
    "position": {
      "x": 120,
      "y": 1320,
      "width": 420
    }
  },
  {
    "id": "C2",
    "label": "물의 접근\n연결된 틈·화학 조건",
    "evidence_ids": [
      "MAT-10",
      "MAT-12"
    ],
    "kind": "necessary_condition",
    "era": "after_crack",
    "position": {
      "x": 810,
      "y": 1320,
      "width": 470
    }
  },
  {
    "id": "P1",
    "label": "석회 덩어리 일부 용해\n칼슘 공급 가능",
    "evidence_ids": [
      "MAT-11"
    ],
    "kind": "proposed_mechanism",
    "era": "after_crack",
    "position": {
      "x": 1520,
      "y": 1320,
      "width": 450
    }
  },
  {
    "id": "P2",
    "label": "칼슘이 풍부한\n용액의 이동 가능",
    "evidence_ids": [
      "MAT-12"
    ],
    "kind": "proposed_mechanism",
    "era": "after_crack",
    "position": {
      "x": 2200,
      "y": 1320,
      "width": 440
    }
  },
  {
    "id": "P3",
    "label": "탄산칼슘(CaCO₃) 석출\n작은 틈의 충전 가능",
    "evidence_ids": [
      "MAT-13",
      "MAT-21"
    ],
    "kind": "proposed_mechanism",
    "era": "after_crack",
    "position": {
      "x": 2890,
      "y": 1110,
      "width": 510
    }
  },
  {
    "id": "P4",
    "label": "남은 포졸란과\n추가 반응 가능",
    "evidence_ids": [
      "MAT-14"
    ],
    "kind": "optional_mechanism",
    "era": "after_crack",
    "position": {
      "x": 2890,
      "y": 1630,
      "width": 510
    }
  },
  {
    "id": "R0",
    "label": "작은 틈의 자기치유\n내구성 기여 가능성",
    "evidence_ids": [
      "MAT-13",
      "MAT-14",
      "MAT-20",
      "MAT-21"
    ],
    "kind": "qualified_synthesis",
    "era": "synthesis",
    "position": {
      "x": 3590,
      "y": 1270,
      "width": 620
    }
  },
  {
    "id": "E1",
    "label": "로마 재료에서 착안한\n현대 모르타르 시편",
    "evidence_ids": [
      "MAT-15"
    ],
    "kind": "experimental_material",
    "era": "modern_experiment",
    "position": {
      "x": 120,
      "y": 2160,
      "width": 540
    }
  },
  {
    "id": "E2",
    "label": "시험 틈 0.5 ± 0.1 mm\n28일 양생 · 2개월 습윤/건조\n30일 범위 유량 관찰",
    "evidence_ids": [
      "MAT-16",
      "MAT-17",
      "MAT-18",
      "MAT-19"
    ],
    "kind": "experimental_condition",
    "era": "modern_experiment",
    "position": {
      "x": 850,
      "y": 2130,
      "width": 670
    }
  },
  {
    "id": "E3",
    "label": "조건별 약 1–3주\n유량이 거의 0",
    "evidence_ids": [
      "MAT-20"
    ],
    "kind": "observed_result",
    "era": "modern_experiment",
    "position": {
      "x": 2280,
      "y": 2160,
      "width": 500
    }
  },
  {
    "id": "E4",
    "label": "새 균열 충전물\n방해석 확인",
    "evidence_ids": [
      "MAT-21"
    ],
    "kind": "observed_result",
    "era": "modern_experiment",
    "position": {
      "x": 3590,
      "y": 2160,
      "width": 530
    }
  },
  {
    "id": "L1",
    "label": "유량 감소 ≠\n하중 지지 능력 회복의 입증",
    "evidence_ids": [
      "MAT-22"
    ],
    "kind": "limitation",
    "era": "cross_era",
    "position": {
      "x": 2280,
      "y": 2700,
      "width": 680
    }
  },
  {
    "id": "L2",
    "label": "일부 현장·현대 시편\n모든 로마 콘크리트로 일반화 불가",
    "evidence_ids": [
      "MAT-23"
    ],
    "kind": "limitation",
    "era": "cross_era",
    "position": {
      "x": 3490,
      "y": 2770,
      "width": 730
    }
  }
];
const RELATIONS = [
  {
    "id": "REL-01",
    "source": "A1",
    "target": "F1",
    "type": "archaeological_support",
    "label": "현장 해석\n건식 혼합을 지지",
    "evidence_ids": [
      "MAT-03",
      "MAT-08",
      "MAT-09"
    ],
    "visual": {
      "color": "#9C79C1",
      "start_magnet": "BOTTOM",
      "end_magnet": "TOP",
      "arrow": true,
      "dashed": false
    }
  },
  {
    "id": "REL-02",
    "source": "F1",
    "target": "F2",
    "type": "manufacturing_sequence",
    "label": "시간 · 제조\n이후 물 첨가",
    "evidence_ids": [
      "MAT-02",
      "MAT-03",
      "MAT-04",
      "MAT-05"
    ],
    "visual": {
      "color": "#E67845",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": true,
      "dashed": false
    }
  },
  {
    "id": "REL-03",
    "source": "F2",
    "target": "M2",
    "type": "proposed_formation_context",
    "label": "제조 기작(제안)\n칼슘 공급원 잔류",
    "evidence_ids": [
      "MAT-03",
      "MAT-04",
      "MAT-05",
      "MAT-06",
      "MAT-11"
    ],
    "visual": {
      "color": "#E67845",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": true,
      "dashed": true
    }
  },
  {
    "id": "REL-04",
    "source": "M1",
    "target": "M2",
    "type": "whole_part",
    "label": "전체–부분\n모르타르 속 덩어리",
    "evidence_ids": [
      "MAT-01",
      "MAT-06"
    ],
    "visual": {
      "color": "#D29F2A",
      "start_magnet": "BOTTOM",
      "end_magnet": "TOP",
      "arrow": false,
      "dashed": false
    }
  },
  {
    "id": "REL-05",
    "source": "A2",
    "target": "M2",
    "type": "ancient_observation",
    "label": "시료 관찰\n방해석 주성분",
    "evidence_ids": [
      "MAT-06",
      "MAT-07"
    ],
    "visual": {
      "color": "#9C79C1",
      "start_magnet": "LEFT",
      "end_magnet": "RIGHT",
      "arrow": true,
      "dashed": false
    }
  },
  {
    "id": "REL-06",
    "source": "F1",
    "target": "L3",
    "type": "intent_limit",
    "label": "추론의 한계\n제조법 ≠ 치유 의도",
    "evidence_ids": [
      "MAT-03",
      "MAT-24"
    ],
    "visual": {
      "color": "#BD687B",
      "start_magnet": "TOP",
      "end_magnet": "LEFT",
      "arrow": false,
      "dashed": true
    }
  },
  {
    "id": "REL-07",
    "source": "F2",
    "target": "C1",
    "type": "manufacture_before_damage",
    "label": "시간 경과\n제조와 이후 균열",
    "evidence_ids": [
      "MAT-04",
      "MAT-05",
      "MAT-10"
    ],
    "visual": {
      "color": "#E67845",
      "start_magnet": "BOTTOM",
      "end_magnet": "TOP",
      "arrow": true,
      "dashed": false
    }
  },
  {
    "id": "REL-08",
    "source": "C1",
    "target": "C2",
    "type": "necessary_condition",
    "label": "필요조건(제안)\n균열에 물이 닿을 때",
    "evidence_ids": [
      "MAT-10",
      "MAT-12"
    ],
    "visual": {
      "color": "#36A091",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": true,
      "dashed": false
    }
  },
  {
    "id": "REL-09",
    "source": "C2",
    "target": "P1",
    "type": "necessary_condition",
    "label": "필요조건(제안)\n물의 접근",
    "evidence_ids": [
      "MAT-10",
      "MAT-11",
      "MAT-12"
    ],
    "visual": {
      "color": "#36A091",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": true,
      "dashed": false
    }
  },
  {
    "id": "REL-10",
    "source": "M2",
    "target": "P1",
    "type": "proposed_causal_pathway",
    "label": "제안 기작\n칼슘 공급원 가능",
    "evidence_ids": [
      "MAT-06",
      "MAT-11"
    ],
    "visual": {
      "color": "#36A091",
      "start_magnet": "BOTTOM",
      "end_magnet": "TOP",
      "arrow": true,
      "dashed": true
    }
  },
  {
    "id": "REL-11",
    "source": "P1",
    "target": "P2",
    "type": "proposed_causal_pathway",
    "label": "제안 기작\n연결된 물길로 이동",
    "evidence_ids": [
      "MAT-11",
      "MAT-12"
    ],
    "visual": {
      "color": "#36A091",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": true,
      "dashed": true
    }
  },
  {
    "id": "REL-12",
    "source": "P2",
    "target": "P3",
    "type": "proposed_causal_pathway",
    "label": "제안 기작\n탄산칼슘 석출 가능",
    "evidence_ids": [
      "MAT-12",
      "MAT-13",
      "MAT-21"
    ],
    "visual": {
      "color": "#36A091",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": true,
      "dashed": true
    }
  },
  {
    "id": "REL-13",
    "source": "P2",
    "target": "P4",
    "type": "optional_proposed_pathway",
    "label": "선택 경로(제안)\n포졸란이 남으면",
    "evidence_ids": [
      "MAT-12",
      "MAT-14"
    ],
    "visual": {
      "color": "#36A091",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": true,
      "dashed": true
    }
  },
  {
    "id": "REL-14",
    "source": "P3",
    "target": "R0",
    "type": "qualified_contribution",
    "label": "제안 기작\n틈 충전에 기여 가능",
    "evidence_ids": [
      "MAT-13",
      "MAT-20",
      "MAT-21"
    ],
    "visual": {
      "color": "#36A091",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": true,
      "dashed": true
    }
  },
  {
    "id": "REL-15",
    "source": "P4",
    "target": "R0",
    "type": "qualified_contribution",
    "label": "제안 기작\n추가 결합 가능",
    "evidence_ids": [
      "MAT-14"
    ],
    "visual": {
      "color": "#36A091",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": true,
      "dashed": true
    }
  },
  {
    "id": "REL-16",
    "source": "E1",
    "target": "E2",
    "type": "experimental_design",
    "label": "시험 설계\n해당 시편의 조건",
    "evidence_ids": [
      "MAT-15",
      "MAT-16",
      "MAT-17",
      "MAT-18",
      "MAT-19"
    ],
    "visual": {
      "color": "#4785C9",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": true,
      "dashed": false
    }
  },
  {
    "id": "REL-17",
    "source": "E2",
    "target": "E3",
    "type": "experimental_observation",
    "label": "시험 관찰\n조건별 유량 감소",
    "evidence_ids": [
      "MAT-16",
      "MAT-17",
      "MAT-18",
      "MAT-19",
      "MAT-20"
    ],
    "visual": {
      "color": "#4785C9",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": true,
      "dashed": false
    }
  },
  {
    "id": "REL-18",
    "source": "E3",
    "target": "E4",
    "type": "joint_explanation",
    "label": "공동 설명\n유량 + 충전물",
    "evidence_ids": [
      "MAT-20",
      "MAT-21"
    ],
    "visual": {
      "color": "#4785C9",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": false,
      "dashed": false
    }
  },
  {
    "id": "REL-19",
    "source": "E4",
    "target": "R0",
    "type": "experimental_support",
    "label": "실험 지원\n현대 시편의 관찰",
    "evidence_ids": [
      "MAT-15",
      "MAT-20",
      "MAT-21"
    ],
    "visual": {
      "color": "#4785C9",
      "start_magnet": "TOP",
      "end_magnet": "BOTTOM",
      "arrow": true,
      "dashed": false
    }
  },
  {
    "id": "REL-20",
    "source": "E3",
    "target": "L1",
    "type": "measured_outcome_limit",
    "label": "추론의 한계\n구조 강도는 미검증",
    "evidence_ids": [
      "MAT-19",
      "MAT-20",
      "MAT-21",
      "MAT-22"
    ],
    "visual": {
      "color": "#BD687B",
      "start_magnet": "BOTTOM",
      "end_magnet": "TOP",
      "arrow": false,
      "dashed": true
    }
  },
  {
    "id": "REL-21",
    "source": "E4",
    "target": "L2",
    "type": "generalization_limit",
    "label": "일반화 한계\n해당 현장·배합의 범위",
    "evidence_ids": [
      "MAT-07",
      "MAT-08",
      "MAT-15",
      "MAT-21",
      "MAT-23"
    ],
    "visual": {
      "color": "#BD687B",
      "start_magnet": "BOTTOM",
      "end_magnet": "TOP",
      "arrow": false,
      "dashed": true
    }
  }
];

if (figma.editorType !== 'figjam') throw new Error('This script requires the approved FigJam board.');
const sectionName = '03 · 관계 마인드맵';
const page = figma.currentPage;
if (page.children.some(n => n.name === sectionName)) throw new Error('Stage 3 already exists; inspect it before retrying.');
const originX = Math.max(120, ...page.children.map(n => n.x + n.width + 360));
const created = [], imageTargets = [], nodes = {}, edgeMap = [];
const regular = { family:'Noto Sans KR', style:'Regular' };
const bold = { family:'Noto Sans KR', style:'Bold' };
await Promise.all([
  figma.loadFontAsync(regular),
  figma.loadFontAsync(bold),
  figma.loadFontAsync({ family:'Inter', style:'Regular' }),
  figma.loadFontAsync({ family:'Inter', style:'Medium' })
]);
const ink = '#1E1E1E';
const rgb = h => ({r:parseInt(h.slice(1,3),16)/255,g:parseInt(h.slice(3,5),16)/255,b:parseInt(h.slice(5,7),16)/255});
const paint = h => [{type:'SOLID',color:rgb(h)}];
function keep(n) { created.push(n.id); return n; }
function text(parent, value, x, y, width, size=30, strong=false, name=value) {
  const n=keep(figma.createText());
  parent.appendChild(n);
  n.fontName=strong ? bold : regular;
  n.fontSize=size;
  n.lineHeight={unit:'PERCENT',value:145};
  n.textAutoResize='HEIGHT';
  n.resize(width,Math.max(44,size*1.45));
  n.characters=value;
  n.x=x; n.y=y; n.fills=paint(ink); n.name=name;
  if (!(n.width>0)) throw new Error('Text width failed: '+name);
  return n;
}
const section=keep(figma.createSection());
section.name=sectionName;
section.resize(4360,3650);
section.x=originX; section.y=120;
section.fills=paint('#FFFFFF');
text(section,'3단계 · 관계맺기',100,55,4080,54,true,'관계 마인드맵 제목');
text(section,'작은 균열을 메우는 반응은 무엇을 필요로 하며, 어떤 근거가 설명을 뒷받침할까?',100,152,4080,28,false,'핵심 질문');
text(section,'제조 시기와 재료',100,240,600,27,true,'시기 · 제조');
text(section,'시간이 흐른 뒤 · 균열 이후의 제안 기작',100,1140,1700,29,true,'시기 · 균열 이후');
text(section,'현대 모르타르 시험 · 조건과 관찰 지표',100,1970,1800,29,true,'시기 · 현대 시험');
for (const item of CONCEPTS) {
  const p=item.position;
  const refs='['+item.evidence_ids.map(id=>id.slice(4)).join('·')+']';
  const value=item.label+'\n'+refs;
  const strong=item.id==='R0' || item.kind==='limitation';
  const size=item.id==='R0' ? 46 : (item.kind==='limitation' ? 30 : 32);
  const node=text(section,value,p.x,p.y,p.width,size,strong,item.id+' · '+item.label.replace(/\n/g,' '));
  const refStart=item.label.length+1;
  node.setRangeFontSize(refStart,value.length,19);
  node.setRangeFontName(refStart,value.length,regular);
  if (item.id==='R0') node.textAlignHorizontal='CENTER';
  nodes[item.id]=node;
}
for (const relation of RELATIONS) {
  const source=nodes[relation.source], target=nodes[relation.target];
  if (!source || !target) throw new Error('Unresolved relation: '+relation.id);
  const connector=keep(figma.createConnector());
  section.appendChild(connector);
  connector.name=relation.id+' · '+relation.type+' · '+relation.source+' → '+relation.target;
  connector.connectorLineType='CURVED';
  connector.connectorStart={endpointNodeId:source.id,magnet:relation.visual.start_magnet};
  connector.connectorEnd={endpointNodeId:target.id,magnet:relation.visual.end_magnet};
  connector.connectorStartStrokeCap='NONE';
  connector.connectorEndStrokeCap=relation.visual.arrow ? 'ARROW_LINES' : 'NONE';
  connector.strokes=paint(relation.visual.color);
  connector.strokeWeight=relation.type==='whole_part' ? 4 : 3;
  connector.dashPattern=relation.visual.dashed ? [12,8] : [];
  // Connector labels are visible text; a layer name alone is not a label.
  // The connector's initial text font is invalid, so assign the already-loaded font explicitly.
  connector.text.fontName=regular;
  connector.text.fontSize=21;
  connector.text.lineHeight={unit:'PERCENT',value:140};
  connector.text.characters=relation.label;
  connector.text.fills=paint(ink);
  connector.textBackground.fills=paint('#FFFFFF');
  edgeMap.push({id:relation.id,nodeId:connector.id,source:relation.source,target:relation.target,type:relation.type,label:relation.label,evidenceIds:relation.evidence_ids});
}
function imageTarget(key,x,y,w,h,caption,path) {
  const shape=keep(figma.createShapeWithText());
  section.appendChild(shape);
  shape.shapeType='SQUARE';
  shape.text.fontName=regular; shape.text.characters='';
  shape.resize(w,h); shape.x=x; shape.y=y;
  shape.name='도판 · '+key;
  shape.fills=paint('#FFFFFF'); shape.strokes=[];
  text(section,caption,x,y+h+18,w,20,false,'출처 · '+key);
  imageTargets.push({nodeId:shape.id,key,path,scaleMode:'FIT',width:w,height:h});
}
imageTarget('2023-mechanism',120,2670,950,442,
  '제안된 제조·자기치유 기작 · Seymour 외(2023), Fig. 6\nCC BY-NC 4.0 · 원문 도판, 원본 비율 유지',
  '/Users/um-yunsang/.planning/2026-09-23-figma-evidence-mindmap/evidence/images/2023-mechanism.jpg');
imageTarget('2023-experiment',1170,2670,950,479,
  '현대 모르타르 시험 · Seymour 외(2023), Fig. 5\nCC BY-NC 4.0 · 원문 도판, 원본 비율 유지',
  '/Users/um-yunsang/.planning/2026-09-23-figma-evidence-mindmap/evidence/images/2023-experiment.jpg');
text(section,'연결선 읽기  실선: 부분·시간·조건·관찰   /   점선: 제안된 반응·해석의 한계   /   양방향 인과관계는 가정하지 않음',120,3300,4080,24,true,'관계선 범례');
text(section,'제조 → 이후 균열은 시간 구분입니다. 두 반응 경로가 늘 함께 일어나는 것은 아니며, 현대 시편의 유량 감소는 건물 전체의 강도 회복을 입증하지 않습니다.',120,3360,4080,23,false,'과정과 증거의 범위');
text(section,'[01–24]는 승인된 근거 식별자입니다. 연결도는 그 근거를 종합한 설명이며, 모든 화살표를 직접 측정한 실험 결과가 아닙니다.',120,3425,4080,22,false,'근거 식별자 설명');
text(section,'S2023 · Seymour et al. · doi.org/10.1126/sciadv.add1602   /   S2025 · Vaserman et al. · doi.org/10.1038/s41467-025-66634-7',120,3485,4080,21,false,'논문 출처');
let maxRight=0,maxBottom=0;
for (const child of section.children) {
  maxRight=Math.max(maxRight,child.x+child.width);
  maxBottom=Math.max(maxBottom,child.y+child.height);
}
section.resize(Math.max(4360,Math.ceil(maxRight+100)),Math.max(3600,Math.ceil(maxBottom+100)));
const bounds=CONCEPTS.map(item=>{const n=nodes[item.id];return {id:item.id,nodeId:n.id,x:n.x,y:n.y,width:n.width,height:n.height};});
const nodeOverlaps=[];
for(let i=0;i<bounds.length;i++) for(let j=i+1;j<bounds.length;j++) {
  const a=bounds[i],b=bounds[j];
  if(a.x < b.x+b.width && a.x+a.width > b.x && a.y < b.y+b.height && a.y+a.height > b.y)
    nodeOverlaps.push([a.id,b.id]);
}
return {
  createdNodeIds:created,
  mutatedNodeIds:[],
  sectionId:section.id,
  pageId:page.id,
  rootNodeId:nodes.R0.id,
  nodes:CONCEPTS.map(item=>({id:item.id,nodeId:nodes[item.id].id,evidenceIds:item.evidence_ids})),
  edges:edgeMap,
  imageTargets,
  conceptCount:CONCEPTS.length,
  connectorCount:edgeMap.length,
  evidenceCount:new Set(CONCEPTS.flatMap(item=>item.evidence_ids)).size,
  bounds:{x:section.x,y:section.y,width:section.width,height:section.height},
  nodeBounds:bounds,
  layoutIssues:nodeOverlaps,
  imageUploadPending:true,
  nativeNodeTypes:['SECTION','TEXT','CONNECTOR','SHAPE_WITH_TEXT'],
  proposalSha256:PROPOSAL_SHA256
};
