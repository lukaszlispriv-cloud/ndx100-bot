"""Biblioteka pomocnicza (czysty Python, bez numpy) do dekompozycji wyników W1–W7.

Dane: closes_5y.csv (zamknięcia dzienne, surowe, bez korekty o dywidendy).
"""
import csv, math

CSV = '/tmp/claude-0/-home-user-ndx100-bot/c6f6cc06-201a-5d61-83f7-57dd73cc6d16/scratchpad/dane/closes_5y.csv'


def load_closes(path=CSV):
    rows = list(csv.DictReader(open(path, encoding='utf-8')))
    rows = [r for r in rows if r.get('^NDX')]          # wiersze świąt (puste) odpadają
    dates = [r['date'] for r in rows]
    cols = [c for c in rows[0].keys() if c != 'date']
    px = {c: [float(r[c]) if r[c] else None for r in rows] for c in cols}
    return dates, px


def rets(series):
    out = [None]
    for a, b in zip(series[:-1], series[1:]):
        out.append(b / a - 1 if (a and b) else None)
    return out


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def sd(xs, ddof=1):
    xs = [x for x in xs if x is not None]
    n = len(xs)
    if n - ddof <= 0:
        return None
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - ddof))


def corr(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 3:
        return None
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pairs)
    sxx = sum((p[0] - mx) ** 2 for p in pairs)
    syy = sum((p[1] - my) ** 2 for p in pairs)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else None


def solve(A, b):
    """Rozwiązanie układu A x = b eliminacją Gaussa z wyborem elementu głównego."""
    n = len(A)
    M = [row[:] + [bv] for row, bv in zip(A, b)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i]))
        M[i], M[p] = M[p], M[i]
        if abs(M[i][i]) < 1e-14:
            raise ValueError('macierz osobliwa')
        for r in range(n):
            if r != i:
                f = M[r][i] / M[i][i]
                for c in range(i, n + 1):
                    M[r][c] -= f * M[i][c]
    return [M[i][n] / M[i][i] for i in range(n)]


def ols(y, X, intercept=True):
    """OLS: y (lista), X (lista wierszy). Zwraca dict: beta, se, r2, resid, n, tstat."""
    data = [(yy, xx) for yy, xx in zip(y, X) if yy is not None and all(v is not None for v in xx)]
    n = len(data)
    if n < 10:
        return None
    Y = [d[0] for d in data]
    Xm = [([1.0] if intercept else []) + list(d[1]) for d in data]
    k = len(Xm[0])
    XtX = [[sum(Xm[r][i] * Xm[r][j] for r in range(n)) for j in range(k)] for i in range(k)]
    Xty = [sum(Xm[r][i] * Y[r] for r in range(n)) for i in range(k)]
    beta = solve(XtX, Xty)
    fitted = [sum(b * x for b, x in zip(beta, row)) for row in Xm]
    resid = [yy - f for yy, f in zip(Y, fitted)]
    ssr = sum(e * e for e in resid)
    my = sum(Y) / n
    sst = sum((yy - my) ** 2 for yy in Y)
    r2 = 1 - ssr / sst if sst > 0 else None
    dof = n - k
    s2 = ssr / dof if dof > 0 else float('nan')
    # (X'X)^-1 przez rozwiązanie k układów
    inv = []
    for j in range(k):
        e = [1.0 if i == j else 0.0 for i in range(k)]
        inv.append(solve(XtX, e))
    se = [math.sqrt(max(s2 * inv[i][i], 0)) for i in range(k)]
    t = [b / s if s > 0 else None for b, s in zip(beta, se)]
    return {'beta': beta, 'se': se, 't': t, 'r2': r2, 'resid': resid, 'n': n, 'sigma': math.sqrt(s2)}


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (centre - half, centre + half)


def binom_two_sided_p(k, n, p0=0.5):
    """Dokładny dwustronny test dwumianowy (suma prawdopodobieństw ≤ P(k))."""
    from math import comb
    pk = comb(n, k) * p0 ** k * (1 - p0) ** (n - k)
    tot = 0.0
    for i in range(n + 1):
        pi = comb(n, i) * p0 ** i * (1 - p0) ** (n - i)
        if pi <= pk + 1e-15:
            tot += pi
    return min(tot, 1.0)


def t_pvalue_two_sided(t, dof):
    """Przybliżenie p-value dla rozkładu t (numeryczna całka funkcji gęstości)."""
    if t is None or dof <= 0:
        return None
    from math import lgamma, exp, log, pi
    def pdf(x):
        return exp(lgamma((dof + 1) / 2) - lgamma(dof / 2) - 0.5 * log(dof * pi)
                   - (dof + 1) / 2 * log(1 + x * x / dof))
    a = abs(t)
    # całka od a do a+40 metodą Simpsona (ogon dalej pomijalny dla dof>=3)
    N = 20000
    hi = a + 60
    h = (hi - a) / N
    s = pdf(a) + pdf(hi)
    for i in range(1, N):
        s += pdf(a + i * h) * (4 if i % 2 else 2)
    tail = s * h / 3
    return min(2 * tail, 1.0)
