"""워커 B: terrain.py가 만드는 옛 평평한 땅판 T_ground를 렌더 전에 지움(같은 실행 안에서 렌더하면 T_land와 겹쳐 유령 선·흰 해안 벽이 생김)."""
import bpy
for o in [o for o in bpy.data.objects if o.name == 'T_ground']:
    bpy.data.objects.remove(o, do_unlink=True)
print('T_ground removed')
