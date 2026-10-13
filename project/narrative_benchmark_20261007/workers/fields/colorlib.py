"""sRGB <-> Oklab/Oklch and CIELAB L* (D65), numpy, no deps beyond numpy."""
import numpy as np
def srgb_to_lin(c):
    c = np.asarray(c, float); return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lin_to_srgb(c):
    c = np.clip(np.asarray(c, float), 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)
def hex_to_srgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])
def srgb_to_hex(c):
    c = np.clip(np.round(np.asarray(c) * 255), 0, 255).astype(int); return '#%02X%02X%02X' % tuple(c)
def lin_to_oklab(l):
    l = np.asarray(l, float)
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
    lms = l @ M1.T; return np.cbrt(lms) @ M2.T
def oklab_to_lin(lab):
    lab = np.asarray(lab, float)
    M2i = np.array([[1, 0.3963377774, 0.2158037573], [1, -0.1055613458, -0.0638541728], [1, -0.0894841775, -1.2914855480]])
    M1i = np.array([[4.0767416621, -3.3077115913, 0.2309699292], [-1.2684380046, 2.6097574011, -0.3413193965], [-0.0041960863, -0.7034186147, 1.7076147010]])
    lms = (lab @ M2i.T) ** 3; return lms @ M1i.T
def oklch(lin):
    lab = lin_to_oklab(lin); C = np.hypot(lab[..., 1], lab[..., 2]); h = np.degrees(np.arctan2(lab[..., 2], lab[..., 1])) % 360
    return np.stack([lab[..., 0], C, h], -1)
def oklch_to_lin(L, C, h):
    return oklab_to_lin(np.array([L, C * np.cos(np.radians(h)), C * np.sin(np.radians(h))]))
def lstar(lin):
    Y = np.asarray(lin, float) @ np.array([0.2126729, 0.7151522, 0.0721750])
    f = np.where(Y > 216 / 24389, np.cbrt(Y), (24389 / 27 * Y + 16) / 116); return 116 * f - 16
def describe(hexv):
    l = srgb_to_lin(hex_to_srgb(hexv)); L, C, h = oklch(l); return dict(hex=hexv, L_star=round(float(lstar(l)), 1), okL=round(float(L), 3), C=round(float(C), 3), h=round(float(h), 1))
