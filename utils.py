"""utils.py — loader data & fungsi statistik yang dipakai bersama oleh analisis.py dan app.py."""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DATA_DIR = Path(__file__).parent / "data"
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
LABEL_IPK = ["< 2.75", "2.75 - 3.24", "3.25 - 3.49", ">= 3.50"]
KONDISI_URUT = ["Cerah", "Berawan", "Hujan", "Hujan Lebat"]


# ------------------------------------------------------------------ loader
def load_kasus1() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "kasus1_penjualan.csv", parse_dates=["Tanggal"])
    df["Pendapatan"] = df["Harga (Rp)"] * df["Jumlah Terjual"]
    df["Hari"] = pd.Categorical(df["Tanggal"].dt.dayofweek.map(dict(enumerate(HARI))),
                                categories=HARI, ordered=True)
    df["Bulan"] = df["Tanggal"].dt.to_period("M").dt.to_timestamp()
    df["Akhir Pekan"] = df["Tanggal"].dt.dayofweek >= 5
    return df


def load_kasus2() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "kasus2_mahasiswa.csv")
    df["Semester (Ordinal)"] = pd.Categorical(
        "Sem " + df["Semester"].astype(str),
        categories=[f"Sem {i}" for i in range(1, 9)], ordered=True)
    df["Kategori IPK"] = pd.cut(df["IPK"], bins=[0, 2.75, 3.25, 3.50, 4.01],
                                labels=LABEL_IPK, right=False, ordered=True)
    return df


def load_kasus3() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "kasus3_cuaca.csv")
    df["Kondisi"] = pd.Categorical(df["Kondisi"], categories=KONDISI_URUT, ordered=True)
    df["Hujan?"] = df["Kondisi"].isin(["Hujan", "Hujan Lebat"])
    df["Suhu (K)"] = df["Suhu (°C)"] + 273.15
    return df


# ------------------------------------------------------------------ statistik
def ringkasan_numerik(df: pd.DataFrame, cols) -> pd.DataFrame:
    """Statistik deskriptif lengkap + outlier IQR + uji normalitas (D'Agostino)."""
    rows = {}
    for c in cols:
        s = df[c].dropna()
        q1, q3 = s.quantile([0.25, 0.75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        rows[c] = {
            "n": len(s), "mean": s.mean(), "median": s.median(), "std": s.std(),
            "min": s.min(), "Q1": q1, "Q3": q3, "max": s.max(),
            "CV (%)": s.std() / s.mean() * 100,
            "skewness": s.skew(), "kurtosis": s.kurt(),
            "outlier (IQR)": int(((s < lo) | (s > hi)).sum()),
            "p normaltest": stats.normaltest(s).pvalue if len(s) >= 8 else np.nan,
        }
    return pd.DataFrame(rows).T


def label_korelasi(r: float) -> str:
    a = abs(r)
    kuat = ("sangat lemah" if a < 0.2 else "lemah" if a < 0.4 else "sedang" if a < 0.6
            else "kuat" if a < 0.8 else "sangat kuat")
    return f"{kuat} ({'positif' if r > 0 else 'negatif'})"


def label_skew(s: float) -> str:
    a = abs(s)
    if a < 0.5:
        return "hampir simetris"
    return ("agak miring" if a < 1 else "sangat miring") + (" ke kanan" if s > 0 else " ke kiri")


def fp(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def uji_kelompok(df: pd.DataFrame, num: str, cat: str):
    """ANOVA + Kruskal-Wallis + eta-squared untuk beda rata-rata `num` antar grup `cat`."""
    grup = [g[num].to_numpy() for _, g in df.groupby(cat, observed=True) if len(g) > 1]
    if len(grup) < 2:
        return None
    F, p = stats.f_oneway(*grup)
    H, pk = stats.kruskal(*grup)
    mu = df[num].mean()
    ss_b = sum(len(g) * (g.mean() - mu) ** 2 for g in grup)
    ss_t = ((df[num] - mu) ** 2).sum()
    return {"F": F, "p_anova": p, "H": H, "p_kruskal": pk, "eta2": ss_b / ss_t}


def cramers_v(ct: pd.DataFrame):
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    n = ct.to_numpy().sum()
    v = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))
    return {"chi2": chi2, "p": p, "dof": dof, "V": v}


def regresi(x, y):
    lr = stats.linregress(x, y)
    return {"slope": lr.slope, "intercept": lr.intercept, "r": lr.rvalue,
            "r2": lr.rvalue ** 2, "p": lr.pvalue}
