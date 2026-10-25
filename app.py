"""
app.py — Dashboard Streamlit: Bedah Kasus 1, 2, dan 3
Jalankan:  streamlit run app.py
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

import utils as U

st.set_page_config(page_title="Dashboard Bedah Kasus", page_icon="📊", layout="wide")

BIRU, ORANYE, ABU = "#2E9CCA", "#F28C28", "#7F8C8D"
WARNA_KONDISI = {"Cerah": "#F5B041", "Berawan": "#95A5A6", "Hujan": "#3498DB", "Hujan Lebat": "#1B4F72"}

st.markdown(
    """
    <style>
    [data-testid="stMetric"] {background: rgba(128,128,128,0.08); border: 1px solid rgba(128,128,128,0.25);
        padding: 12px 16px; border-radius: 12px;}
    .block-container {padding-top: 2rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------ data & util
@st.cache_data
def d1():
    return U.load_kasus1()


@st.cache_data
def d2():
    return U.load_kasus2()


@st.cache_data
def d3():
    return U.load_kasus3()


def rp(x):
    if abs(x) >= 1e9:
        return f"Rp {x / 1e9:,.2f} M"
    if abs(x) >= 1e6:
        return f"Rp {x / 1e6:,.1f} jt"
    return f"Rp {x:,.0f}"


def tampil(fig):
    fig.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig)


def unduh(df, nama):
    st.download_button("⬇️ Unduh data terfilter (CSV)", df.to_csv(index=False).encode("utf-8"),
                       file_name=nama, mime="text/csv")


def tabel_uji(res, judul):
    if res is None:
        return
    st.markdown(f"**{judul}**")
    a, b, c = st.columns(3)
    a.metric("ANOVA (F)", f"{res['F']:.2f}", f"p {U.fp(res['p_anova'])}", delta_color="off")
    b.metric("Kruskal-Wallis (H)", f"{res['H']:.2f}", f"p {U.fp(res['p_kruskal'])}", delta_color="off")
    c.metric("Ukuran efek (eta²)", f"{res['eta2']:.3f}")


# ------------------------------------------------------------------ BERANDA
def halaman_beranda():
    st.title("📊 Dashboard Bedah Kasus: Tipe Data & Visualisasi")
    st.write("Tiga dataset sintesis (masing-masing **1.000 baris**) yang dikembangkan dari 2 baris contoh tiap kasus. "
             "Pilih kasus pada menu di sidebar kiri.")
    c1, c2, c3 = st.columns(3)
    for kol, df, judul in [(c1, d1(), "Kasus 1 - Penjualan"), (c2, d2(), "Kasus 2 - Mahasiswa"), (c3, d3(), "Kasus 3 - Cuaca")]:
        kol.metric(judul, f"{len(df):,} baris", f"{df.shape[1]} kolom (termasuk kolom turunan)", delta_color="off")

    st.subheader("Peta tipe data & visualisasi yang tepat")
    skala = pd.DataFrame([
        ("1", "Produk, Kategori", "Kategorik - Nominal", "Bar Chart / Pie Chart"),
        ("1", "Harga (Rp)", "Numerik Kontinu - Rasio", "Histogram"),
        ("1", "Jumlah Terjual", "Numerik Diskrit - Rasio", "Histogram / Bar"),
        ("1", "Tanggal", "Waktu - Interval", "Line Chart (tren)"),
        ("2", "Jurusan", "Kategorik - Nominal", "Bar Chart"),
        ("2", "Semester", "Kategorik - Ordinal", "Bar Chart berurutan"),
        ("2", "IPK, Usia", "Numerik Kontinu", "Histogram / Box Plot"),
        ("3", "Kota, Kondisi", "Kategorik - Nominal", "Bar / Pie Chart"),
        ("3", "Suhu (°C)", "Numerik - Interval", "Histogram / Box Plot"),
        ("3", "Kelembapan (%)", "Numerik - Rasio", "Histogram / Box Plot"),
    ], columns=["Kasus", "Kolom", "Tipe / Skala", "Visualisasi"])
    st.dataframe(skala, hide_index=True)
    st.info("**Inti perbedaan:** Nominal = label tanpa urutan | Ordinal = ada urutan | Interval = jarak bermakna, nol tidak mutlak "
            "(°C) | Rasio = ada nol mutlak sehingga perbandingan 2x / 3x bermakna (harga, jumlah, kelembapan).")


# ------------------------------------------------------------------ KASUS 1
def halaman_kasus1():
    df = d1()
    st.title("🛒 Kasus 1 — Dataset Operasional Penjualan")
    tmin, tmax = df["Tanggal"].min().date(), df["Tanggal"].max().date()
    hmin, hmax = int(df["Harga (Rp)"].min()), int(df["Harga (Rp)"].max())
    semua_kat = sorted(df["Kategori"].unique())
    with st.sidebar:
        st.subheader("Filter Kasus 1")
        kat = st.multiselect("Kategori", semua_kat, default=semua_kat)
        rentang = st.date_input("Rentang tanggal", value=(tmin, tmax), min_value=tmin, max_value=tmax)
        harga = st.slider("Rentang harga (Rp)", hmin, hmax, (hmin, hmax), step=1000)
    a, b = (rentang if isinstance(rentang, (tuple, list)) and len(rentang) == 2 else (tmin, tmax))
    f = df[df["Kategori"].isin(kat) & df["Tanggal"].between(pd.Timestamp(a), pd.Timestamp(b))
           & df["Harga (Rp)"].between(harga[0], harga[1])].copy()
    if f.empty:
        st.warning("Tidak ada data pada filter ini. Longgarkan filter di sidebar.")
        return

    top = f.groupby("Produk")["Pendapatan"].sum().idxmax()
    k = st.columns(5)
    k[0].metric("Total Pendapatan", rp(f["Pendapatan"].sum()))
    k[1].metric("Unit Terjual", f"{f['Jumlah Terjual'].sum():,}")
    k[2].metric("Jumlah Transaksi", f"{len(f):,}")
    k[3].metric("Rata-rata Harga", rp(f["Harga (Rp)"].mean()))
    k[4].metric("Produk Terbesar", top)

    t1, t2, t3, t4, t5, t6 = st.tabs(["Ringkasan", "Tren Waktu", "Distribusi", "Hubungan", "Statistik", "Data"])

    with t1:
        kt = f.groupby("Kategori", as_index=False).agg(Pendapatan=("Pendapatan", "sum"), Unit=("Jumlah Terjual", "sum"))
        c1, c2 = st.columns(2)
        with c1:
            tampil(px.bar(kt.sort_values("Pendapatan", ascending=False), x="Kategori", y="Pendapatan",
                          color="Kategori", title="Pendapatan per Kategori (Nominal -> Bar Chart)"))
        with c2:
            tampil(px.pie(kt, names="Kategori", values="Pendapatan", hole=0.5, title="Porsi Pendapatan (Pie/Donut Chart)"))
        tp = (f.groupby(["Produk", "Kategori"], as_index=False)["Pendapatan"].sum()
              .sort_values("Pendapatan", ascending=False).head(10))
        tampil(px.bar(tp[::-1], x="Pendapatan", y="Produk", color="Kategori", orientation="h",
                      title="10 Produk dengan Pendapatan Tertinggi"))

    with t2:
        pilih = st.selectbox("Agregasi waktu", ["Bulanan", "Mingguan", "Harian"])
        freq = {"Bulanan": "MS", "Mingguan": "W", "Harian": "D"}[pilih]
        ts = f.set_index("Tanggal")["Pendapatan"].resample(freq).sum().reset_index()
        tampil(px.line(ts, x="Tanggal", y="Pendapatan", markers=True, title=f"Tren Pendapatan {pilih} (Line Chart)",
                       color_discrete_sequence=[ABU]))
        c1, c2 = st.columns(2)
        with c1:
            ph = f.groupby("Hari", observed=True)["Jumlah Terjual"].mean().reset_index()
            tampil(px.bar(ph, x="Hari", y="Jumlah Terjual", title="Rata-rata Unit per Transaksi menurut Hari",
                          color_discrete_sequence=[BIRU]))
        with c2:
            f["Bln"] = f["Tanggal"].dt.month.map(lambda m: U.BULAN[m - 1])
            pv = f.pivot_table(index="Hari", columns="Bln", values="Pendapatan", aggfunc="sum", observed=True)
            pv = pv.reindex(columns=[x for x in U.BULAN if x in pv.columns])
            tampil(px.imshow(pv / 1e6, aspect="auto", color_continuous_scale="Oranges",
                             title="Heatmap Pendapatan (juta Rp): Hari x Bulan"))

    with t3:
        log = st.checkbox("Skala log untuk harga", value=True)
        c1, c2 = st.columns(2)
        with c1:
            tampil(px.histogram(f, x="Harga (Rp)", nbins=40, log_x=log, marginal="box",
                                title="Distribusi Harga (Kontinu -> Histogram)", color_discrete_sequence=[ORANYE]))
        with c2:
            tampil(px.histogram(f, x="Jumlah Terjual", nbins=40, marginal="box",
                                title="Distribusi Jumlah Terjual (Diskrit)", color_discrete_sequence=[ORANYE]))
        tampil(px.box(f, x="Kategori", y="Jumlah Terjual", color="Kategori", points="outliers",
                      title="Jumlah Terjual per Kategori"))

    with t4:
        c1, c2 = st.columns([3, 2])
        with c1:
            fig = px.scatter(f, x="Harga (Rp)", y="Jumlah Terjual", color="Kategori", log_x=True,
                             opacity=0.6, hover_name="Produk", title="Harga vs Jumlah Terjual")
            if len(f) >= 10 and f["Harga (Rp)"].nunique() > 1:
                lr = stats.linregress(np.log(f["Harga (Rp)"]), np.log(f["Jumlah Terjual"]))
                xs = np.linspace(f["Harga (Rp)"].min(), f["Harga (Rp)"].max(), 100)
                fig.add_trace(go.Scatter(x=xs, y=np.exp(lr.intercept) * xs ** lr.slope, mode="lines",
                                         name=f"Fit log-log (elastisitas {lr.slope:.2f})",
                                         line=dict(color="black", dash="dash")))
            tampil(fig)
        with c2:
            corr = f[["Harga (Rp)", "Jumlah Terjual", "Pendapatan"]].corr(method="spearman")
            tampil(px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdBu_r",
                             title="Korelasi Spearman"))

    with t5:
        st.markdown("**Statistik deskriptif**")
        st.dataframe(U.ringkasan_numerik(f, ["Harga (Rp)", "Jumlah Terjual", "Pendapatan"]).round(3))
        tabel_uji(U.uji_kelompok(f, "Jumlah Terjual", "Kategori"), "Beda jumlah terjual antar kategori")
        if len(f) > 3:
            rho, p = stats.spearmanr(f["Harga (Rp)"], f["Jumlah Terjual"])
            st.write(f"Korelasi Spearman harga vs jumlah: **{rho:.2f}** -> {U.label_korelasi(rho)} (p {U.fp(p)})")

    with t6:
        st.dataframe(f.drop(columns=["Bulan", "Akhir Pekan", "Bln"], errors="ignore").reset_index(drop=True))
        unduh(f.drop(columns=["Bln"], errors="ignore"), "kasus1_terfilter.csv")


# ------------------------------------------------------------------ KASUS 2
def halaman_kasus2():
    df = d2()
    st.title("🎓 Kasus 2 — Dataset Profil Mahasiswa")
    semua_jur = sorted(df["Jurusan"].unique())
    with st.sidebar:
        st.subheader("Filter Kasus 2")
        jur = st.multiselect("Jurusan", semua_jur, default=semua_jur)
        sem = st.slider("Rentang semester", 1, 8, (1, 8))
        ipk = st.slider("Rentang IPK", 2.0, 4.0, (2.0, 4.0), step=0.05)
    f = df[df["Jurusan"].isin(jur) & df["Semester"].between(sem[0], sem[1]) & df["IPK"].between(ipk[0], ipk[1])].copy()
    if f.empty:
        st.warning("Tidak ada data pada filter ini. Longgarkan filter di sidebar.")
        return

    rata_jur = f.groupby("Jurusan")["IPK"].mean()
    k = st.columns(5)
    k[0].metric("Jumlah Mahasiswa", f"{len(f):,}")
    k[1].metric("Rata-rata IPK", f"{f['IPK'].mean():.2f}")
    k[2].metric("Median Usia", f"{f['Usia'].median():.0f} th")
    k[3].metric("IPK ≥ 3.50", f"{(f['IPK'] >= 3.5).mean() * 100:.1f}%")
    k[4].metric("IPK Tertinggi (Jurusan)", rata_jur.idxmax(), f"{rata_jur.max():.2f}", delta_color="off")

    t1, t2, t3, t4, t5 = st.tabs(["Ringkasan", "Distribusi", "Hubungan", "Statistik", "Data"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            j = f["Jurusan"].value_counts().reset_index()
            j.columns = ["Jurusan", "Jumlah"]
            tampil(px.bar(j, x="Jurusan", y="Jumlah", color="Jurusan", title="Mahasiswa per Jurusan (Nominal)"))
        with c2:
            s = f["Semester (Ordinal)"].value_counts().sort_index().reset_index()
            s.columns = ["Semester", "Jumlah"]
            tampil(px.bar(s, x="Semester", y="Jumlah", title="Mahasiswa per Semester (Ordinal, berurutan)",
                          color_discrete_sequence=[BIRU]))
        kp = f["Kategori IPK"].value_counts().sort_index().reset_index()
        kp.columns = ["Kategori IPK", "Jumlah"]
        tampil(px.bar(kp, x="Kategori IPK", y="Jumlah", title="Sebaran Kategori IPK",
                      color_discrete_sequence=[ORANYE]))

    with t2:
        c1, c2 = st.columns(2)
        with c1:
            tampil(px.histogram(f, x="IPK", nbins=30, marginal="box", title="Distribusi IPK (Histogram + Box Plot)",
                                color_discrete_sequence=[ORANYE]))
        with c2:
            tampil(px.histogram(f, x="Usia", nbins=20, marginal="box", title="Distribusi Usia (Histogram + Box Plot)",
                                color_discrete_sequence=[ORANYE]))
        tampil(px.box(f, x="Jurusan", y="IPK", color="Jurusan", points="outliers", title="IPK per Jurusan (sebaran & outlier)"))
        tampil(px.violin(f, x="Semester (Ordinal)", y="IPK", box=True, points=False, title="IPK per Semester",
                         color_discrete_sequence=[BIRU]))

    with t3:
        c1, c2 = st.columns(2)
        with c1:
            tampil(px.scatter(f, x="Usia", y="IPK", color="Jurusan", opacity=0.6, title="IPK vs Usia"))
        with c2:
            g = f.groupby("Semester").agg(IPK=("IPK", "mean"), SD=("IPK", "std")).reset_index()
            fig = px.line(g, x="Semester", y="IPK", markers=True, error_y="SD", title="Rata-rata IPK per Semester (±1 SD)",
                          color_discrete_sequence=[ORANYE])
            tampil(fig)
        ct = pd.crosstab(f["Jurusan"], f["Semester"])
        tampil(px.imshow(ct, text_auto=True, aspect="auto", color_continuous_scale="Blues",
                         title="Jumlah Mahasiswa: Jurusan x Semester"))

    with t4:
        st.markdown("**Statistik deskriptif**")
        st.dataframe(U.ringkasan_numerik(f, ["IPK", "Usia"]).round(3))
        tabel_uji(U.uji_kelompok(f, "IPK", "Jurusan"), "Beda IPK antar jurusan")
        if len(f) > 3:
            r1, p1 = stats.spearmanr(f["Semester"], f["IPK"])
            r2, p2 = stats.spearmanr(f["Semester"], f["Usia"])
            st.write(f"Semester vs IPK (Spearman): **{r1:.2f}** -> {U.label_korelasi(r1)} (p {U.fp(p1)})")
            st.write(f"Semester vs Usia (Spearman): **{r2:.2f}** -> {U.label_korelasi(r2)} (p {U.fp(p2)})")

    with t5:
        st.dataframe(f.reset_index(drop=True))
        unduh(f, "kasus2_terfilter.csv")


# ------------------------------------------------------------------ KASUS 3
def halaman_kasus3():
    df = d3()
    st.title("🌦️ Kasus 3 — Dataset Pengamatan Cuaca")
    semua_kota = sorted(df["Kota"].unique())
    with st.sidebar:
        st.subheader("Filter Kasus 3")
        kota = st.multiselect("Kota", semua_kota, default=semua_kota)
        kond = st.multiselect("Kondisi", U.KONDISI_URUT, default=U.KONDISI_URUT)
        smin, smax = float(df["Suhu (°C)"].min()), float(df["Suhu (°C)"].max())
        suhu = st.slider("Rentang suhu (°C)", smin, smax, (smin, smax), step=0.5)
    f = df[df["Kota"].isin(kota) & df["Kondisi"].isin(kond) & df["Suhu (°C)"].between(suhu[0], suhu[1])].copy()
    if f.empty:
        st.warning("Tidak ada data pada filter ini. Longgarkan filter di sidebar.")
        return

    pk = f.groupby("Kota").agg(Suhu=("Suhu (°C)", "mean"), Lembap=("Kelembapan (%)", "mean"))
    k = st.columns(5)
    k[0].metric("Rata-rata Suhu", f"{f['Suhu (°C)'].mean():.1f} °C")
    k[1].metric("Rata-rata Kelembapan", f"{f['Kelembapan (%)'].mean():.1f} %")
    k[2].metric("Hari Hujan", f"{f['Hujan?'].mean() * 100:.1f}%")
    k[3].metric("Kota Terpanas", pk["Suhu"].idxmax(), f"{pk['Suhu'].max():.1f} °C", delta_color="off")
    k[4].metric("Kota Terlembap", pk["Lembap"].idxmax(), f"{pk['Lembap'].max():.1f} %", delta_color="off")

    t1, t2, t3, t4, t5, t6 = st.tabs(["Ringkasan", "Distribusi", "Hubungan", "Interval vs Rasio", "Statistik", "Data"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            p = pk.reset_index().sort_values("Suhu", ascending=False)
            tampil(px.bar(p, x="Kota", y="Suhu", color="Suhu", color_continuous_scale="Oranges",
                          title="Rata-rata Suhu per Kota (°C)"))
        with c2:
            kc = (pd.crosstab(f["Kota"], f["Kondisi"], normalize="index") * 100).reset_index().melt(
                id_vars="Kota", var_name="Kondisi", value_name="Persen")
            tampil(px.bar(kc, x="Kota", y="Persen", color="Kondisi", color_discrete_map=WARNA_KONDISI,
                          category_orders={"Kondisi": U.KONDISI_URUT}, title="Komposisi Kondisi Cuaca per Kota (%)"))
        kd = f["Kondisi"].value_counts().reset_index()
        kd.columns = ["Kondisi", "Jumlah"]
        tampil(px.pie(kd, names="Kondisi", values="Jumlah", hole=0.5, color="Kondisi",
                      color_discrete_map=WARNA_KONDISI, title="Proporsi Kondisi Cuaca"))

    with t2:
        c1, c2 = st.columns(2)
        with c1:
            tampil(px.histogram(f, x="Suhu (°C)", nbins=30, marginal="box", title="Distribusi Suhu (Interval)",
                                color_discrete_sequence=[ORANYE]))
        with c2:
            tampil(px.histogram(f, x="Kelembapan (%)", nbins=30, marginal="box", title="Distribusi Kelembapan (Rasio)",
                                color_discrete_sequence=[ORANYE]))
        c3, c4 = st.columns(2)
        with c3:
            tampil(px.box(f, x="Kondisi", y="Suhu (°C)", color="Kondisi", color_discrete_map=WARNA_KONDISI,
                          category_orders={"Kondisi": U.KONDISI_URUT}, title="Suhu menurut Kondisi"))
        with c4:
            tampil(px.box(f, x="Kota", y="Kelembapan (%)", color="Kota", title="Kelembapan per Kota"))

    with t3:
        fig = px.scatter(f, x="Suhu (°C)", y="Kelembapan (%)", color="Kondisi", color_discrete_map=WARNA_KONDISI,
                         category_orders={"Kondisi": U.KONDISI_URUT}, opacity=0.65, hover_data=["Kota"],
                         title="Suhu vs Kelembapan")
        if len(f) > 3 and f["Suhu (°C)"].nunique() > 1:
            rg = U.regresi(f["Suhu (°C)"], f["Kelembapan (%)"])
            xs = np.linspace(f["Suhu (°C)"].min(), f["Suhu (°C)"].max(), 50)
            fig.add_trace(go.Scatter(x=xs, y=rg["intercept"] + rg["slope"] * xs, mode="lines",
                                     name=f"Regresi (r = {rg['r']:.2f})", line=dict(color="black", dash="dash")))
        tampil(fig)
        hm = f.pivot_table(index="Kota", columns="Kondisi", values="Suhu (°C)", aggfunc="mean", observed=True)
        tampil(px.imshow(hm, text_auto=".1f", aspect="auto", color_continuous_scale="RdYlBu_r",
                         title="Rata-rata Suhu (°C): Kota x Kondisi"))

    with t4:
        st.subheader("Mengapa Suhu = Interval dan Kelembapan = Rasio?")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🌡️ Suhu (°C) — Interval")
            ta = st.number_input("Suhu A (°C)", value=20.0, step=1.0)
            tb = st.number_input("Suhu B (°C)", value=10.0, step=1.0)
            m1, m2 = st.columns(2)
            m1.metric("Rasio A/B dalam °C", f"{ta / tb:.2f}" if tb != 0 else "tak terdefinisi")
            m2.metric("Rasio A/B dalam Kelvin", f"{(ta + 273.15) / (tb + 273.15):.3f}")
            st.caption("Rasio berubah ketika satuan diganti -> 20 °C **bukan** '2x lebih panas' dari 10 °C. "
                       "Nol Celsius adalah titik beku air, bukan 'tidak ada suhu'.")
        with c2:
            st.markdown("#### 💧 Kelembapan (%) — Rasio")
            ha = st.number_input("Kelembapan A (%)", value=80.0, min_value=0.0, max_value=100.0, step=5.0)
            hb = st.number_input("Kelembapan B (%)", value=40.0, min_value=0.0, max_value=100.0, step=5.0)
            m1, m2 = st.columns(2)
            m1.metric("Rasio A/B dalam %", f"{ha / hb:.2f}" if hb != 0 else "tak terdefinisi")
            m2.metric("Rasio A/B dalam fraksi", f"{(ha / 100) / (hb / 100):.2f}" if hb != 0 else "tak terdefinisi")
            st.caption("Rasio tetap sama di satuan mana pun -> 80% memang 2x lebih lembap dari 40%. 0% = tidak ada uap air.")

    with t5:
        st.markdown("**Statistik deskriptif**")
        st.dataframe(U.ringkasan_numerik(f, ["Suhu (°C)", "Kelembapan (%)"]).round(3))
        tabel_uji(U.uji_kelompok(f, "Suhu (°C)", "Kota"), "Beda suhu antar kota")
        tabel_uji(U.uji_kelompok(f, "Kelembapan (%)", "Kondisi"), "Beda kelembapan antar kondisi")
        if len(f) > 3:
            r, p = stats.pearsonr(f["Suhu (°C)"], f["Kelembapan (%)"])
            st.write(f"Korelasi Pearson suhu vs kelembapan: **{r:.2f}** -> {U.label_korelasi(r)} (p {U.fp(p)})")

    with t6:
        st.dataframe(f.drop(columns=["Hujan?", "Suhu (K)"]).reset_index(drop=True))
        unduh(f, "kasus3_terfilter.csv")


# ------------------------------------------------------------------ NAVIGASI
st.sidebar.title("📊 Bedah Kasus")
menu = st.sidebar.radio("Pilih halaman", ["Beranda", "Kasus 1 - Penjualan", "Kasus 2 - Mahasiswa", "Kasus 3 - Cuaca"])
st.sidebar.divider()

if menu == "Beranda":
    halaman_beranda()
elif menu.startswith("Kasus 1"):
    halaman_kasus1()
elif menu.startswith("Kasus 2"):
    halaman_kasus2()
else:
    halaman_kasus3()
