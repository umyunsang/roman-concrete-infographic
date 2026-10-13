"""Compose v8.2 Blender passes (CORE colour unified, timeline off, Roman milestone direction signs) without text."""
from pathlib import Path
from PIL import Image
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
maps=Image.open(ROOT/'renders/narrative_v8_2_milestones_map_pass.png').convert('RGBA')
overlay=Image.open(ROOT/'renders/narrative_v8_2_milestones_overlay_pass.png').convert('RGBA')
assert maps.size==overlay.size==(2381,3367),maps.size
out=Image.alpha_composite(maps,overlay).convert('RGB')
padded=Image.new('RGB',(2382,3368));padded.paste(out,(0,0))
padded.paste(out.crop((2380,0,2381,3367)),(2381,0));padded.paste(padded.crop((0,3366,2382,3367)),(0,3367))
dir=ROOT/'out/figma_import';dir.mkdir(exist_ok=True)
png=dir/'map_v8_2_milestones_without_text_2x.png';padded.save(png,optimize=True)
upload=png
if png.stat().st_size>10*1024*1024:
 upload=dir/'map_v8_2_milestones_without_text_2x.webp';padded.save(upload,'WEBP',lossless=True,quality=100,method=6)
assert padded.tobytes()==Image.open(upload).convert('RGB').tobytes()
assert upload.stat().st_size<10*1024*1024
padded.resize((1191,1684),Image.Resampling.LANCZOS).save(ROOT/'out/map_v8_2_milestones_without_text_1x.png')
receipt={'png':str(png),'upload':str(upload),'upload_bytes':upload.stat().st_size,'type':'image/webp'if upload.suffix=='.webp'else'image/png','pixels_identical':True,'size':list(padded.size),'sha256':hashlib.sha256(upload.read_bytes()).hexdigest()}
(ROOT/'out/milestones-map-v8_2-composition.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
