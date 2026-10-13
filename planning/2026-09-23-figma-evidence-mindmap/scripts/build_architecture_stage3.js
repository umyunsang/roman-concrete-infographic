// Native FigJam architecture-survival relationship map.
// Source-only delivery: root reviews, executes use_figma, uploads images and checks screenshots.
// Requires figma-use + figma-use-figjam. All original fact/edge limits live in architecture-relationships.json.
const PROPOSAL_SHA256="5179a2897f9c25aaa677609a8ed32b88eb628dae46c6b84487bb4c8027ce534a";
const CONCEPTS=[
  {
    "id": "P",
    "label": "판테온\n오늘도 남은 건축물",
    "evidence_ids": [
      "ARC01"
    ],
    "kind": "primary_case",
    "position": {
      "x": 2080,
      "y": 1080,
      "width": 680
    },
    "source_ids": [
      "A-PANTHEON-ROMA"
    ]
  },
  {
    "id": "D",
    "label": "원통형 몸체 위의\n반구형 돔",
    "evidence_ids": [
      "ARC02"
    ],
    "kind": "structure",
    "position": {
      "x": 1210,
      "y": 820,
      "width": 490
    },
    "source_ids": [
      "A-PANTHEON-ROMA"
    ]
  },
  {
    "id": "W",
    "label": "두꺼운 벽체\n여덟 큰 지지부",
    "evidence_ids": [
      "ARC03",
      "ARC04"
    ],
    "kind": "structure",
    "position": {
      "x": 190,
      "y": 820,
      "width": 590
    },
    "source_ids": [
      "A-PANTHEON-ROMA"
    ]
  },
  {
    "id": "PD",
    "label": "청동 덮개의 상실\n바닥의 균열·결손",
    "evidence_ids": [
      "PRE04",
      "PRE05"
    ],
    "kind": "damage",
    "position": {
      "x": 1230,
      "y": 370,
      "width": 740
    },
    "source_ids": [
      "PANTHEON_FLOOR",
      "PANTHEON_HISTORY"
    ]
  },
  {
    "id": "U",
    "label": "609년 교회 전환\n지금도 이어지는 예배",
    "evidence_ids": [
      "ARC05",
      "PRE02"
    ],
    "kind": "use",
    "position": {
      "x": 3440,
      "y": 380,
      "width": 680
    },
    "source_ids": [
      "A-PANTHEON-ROMA",
      "PANTHEON_CHAPTER"
    ]
  },
  {
    "id": "H",
    "label": "지속된 쓰임\n보존에 일부 기여",
    "evidence_ids": [
      "ARC05"
    ],
    "kind": "historical_interpretation",
    "position": {
      "x": 3210,
      "y": 870,
      "width": 780
    },
    "source_ids": [
      "A-PANTHEON-ROMA"
    ]
  },
  {
    "id": "PC",
    "label": "바닥 복원과\n오늘의 유지관리",
    "evidence_ids": [
      "PRE06",
      "PRE07",
      "PRE08"
    ],
    "kind": "conservation",
    "position": {
      "x": 3400,
      "y": 1360,
      "width": 760
    },
    "source_ids": [
      "PANTHEON_CHAPTER",
      "PANTHEON_FLOOR"
    ]
  },
  {
    "id": "S",
    "label": "다른 유적·현대 시편 연구\n조건부 균열 충전 단서",
    "evidence_ids": [
      "ARC12"
    ],
    "kind": "conditional_material_detail",
    "position": {
      "x": 130,
      "y": 1460,
      "width": 720
    },
    "source_ids": [
      "S2023",
      "S2025"
    ]
  },
  {
    "id": "L",
    "label": "잔존 ≠ 무손상·무보수\n타유적 치유 ≠ 판테온 직접 입증",
    "evidence_ids": [
      "PRE12",
      "ARC12"
    ],
    "kind": "interpretation_limit",
    "position": {
      "x": 1190,
      "y": 1460,
      "width": 740
    },
    "source_ids": [
      "COLOSSEUM_DIARY",
      "S2023",
      "S2025"
    ]
  },
  {
    "id": "C",
    "label": "콜로세움\n일부를 잃고 남은 비교 사례",
    "evidence_ids": [
      "ARC06"
    ],
    "kind": "comparison_case",
    "position": {
      "x": 2130,
      "y": 2280,
      "width": 750
    },
    "source_ids": [
      "A-COLOSSEO-CONSTRUCTION",
      "A-VESTRONI"
    ]
  },
  {
    "id": "CD",
    "label": "지진과 철거\n남측 회랑의 붕괴",
    "evidence_ids": [
      "PRE09"
    ],
    "kind": "damage",
    "position": {
      "x": 3500,
      "y": 2220,
      "width": 670
    },
    "source_ids": [
      "COLOSSEUM_DIARY"
    ]
  },
  {
    "id": "B",
    "label": "19세기 버팀 구조\n남은 외벽의 후대 보강",
    "evidence_ids": [
      "PRE10"
    ],
    "kind": "conservation",
    "position": {
      "x": 3500,
      "y": 2740,
      "width": 700
    },
    "source_ids": [
      "COLOSSEUM_DIARY"
    ]
  },
  {
    "id": "CC",
    "label": "통로 복원·방수\n계속되는 계획적 유지관리",
    "evidence_ids": [
      "ARC10",
      "PRE11"
    ],
    "kind": "conservation",
    "position": {
      "x": 2140,
      "y": 2990,
      "width": 760
    },
    "source_ids": [
      "A-COLOSSEO-MAINTENANCE",
      "COLOSSEUM_DIARY"
    ]
  },
  {
    "id": "CS",
    "label": "고리형·방사형 벽\n기둥과 볼트의 연결",
    "evidence_ids": [
      "ARC07",
      "ARC08"
    ],
    "kind": "structure",
    "position": {
      "x": 1190,
      "y": 2360,
      "width": 700
    },
    "source_ids": [
      "A-COLOSSEO-CONSTRUCTION",
      "A-VESTRONI"
    ]
  },
  {
    "id": "M",
    "label": "석재·벽돌·콘크리트\n부위·용도별 재료와 배합",
    "evidence_ids": [
      "ARC09",
      "ARC11"
    ],
    "kind": "material",
    "position": {
      "x": 150,
      "y": 2380,
      "width": 740
    },
    "source_ids": [
      "A-COLOSSEO-MAINTENANCE",
      "A-VESTRONI",
      "S2023",
      "S2025"
    ]
  }
];
const RELATIONS=[
  {
    "id": "AR01",
    "source": "P",
    "target": "D",
    "type": "whole_part",
    "label": "전체–부분\n판테온의 돔",
    "evidence_ids": [
      "ARC01",
      "ARC02"
    ],
    "visual": {
      "color": "#D29F2A",
      "start_magnet": "LEFT",
      "end_magnet": "RIGHT",
      "arrow": false,
      "dashed": false
    },
    "source_ids": [
      "A-PANTHEON-ROMA"
    ]
  },
  {
    "id": "AR02",
    "source": "D",
    "target": "W",
    "type": "mechanical_load_path",
    "label": "역학 원리\n돔 무게의 전달·분산",
    "evidence_ids": [
      "ARC02",
      "ARC03",
      "ARC04"
    ],
    "visual": {
      "color": "#E67845",
      "start_magnet": "LEFT",
      "end_magnet": "RIGHT",
      "arrow": true,
      "dashed": false
    },
    "source_ids": [
      "A-PANTHEON-ROMA"
    ]
  },
  {
    "id": "AR03",
    "source": "PD",
    "target": "P",
    "type": "preservation_state_limit",
    "label": "상태의 한계\n모든 부분이 원형은 아님",
    "evidence_ids": [
      "ARC01",
      "PRE04",
      "PRE05"
    ],
    "visual": {
      "color": "#BD687B",
      "start_magnet": "BOTTOM",
      "end_magnet": "TOP",
      "arrow": false,
      "dashed": true
    },
    "source_ids": [
      "A-PANTHEON-ROMA",
      "PANTHEON_FLOOR",
      "PANTHEON_HISTORY"
    ]
  },
  {
    "id": "AR04",
    "source": "U",
    "target": "H",
    "type": "qualified_historical_interpretation",
    "label": "역사 해석\n보존의 한 요인",
    "evidence_ids": [
      "ARC05",
      "PRE02"
    ],
    "visual": {
      "color": "#9C79C1",
      "start_magnet": "BOTTOM",
      "end_magnet": "TOP",
      "arrow": true,
      "dashed": true
    },
    "source_ids": [
      "A-PANTHEON-ROMA",
      "PANTHEON_CHAPTER"
    ]
  },
  {
    "id": "AR05",
    "source": "H",
    "target": "P",
    "type": "qualified_contribution",
    "label": "공동 설명\n보존에 일부 기여",
    "evidence_ids": [
      "ARC01",
      "ARC05"
    ],
    "visual": {
      "color": "#9C79C1",
      "start_magnet": "LEFT",
      "end_magnet": "RIGHT",
      "arrow": true,
      "dashed": true
    },
    "source_ids": [
      "A-PANTHEON-ROMA"
    ]
  },
  {
    "id": "AR06",
    "source": "PC",
    "target": "P",
    "type": "conservation_action",
    "label": "보존 활동\n후대의 복원·관리",
    "evidence_ids": [
      "PRE06",
      "PRE07",
      "PRE08"
    ],
    "visual": {
      "color": "#4785C9",
      "start_magnet": "LEFT",
      "end_magnet": "RIGHT",
      "arrow": true,
      "dashed": false
    },
    "source_ids": [
      "PANTHEON_CHAPTER",
      "PANTHEON_FLOOR"
    ]
  },
  {
    "id": "AR07",
    "source": "C",
    "target": "P",
    "type": "case_comparison",
    "label": "사례 비교\n남아 있는 상태가 다름",
    "evidence_ids": [
      "ARC01",
      "ARC06",
      "PRE12"
    ],
    "visual": {
      "color": "#D29F2A",
      "start_magnet": "TOP",
      "end_magnet": "BOTTOM",
      "arrow": false,
      "dashed": false
    },
    "source_ids": [
      "A-COLOSSEO-CONSTRUCTION",
      "A-PANTHEON-ROMA",
      "A-VESTRONI",
      "COLOSSEUM_DIARY"
    ]
  },
  {
    "id": "AR08",
    "source": "CD",
    "target": "C",
    "type": "recorded_damage_consequence",
    "label": "손상 이력\n붕괴·철거 뒤 부분 잔존",
    "evidence_ids": [
      "ARC06",
      "PRE09"
    ],
    "visual": {
      "color": "#BD687B",
      "start_magnet": "LEFT",
      "end_magnet": "RIGHT",
      "arrow": true,
      "dashed": false
    },
    "source_ids": [
      "A-COLOSSEO-CONSTRUCTION",
      "A-VESTRONI",
      "COLOSSEUM_DIARY"
    ]
  },
  {
    "id": "AR09",
    "source": "CD",
    "target": "B",
    "type": "temporal_sequence",
    "label": "시간 관계\n손상 뒤의 후대 보강",
    "evidence_ids": [
      "PRE09",
      "PRE10"
    ],
    "visual": {
      "color": "#9C79C1",
      "start_magnet": "BOTTOM",
      "end_magnet": "TOP",
      "arrow": true,
      "dashed": false
    },
    "source_ids": [
      "COLOSSEUM_DIARY"
    ]
  },
  {
    "id": "AR10",
    "source": "B",
    "target": "C",
    "type": "later_structural_support",
    "label": "후대 보강\n추가 붕괴를 막기 위한 지지",
    "evidence_ids": [
      "PRE10",
      "ARC06"
    ],
    "visual": {
      "color": "#4785C9",
      "start_magnet": "LEFT",
      "end_magnet": "RIGHT",
      "arrow": true,
      "dashed": false
    },
    "source_ids": [
      "A-COLOSSEO-CONSTRUCTION",
      "A-VESTRONI",
      "COLOSSEUM_DIARY"
    ]
  },
  {
    "id": "AR11",
    "source": "CC",
    "target": "C",
    "type": "ongoing_conservation",
    "label": "보존 활동\n복원·방수·유지관리",
    "evidence_ids": [
      "ARC10",
      "PRE11"
    ],
    "visual": {
      "color": "#4785C9",
      "start_magnet": "TOP",
      "end_magnet": "BOTTOM",
      "arrow": true,
      "dashed": false
    },
    "source_ids": [
      "A-COLOSSEO-MAINTENANCE",
      "COLOSSEUM_DIARY"
    ]
  },
  {
    "id": "AR12",
    "source": "C",
    "target": "CS",
    "type": "whole_part",
    "label": "전체–부분\n회랑을 이루는 구조",
    "evidence_ids": [
      "ARC07",
      "ARC08"
    ],
    "visual": {
      "color": "#E67845",
      "start_magnet": "LEFT",
      "end_magnet": "RIGHT",
      "arrow": false,
      "dashed": false
    },
    "source_ids": [
      "A-COLOSSEO-CONSTRUCTION",
      "A-VESTRONI"
    ]
  },
  {
    "id": "AR13",
    "source": "M",
    "target": "CS",
    "type": "material_composition",
    "label": "재료 구성\n부위별로 조합",
    "evidence_ids": [
      "ARC07",
      "ARC08",
      "ARC09",
      "ARC11"
    ],
    "visual": {
      "color": "#36A091",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": false,
      "dashed": false
    },
    "source_ids": [
      "A-COLOSSEO-CONSTRUCTION",
      "A-COLOSSEO-MAINTENANCE",
      "A-VESTRONI",
      "S2023",
      "S2025"
    ]
  },
  {
    "id": "AR14",
    "source": "S",
    "target": "M",
    "type": "conditional_supporting_detail",
    "label": "재료 보조 단서\n조건부·다른 유적 연구",
    "evidence_ids": [
      "ARC11",
      "ARC12"
    ],
    "visual": {
      "color": "#36A091",
      "start_magnet": "BOTTOM",
      "end_magnet": "TOP",
      "arrow": false,
      "dashed": true
    },
    "source_ids": [
      "S2023",
      "S2025"
    ]
  },
  {
    "id": "AR15",
    "source": "S",
    "target": "L",
    "type": "evidence_scope_limit",
    "label": "근거의 범위\n타유적 관찰·현대 시편",
    "evidence_ids": [
      "ARC12"
    ],
    "visual": {
      "color": "#BD687B",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": false,
      "dashed": true
    },
    "source_ids": [
      "S2023",
      "S2025"
    ]
  },
  {
    "id": "AR16",
    "source": "L",
    "target": "P",
    "type": "application_limit",
    "label": "적용의 한계\n자가치유의 직접 입증 아님",
    "evidence_ids": [
      "ARC12",
      "PRE12"
    ],
    "visual": {
      "color": "#BD687B",
      "start_magnet": "RIGHT",
      "end_magnet": "LEFT",
      "arrow": false,
      "dashed": true
    },
    "source_ids": [
      "COLOSSEUM_DIARY",
      "S2023",
      "S2025"
    ]
  },
  {
    "id": "AR17",
    "source": "C",
    "target": "L",
    "type": "survivorship_limit",
    "label": "일반화 한계\n남아 있음 ≠ 무손상",
    "evidence_ids": [
      "ARC06",
      "PRE09",
      "PRE10",
      "PRE12"
    ],
    "visual": {
      "color": "#BD687B",
      "start_magnet": "LEFT",
      "end_magnet": "BOTTOM",
      "arrow": false,
      "dashed": true
    },
    "source_ids": [
      "A-COLOSSEO-CONSTRUCTION",
      "A-VESTRONI",
      "COLOSSEUM_DIARY"
    ]
  }
];

if(figma.editorType!=='figjam') throw new Error('Open the approved FigJam board for this relationship map.');
if(figma.fileKey && figma.fileKey!=='Ob3wzRNRC0OSzDCDFp4gtF') throw new Error('Unexpected FigJam file.');
const page=figma.currentPage;
const sectionName='03 · 건축물 관계 마인드맵';
if(page.children.some(n=>n.name===sectionName)) throw new Error('Architecture Stage 3 already exists. Inspect before retrying.');
const clearX=Math.max(120,...page.children.map(n=>n.x+n.width+360));
const created=[], imageTargets=[], nodeMap={}, edges=[];
const regular={family:'Noto Sans KR',style:'Regular'};
const bold={family:'Noto Sans KR',style:'Bold'};
await Promise.all([
  figma.loadFontAsync(regular),figma.loadFontAsync(bold),
  figma.loadFontAsync({family:'Inter',style:'Regular'}),
  figma.loadFontAsync({family:'Inter',style:'Medium'})
]);
const ink='#1E1E1E';
const rgb=h=>({r:parseInt(h.slice(1,3),16)/255,g:parseInt(h.slice(3,5),16)/255,b:parseInt(h.slice(5,7),16)/255});
const paint=h=>[{type:'SOLID',color:rgb(h)}];
function keep(n){created.push(n.id);return n;}
function text(parent,value,x,y,width,size=32,strong=false,name=value){
  const n=keep(figma.createText()); parent.appendChild(n);
  n.fontName=strong?bold:regular; n.fontSize=size;
  n.lineHeight={unit:'PERCENT',value:145};
  n.textAutoResize='HEIGHT'; n.resize(width,Math.max(44,size*1.45));
  n.characters=value; n.x=x; n.y=y; n.name=name; n.fills=paint(ink);
  if(!(n.width>0)) throw new Error('Collapsed text width: '+name);
  return n;
}
const section=keep(figma.createSection());
section.name=sectionName; section.resize(4380,3540);
section.x=clearX; section.y=120; section.fills=paint('#FFFFFF');
text(section,'3단계 · 관계맺기',100,60,4100,53,true,'단계 제목');
text(section,'로마 건축물은 어떻게 약 2천 년을 버텼을까?',100,150,4100,35,true,'확인된 핵심 질문');
text(section,'판테온을 중심에 두고 구조·쓰임·보존을 연결합니다. 콜로세움의 결손과 후대 보강은 비교 사례입니다.',100,230,4100,25,false,'중심 사례와 비교 범위');
for(const item of CONCEPTS){
  const p=item.position;
  const refs='['+item.evidence_ids.join(' · ')+']';
  const value=item.label+'\n'+refs;
  const strong=['primary_case','comparison_case','interpretation_limit'].includes(item.kind);
  const size=item.kind==='primary_case'?50:(item.kind==='comparison_case'?39:32);
  const n=text(section,value,p.x,p.y,p.width,size,strong,item.id+' · '+item.label.replace(/\n/g,' '));
  n.setRangeFontSize(item.label.length+1,value.length,19);
  n.setRangeFontName(item.label.length+1,value.length,regular);
  if(item.kind==='primary_case'||item.kind==='comparison_case') n.textAlignHorizontal='CENTER';
  nodeMap[item.id]=n;
}
for(const r of RELATIONS){
  const a=nodeMap[r.source],b=nodeMap[r.target];
  if(!a||!b)throw new Error('Unresolved relation: '+r.id);
  const c=keep(figma.createConnector());section.appendChild(c);
  c.name=r.id+' · '+r.type+' · '+r.source+' → '+r.target;
  c.connectorLineType='CURVED';
  c.connectorStart={endpointNodeId:a.id,magnet:r.visual.start_magnet};
  c.connectorEnd={endpointNodeId:b.id,magnet:r.visual.end_magnet};
  c.connectorStartStrokeCap='NONE';c.connectorEndStrokeCap=r.visual.arrow?'ARROW_LINES':'NONE';
  c.strokes=paint(r.visual.color);c.strokeWeight=r.type==='mechanical_load_path'?5:3;
  c.dashPattern=r.visual.dashed?[12,8]:[];
  c.text.fontName=regular;c.text.fontSize=22;c.text.lineHeight={unit:'PERCENT',value:140};
  c.text.characters=r.label;c.text.fills=paint(ink);
  c.textBackground.fills=paint('#FFFFFF');
  edges.push({id:r.id,nodeId:c.id,source:r.source,target:r.target,type:r.type,label:r.label,evidenceIds:r.evidence_ids,sourceIds:r.source_ids});
}
function imageTarget(key,x,y,w,h,caption,path=null){
  const n=keep(figma.createShapeWithText());section.appendChild(n);
  n.shapeType='SQUARE';n.text.fontName=regular;n.text.characters='';
  n.resize(w,h);n.x=x;n.y=y;n.name='도판 · '+key;n.fills=paint('#FFFFFF');n.strokes=[];
  text(section,caption,x,y+h+16,w,19,false,'사진 출처 · '+key);
  imageTargets.push({nodeId:n.id,key,scaleMode:'FIT',width:w,height:h,...(path?{path}:{})});
}
imageTarget('pantheon-exterior',2210,410,690,420,
  '중심 사례 · 판테온 / NikonZ7II · CC BY-SA 4.0',
  '/Users/um-yunsang/.planning/2026-09-23-figma-evidence-mindmap/evidence/images/pantheon-exterior.jpg');
imageTarget('colosseum-photo',3360,1700,700,390,
  '비교 사례 · 콜로세움 / Kasa Fue · CC BY-SA 4.0');
text(section,'부분 관계 · 역학 원리 · 시간 선후 · 역사 해석 · 보존 활동 · 근거의 한계',120,3280,4100,27,true,'관계 유형 범례');
text(section,'관계의 종류는 선 위의 이름으로 구분합니다. 점선은 제안·해석 또는 적용의 한계를 표시하며, 비교선과 부분선에는 인과 화살표를 붙이지 않았습니다.',120,3350,4100,23,false,'선의 의미');
text(section,'자가치유는 다른 유적·현대 시편에서 얻은 재료의 보조 단서입니다. 판테온·콜로세움의 직접 시험, 강도 회복, 단일 생존 원인으로 확대하지 않습니다.',120,3415,4100,23,false,'재료 설명의 적용 범위');
text(section,'[ARC·PRE]는 22개 통합 근거의 식별자입니다. 로마시·유적 관리기관·판테온 운영기관·구조 및 재료 원논문의 범위를 유지했습니다.',120,3480,4100,21,false,'출처 추적 안내');
let maxRight=0,maxBottom=0;
for(const n of section.children){maxRight=Math.max(maxRight,n.x+n.width);maxBottom=Math.max(maxBottom,n.y+n.height);}
section.resize(Math.max(4380,Math.ceil(maxRight+100)),Math.max(3580,Math.ceil(maxBottom+100)));
const nodeBounds=CONCEPTS.map(item=>{const n=nodeMap[item.id];return{id:item.id,nodeId:n.id,x:n.x,y:n.y,width:n.width,height:n.height};});
const overlaps=[];
for(let i=0;i<nodeBounds.length;i++)for(let j=i+1;j<nodeBounds.length;j++){
  const a=nodeBounds[i],b=nodeBounds[j];
  if(a.x<b.x+b.width&&a.x+a.width>b.x&&a.y<b.y+b.height&&a.y+a.height>b.y)overlaps.push([a.id,b.id]);
}
return{
  createdNodeIds:created,mutatedNodeIds:[],sectionId:section.id,pageId:page.id,rootNodeId:nodeMap.P.id,
  nodes:CONCEPTS.map(item=>({id:item.id,nodeId:nodeMap[item.id].id,evidenceIds:item.evidence_ids,sourceIds:item.source_ids})),
  edges,imageTargets,conceptCount:CONCEPTS.length,connectorCount:edges.length,
  canonicalEvidenceCount:new Set(CONCEPTS.flatMap(n=>n.evidence_ids)).size,
  bounds:{x:section.x,y:section.y,width:section.width,height:section.height},nodeBounds,layoutIssues:overlaps,
  imageUploadPending:true,nativeNodeTypes:['SECTION','TEXT','CONNECTOR','SHAPE_WITH_TEXT'],
  fullLimitsMetadata:'evidence/architecture-relationships.json',proposalSha256:PROPOSAL_SHA256
};
