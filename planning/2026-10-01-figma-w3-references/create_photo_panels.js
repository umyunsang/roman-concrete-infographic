const specs = __PANEL_SPECS__;
const page = await figma.getNodeByIdAsync('19:4');
await figma.setCurrentPageAsync(page);
await Promise.all([
  figma.loadFontAsync({family:'Noto Sans KR',style:'Regular'}),
  figma.loadFontAsync({family:'Noto Sans KR',style:'Bold'})
]);
const createdNodeIds = [];
const photoTargets = [];
const panelRoots = [];
const ink = {r:0.07,g:0.07,b:0.07};
const muted = {r:0.35,g:0.35,b:0.35};
function remember(n) { createdNodeIds.push(n.id); return n; }
function text(parent, name, value, size, bold, width, color=ink) {
  const t=remember(figma.createText());
  t.fontName={family:'Noto Sans KR',style:bold?'Bold':'Regular'};
  t.name=name;
  t.fontSize=size;
  t.lineHeight={unit:'PIXELS',value:Math.round(size*1.45)};
  t.characters=value;
  t.fills=[{type:'SOLID',color}];
  t.textAutoResize='HEIGHT';
  t.resize(width,1);
  parent.appendChild(t);
  t.layoutSizingHorizontal='FIXED';
  t.layoutSizingVertical='HUG';
  return t;
}
function layout(parent, name, direction, width, spacing) {
  const n=remember(figma.createAutoLayout(direction));
  n.name=name;
  n.fills=[];
  n.itemSpacing=spacing;
  n.primaryAxisAlignItems='MIN';
  n.counterAxisAlignItems='MIN';
  n.resize(width,100);
  parent.appendChild(n);
  n.layoutSizingHorizontal='FIXED';
  n.layoutSizingVertical='HUG';
  return n;
}
for(const spec of specs) {
  const exists=page.children.find(n=>n.name===spec.name);
  if(exists) throw new Error('Panel already exists; inspect before recreating: '+exists.id);
  const panel=layout(page,spec.name,'VERTICAL',spec.width,24);
  panel.x=spec.x; panel.y=spec.y;
  panel.paddingLeft=24; panel.paddingRight=24;
  panel.paddingTop=24; panel.paddingBottom=24;
  panel.fills=[{type:'SOLID',color:{r:1,g:1,b:1}}];
  const inside=spec.width-48;
  const head=layout(panel,'사진 자료 제목','VERTICAL',inside,8);
  text(head,'사진 자료 제목',spec.title,30,true,inside);
  text(head,'W3 사진 대응 설명',spec.subtitle,15,false,inside,muted);
  const cardWidth=(inside-20*(spec.columns-1))/spec.columns;
  for(let i=0;i<spec.items.length;i+=spec.columns) {
    const row=layout(panel,'사진 행 '+(i/spec.columns+1),'HORIZONTAL',inside,20);
    for(const item of spec.items.slice(i,i+spec.columns)) {
      const card=layout(row,item.tag+' · '+item.title_ko,'VERTICAL',cardWidth,8);
      const photo=remember(figma.createRectangle());
      photo.name='사진 · '+item.id+' · '+item.title_ko;
      photo.resize(cardWidth,spec.imageHeight);
      photo.fills=[{type:'SOLID',color:{r:0.93,g:0.93,b:0.93}}];
      photo.placeholder=true;
      card.appendChild(photo);
      photo.layoutSizingHorizontal='FIXED';
      photo.layoutSizingVertical='FIXED';
      text(card,'사진 이름',item.tag+' · '+item.title_ko,18,true,cardWidth);
      text(card,'사진 내용과 W3 대응',item.caption_ko,13,false,cardWidth,muted);
      const link=text(card,'사진 출처 링크','출처 · '+item.source_label+' ↗',12,false,cardWidth,{r:0.18,g:0.29,b:0.40});
      link.hyperlink={type:'URL',value:item.source_page};
      photoTargets.push({id:item.id,tag:item.tag,photoNodeId:photo.id,cardNodeId:card.id,panelNodeId:panel.id,sourceNodeId:link.id,local_path:item.local_path});
    }
  }
  panelRoots.push({id:panel.id,name:panel.name,bounds:panel.absoluteBoundingBox,count:spec.items.length});
}
return {createdNodeIds,panelRoots,photoTargets,totalPhotos:photoTargets.length};
