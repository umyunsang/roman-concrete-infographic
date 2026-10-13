"""Part-color face selection for preserved v7 geometry. No data mutations.

Roles and intended sRGB colors:
concrete #B9BEC0; steel #344E5A;
labstone #B9C7C5; roof #527882; glass #3F9DAA; base #9FACA6.
The mesh is a stylized illustration. Window recesses are given glazing color;
this is visual interpretation, not proof of the original model's materials.
"""
import numpy as np

PALETTE={'concrete':'#B9BEC0','steel':'#344E5A','labstone':'#B9C7C5',
         'roof':'#527882','glass':'#3F9DAA','base':'#9FACA6'}

def select_arrays(name, centers, normals):
    """Classify original polygon centers/normals in the object's unchanged local space."""
    c,n=np.asarray(centers),np.asarray(normals)
    x,y,z=c.T
    if name=='NB_modern_building':
        # Two exposed narrow ladder/cage shapes occupy the middle of the short sides.
        # Heavy corner columns are at y~+-0.56, outside this region.
        side_cages=(np.abs(x)>.865)&(np.abs(y)<.115)&(z>.065)&(z<1.245)
        # A third small exposed front cage runs beside the x=-.42 column.
        # Only the bar surfaces protruding beyond the broad front concrete face are included.
        front_cage=(x>-.478)&(x<-.397)&(y<-.566)&(y>-.625)&(z>.065)&(z<1.245)
        # Floor concrete beams cross these regions; leave their broad z bands concrete.
        beam_band=((z>.385)&(z<.478))|((z>.807)&(z<.900))
        steel=(side_cages|front_cage)&~beam_band
        return {'steel':np.nonzero(steel)[0].tolist()}
    if name=='S_lab_island':
        # Rough island/plinth and peripheral utility shapes; house itself remains labstone.
        outside_house=(x<-1.35)|(x>2.83)|(y<-.29)|(y>2.76)
        base=(z<6.25)|((z<7.95)&outside_house)
        # Uppermost roof deck and its rooftop shapes, verified near z=9.45.
        roof=(z>9.425)&~base
        upper=(z>8.335)&(z<9.205)
        lower=(z>6.35)&(z<7.55)
        # The flat recessed panels are behind the lighter outer posts/cornices.
        panel_x=((x>-.65)&(x<.05))|((x>.45)&(x<1.10))|((x>1.43)&(x<2.15))
        front_upper=upper&panel_x&(y>.074)&(y<.205)&(n[:,1]<-.78)
        front_lower=lower&panel_x&(y>.055)&(y<.285)&(n[:,1]<-.45)
        side_upper=upper&(x>2.305)&(x<2.398)&(y>.47)&(y<2.065)&(n[:,0]>.78)
        side_lower=lower&(x>2.410)&(x<2.495)&(y>.32)&(y<1.99)&(n[:,0]>.45)
        back_upper=upper&panel_x&(y>2.355)&(y<2.407)&(n[:,1]>.78)
        left_upper=upper&(x>-.955)&(x<-.890)&(y>.46)&(y<2.055)&(n[:,0]<-.78)
        back_lower=lower&panel_x&(y>2.30)&(y<2.407)&(n[:,1]>.45)
        left_panel_y=((y>.32)&(y<.87))|((y>1.38)&(y<2.005))
        left_lower=lower&(x>-1.015)&(x<-.930)&left_panel_y&(n[:,0]<-.45)
        glass=(front_upper|front_lower|side_upper|side_lower|back_upper|left_upper|back_lower|left_lower)&~base&~roof
        return {'base':np.nonzero(base)[0].tolist(),'roof':np.nonzero(roof)[0].tolist(),
                'glass':np.nonzero(glass)[0].tolist()}
    raise ValueError(name)

def build_assignments(bpy):
    result={}
    expected={'NB_modern_building':(28609,24975),'S_lab_island':(4851,6783)}
    for name,(vertices,polygons) in expected.items():
        ob=bpy.data.objects[name]
        if ob.type!='MESH' or (len(ob.data.vertices),len(ob.data.polygons))!=(vertices,polygons):
            raise ValueError(f'{name}: expected preserved v7 mesh topology; face selection cannot be reused after remeshing')
        centers=np.array([p.center[:] for p in ob.data.polygons])
        normals=np.array([p.normal[:] for p in ob.data.polygons])
        faces=select_arrays(name,centers,normals)
        flat=[i for ids in faces.values() for i in ids]
        if len(flat)!=len(set(flat)):raise ValueError(f'{name}: overlapping assignments')
        counts={role:len(ids) for role,ids in faces.items()}
        default='concrete' if name=='NB_modern_building' else 'labstone'
        counts[default]=polygons-len(flat)
        result[name]={'default':default,'faces':faces,
            'notes':{'counts':counts,'palette':{k:PALETTE[k] for k in counts},
                'method':'Read-only local polygon-center/normal selection, bounded by manually inspected actual geometry views. No automatic semantic part recognition claimed.',
                'evidence':'part-color/modern-geometry-four-views.png; lab-geometry-four-views.png; modern-lab-part-audit.png',
                'steel_scope':'Only exposed narrow cage/bar shapes; broad columns and floor beams remain concrete.' if name=='NB_modern_building' else None,
                'glass_scope':'Window-colored recessed panels, not a claim of a scanned glazing material.' if name=='S_lab_island' else None}}
    return result
