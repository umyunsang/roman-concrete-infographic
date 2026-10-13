import bpy, sys, json
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WD1')
import wd1lib as L
out = sys.argv[sys.argv.index('--') + 1]
fp = L.fingerprint(set())
fp['_materials'] = {m.name: L.mat_sig(m) for m in bpy.data.materials}
json.dump(fp, open(out, 'w'), sort_keys=True)
print('FPDUMP', len(fp))
