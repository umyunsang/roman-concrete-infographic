// Read-only use_figma script (fileKey jQPriO85F6wtPy1NPo752p). Run before and after the manual tile upload (step 3).
// 1) the print frame 810:78 must carry the same lettering as the design frame 790:78, shifted by the 8.5 pt bleed
//    (characters, size, fonts, fills, opacity, rotation); 2) returns the tile image hashes (= SHA-1 of the uploaded JPEGs).
// Expect: diffs = [], nTextPrint == nTextDesign, tiles[i].imageHash == shasum of <tag>_tile_<r?c?>.jpg.
const page = await figma.getNodeByIdAsync('19:4');
await figma.setCurrentPageAsync(page);
const tiles = [];
for (const id of ['810:187', '810:186', '810:185', '810:184']) {
  const n = await figma.getNodeByIdAsync(id);
  tiles.push({ id, name: n.name, fills: n.fills.map(f => ({ type: f.type, scaleMode: f.scaleMode, imageHash: f.imageHash })) });
}
const P = await figma.getNodeByIdAsync('810:78');
const D = await figma.getNodeByIdAsync('790:78');
const fillStr = t => t.getStyledTextSegments(['fills']).map(s => s.fills.map(f => f.type === 'SOLID'
  ? [f.color.r, f.color.g, f.color.b].map(v => Math.round(v * 255)).join(',') + '@' + (f.opacity ?? 1) : f.type).join('+')).join('|');
const fontStr = t => t.getStyledTextSegments(['fontName', 'fontSize']).map(s => s.fontName.family + ' ' + s.fontName.style + ' ' + s.fontSize).join('|');
const txt = root => root.findAllWithCriteria({ types: ['TEXT'] }).map(t => {
  const bb = t.absoluteBoundingBox, rb = root.absoluteBoundingBox;
  return { chars: t.characters, x: +(bb.x - rb.x).toFixed(2), y: +(bb.y - rb.y).toFixed(2), w: +bb.width.toFixed(2), h: +bb.height.toFixed(2),
           font: fontStr(t), fills: fillStr(t), visible: t.visible, opacity: t.opacity, rot: +t.rotation.toFixed(3) };
});
const tp = txt(P), td = txt(D), diffs = [], used = new Set();
for (const d of td) {
  const i = tp.findIndex((p, k) => !used.has(k) && p.chars === d.chars && Math.abs(p.x - d.x - 8.5) < 0.05 && Math.abs(p.y - d.y - 8.5) < 0.05);
  if (i < 0) { diffs.push({ missing_in_print: d }); continue; }
  used.add(i);
  for (const k of ['w', 'h', 'font', 'fills', 'visible', 'opacity', 'rot']) if (String(tp[i][k]) !== String(d[k])) diffs.push({ chars: d.chars, k, design: d[k], print: tp[i][k] });
}
tp.forEach((p, k) => { if (!used.has(k)) diffs.push({ extra_in_print: p }); });
return { tiles, nTextPrint: tp.length, nTextDesign: td.length, diffs };
