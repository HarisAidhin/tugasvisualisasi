"""
analisis.py
-----------
Analisis detail untuk Bedah Kasus 1, 2, dan 3:
statistik deskriptif, kualitas data, outlier, korelasi, uji hipotesis, dan insight otomatis.

Output:
  output/laporan_kasus1.md, laporan_kasus2.md, laporan_kasus3.md
  output/figures/kasus1_ringkasan.png, kasus2_ringkasan.png, kasus3_ringkasan.png

Jalankan:  python analisis.py   (setelah python generate_data.py)
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

import utils as U

BASE = Path(__file__).parent
OUT = BASE / "output"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

BIRU, ORANYE, ABU = "#2E9CCA", "#F28C28", "#7F8C8D"
sns.set_theme(style="whitegrid", context="notebook")
pd.options.display.float_format = "{:,.2f}".format
pd.options.display.width = 200


class Laporan:
    """Pengumpul teks laporan (Markdown) sekaligus dicetak ke terminal."""

    def __init__(self, judul):
        self.baris = [f"# {judul}\n"]

    def h(self, teks):
        self.baris.append(f"\n## {teks}\n")

    def p(self, teks):
        self.baris.append(teks + "\n")

    def tbl(self, df, nd=2):
        self.baris.append("```\n" + df.round(nd).to_string() + "\n```\n")

    def simpan(self, nama):
        teks = "\n".join(self.baris)
        (OUT / nama).write_text(teks, encoding="utf-8")
        print(teks)


def struktur(L, df, kolom_asli, skala):
    L.h("1. Struktur & kualitas data")
    L.p(f"- Jumlah baris: **{len(df):,}** | kolom asli: **{len(kolom_asli)}**")
    L.p(f"- Missing value: **{int(df[kolom_asli].isna().sum().sum())}** | "
        f"baris duplikat: **{int(df[kolom_asli].duplicated().sum())}**")
    L.p("**Skala pengukuran & visualisasi yang sesuai**")
    L.tbl(pd.DataFrame(skala, columns=["Kolom", "Tipe / Skala", "Visualisasi"]).set_index("Kolom"))


# ====================================================================== KASUS 1
def analisis_kasus1():
    df = U.load_kasus1()
    L = Laporan("Bedah Kasus 1 - Dataset Operasional Penjualan")
    struktur(L, df, ["Produk", "Kategori", "Harga (Rp)", "Jumlah Terjual", "Tanggal"], [
        ("Produk", "Kategorik (Nominal)", "Bar / Pie Chart"),
        ("Kategori", "Kategorik (Nominal)", "Bar / Pie Chart"),
        ("Harga (Rp)", "Numerik Kontinu - Rasio", "Histogram"),
        ("Jumlah Terjual", "Numerik Diskrit - Rasio", "Histogram / Bar"),
        ("Tanggal", "Waktu - Interval", "Line Chart (tren)"),
    ])

    L.h("2. Statistik deskriptif numerik")
    rn = U.ringkasan_numerik(df, ["Harga (Rp)", "Jumlah Terjual", "Pendapatan"])
    L.tbl(rn)
    for c in rn.index:
        L.p(f"- **{c}**: distribusi {U.label_skew(rn.loc[c, 'skewness'])} "
            f"(skewness {rn.loc[c, 'skewness']:.2f}), outlier IQR: {int(rn.loc[c, 'outlier (IQR)'])} data.")

    L.h("3. Kategori: kontribusi pendapatan")
    kat = df.groupby("Kategori", observed=True).agg(
        Transaksi=("Produk", "size"), Unit=("Jumlah Terjual", "sum"),
        Pendapatan=("Pendapatan", "sum"), Rata_Harga=("Harga (Rp)", "mean"),
    ).sort_values("Pendapatan", ascending=False)
    kat["Share Pendapatan (%)"] = kat["Pendapatan"] / kat["Pendapatan"].sum() * 100
    L.tbl(kat, 1)

    L.h("4. Produk terlaris & analisis Pareto")
    prod = df.groupby(["Produk", "Kategori"], observed=True).agg(
        Unit=("Jumlah Terjual", "sum"), Pendapatan=("Pendapatan", "sum")
    ).sort_values("Pendapatan", ascending=False)
    prod["Kumulatif (%)"] = prod["Pendapatan"].cumsum() / prod["Pendapatan"].sum() * 100
    L.tbl(prod.head(10), 1)
    n80 = int((prod["Kumulatif (%)"] < 80).sum() + 1)
    L.p(f"- **{n80} dari {len(prod)} produk** ({n80 / len(prod) * 100:.0f}%) menyumbang sekitar 80% pendapatan (prinsip Pareto).")

    L.h("5. Tren waktu")
    bulanan = df.groupby("Bulan")["Pendapatan"].sum()
    mom = bulanan.pct_change() * 100
    tabel_bln = pd.DataFrame({"Pendapatan": bulanan, "Pertumbuhan MoM (%)": mom})
    tabel_bln.index = tabel_bln.index.strftime("%Y-%m")
    L.tbl(tabel_bln, 1)
    reg = U.regresi(np.arange(len(bulanan)), bulanan.to_numpy())
    L.p(f"- Bulan puncak: **{bulanan.idxmax():%B %Y}** | bulan terendah: **{bulanan.idxmin():%B %Y}**.")
    L.p(f"- Tren linear: {reg['slope'] / 1e6:+,.1f} juta Rp per bulan (R2 = {reg['r2']:.2f}, p {U.fp(reg['p'])}).")

    L.h("6. Pola hari (weekday vs weekend)")
    per_hari = df.groupby("Hari", observed=True)["Jumlah Terjual"].agg(["count", "mean", "median"])
    L.tbl(per_hari)
    a = df.loc[df["Akhir Pekan"], "Jumlah Terjual"]
    b = df.loc[~df["Akhir Pekan"], "Jumlah Terjual"]
    mw = stats.mannwhitneyu(a, b)
    L.p(f"- Rata-rata unit/transaksi: akhir pekan **{a.mean():.1f}** vs hari kerja **{b.mean():.1f}** "
        f"(Mann-Whitney p {U.fp(mw.pvalue)}).")

    L.h("7. Hubungan harga dan jumlah terjual")
    rho, prho = stats.spearmanr(df["Harga (Rp)"], df["Jumlah Terjual"])
    ll = U.regresi(np.log(df["Harga (Rp)"]), np.log(df["Jumlah Terjual"]))
    L.p(f"- Spearman harga vs jumlah: **{rho:.2f}** -> {U.label_korelasi(rho)} (p {U.fp(prho)}).")
    L.p(f"- Regresi log-log: elastisitas harga = **{ll['slope']:.2f}** "
        f"(naik harga 1% -> jumlah terjual berubah sekitar {ll['slope']:.2f}%), R2 = {ll['r2']:.2f}.")
    uk = U.uji_kelompok(df, "Jumlah Terjual", "Kategori")
    L.p(f"- Beda jumlah terjual antar kategori: Kruskal-Wallis H = {uk['H']:.1f} (p {U.fp(uk['p_kruskal'])}), "
        f"eta2 = {uk['eta2']:.2f}.")

    L.h("8. Kesimpulan otomatis")
    top_k, top_p = kat.index[0], prod.index[0][0]
    L.p(f"- Kategori dengan pendapatan terbesar: **{top_k}** ({kat['Share Pendapatan (%)'].iloc[0]:.1f}%).")
    L.p(f"- Produk dengan pendapatan terbesar: **{top_p}**.")
    L.p(f"- Harga bersifat sangat miring ke kanan -> gunakan skala log / median, bukan hanya rata-rata.")
    L.p(f"- Produk murah terjual jauh lebih banyak per transaksi (elastisitas {ll['slope']:.2f}), "
        "tetapi produk mahal tetap bisa unggul di total pendapatan.")
    L.simpan("laporan_kasus1.md")
    fig_kasus1(df, kat, prod, bulanan, ll)


def fig_kasus1(df, kat, prod, bulanan, ll):
    fig, ax = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Kasus 1 - Dataset Operasional Penjualan", fontsize=18, fontweight="bold")
    sns.barplot(x=kat.index.to_list(), y=(kat["Pendapatan"] / 1e6).to_numpy(), color=BIRU, ax=ax[0, 0])
    ax[0, 0].set(title="Pendapatan per Kategori", ylabel="Juta Rp", xlabel="")
    ax[0, 0].tick_params(axis="x", rotation=20)
    top = prod.head(10).reset_index()
    ax[0, 1].barh(top["Produk"][::-1], (top["Pendapatan"][::-1] / 1e6), color=ORANYE)
    ax[0, 1].set(title="10 Produk dengan Pendapatan Tertinggi", xlabel="Juta Rp")
    ax[0, 2].plot(bulanan.index, bulanan / 1e6, marker="o", color=ABU)
    ax[0, 2].xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax[0, 2].set(title="Tren Pendapatan Bulanan", ylabel="Juta Rp")
    sns.histplot(df["Harga (Rp)"], bins=40, log_scale=True, color=ORANYE, ax=ax[1, 0])
    ax[1, 0].set(title="Distribusi Harga (skala log)")
    sns.histplot(df["Jumlah Terjual"], bins=40, kde=True, color=ORANYE, ax=ax[1, 1])
    ax[1, 1].set(title="Distribusi Jumlah Terjual")
    sns.scatterplot(data=df, x="Harga (Rp)", y="Jumlah Terjual", hue="Kategori", alpha=0.5, s=18, ax=ax[1, 2])
    xs = np.linspace(df["Harga (Rp)"].min(), df["Harga (Rp)"].max(), 100)
    ax[1, 2].plot(xs, np.exp(ll["intercept"]) * xs ** ll["slope"], "k--", label="Fit log-log")
    ax[1, 2].set(xscale="log", yscale="log", title=f"Harga vs Jumlah (elastisitas {ll['slope']:.2f})")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIG / "kasus1_ringkasan.png", dpi=110)
    plt.close(fig)


# ====================================================================== KASUS 2
def analisis_kasus2():
    df = U.load_kasus2()
    L = Laporan("Bedah Kasus 2 - Dataset Profil Mahasiswa")
    struktur(L, df, ["Jurusan", "Semester", "IPK", "Usia"], [
        ("Jurusan", "Kategorik (Nominal)", "Bar Chart"),
        ("Semester", "Kategorik (Ordinal)", "Bar Chart berurutan"),
        ("IPK", "Numerik Kontinu", "Histogram / Box Plot"),
        ("Usia", "Numerik Kontinu", "Histogram / Box Plot"),
    ])

    L.h("2. Statistik deskriptif numerik")
    rn = U.ringkasan_numerik(df, ["IPK", "Usia"])
    L.tbl(rn, 3)
    for c in rn.index:
        L.p(f"- **{c}**: {U.label_skew(rn.loc[c, 'skewness'])}, outlier IQR = {int(rn.loc[c, 'outlier (IQR)'])} data, "
            f"normaltest p {U.fp(rn.loc[c, 'p normaltest'])}.")

    L.h("3. Sebaran kategorik")
    jur = df["Jurusan"].value_counts()
    L.tbl(pd.DataFrame({"Jumlah": jur, "Persen (%)": jur / len(df) * 100}), 1)
    sem = df["Semester"].value_counts().sort_index()
    L.tbl(pd.DataFrame({"Jumlah": sem, "Persen (%)": sem / len(df) * 100}), 1)
    kip = df["Kategori IPK"].value_counts().sort_index()
    L.tbl(pd.DataFrame({"Jumlah": kip, "Persen (%)": kip / len(df) * 100}), 1)

    L.h("4. IPK per jurusan")
    pj = df.groupby("Jurusan")["IPK"].agg(["count", "mean", "median", "std", "min", "max"]).sort_values("mean", ascending=False)
    L.tbl(pj, 3)
    uk = U.uji_kelompok(df, "IPK", "Jurusan")
    L.p(f"- ANOVA: F = {uk['F']:.2f}, p {U.fp(uk['p_anova'])} | Kruskal-Wallis p {U.fp(uk['p_kruskal'])} | eta2 = {uk['eta2']:.3f}.")
    L.p("- " + ("Ada perbedaan IPK yang signifikan antar jurusan," if uk["p_anova"] < 0.05
                else "Tidak ada perbedaan IPK yang signifikan antar jurusan,")
        + f" namun ukuran efeknya {'kecil' if uk['eta2'] < 0.06 else 'sedang'} (eta2 {uk['eta2']:.3f}).")

    L.h("5. IPK dan usia menurut semester (ordinal -> Spearman)")
    ps = df.groupby("Semester").agg(n=("IPK", "size"), IPK_rata=("IPK", "mean"), IPK_std=("IPK", "std"), Usia_rata=("Usia", "mean"))
    L.tbl(ps, 3)
    r1, p1 = stats.spearmanr(df["Semester"], df["IPK"])
    r2, p2 = stats.spearmanr(df["Semester"], df["Usia"])
    r3, p3 = stats.pearsonr(df["IPK"], df["Usia"])
    L.p(f"- Semester vs IPK: rho = **{r1:.2f}** -> {U.label_korelasi(r1)} (p {U.fp(p1)}).")
    L.p(f"- Semester vs Usia: rho = **{r2:.2f}** -> {U.label_korelasi(r2)} (p {U.fp(p2)}).")
    L.p(f"- IPK vs Usia (Pearson): r = **{r3:.2f}** -> {U.label_korelasi(r3)} (p {U.fp(p3)}).")

    L.h("6. Keterkaitan jurusan x semester")
    ct = pd.crosstab(df["Jurusan"], df["Semester"])
    L.tbl(ct, 0)
    cv = U.cramers_v(ct)
    L.p(f"- Chi-square = {cv['chi2']:.1f}, dof = {cv['dof']}, p {U.fp(cv['p'])}, Cramer's V = {cv['V']:.2f} "
        f"-> {'ada' if cv['p'] < 0.05 else 'tidak ada'} asosiasi signifikan antara jurusan dan semester.")

    L.h("7. Kesimpulan otomatis")
    L.p(f"- Jurusan ber-IPK rata-rata tertinggi: **{pj.index[0]}** ({pj['mean'].iloc[0]:.2f}); terendah: **{pj.index[-1]}** ({pj['mean'].iloc[-1]:.2f}).")
    L.p(f"- Mahasiswa ber-IPK >= 3.50: **{(df['IPK'] >= 3.5).mean() * 100:.1f}%**; ber-IPK < 2.75: **{(df['IPK'] < 2.75).mean() * 100:.1f}%**.")
    L.p(f"- IPK cenderung naik seiring semester (rho {r1:.2f}); usia naik seiring semester (rho {r2:.2f}).")
    L.p("- Outlier usia = mahasiswa dewasa / kelas karyawan; outlier IPK = IPK rendah. Keduanya terlihat jelas di Box Plot.")
    L.simpan("laporan_kasus2.md")
    fig_kasus2(df, jur, sem)


def fig_kasus2(df, jur, sem):
    fig, ax = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Kasus 2 - Dataset Profil Mahasiswa", fontsize=18, fontweight="bold")
    sns.barplot(x=jur.index.to_list(), y=jur.to_numpy(), color=BIRU, ax=ax[0, 0])
    ax[0, 0].set(title="Jumlah Mahasiswa per Jurusan (Nominal)", xlabel="")
    ax[0, 0].tick_params(axis="x", rotation=30)
    sns.barplot(x=sem.index.to_list(), y=sem.to_numpy(), color=BIRU, ax=ax[0, 1])
    ax[0, 1].set(title="Jumlah Mahasiswa per Semester (Ordinal)", xlabel="Semester")
    sns.histplot(df["IPK"], bins=30, kde=True, color=ORANYE, ax=ax[0, 2])
    ax[0, 2].set(title="Distribusi IPK")
    sns.boxplot(data=df, x="Jurusan", y="IPK", color=ORANYE, ax=ax[1, 0])
    ax[1, 0].set(title="IPK per Jurusan (Box Plot)", xlabel="")
    ax[1, 0].tick_params(axis="x", rotation=30)
    g = df.groupby("Semester")["IPK"].agg(["mean", "std"])
    ax[1, 1].plot(g.index, g["mean"], marker="o", color=ORANYE)
    ax[1, 1].fill_between(g.index, g["mean"] - g["std"], g["mean"] + g["std"], alpha=0.2, color=ORANYE)
    ax[1, 1].set(title="Rata-rata IPK per Semester (+-1 SD)", xlabel="Semester", ylabel="IPK")
    sns.boxplot(data=df, x="Semester", y="Usia", color=ORANYE, ax=ax[1, 2])
    ax[1, 2].set(title="Usia per Semester (Box Plot, outlier terlihat)")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIG / "kasus2_ringkasan.png", dpi=110)
    plt.close(fig)


# ====================================================================== KASUS 3
def analisis_kasus3():
    df = U.load_kasus3()
    L = Laporan("Bedah Kasus 3 - Dataset Pengamatan Cuaca")
    struktur(L, df, ["Kota", "Suhu (°C)", "Kelembapan (%)", "Kondisi"], [
        ("Kota", "Kategorik (Nominal)", "Bar Chart"),
        ("Suhu (°C)", "Numerik - Interval", "Histogram / Box Plot"),
        ("Kelembapan (%)", "Numerik - Rasio", "Histogram / Box Plot"),
        ("Kondisi", "Kategorik (Nominal)", "Bar / Pie Chart"),
    ])

    L.h("2. Statistik deskriptif numerik")
    rn = U.ringkasan_numerik(df, ["Suhu (°C)", "Kelembapan (%)"])
    L.tbl(rn, 3)
    for c in rn.index:
        L.p(f"- **{c}**: {U.label_skew(rn.loc[c, 'skewness'])}, outlier IQR = {int(rn.loc[c, 'outlier (IQR)'])} data.")

    L.h("3. Profil per kota")
    pk = df.groupby("Kota").agg(n=("Kota", "size"), Suhu_rata=("Suhu (°C)", "mean"), Suhu_std=("Suhu (°C)", "std"),
                                Lembap_rata=("Kelembapan (%)", "mean"), Persen_Hujan=("Hujan?", "mean"))
    pk["Persen_Hujan"] *= 100
    pk = pk.sort_values("Suhu_rata", ascending=False)
    L.tbl(pk, 2)
    us = U.uji_kelompok(df, "Suhu (°C)", "Kota")
    L.p(f"- Beda suhu antar kota: ANOVA F = {us['F']:.1f} (p {U.fp(us['p_anova'])}), eta2 = {us['eta2']:.2f}.")

    L.h("4. Profil per kondisi cuaca")
    pc = df.groupby("Kondisi", observed=True).agg(n=("Kota", "size"), Suhu_rata=("Suhu (°C)", "mean"), Lembap_rata=("Kelembapan (%)", "mean"))
    L.tbl(pc, 2)
    uc1 = U.uji_kelompok(df, "Suhu (°C)", "Kondisi")
    uc2 = U.uji_kelompok(df, "Kelembapan (%)", "Kondisi")
    L.p(f"- Suhu antar kondisi: F = {uc1['F']:.1f} (p {U.fp(uc1['p_anova'])}), eta2 = {uc1['eta2']:.2f}.")
    L.p(f"- Kelembapan antar kondisi: F = {uc2['F']:.1f} (p {U.fp(uc2['p_anova'])}), eta2 = {uc2['eta2']:.2f}.")

    L.h("5. Hubungan suhu dan kelembapan")
    r, p = stats.pearsonr(df["Suhu (°C)"], df["Kelembapan (%)"])
    rho, prho = stats.spearmanr(df["Suhu (°C)"], df["Kelembapan (%)"])
    rg = U.regresi(df["Suhu (°C)"], df["Kelembapan (%)"])
    L.p(f"- Pearson r = **{r:.2f}** -> {U.label_korelasi(r)} (p {U.fp(p)}) | Spearman rho = {rho:.2f}.")
    L.p(f"- Regresi: Kelembapan = {rg['intercept']:.1f} + ({rg['slope']:.2f}) x Suhu, R2 = {rg['r2']:.2f} "
        f"(tiap +1 °C, kelembapan turun sekitar {abs(rg['slope']):.1f} poin persen).")

    L.h("6. Keterkaitan kota x kondisi")
    ct = pd.crosstab(df["Kota"], df["Kondisi"])
    L.tbl(ct, 0)
    cv = U.cramers_v(ct)
    L.p(f"- Chi-square = {cv['chi2']:.1f}, dof = {cv['dof']}, p {U.fp(cv['p'])}, Cramer's V = {cv['V']:.2f}.")

    L.h("7. Interval vs Rasio (inti Bedah Kasus 3)")
    L.p(f"- Suhu 20 °C vs 10 °C: rasio angka = 2.00, tetapi dalam Kelvin = {293.15 / 283.15:.3f} -> "
        "rasio suhu Celsius **tidak bermakna** (skala interval, nol tidak mutlak).")
    L.p("- Kelembapan 80% vs 40%: rasio = 2.00 dan tetap 2.00 pada satuan apa pun "
        "-> rasio **bermakna** (skala rasio, 0% = tidak ada uap air).")

    L.h("8. Kesimpulan otomatis")
    L.p(f"- Kota terpanas: **{pk.index[0]}** ({pk['Suhu_rata'].iloc[0]:.1f} °C); tersejuk: **{pk.index[-1]}** ({pk['Suhu_rata'].iloc[-1]:.1f} °C).")
    L.p(f"- Kota dengan hari hujan terbanyak: **{pk['Persen_Hujan'].idxmax()}** ({pk['Persen_Hujan'].max():.1f}%).")
    L.p(f"- Suhu dan kelembapan berkorelasi {U.label_korelasi(r)}; kondisi hujan identik dengan suhu lebih rendah & kelembapan tinggi.")
    L.simpan("laporan_kasus3.md")
    fig_kasus3(df, pk)


def fig_kasus3(df, pk):
    warna = dict(zip(U.KONDISI_URUT, ["#F5B041", "#95A5A6", "#3498DB", "#1B4F72"]))
    fig, ax = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Kasus 3 - Dataset Pengamatan Cuaca", fontsize=18, fontweight="bold")
    sns.barplot(x=pk.index.to_list(), y=pk["Suhu_rata"].to_numpy(), color=ORANYE, ax=ax[0, 0])
    ax[0, 0].set(title="Rata-rata Suhu per Kota", ylabel="°C", xlabel="", ylim=(20, 35))
    ax[0, 0].tick_params(axis="x", rotation=30)
    kp = pd.crosstab(df["Kota"], df["Kondisi"], normalize="index") * 100
    kp.loc[pk.index].plot(kind="bar", stacked=True, color=[warna[c] for c in kp.columns], ax=ax[0, 1])
    ax[0, 1].set(title="Komposisi Kondisi Cuaca per Kota (%)", xlabel="")
    ax[0, 1].legend(title="Kondisi", loc="lower center", bbox_to_anchor=(0.5, 1.08), ncol=4, fontsize=8, frameon=False)
    ax[0, 1].tick_params(axis="x", rotation=30)
    sns.boxplot(data=df, x="Kondisi", y="Suhu (°C)", hue="Kondisi", palette=warna, legend=False, ax=ax[0, 2])
    ax[0, 2].set(title="Suhu menurut Kondisi")
    sns.histplot(df["Suhu (°C)"], bins=30, kde=True, color=ORANYE, ax=ax[1, 0])
    ax[1, 0].set(title="Distribusi Suhu (Interval)")
    sns.histplot(df["Kelembapan (%)"], bins=30, kde=True, color=ORANYE, ax=ax[1, 1])
    ax[1, 1].set(title="Distribusi Kelembapan (Rasio)")
    sns.scatterplot(data=df, x="Suhu (°C)", y="Kelembapan (%)", hue="Kondisi", palette=warna, alpha=0.6, s=22, ax=ax[1, 2])
    rg = U.regresi(df["Suhu (°C)"], df["Kelembapan (%)"])
    xs = np.linspace(df["Suhu (°C)"].min(), df["Suhu (°C)"].max(), 50)
    ax[1, 2].plot(xs, rg["intercept"] + rg["slope"] * xs, "k--")
    ax[1, 2].set(title=f"Suhu vs Kelembapan (r = {rg['r']:.2f})")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIG / "kasus3_ringkasan.png", dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    analisis_kasus1()
    analisis_kasus2()
    analisis_kasus3()
    print(f"\nLaporan & grafik tersimpan di: {OUT}")
