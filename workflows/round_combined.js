export const meta = {
  name: 'poster-round-combined',
  description: 'One full review round: per-object critics (6 fields x asset batches) plus poster-level critics (7 fields) and the print-master critic, all blind',
  phases: [{ title: 'Object + poster review', detail: 'object_round.js and round_full.js side by side' }],
}
// args: { loopDir, objDir, round, printDir, tag, batches }
phase('Object + poster review')
const [obj, poster] = await Promise.all([
  workflow({ scriptPath: '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/object_round.js' },
    { loopDir: args.loopDir, objDir: args.objDir, round: args.round, makeRubrics: false, batches: args.batches }),
  workflow({ scriptPath: '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/round_full.js' },
    { loopDir: args.loopDir, round: args.round, printDir: args.printDir, tag: args.tag }),
])
const tally = {}
for (const r of (obj || []).filter(Boolean)) for (const a of r.assets) {
  tally[r.field] = tally[r.field] || { AAA: 0, other: 0 }
  tally[r.field][a.grade === 'AAA' ? 'AAA' : 'other']++
}
log('object: ' + Object.entries(tally).map(([k, v]) => `${k} ${v.AAA}/${v.AAA + v.other}`).join(' · '))
log('poster: ' + (poster || []).filter(Boolean).map(r => `${r.field} ${r.grade}`).join(' · '))
return { object: obj, poster }
