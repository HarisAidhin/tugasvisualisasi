"""
generate_data.py
----------------
Membuat data sintesis 1000 baris untuk Bedah Kasus 1, 2, dan 3.

* Dua baris contoh asli dari tugas selalu menjadi 2 baris pertama tiap dataset.
* 998 baris sisanya dibangkitkan acak dengan pola yang realistis
  (ada hubungan antarvariabel, musiman, outlier kecil) agar analisis menjadi bermakna.
* Seed tetap (42) -> hasil selalu bisa direproduksi.

Jalankan:  python generate_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N = 1000
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- KASUS 1
def kasus1(n=N):
    katalog = {
        "Elektronik": {"Laptop": 8_500_000, "Smartphone": 4_200_000, "Tablet": 3_600_000,
                       "Smart TV": 5_500_000, "Headphone": 450_000, "Keyboard": 350_000,
                       "Mouse": 150_000},
        "Pendidikan": {"Buku": 75_000, "Alat Tulis": 25_000, "Kalkulator": 120_000,
                       "Kamus": 90_000, "Modul Belajar": 60_000},
        "Fashion": {"Kaos": 90_000, "Jaket": 350_000, "Sepatu": 600_000, "Tas": 280_000,
                    "Topi": 70_000},
        "Makanan": {"Kopi": 45_000, "Teh": 25_000, "Cokelat": 30_000, "Biskuit": 15_000,
                    "Snack": 12_000},
        "Rumah Tangga": {"Blender": 350_000, "Rice Cooker": 450_000, "Lampu LED": 40_000,
                         "Setrika": 200_000},
    }
    faktor_kategori = {"Elektronik": 0.9, "Pendidikan": 1.0, "Fashion": 1.1,
                       "Makanan": 1.8, "Rumah Tangga": 1.0}
    produk = [(p, k, h) for k, d in katalog.items() for p, h in d.items()]

    m = n - 2
    bobot = rng.dirichlet(np.ones(len(produk)) * 4)          # popularitas tiap produk
    idx = rng.choice(len(produk), size=m, p=bobot)
    offset = np.sort(rng.integers(2, 366, size=m))            # 2024 = tahun kabisat
    tanggal = pd.to_datetime("2024-01-01") + pd.to_timedelta(offset, unit="D")

    nama = [produk[i][0] for i in idx]
    kat = [produk[i][1] for i in idx]
    base = np.array([produk[i][2] for i in idx], dtype=float)

    # harga = harga dasar +- variasi (diskon / varian), dibulatkan ke ribuan
    harga = np.maximum(np.round(base * (1 + rng.normal(0, 0.06, size=m)), -3), 1000).astype(int)

    # jumlah terjual: makin mahal makin sedikit, lebih ramai akhir pekan, akhir tahun & tren naik
    doy = tanggal.dayofyear.to_numpy()
    musim = (1 + 0.15 * np.sin(2 * np.pi * (doy - 80) / 365)
             + 0.25 * np.isin(tanggal.month, [11, 12]) + 0.2 * doy / 366)
    akhir_pekan = np.where(tanggal.dayofweek >= 5, 1.2, 1.0)
    lam = (130 / np.sqrt(1 + harga / 1e6) * musim * akhir_pekan
           * np.array([faktor_kategori[k] for k in kat]))
    jumlah = np.maximum(1, rng.poisson(lam))

    df = pd.DataFrame({"Produk": nama, "Kategori": kat, "Harga (Rp)": harga,
                       "Jumlah Terjual": jumlah, "Tanggal": tanggal})
    contoh = pd.DataFrame({
        "Produk": ["Laptop", "Buku"], "Kategori": ["Elektronik", "Pendidikan"],
        "Harga (Rp)": [8_500_000, 75_000], "Jumlah Terjual": [45, 120],
        "Tanggal": pd.to_datetime(["2024-01-01", "2024-01-02"]),
    })
    return pd.concat([contoh, df], ignore_index=True)


# ---------------------------------------------------------------- KASUS 2
def kasus2(n=N):
    jurusan = ["Sistem Informasi", "Manajemen", "Informatika", "Akuntansi",
               "Teknik Sipil", "Psikologi", "Hukum", "Ilmu Komunikasi"]
    p_jur = [0.20, 0.16, 0.18, 0.12, 0.09, 0.09, 0.08, 0.08]
    geser = {"Sistem Informasi": 0.05, "Manajemen": 0.0, "Informatika": -0.05, "Akuntansi": 0.0,
             "Teknik Sipil": -0.10, "Psikologi": 0.08, "Hukum": -0.02, "Ilmu Komunikasi": 0.06}
    p_sem = [0.17, 0.15, 0.16, 0.13, 0.14, 0.10, 0.09, 0.06]  # mhs semester atas makin sedikit

    m = n - 2
    jur = rng.choice(jurusan, size=m, p=p_jur)
    sem = rng.choice(np.arange(1, 9), size=m, p=p_sem)

    ipk = 3.15 + 0.035 * (sem - 1) + np.array([geser[j] for j in jur]) + rng.normal(0, 0.33, size=m)
    rendah = rng.random(m) < 0.015                       # sebagian kecil mahasiswa ber-IPK rendah
    ipk = np.where(rendah, rng.uniform(2.0, 2.5, size=m), ipk)
    ipk = np.round(np.clip(ipk, 2.0, 4.0), 2)

    usia = 18 + (sem - 1) // 2 + rng.poisson(0.5, size=m)
    dewasa = rng.random(m) < 0.03                         # mahasiswa dewasa -> outlier usia
    usia = np.clip(np.where(dewasa, usia + rng.integers(3, 10, size=m), usia), 17, 40)

    df = pd.DataFrame({"Jurusan": jur, "Semester": sem, "IPK": ipk, "Usia": usia})
    contoh = pd.DataFrame({"Jurusan": ["Sistem Informasi", "Manajemen"], "Semester": [3, 1],
                           "IPK": [3.85, 3.50], "Usia": [20, 19]})
    return pd.concat([contoh, df], ignore_index=True)


# ---------------------------------------------------------------- KASUS 3
def kasus3(n=N):
    kondisi = ["Cerah", "Berawan", "Hujan", "Hujan Lebat"]
    # kota: (suhu dasar, geser kelembapan, peluang tiap kondisi)
    kota = {
        "Jakarta": (31.0, 0, [0.35, 0.30, 0.28, 0.07]),
        "Bandung": (25.5, 4, [0.20, 0.30, 0.40, 0.10]),
        "Surabaya": (32.0, -2, [0.45, 0.30, 0.20, 0.05]),
        "Medan": (31.0, 1, [0.35, 0.28, 0.30, 0.07]),
        "Semarang": (31.0, 0, [0.40, 0.30, 0.25, 0.05]),
        "Makassar": (32.0, -1, [0.42, 0.28, 0.25, 0.05]),
        "Yogyakarta": (29.5, 2, [0.38, 0.30, 0.27, 0.05]),
        "Denpasar": (30.5, 1, [0.42, 0.30, 0.24, 0.04]),
    }
    efek_suhu = {"Cerah": 1.5, "Berawan": 0.0, "Hujan": -3.0, "Hujan Lebat": -4.0}
    dasar_lembap = {"Cerah": 65, "Berawan": 74, "Hujan": 85, "Hujan Lebat": 92}

    m = n - 2
    kt = rng.choice(list(kota), size=m)
    kd = np.array([rng.choice(kondisi, p=kota[c][2]) for c in kt])
    suhu = np.round([kota[c][0] + efek_suhu[k] for c, k in zip(kt, kd)] + rng.normal(0, 1.2, size=m), 1)
    lembap = np.round(np.clip(
        [dasar_lembap[k] + kota[c][1] for c, k in zip(kt, kd)] + rng.normal(0, 5, size=m), 35, 100)).astype(int)

    df = pd.DataFrame({"Kota": kt, "Suhu (°C)": suhu, "Kelembapan (%)": lembap, "Kondisi": kd})
    contoh = pd.DataFrame({"Kota": ["Jakarta", "Bandung"], "Suhu (°C)": [32.5, 24.0],
                           "Kelembapan (%)": [75, 85], "Kondisi": ["Cerah", "Hujan"]})
    return pd.concat([contoh, df], ignore_index=True)


if __name__ == "__main__":
    d1, d2, d3 = kasus1(), kasus2(), kasus3()
    d1.assign(Tanggal=d1["Tanggal"].dt.strftime("%Y-%m-%d")).to_csv(OUT / "kasus1_penjualan.csv", index=False)
    d2.to_csv(OUT / "kasus2_mahasiswa.csv", index=False)
    d3.to_csv(OUT / "kasus3_cuaca.csv", index=False)
    for nama, d in [("Kasus 1 (Penjualan)", d1), ("Kasus 2 (Mahasiswa)", d2), ("Kasus 3 (Cuaca)", d3)]:
        print(f"{nama}: {d.shape[0]} baris x {d.shape[1]} kolom")
    print(f"Tersimpan di: {OUT}")
