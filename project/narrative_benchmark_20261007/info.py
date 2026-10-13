from PIL import Image
Image.MAX_IMAGE_PIXELS=None
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11'
for f in ['full/full_map_pass.png','full/full_overlay_pass.png','idpass/id_id_map.png','idpass/id_id_overlay.png']:
    im=Image.open(R+'/'+f); print(f, im.size, im.mode)
for a in ['shape_core1_marker','shape_d2_leader']:
    for f in ['context.png','isolated.png','isolated_rgba.png','iso_map_pass.png','iso_overlay_pass.png']:
        im=Image.open(f'{R}/assets/{a}/{f}'); print(a,f,im.size,im.mode)
