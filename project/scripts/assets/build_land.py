"""땅 전체 다시 만들기 (v2): terrain.py(바다·강 수면; T_ground는 지움) + terrain_mesh.py(맵 전체 높이장 → T_land).
먼저 시스템 python3로 terrain_polys.py → terrain_hf.py <dem 폴더> 를 돌려 둘 것.
Blender에서: exec(open(<이 파일>).read())
"""
import bpy

S = '/Users/um-yunsang/Documents/로마콘크리트_3D/scripts/assets/'
U = bpy.data.texts['asset_utils.py'].as_module()
exec(open(S + 'terrain.py').read())
U.remove_obj('T_ground')
U.remove_obj('L01_apennines')
exec(open(S + 'terrain_mesh.py').read())
