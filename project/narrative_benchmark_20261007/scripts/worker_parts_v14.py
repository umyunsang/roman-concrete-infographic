"""Pure material and correction selections for the three inspected Meshy workers.

Coordinates are mesh-local after integrate_assets.H.import_glb has baked glTF
transforms, centered XY, and put the original bottom at Z=0. Apply material
masks BEFORE carrier surgery. All source GLBs remain untouched. No bpy data
is mutated by these functions. Root alone removes/copies/adds geometry.

Carrier is a rejected bucket-head generation, not a valid mortar carrier.
Builder has one block, not a wall. Pair's actual shallow trough is empty.
No faces are claimed as mortar fill or nonexistent wall/form geometry.
"""
import numpy as np

PALETTE = {
    'skin': '#C99C78',
    'linen': '#DED1AF',
    'worker_cloth': '#B77B60',
    'worker_dark': '#735A42',
    'toolwood': '#8D6C49',
    'toolmetal': '#526873',
    'roman_stone': '#D3BE9E',
    # For root's separately created, explicit fill only; no source faces.
    'worker_mortar': '#B5AD97',
}

EXPECTED_FACES = {
    'NB_worker_carrier': 20669,
    'NB_worker_builder': 20601,
    'NB_worker_pair': 20763,
}

CORRECTION_GUIDES = {
    'carrier_neck_cut_z': 1.435,
    'carrier_original_head_bucket_center': [0.025, -0.034, 1.666],
    'carrier_neck_target_center': [0.020, -0.060, 1.435],
    'carrier_hand_centers': [[-0.173, -0.345, 1.155], [0.207, -0.341, 1.150]],
    'carrier_unwanted_bar_axes': [
        [[-0.340, -0.264, 1.464], [-0.122, -0.356, 1.044]],
        [[0.403, -0.276, 1.494], [0.159, -0.300, 1.030]],
    ],
    'builder_head_center': [-0.013, -0.259, 1.728],
    'builder_head_selection': 'z>1.55, -.245<x<.235, y<.06; head/upper neck only, avoid rear shoulder.',
    'pair_trough_candidate_fill_box': [[-0.145, -0.175, 0.980], [0.085, -0.035, 1.012]],
    'pair_trough_fill_note': 'A small inset fill surface, not the full trough outside bbox. Trough is slightly oblique; root checks final view.',
}

def _geometry(ob):
    mesh=ob.data
    v=np.empty(len(mesh.vertices)*3,dtype=np.float64)
    c=np.empty(len(mesh.polygons)*3,dtype=np.float64)
    mesh.vertices.foreach_get('co',v);mesh.polygons.foreach_get('center',c)
    return v.reshape(-1,3),c.reshape(-1,3)

def _ellipsoid(p,center,radius):
    return np.sum(((p-np.asarray(center))/np.asarray(radius))**2,axis=1)<1

def _segment(p,a,b,radius):
    a=np.asarray(a);d=np.asarray(b)-a
    t=np.clip(((p-a)@d)/(d@d),0,1)
    return np.linalg.norm(p-a-t[:,None]*d,axis=1)<radius

def _ids(mask):
    return np.flatnonzero(mask).astype(int).tolist()

def _carrier_corrections(c):
    # At the inspected cutoff, the wrong bucket/fake upper hands are removed
    # as one compact head region. Root supplies a proper head separately.
    head=c[:,2]>CORRECTION_GUIDES['carrier_neck_cut_z']
    hands=np.zeros(len(c),dtype=bool)
    for center in CORRECTION_GUIDES['carrier_hand_centers']:
        hands|=_ellipsoid(c,center,[.068,.085,.090])
    bars=np.zeros(len(c),dtype=bool)
    for a,b in CORRECTION_GUIDES['carrier_unwanted_bar_axes']:
        bars|=_segment(c,a,b,.047)
    # Preserve palm volumes. Remaining buried bar pieces are occluded; root
    # can form new bucket handles into the preserved, actual lower hands.
    bars&=~hands&~head
    return {'head_bucket':head,'unwanted_hand_bars':bars,'preserve_lower_hands':hands&~head}

def _builder_head(c):
    x,y,z=c.T
    return (z>1.55)&(x>-.245)&(x<.235)&(y<.06)

def _carrier_roles(c):
    x,y,z=c.T
    role=np.full(len(c),'linen',dtype=object)
    # Actual lower legs; short garment hem is above this bounded low region.
    role[z<.590]='skin'
    # Existing sandals, not all lower legs: front foot and raised rear foot.
    shoe=(z<.115)|((x>.135)&(y>.13)&(z<.240))
    role[shoe]='worker_dark'
    arms=np.zeros(len(c),dtype=bool)
    for a,b,r in [
        ((-.31,.080,1.37),(-.32,-.13,1.20),.081),
        ((-.32,-.13,1.20),(-.173,-.345,1.155),.077),
        ((.30,.075,1.38),(.31,-.13,1.21),.078),
        ((.31,-.13,1.21),(.207,-.341,1.150),.078),
    ]: arms|=_segment(c,a,b,r)
    for center in CORRECTION_GUIDES['carrier_hand_centers']:
        arms|=_ellipsoid(c,center,[.078,.097,.100])
    role[arms]='skin'
    # Narrow existing belt around the waist; no historic leather assertion.
    role[(z>1.080)&(z<1.118)&(np.abs(x)<.265)&(y>-.23)]='worker_dark'
    corrections=_carrier_corrections(c)
    role[corrections['head_bucket']|corrections['unwanted_hand_bars']]='toolwood'
    return role

def _builder_roles(c):
    x,y,z=c.T
    role=np.full(len(c),'linen',dtype=object)
    # Actual square masonry block in front of the kneeling figure.
    block=(x>.040)&(y<-.180)&(z<.630)
    role[block]='roman_stone'
    # Existing vertical punch/mallet shank and its broad horizontal handle.
    tool=(x>.195)&(y>-.330)&(y<.075)&(z>.565)&(z<.925)
    role[tool]='toolwood'
    shank=(x>.255)&(x<.445)&(y>-.290)&(y<-.145)&(z>.565)&(z<.745)
    role[shank]='toolmetal'
    # Exposed left arm from the sleeveless shoulder to its real front hand.
    arm=np.zeros(len(c),dtype=bool)
    for a,b,r in [
        ((-.31,-.20,1.47),(-.46,-.24,1.13),.151),
        ((-.46,-.24,1.13),(-.15,-.47,.956),.117),
        ((.126,.16,1.28),(.190,.045,1.01),.095),
        ((.190,.045,1.01),(.306,-.190,.881),.096),
    ]:arm|=_segment(c,a,b,r)
    for center,radius in [((-.090,-.525,.928),(.125,.090,.105)),((.300,-.197,.890),(.105,.085,.082))]:
        arm|=_ellipsoid(c,center,radius)
    # The broad upper-left arm stays beyond the chest volume, even where its
    # irregular triangulation spans the segment boundary.
    arm|=(x<-.280)&(y<.055)&(z>1.065)&(z<1.515)
    role[arm&~block]='skin'
    # Visible front kneeling knee stays below garment hem, in its own volume.
    knee=_ellipsoid(c,(-.140,-.225,.260),(.174,.161,.248))|(z<.340)
    role[knee&~block]='skin'
    # Existing bent rear foot/sandal remains separate from the front knee.
    shoe=(x<-.305)&(y>.055)&(z<.395)
    role[shoe&~block]='worker_dark'
    head=_builder_head(c)
    face_lower=(z>1.490)&(z<1.680)&(x>-.220)&(x<.210)&(y<-.185)
    role[head|face_lower]='skin'
    # Actual modeled hair cap occupies the upper dome of the source head.
    hair=head&((z>1.775)|((y>-.100)&(z>1.640)))
    role[hair]='worker_dark'
    # Resolve the whole existing block last so the knee never colors its
    # low left side when a large irregular triangle crosses the knee volume.
    role[block]='roman_stone'
    return role

def _pair_roles(c):
    x,y,z=c.T
    role=np.full(len(c),'linen',dtype=object)
    # Root-requested quiet warm tunic on the actual left figure. Skin, hair,
    # sandals, and the central trough keep their later override precedence.
    role[x<0]='worker_cloth'
    # Trough occupies the small central gap below the inner hands. Source
    # contains no independently readable filled mortar surface.
    # Keep the central basin surface, excluding nearby inner garment faces.
    # Small fused end regions remain linen/skin; no brown patch on the hips.
    trough=(x>-.220)&(x<.175)&(y>-.350)&(y<-.020)&(z>.840)&(z<1.080)
    role[trough]='toolwood'
    for hx,hy in [(-.425,.051),(.364,.070)]:
        head=_ellipsoid(c,(hx,hy,1.716),(.152,.184,.233))&(z>1.517)
        role[head]='skin'
        role[head&(z>1.811)]='worker_dark'
    # Inner and outer lower arms begin below each actual short sleeve.
    arms=np.zeros(len(c),dtype=bool)
    for a,b,r in [
        ((-.555,.250,1.285),(-.533,.301,1.02),.111),
        ((-.241,.181,1.285),(-.174,-.175,1.095),.111),
        ((.159,.140,1.285),(.111,-.141,1.108),.111),
        ((.602,.140,1.285),(.573,.200,1.025),.111),
    ]:arms|=_segment(c,a,b,r)
    for center in [(-.545,.288,1.005),(-.195,-.198,1.090),(.115,-.164,1.103),(.588,.243,1.012)]:
        arms|=_ellipsoid(c,center,[.095,.110,.107])
    # Keep garment side faces out of broadened arm volumes. Actual forearms
    # occupy the two outer strips and the open gap between the figures.
    arm_strips=(x<-.535)|((x>-.265)&(x<.195))|(x>.535)
    role[arms&arm_strips&(z<1.325)]='skin'
    # Exposed shin/ankle volumes end below the actual garment hem.
    role[(z<.564)&~trough]='skin'
    # Front soles and raised rear sandals, with explicit spatial volumes.
    shoe=(z<.102)|((x<-.300)&(y>.05)&(z<.245))|((x>.27)&(y>.18)&(z<.245))
    role[shoe]='worker_dark'
    return role

def build_correction_masks(bpy):
    """Read-only surgical selections for root, on original imported topology."""
    result={}
    for name in EXPECTED_FACES:
        ob=bpy.data.objects.get(name)
        if ob is None or ob.type!='MESH':continue
        if len(ob.data.polygons)!=EXPECTED_FACES[name]:
            raise ValueError('Apply correction selections before topology edits: '+name)
        v,c=_geometry(ob)
        if name=='NB_worker_carrier':masks=_carrier_corrections(c)
        elif name=='NB_worker_builder':masks={'head_for_copy':_builder_head(c)}
        else:
            x,y,z=c.T
            masks={'actual_trough':(x>-.270)&(x<.230)&(y>-.360)&(y<.140)&(z>.840)&(z<1.090)}
        entry={}
        for label,mask in masks.items():
            ids=_ids(mask);vi=np.unique([j for i in ids for j in ob.data.polygons[i].vertices])
            entry[label]={'faces':ids,'face_count':len(ids),'bbox':[v[vi].min(0).tolist(),v[vi].max(0).tolist()] if len(vi) else None}
        result[name]=entry
    return result

def build_assignments(bpy):
    """Pure, disjoint material masks; apply before carrier surgery."""
    result={}
    for name,build in [('NB_worker_carrier',_carrier_roles),('NB_worker_builder',_builder_roles),('NB_worker_pair',_pair_roles)]:
        ob=bpy.data.objects.get(name)
        if ob is None or ob.type!='MESH':continue
        if len(ob.data.polygons)!=EXPECTED_FACES[name]:
            raise ValueError('Worker masks require original pre-surgery topology: '+name)
        v,c=_geometry(ob);roles=build(c)
        faces={r:_ids(roles==r)for r in sorted(set(roles))if r!='linen'}
        result[name]={'default':'linen','faces':faces,'notes':{
            'local_bbox':[v.min(0).tolist(),v.max(0).tolist()],
            'source_face_count':EXPECTED_FACES[name],
            'explicit_face_counts':{r:len(ids)for r,ids in faces.items()},
            'default_face_count':int(np.count_nonzero(roles=='linen')),
            'actual_mortar_fill_faces':0,
            'actual_wall_or_form_faces':0,
            'carrier_requires_geometry_correction':name=='NB_worker_carrier',
            'use_order':'Apply assignments before carrier surgery; preserve materials when copying builder head.',
            'illustrative_materials':'Palette roles distinguish actual visible parts, not verified historical material composition.',
        }}
    return result
