"""Independent names generated from bounded user-authorized construction topology."""
import json
from pathlib import Path

def expected(report,root):
    prior=json.loads((Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/construction-detail')/'v11-saved-validation.json').read_text())
    out=set(prior['new_objects'])-{'NB_detail_calcium_clast','NB_detail4_micro','NB_detail4_matrix','NB_detail4_crack','NB_detail4_crystal'}
    out|={'NB_village_house','NB_village_market','NB_village_citizens','V_citizen_head','V_citizen_carried_amphora','V_citizen_jarhandle0','V_citizen_jarhandle1'}
    layout=json.loads((root/'copy/village_layout_v15.json').read_text())
    for i in range(len(layout['houses'])):
        if i:out.add(f'V_house_{i:02}')
        out.add(f'V_house_courtyard_{i:02}')
    for i in range(1,len(layout['citizens'])):
        n=f'V_citizens_{i:02}';out.add(n)
        out|={n+'__'+c for c in ['V_citizen_head','V_citizen_carried_amphora','V_citizen_jarhandle0','V_citizen_jarhandle1']}
    out|={'V_market_ground','V_making_ground','V_sw_workyard','V_se_workyard','V_grounded_research_building','V_research_ground'}
    for prefix in ['raw','rubble']:
        out.add(f'V_{prefix}_pile');out|={f'V_{prefix}_chunk{i:02}' for i in range(8)}
    for i in range(len(layout['walls'])):
        out|={f'V_mortar_wall_{i}',f'V_wall_core_{i}'}
        out|={f'V_wall_facing_{i}_{z}_{x}' for z in [.30,.80,1.30,1.80] for x in [-1.42,-.48,.48,1.42]}
        if i==0:out|={f'V_wall_lime_{k:02}' for k in range(9)}
        else:out|={f'V_wall_crack{k}' for k in range(4)}|{f'V_wall_whitefill{k}' for k in [2,3]}
    builder_children={n for n in prior['new_objects'] if n.startswith('NB_build_')}
    for i,s in enumerate(report['village']['scaffolds']):
        out.add(f'V_COL_scaffold_{i}')
        out|={f'V_COL_post_{i}_{a}_{b}' for a in [-1.9,1.9] for b in [.25,1.5]}
        for z in [s['platform_level']-2.7,s['platform_level']]:
            if z<1.:continue
            out|={f'V_COL_plank_{i}_{z}_{k}' for k in range(5)}
            out|={f'V_COL_rail_{i}_{z}_{b}' for b in [.25,1.5]}
        out|={f'V_COL_brace_{i}_{side}' for side in [-1.9,1.9]}
        n=f'V_COL_mason_{i}';out.add(n);out|={n+'__'+c for c in builder_children}
    for i in range(len(layout['col_rubble'])):
        out.add(f'V_COL_materials{i}');out|={f'V_COL_rubble_{i}_{k}' for k in range(4)}
    return out
