import numpy as np
def spline_clamped_nak(d, Q, t0):
    """cubic spline through Q (n+1, k) at params d; first derivative t0 at the start, not-a-knot at the end.
    Returns f(t) evaluating the curve (same as scipy CubicSpline(d, Q, bc_type=((1, t0), 'not-a-knot')))."""
    n = len(d) - 1; h = np.diff(d); K = Q.shape[1]
    A = np.zeros((4 * n, 4 * n)); B = np.zeros((4 * n, K)); r = 0
    # piece i: a + b x + c x^2 + e x^3, x = t - d_i
    for i in range(n):
        A[r, 4 * i] = 1; B[r] = Q[i]; r += 1
        A[r, 4 * i:4 * i + 4] = (1, h[i], h[i] ** 2, h[i] ** 3); B[r] = Q[i + 1]; r += 1
    for i in range(n - 1):
        A[r, 4 * i:4 * i + 4] = (0, 1, 2 * h[i], 3 * h[i] ** 2); A[r, 4 * (i + 1) + 1] = -1; r += 1
        A[r, 4 * i:4 * i + 4] = (0, 0, 2, 6 * h[i]); A[r, 4 * (i + 1) + 2] = -2; r += 1
    A[r, 1] = 1; B[r] = t0; r += 1
    A[r, 4 * (n - 2) + 3] = 1; A[r, 4 * (n - 1) + 3] = -1; r += 1
    Cf = np.linalg.solve(A, B).reshape(n, 4, K)
    def f(t):
        t = np.asarray(t, float); i = np.clip(np.searchsorted(d, t, side='right') - 1, 0, n - 1); x = (t - d[i])[:, None]
        c = Cf[i]; return c[:, 0] + c[:, 1] * x + c[:, 2] * x ** 2 + c[:, 3] * x ** 3
    return f
if __name__ == '__main__':
    from scipy.interpolate import CubicSpline
    rng = np.random.default_rng(3); Q = np.cumsum(rng.normal(0, 1, (16, 2)) + (1, 0.5), axis=0)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]; t0 = np.array((0.3, 0.95))
    cs = CubicSpline(d, Q, bc_type=((1, t0), 'not-a-knot')); f = spline_clamped_nak(d, Q, t0)
    t = np.linspace(0, d[-1], 2001); print('max diff vs scipy', np.abs(cs(t) - f(t)).max())
