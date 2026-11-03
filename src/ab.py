"""Funciones estadísticas para analizar el A/B test (proporciones, bootstrap, potencia)."""
import numpy as np
from scipy import stats
from scipy.optimize import brentq


def wilson_ci(x, n, alpha=0.05):
    """Intervalo de Wilson para una proporción."""
    z = stats.norm.ppf(1 - alpha / 2)
    p = x / n
    denom = 1 + z**2 / n
    centro = (p + z**2 / (2 * n)) / denom
    mitad = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return centro - mitad, centro + mitad


def compare_proportions(x1, n1, x0, n0, alpha=0.05):
    """Compara la tasa del grupo 1 (tratamiento) contra la del grupo 0 (referencia).

    - Diferencia absoluta con IC de Newcombe (híbrido de intervalos de Wilson).
    - Prueba z de dos proporciones (error estándar combinado), bilateral.
    - Razón de tasas (aumento relativo + 1) con IC en escala logarítmica.
    """
    p1, p0 = x1 / n1, x0 / n0
    diff = p1 - p0

    l1, u1 = wilson_ci(x1, n1, alpha)
    l0, u0 = wilson_ci(x0, n0, alpha)
    lo = diff - np.sqrt((p1 - l1) ** 2 + (u0 - p0) ** 2)
    hi = diff + np.sqrt((u1 - p1) ** 2 + (p0 - l0) ** 2)

    p_comb = (x1 + x0) / (n1 + n0)
    se = np.sqrt(p_comb * (1 - p_comb) * (1 / n1 + 1 / n0))
    if se > 0:
        z = diff / se
        p_valor = 2 * stats.norm.sf(abs(z))
    else:  # sin eventos en ningún grupo
        z, p_valor = np.nan, 1.0

    # La razón de tasas solo está definida si hay eventos en ambos grupos
    if x1 > 0 and x0 > 0:
        rr = p1 / p0
        se_log = np.sqrt(1 / x1 - 1 / n1 + 1 / x0 - 1 / n0)
        za = stats.norm.ppf(1 - alpha / 2)
        rr_bajo, rr_alto = rr * np.exp(-za * se_log), rr * np.exp(za * se_log)
    else:
        rr = rr_bajo = rr_alto = np.nan
    return {
        "p1": p1, "p0": p0, "diff": diff, "ic_bajo": lo, "ic_alto": hi,
        "z": z, "p_valor": p_valor,
        "rr": rr, "rr_bajo": rr_bajo, "rr_alto": rr_alto,
    }


def holm_adjust(pvals):
    """P-valores ajustados por el método de Holm-Bonferroni."""
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    orden = np.argsort(p)
    ajustados = np.empty(m)
    maximo = 0.0
    for rango, idx in enumerate(orden):
        maximo = max(maximo, (m - rango) * p[idx])
        ajustados[idx] = min(1.0, maximo)
    return ajustados


def bootstrap_means(x, n_boot=10_000, rng=None, chunk=500):
    """Distribución bootstrap de la media de x (remuestreo con reemplazo)."""
    rng = rng if rng is not None else np.random.default_rng()
    x = np.asarray(x, dtype=float)
    n = len(x)
    medias = np.empty(n_boot)
    for ini in range(0, n_boot, chunk):
        b = min(chunk, n_boot - ini)
        idx = rng.integers(0, n, size=(b, n))
        medias[ini:ini + b] = x[idx].mean(axis=1)
    return medias


def welch_diff(a, b, alpha=0.05):
    """Diferencia de medias (a - b) con prueba t de Welch e IC normal."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    diff = a.mean() - b.mean()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    t, p = stats.ttest_ind(a, b, equal_var=False)
    za = stats.norm.ppf(1 - alpha / 2)
    return {"diff": diff, "ic_bajo": diff - za * se, "ic_alto": diff + za * se, "p_valor": p}


def _n_requerido(p0, p1, alpha, power):
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    return (za + zb) ** 2 * (p0 * (1 - p0) + p1 * (1 - p1)) / (p1 - p0) ** 2


def n_per_group(p0, p1, alpha=0.05, power=0.8):
    """Tamaño de muestra por grupo para detectar p0 -> p1 (prueba bilateral)."""
    return int(np.ceil(_n_requerido(p0, p1, alpha, power)))


def mde_two_props(p0, n, alpha=0.05, power=0.8):
    """Mínimo aumento absoluto detectable con n clientes por grupo."""
    return brentq(lambda d: _n_requerido(p0, p0 + d, alpha, power) - n, 1e-7, 1 - p0 - 1e-7)


def bayesian_bootstrap_mean(x, n_draws=10_000, rng=None):
    """Distribución posterior de la media de x con el bootstrap bayesiano.

    Cada observación recibe un peso aleatorio (Dirichlet uniforme) y se calcula la
    media ponderada. Con muchos ceros se evita recorrerlos: la suma de los pesos de
    los n0 ceros sigue una distribución Gamma(n0, 1), lo que da exactamente el mismo
    resultado con muchísimo menos cómputo.
    """
    rng = rng if rng is not None else np.random.default_rng()
    x = np.asarray(x, dtype=float)
    positivos = x[x != 0]
    n_ceros = len(x) - len(positivos)
    pesos = rng.exponential(size=(n_draws, len(positivos)))
    peso_ceros = rng.gamma(n_ceros, size=n_draws) if n_ceros > 0 else 0.0
    return (pesos @ positivos) / (pesos.sum(axis=1) + peso_ceros)


def heterogeneity_test(x1, n1, x0, n0):
    """Prueba Q de Cochran: ¿el efecto (diferencia de tasas) es el mismo en todos los estratos?

    x1, n1: eventos y tamaños del grupo de tratamiento en cada estrato (arrays).
    x0, n0: lo mismo para el grupo de referencia.
    La varianza se calcula con una corrección de 0,5 eventos para evitar divisiones por cero.
    """
    x1, n1, x0, n0 = (np.asarray(a, dtype=float) for a in (x1, n1, x0, n0))
    d = x1 / n1 - x0 / n0
    p1s, p0s = (x1 + 0.5) / (n1 + 1), (x0 + 0.5) / (n0 + 1)
    var = p1s * (1 - p1s) / n1 + p0s * (1 - p0s) / n0
    w = 1 / var
    d_medio = np.sum(w * d) / np.sum(w)
    q = float(np.sum(w * (d - d_medio) ** 2))
    gl = len(d) - 1
    return {"Q": q, "gl": gl, "p_valor": float(stats.chi2.sf(q, gl)), "efecto_comun": float(d_medio)}
