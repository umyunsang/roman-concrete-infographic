from pathlib import Path
import base64
import json

out = Path(__file__).parent
evidence = json.loads((out / 'live-reading-evidence.json').read_text())
image_data = base64.b64encode((out / 'current-W3-sketch.png').read_bytes()).decode()
regions = evidence['regions'][0]
core_ids = {'204:8729', '204:8739', '204:8751', '204:8761', '204:8778'}
removed = []
for n in regions['numbers']:
    if n['id'] in core_ids or n['parent'] == '작업 · W3':
        continue
    if n['id'] == '231:21388':
        continue
    b = n['bounds']
    removed.append({'x': b['x'] - 5700 + b['width'] / 2,
                    'y': b['y'] - 100 + b['height'] / 2,
                    'name': n['parent']})

details = [
    {'key': 'material', 'name': '재료 원리', 'title': '해수에서 생기는 결정',
     'point': [238, 430], 'caption': [300, 548], 'core': [326, 490],
     'path': 'M 300 548 Q 315 535 326 490',
     'parent': '① 굳은 뒤에도 단단해지는 재료',
     'meaning': '결정 모형은 해수 반응을 설명합니다. 코어의 해수 반응 문구와 원리 제목을 가는 선으로 대응시킵니다.',
     'context': '해양 콘크리트의 원리와 항만 시료',
     'sites': [{'point': [246, 1497], 'name': '항만 시료 · 결정 관찰'}],
     'note': '항만 오브젝트가 해수 환경과 관찰 출처를 맡습니다. 지명과 시료 이름을 그 장소에 남깁니다.'},
    {'key': 'production', 'name': '제작 원리', 'title': '열과 석회 알갱이',
     'point': [75, 1005], 'caption': [119, 1150], 'core': [212, 1067],
     'path': 'M 119 1150 Q 153 1141 169 1110 Q 185 1085 212 1067',
     'parent': '② 뜨겁게 섞어 빨리 굳힘',
     'meaning': '제작 오브젝트와 알갱이 모형에 같은 원리 이름을 사용합니다. 남은 석회 알갱이가 균열 모형에서도 같은 형태로 등장하면 두 설명의 관계를 찾기 쉽습니다.',
     'context': '폼페이의 배합 흔적과 프리베르눔의 석회 입자',
     'sites': [{'point': [897, 1412], 'name': '폼페이 공사장 · 배합 흔적'},
               {'point': [1074, 1076], 'name': '프리베르눔 · 석회 입자'}],
     'note': '섞는 통은 공정을 설명하는 오브젝트입니다. 실제 배합·입자의 근거는 각각의 지역 오브젝트 옆에서 읽게 합니다.'},
    {'key': 'structure', 'name': '구조 원리', 'title': '하중이 기초로 이어짐',
     'point': [709, 1169], 'caption': [676, 1267], 'core': [608, 1245],
     'path': 'M 676 1267 Q 637 1284 608 1245',
     'parent': '③ 구조와 하중',
     'meaning': '현재 층 모형을 코어의 구조 설명과 대응시킵니다. 부위 확대인지 구조 설명 모형인지 캡션으로 역할을 명명합니다.',
     'context': '콜로세움의 절개·아치·볼트·기초',
     'sites': [{'point': [577, 855], 'name': '콜로세움 · 구조와 기초'}],
     'note': '그림의 단계별 재료가 실제 콜로세움 단면인지 근거 점검이 필요합니다. 실제 부위 확대는 정확한 부위에서 연결하고, 개념 모형은 코어 설명에 연결합니다.'},
    {'key': 'crack', 'name': '균열 원리', 'title': '물이 칼슘을 옮김',
     'point': [1084, 614], 'caption': [1082, 719], 'core': [1119, 844],
     'path': 'M 1082 719 Q 1142 761 1119 844',
     'parent': '④ 금을 메우고, 쓰면서 고침',
     'meaning': '모형의 내부 진행은 ‘균열 발생 → 물 유입 → 균열 충전’으로 읽습니다. 버팀벽에는 ‘사람이 보강’이라는 별도 행위 이름을 둡니다.',
     'context': '석회 입자에 관한 원리와 현대 재현 실험',
     'sites': [{'point': [587, 1557], 'name': '현대 실험실 · 균열 충전 시험'},
               {'point': [1074, 1076], 'name': '프리베르눔 · 석회 입자'}],
     'note': '떠 있는 실험실은 현대 시험의 맥락을 유지합니다. 재료 내부의 변화와 사람이 세운 버팀벽은 다른 행위 이름으로 구분합니다.'}
]

template = r'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>W3 · 지역과 설명 오브젝트의 관계 검토</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#eeeae3;color:#262521;font-family:"Noto Sans CJK KR","Apple SD Gothic Neo",sans-serif;line-height:1.65}
header{max-width:1450px;margin:auto;padding:28px 26px 20px}h1{font-size:26px;line-height:1.4;margin:0 0 10px}p{margin:8px 0}header p{max-width:1050px;font-size:15px;color:#53514c}
main{display:grid;grid-template-columns:minmax(0,1fr) 350px;gap:24px;max-width:1450px;padding:0 26px 36px;margin:auto;align-items:start}.scene{position:relative;background:white;box-shadow:0 5px 22px #0001}.scene img{width:100%;display:block}.scene svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
aside{background:#fffdf9;padding:22px;position:sticky;top:16px;border-radius:7px}h2{font-size:18px;line-height:1.45;margin:0 0 12px}nav{display:grid;grid-template-columns:1fr 1fr;gap:7px}button{font:inherit;background:#f0eee8;border:1px solid #d6d2c9;border-radius:4px;padding:9px 6px;cursor:pointer;font-size:13px}button.active{background:#263b35;color:white;border-color:#263b35}button:focus-visible,a:focus-visible{outline:3px solid #247e77;outline-offset:3px}
.options{border-block:1px solid #ddd7ce;margin:18px 0;padding:11px 0;display:grid;gap:8px;font-size:13px}.small{font-size:12px;color:#67635c}.role{font-size:12px;color:#247369;margin:16px 0 4px}.parent{font-size:13px;font-weight:700}.body{font-size:14px}.sites{font-size:13px;padding-left:18px}a{color:#14675b;text-underline-offset:3px}details{margin-top:17px;font-size:13px}summary{cursor:pointer;font-weight:600}
.hotspot{cursor:pointer;outline:none}.hotspot circle{fill:#fff;fill-opacity:.18;stroke:#147d72;stroke-width:3}.hotspot text{fill:#147d72;font-size:22px;font-weight:bold;paint-order:stroke;stroke:#fff;stroke-width:5}.hotspot.selected circle{fill:#d5ece6;fill-opacity:.5;stroke-width:5}.hotspot:focus-visible circle{stroke:#d78325;stroke-width:6}
.relation{fill:none;stroke:#137468;stroke-width:3;stroke-linecap:round}.endpoint{fill:#137468;stroke:white;stroke-width:1.5}.site{fill:none;stroke:#af7738;stroke-width:3;stroke-dasharray:6 5}.cross{stroke:#b74637;stroke-width:3;stroke-linecap:round}.origin{fill:none;stroke:#137468;stroke-width:2}
@media(max-width:850px){main{grid-template-columns:1fr;padding:0 12px 24px}header{padding:20px 16px}aside{position:static;order:-1}h1{font-size:21px}}
@media print{header,aside{display:none}main{display:block;padding:0}.scene{box-shadow:none;max-width:100%}body{background:white}}
</style></head><body>
<header><h1>지역 · 3D 오브젝트 · 설명의 관계</h1>
<p>현재 W3 장면에서 네 원리가 관련 코어와 어떤 관계인지 살펴봅니다. 코어 +30° · 디테일 −30°의 각도 구분과 실제 지역·오브젝트의 대응을 유지합니다. 번호 ①–⑤는 코어에만 사용하고, 디테일과 서포트는 이름으로 연결합니다.</p></header>
<main><div class="scene"><img src="data:image/png;base64,__IMAGE__" alt="콜로세움, 로마의 지역, 항만, 폼페이, 프리베르눔, 현대 실험실 오브젝트가 놓인 현재 W3 공간 모델">
<svg viewBox="0 0 1191 1684" aria-label="선택한 원리의 소속과 근거 위치를 보여주는 검토 표시"><g id="number-marks"></g><g id="relation"></g><g id="sites"></g><g id="hotspots"></g></svg></div>
<aside><h2>원리 하나를 선택해 보기</h2><nav id="choices"></nav>
<div class="options"><label><input type="checkbox" id="show-relation" checked> 관련 코어와의 설명 연결</label><label><input type="checkbox" id="show-sites" checked> 해당 지역·시료의 위치</label><label><input type="checkbox" id="show-numbers"> 이름으로 바꿀 반복 번호 표시</label></div>
<div class="role" id="role"></div><h2 id="title"></h2><p class="parent" id="parent"></p><p class="body" id="meaning"></p><ul class="sites" id="site-list"></ul><p class="small" id="note"></p>
<p class="small">초록 선: 원리 설명의 소속 · 갈색 범위: 근거를 읽을 장소 · 붉은 ×: 번호를 이름으로 바꿀 대상. 연결선과 위치 표시는 관계를 검토하기 위한 제안입니다.</p>
<details><summary>각도와 번호를 어떻게 구분하나</summary><p>코어 정보는 +30°, 디테일 정보는 −30°로 구분합니다. ①–⑤는 코어의 길·제목에만 사용합니다. 디테일에는 원리 이름, 서포트에는 번호 없이 장소·관찰 대상·실험 이름을 붙입니다. 버팀벽에는 행위 이름, 연표에는 연도·사건을 사용합니다. 균열 모형 안의 진행은 동사와 화살표로 표시합니다.</p></details>
<details><summary>벤치마크 원자료</summary><p><a href="https://www.johngrimwade.com/images/topkapi.jpg" target="_blank" rel="noopener">Topkapi — 번호 경로와 무번호 장소 상세</a></p><p><a href="https://interactives.natgeofe.com/high-touch/ngm-2202-notre-dame-graphics/builds/main/graphics_combined.html" target="_blank" rel="noopener">Notre-Dame — 실제 부위와 3D 조각의 대응</a></p><p><a href="https://parsnip-semicircle-ctmd.squarespace.com/stages-of-a-whale-fall/" target="_blank" rel="noopener">Whale-Fall — 장면·확대·내부 과정의 구분</a></p></details>
<p><a href="revision-proposal.md">수정 제안과 근거표 읽기</a></p><p class="small">화면은 현재 W3 위의 검토 표시입니다. 오브젝트 이동과 A2 출력 가독성은 확정하지 않았습니다.</p>
</aside></main><script>
const DETAILS=__DETAILS__;const MARKS=__MARKS__;const ns='http://www.w3.org/2000/svg';let selected=DETAILS[0].key;
function el(tag,attrs={},text=''){const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,v);if(text)n.textContent=text;return n}
const buttons=new Map();
for(const d of DETAILS){const b=document.createElement('button');b.textContent=d.name;b.addEventListener('click',()=>{selected=d.key;draw()});document.querySelector('#choices').append(b);buttons.set(d.key,b);
const g=el('g',{class:'hotspot',tabindex:'0',role:'button','aria-label':d.name,'data-key':d.key});g.append(el('circle',{cx:d.point[0],cy:d.point[1],r:36}),el('text',{x:d.point[0],y:d.point[1]+7,'text-anchor':'middle'},'＋'));g.addEventListener('click',()=>{selected=d.key;draw()});g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selected=d.key;draw()}});document.querySelector('#hotspots').append(g)}
for(const m of MARKS){const g=el('g',{class:'cross'});g.append(el('path',{d:`M ${m.x-9} ${m.y-9} L ${m.x+9} ${m.y+9} M ${m.x+9} ${m.y-9} L ${m.x-9} ${m.y+9}`}));g.append(el('title',{},m.name+' → 名前・役割へ'));document.querySelector('#number-marks').append(g)}
function draw(){const d=DETAILS.find(x=>x.key===selected);for(const [key,b] of buttons){b.classList.toggle('active',key===selected);b.setAttribute('aria-pressed',String(key===selected))}for(const g of document.querySelectorAll('.hotspot'))g.classList.toggle('selected',g.dataset.key===selected);
for(const [id,v] of Object.entries({role:d.name+' · 원리 설명 모형',title:d.title,parent:'관련 코어: '+d.parent,meaning:d.meaning,note:d.note}))document.getElementById(id).textContent=v;
const list=document.querySelector('#site-list');list.replaceChildren();for(const s of d.sites){const li=document.createElement('li');li.textContent=s.name;list.append(li)}
const r=document.querySelector('#relation');r.replaceChildren();if(document.querySelector('#show-relation').checked){r.append(el('path',{d:d.path,class:'relation'}));for(const p of [d.caption,d.core])r.append(el('circle',{cx:p[0],cy:p[1],r:5,class:'endpoint'}))}
const ss=document.querySelector('#sites');ss.replaceChildren();if(document.querySelector('#show-sites').checked)for(const s of d.sites){const c=el('circle',{cx:s.point[0],cy:s.point[1],r:46,class:'site'});c.append(el('title',{},s.name));ss.append(c)}
document.querySelector('#number-marks').style.display=document.querySelector('#show-numbers').checked?'':'none';}
for(const id of ['show-relation','show-sites','show-numbers'])document.getElementById(id).addEventListener('change',draw);draw();
</script></body></html>'''

html = template.replace('__IMAGE__', image_data).replace('__DETAILS__', json.dumps(details, ensure_ascii=False)).replace('__MARKS__', json.dumps(removed, ensure_ascii=False))
html = html.replace('名前・役割へ', '이름·역할로 변경')
(out / 'spatial-review.html').write_text(html)
(out / 'spatial-review.js').write_text(html.split('<script>',1)[1].split('</script>',1)[0])
(out / 'review-data.json').write_text(json.dumps({'details': details, 'numberReplacementTargets': removed}, ensure_ascii=False, indent=2))
print(json.dumps({'html': str(out/'spatial-review.html'), 'detailTopics': len(details), 'numberReplacementTargets': len(removed), 'originalImageBytes': (out/'current-W3-sketch.png').stat().st_size}, ensure_ascii=False))
