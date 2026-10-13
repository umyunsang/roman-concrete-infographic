"""Read-only semantic face selection for the existing v7 process/observation meshes.

No geometry, object, material, scene, or file mutation occurs in build_assignments.
Selections use source-local coordinates, checked against isolated top/front/back
renders. All masks classify polygon centroids and are disjoint by precedence.
"""
import math

_EXPECTED = {'C2_hot_mixing': 15801, 'C5_researchers': 15813, 'L08_pompeii_site': 10528}


def _ellipsoid(p, center, radius):
    return sum(((p[k]-center[k])/radius[k])**2 for k in range(3)) <= 1


def _segment_distance(p, a, b):
    delta = [b[k]-a[k] for k in range(3)]
    t = max(0.0, min(1.0, sum((p[k]-a[k])*delta[k] for k in range(3)) / sum(v*v for v in delta)))
    return math.sqrt(sum((p[k]-(a[k]+t*delta[k]))**2 for k in range(3)))


def _mixing_role(p):
    x,y,z=p
    # Stirring shaft and broad wooden paddle: explicit oblique local-space line.
    if _segment_distance(p, (.075,.625,.335), (.675,.285,.865)) < .026:
        return 'toolwood'
    if -.045<x<.165 and .555<y<.675 and .315<z<.397:
        return 'toolwood'
    # The actual basin occupies part of the right figure's broad XY volume.
    # Resolve its low surface first so a garment box cannot leak onto the rim.
    r=math.hypot(x-.020,y-.015)
    if r<.528 and .20<z<.405:
        return 'mixture'
    if .51<r<.659 and .155<z<.335:
        return 'basin'
    # Heads and necks (not the whole upper-body height band).
    if _ellipsoid(p, (-.51,.455,.87), (.105,.11,.125)) and z>.768:
        return 'skin'
    if _ellipsoid(p, (.365,.650,.915), (.125,.125,.13)) and z>.81:
        return 'skin'
    # Exposed hands/forearms and left worker's lower legs.
    if _ellipsoid(p, (-.585,.378,.628), (.13,.060,.060)):
        return 'skin'
    if _ellipsoid(p, (-.362,.478,.628), (.075,.083,.069)):
        return 'skin'
    if _ellipsoid(p, (.298,.494,.535), (.070,.074,.10)):
        return 'skin'
    if _ellipsoid(p, (.602,.384,.735), (.060,.062,.074)):
        return 'skin'
    if -.72<x<-.45 and .395<y<.67 and .08<z<.37:
        return 'skin'
    # A short tunic at left, and long apron/robe at right. The basin masks below
    # only operate under z=.4 so never paint garments by radial overlap.
    if -.765<x<-.27 and .30<y<.70 and z>.37:
        return 'linen'
    if .19<x<.655 and .395<y<.85 and z>.24:
        return 'cloth' if z<.61 else 'linen'
    return None


def _observation_role(p):
    x,y,z=p
    # Four local-volume masks, rather than a global body-height band: the
    # supporting arch and all surrounding masonry remain roman_stone.
    people=[
        ((-.65,.018),(.145,.12),(.16,.70),(-.65,.018,.656),(.060,.065,.068),'linen'),
        ((-.187,-.235),(.16,.115),(.16,.675),(-.184,-.234,.632),(.063,.069,.068),'linen'),
        # Rear observer's face was ray-probed in the exact audit camera:
        # face 10624 hits local (-.04946, .33912, .62255).
        ((-.055,.395),(.145,.145),(.16,.715),(-.055,.392,.645),(.071,.086,.078),'linen'),
        ((.694,-.385),(.105,.10),(.16,.565),(.698,-.376,.531),(.053,.056,.047),'cloth'),
    ]
    # Tripod and its small optical instrument occupy a separate front volume.
    if -.04<x<.23 and -.35<y<-.115 and .162<z<.56:
        return 'toolmetal'
    for (cx,cy),(rx,ry),(zmin,zmax),head,headr,clothing in people:
        if ((x-cx)/rx)**2+((y-cy)/ry)**2<1 and zmin<z<zmax:
            if _ellipsoid(p,head,headr):return 'skin'
            return clothing
    return None


def _pompeii_role(p):
    x,y,z=p
    # Separate scaffold posts in front of the wall, and upper peg ends. Wood
    # assignment stays outside the back wall's broad face (y around .59).
    posts=[(-.623,.267,.155,.72),(-.014,.271,.15,.72),(.469,.203,.17,1.40),(.925,.206,.05,1.03)]
    for cx,cy,lo,hi in posts:
        if abs(x-cx)<.037 and abs(y-cy)<.054 and lo<z<hi:
            return 'toolwood'
    for cx in [-.61,-.015,.47,.89]:
        if abs(x-cx)<.028 and .55<y<.665 and .925<z<1.075:
            return 'toolwood'
    # Horizontal scaffolding decks, narrow horizontal support rail, diagonal
    # bracing. Decks stop ahead of the wall so masonry is not recolored.
    if -.675<x<.025 and .225<y<.545 and (abs(z-.446)<.026 or abs(z-.660)<.030):
        return 'toolwood'
    if .432<x<.975 and .174<y<.545 and (abs(z-.452)<.022 or abs(z-.866)<.022):
        return 'toolwood'
    if _segment_distance(p,(.473,.208,.43),(.929,.208,.855))<.027:
        return 'toolwood'
    if _segment_distance(p,(.473,.208,.853),(.929,.208,.448))<.024:
        return 'toolwood'
    if _segment_distance(p,(-.86,.599,.977),(-.565,.599,.977))<.026:
        return 'toolwood'
    # Large foreground mixing bowl: outer wall/rim vs its schematic powder
    # heap. Geometry proves a pile, not the historical chemical identity.
    r=math.hypot(x-.625,y+.082)
    if r<.190 and .25<z<.57:
        return 'raw_lime'
    if r<.258 and .165<z<.42:
        return 'basin'
    # Small recognizable vessels at foreground and the left bucket.
    for cx,cy,rr,zlo,zhi in [(-.379,.095,.096,.16,.35),(-.180,.098,.085,.16,.41),(-.799,.568,.105,.14,.42)]:
        if math.hypot(x-cx,y-cy)<rr and zlo<z<zhi:
            return 'basin'
    return None


def build_assignments(bpy):
    """Return default roles and polygon-index overrides, without modifying bpy."""
    classifiers={'C2_hot_mixing':_mixing_role,'C5_researchers':_observation_role,'L08_pompeii_site':_pompeii_role}
    notes={
        'C2_hot_mixing':[
            'Two workers: head/neck and exposed extremities skin; short tunic linen; long lower apron/robe cloth.',
            'Circular raised basin and filled mixture surface separated; oblique stirring shaft/paddle toolwood.',
            'Ground and unidentifiable scattered angular fragments stay roman_stone; no chemical assertion from their shape.',
        ],
        'C5_researchers':[
            'Four small observation figures are bounded spatially, not by a global height band; surrounding arch stays roman_stone.',
            'Foreground tripod/optical device toolmetal; facial volumes skin, garments linen/cloth.',
            'Very small fingers, shoes, and backs partly fused to masonry remain conservative garment/stone colors.',
        ],
        'L08_pompeii_site':[
            'Front scaffold posts/decks/diagonal bracing toolwood; wall and indistinct construction blocks remain roman_stone.',
            'Foreground bowl and small vessels basin; central foreground pale powder heap raw_lime is a schematic palette role, not proof of lime chemistry.',
            'No confidently identifiable human face/body in this mesh at the inspected views: no skin/cloth assignment on ambiguous scaffold lumps.',
        ],
    }
    result={}
    for name,classify in classifiers.items():
        ob=bpy.data.objects.get(name)
        if ob is None or ob.type!='MESH':raise ValueError('Missing expected mesh: '+name)
        if len(ob.data.polygons)!=_EXPECTED[name]:raise ValueError('Face topology changed: '+name)
        faces={}
        for poly in ob.data.polygons:
            role=classify(tuple(poly.center))
            if role:faces.setdefault(role,[]).append(poly.index)
        assert sum(len(a) for a in faces.values())==len(set(i for a in faces.values() for i in a))
        result[name]={'default':'roman_stone','faces':faces,'notes':notes[name]}
    return result
