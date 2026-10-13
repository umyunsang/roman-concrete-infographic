import bpy, sys, runpy, time
from pathlib import Path
argv = sys.argv[sys.argv.index('--') + 1:]
L = runpy.run_path(str(Path(__file__).resolve().parent / 'step.py'), run_name='roads_lib')
t = time.time(); print('BASE_SAMPLES', L['export_samples'](argv[0]), round(time.time() - t, 1), 's', 'cam', bpy.context.scene.camera.data.type)
