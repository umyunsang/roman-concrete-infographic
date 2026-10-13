import sys, os, pickle
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WC/meas/c')
from m import *
from parts import segment, stats
from pairs import lit_of, pair, white_p95
def objm(seg, names): return np.isin(seg['O'], names) & seg['mask']
def matm(seg, key): return np.isin(seg['P'], [j for j, mn in enumerate(seg['mlist']) if key in mn])
which=sys.argv[1].split(',')
if 'c4' in which:
    s=segment('detail_core4_three_cubes')
    w=matm(s,'water_process'); body=matm(s,'specimen_matrix')
    wl=lit_of(s,w,erode=False); bl=lit_of(s,body)
    pair('C4 water(all)/body', wl, bl, 0.25)
    pair('C4 groove water/body', lit_of(s, objm(s,['R8_water_step1'])&w, erode=False), bl, 0.25)
    pair('C4 drops/body', lit_of(s, objm(s,['NB_core4_sequence_GRAY04'])&w, erode=False), bl, 0.25)
    lime=matm(s,'calcium_crystal'); print('C4 lime p95 %.1f'%white_p95(s,lime), ' healed p95 %.1f'%white_p95(s,objm(s,['R8_healed_step3'])&lime))
    cr=matm(s,'crack_groove'); Lc=lab(s['rgb'][cr])[:,0]; print('C4 crack p25 %.1f'%np.percentile(Lc,25), 'darkest face', darkest_face_median(s, body) if 'darkest_face_median' in dir() else '')
if 'c5' in which:
    s=segment('support_core5_lab')
    w=matm(s,'water_process'); spec=objm(s,['R1_specimen_healed','R1_specimen_leaking'])&~matm(s,'water')&~matm(s,'calcium')&~matm(s,'crack')
    bench=objm(s,['R1_lab_bench'])
    pud=objm(s,['R1_leak_puddle'])&w; drops=objm(s,['R1_leak_drop0','R1_leak_drop1','R1_leak_drop2'])&w
    pair('C5 puddle/bench', lit_of(s,pud), lit_of(s,bench), 0.25)
    pair('C5 drops/specimen', lit_of(s,drops,erode=False), lit_of(s,spec), 0.25)
    pair('C5 specimen/bench', lit_of(s,spec), lit_of(s,bench), 2)
    fill=objm(s,['R3_healed_fill']); gr=objm(s,['R1_healed_clast0','R1_healed_clast1','R1_healed_clast2'])
    print('C5 fill p95 %.1f grains p95 %.1f'%(white_p95(s,fill), white_p95(s,gr)))
    fl=lit_of(s,fill,erode=False); gl=lit_of(s,gr,erode=False)
    pair('C5 fill/grains', fl, gl, 0.25); pair('C5 fill/specimen', fl, lit_of(s,spec), 0.25)
    bl=lit_of(s,bench); print('C5 bench lit', hx(bl), lab(bl), 'oklch', oklch(bl))
    print('C5 bench top Lab vs K9 ref (58.1,-1.1,-1.4): dLab', lab(bl)-np.array([58.1,-1.1,-1.4]))
    sl=lit_of(s,spec); print('C5 specimen lit', hx(sl), lab(sl))
if 'd1' in which:
    s=segment('detail_d1_seawater')
    w=matm(s,'water_process'); con=objm(s,['D1_concrete']); tank=objm(s,['D1_tank_wall0','D1_tank_wall1','D1_tank_wall2','D1_tank_wall3','D1_tank_floor'])
    pair('D1 water/concrete', lit_of(s,w), lit_of(s,con), 0.25); pair('D1 water/tank', lit_of(s,w), lit_of(s,tank), 0.25)
if 'c3' in which:
    s=segment('detail_core3_lime_specimen')
    body=objm(s,['NB_lime_clast_specimen']); print('C3 body lit', hx(lit_of(s,body)), lab(lit_of(s,body)))
