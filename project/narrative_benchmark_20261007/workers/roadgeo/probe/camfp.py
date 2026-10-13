import bpy, runpy, json, sys
H = runpy.run_path('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/scripts/integrate_assets.py', run_name='x')
r = H['source_fingerprints']([bpy.data.objects['CAM_iso']])['CAM_iso']
open(sys.argv[sys.argv.index('--') + 1], 'w').write(json.dumps(r, sort_keys=True, indent=0, default=str))
