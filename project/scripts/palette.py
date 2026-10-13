"""디오라마 팔레트(OKLCH 정의) → Blender 선형 RGB / 인쇄용 sRGB hex.

성격 우선(파스텔: 높은 L, 낮은 C)으로 묶고, 색상은 로마 안료에서 고른다.
60(땅·중립) / 30(건축·안료) / 10(CORE 길 강조) 비율. 검정 글이 놓이는 땅은 L ≥ 0.90.
"""
import math

PALETTE = {
    # 이름: (L, C, h, 역할 설명)
    'ground_meadow': (0.915, 0.040, 118, '땅·풀밭(녹토 파스텔)'),
    'ground_road':   (0.955, 0.016, 85,  '길·광장(석회 백)'),
    'travertine':    (0.885, 0.042, 78,  '콜로세움(트래버틴)'),
    'tuff_stone':    (0.830, 0.048, 58,  '성벽·수도교·방파제(응회암)'),
    'terracotta':    (0.735, 0.085, 48,  '지붕·가마(적토)'),
    'ochre_field':   (0.870, 0.075, 88,  '밭·계단 언덕(황토)'),
    'house_wall':    (0.945, 0.020, 75,  '주택 벽(석회 회반죽)'),
    'water_river':   (0.815, 0.065, 222, '티베르강(이집션 블루 파스텔)'),
    'water_sea':     (0.760, 0.075, 232, '바다'),
    'mountain':      (0.855, 0.028, 285, '산맥(라벤더 회색)'),
    'volcano_ash':   (0.735, 0.022, 45,  '베수비오 사면(화산재)'),
    'volcano_dark':  (0.520, 0.020, 40,  '분화구'),
    'core_accent':   (0.640, 0.165, 30,  'CORE 길 강조(진사 버밀리언)'),
    'sky_ambient':   (0.950, 0.018, 285, '주변광(라벤더 하늘)'),
}


def oklch_to_linear_srgb(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return tuple(min(1.0, max(0.0, v)) for v in (r, g, bb))


def linear_to_hex(rgb):
    def enc(c):
        return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return '#' + ''.join(f'{round(enc(c) * 255):02X}' for c in rgb)


def in_gamut(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    rgb = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    return all(-1e-4 <= v <= 1 + 1e-4 for v in rgb)


LINEAR = {k: oklch_to_linear_srgb(*v[:3]) for k, v in PALETTE.items()}
HEX = {k: linear_to_hex(v) for k, v in LINEAR.items()}

if __name__ == '__main__':
    for k, (L, C, h, note) in PALETTE.items():
        print(f'{k:14s} oklch({L:.3f} {C:.3f} {h:3d})  {HEX[k]}  gamut={in_gamut(L, C, h)}  {note}')
