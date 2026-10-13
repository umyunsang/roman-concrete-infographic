"""시험: 화산 색 B_VG"""
import os, bpy
g = float(os.environ.get('B_VG', '1.0'))
bpy.data.objects['L07_vesuvius'].color = (g, g, g, 1)
print('volc', g)
