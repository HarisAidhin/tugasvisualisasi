# Bedah Kasus 1 - Dataset Operasional Penjualan


## 1. Struktur & kualitas data

- Jumlah baris: **1,000** | kolom asli: **5**

- Missing value: **0** | baris duplikat: **0**

**Skala pengukuran & visualisasi yang sesuai**

```
                           Tipe / Skala        Visualisasi
Kolom                                                     
Produk              Kategorik (Nominal)    Bar / Pie Chart
Kategori            Kategorik (Nominal)    Bar / Pie Chart
Harga (Rp)      Numerik Kontinu - Rasio          Histogram
Jumlah Terjual  Numerik Diskrit - Rasio    Histogram / Bar
Tanggal                Waktu - Interval  Line Chart (tren)
```


## 2. Statistik deskriptif numerik

```
                      n          mean        median            std          min            Q1            Q3            max  CV (%)  skewness  kurtosis  outlier (IQR)  p normaltest
Harga (Rp)     1,000.00  1,093,112.00    198,000.00   2,097,178.81    11,000.00     66,000.00    452,250.00   9,227,000.00  191.85      2.29      4.40         179.00          0.00
Jumlah Terjual 1,000.00        148.71        143.00          68.36        24.00        112.00        173.00         392.00   45.97      0.84      0.89          90.00          0.00
Pendapatan     1,000.00 73,215,415.00 29,478,000.00 106,260,833.52 2,508,000.00 10,372,500.00 60,006,000.00 517,419,000.00  145.13      1.91      2.60         179.00          0.00
```

- **Harga (Rp)**: distribusi sangat miring ke kanan (skewness 2.29), outlier IQR: 179 data.

- **Jumlah Terjual**: distribusi agak miring ke kanan (skewness 0.84), outlier IQR: 90 data.

- **Pendapatan**: distribusi sangat miring ke kanan (skewness 1.91), outlier IQR: 179 data.


## 3. Kategori: kontribusi pendapatan

```
              Transaksi   Unit   Pendapatan   Rata_Harga  Share Pendapatan (%)
Kategori                                                                      
Elektronik          298  24865  55872151000 3,275,140.90                 76.30
Fashion             188  29042   7681879000   277,303.20                 10.50
Rumah Tangga        158  22627   6294661000   289,025.30                  8.60
Pendidikan          214  32743   2412823000    74,182.20                  3.30
Makanan             142  39431    953901000    24,267.60                  1.30
```


## 4. Produk terlaris & analisis Pareto

```
                          Unit   Pendapatan  Kumulatif (%)
Produk      Kategori                                      
Laptop      Elektronik    1750  14818840000          20.20
Smart TV    Elektronik    2353  12738990000          37.60
Tablet      Elektronik    3424  12117248000          54.20
Smartphone  Elektronik    2738  11448060000          69.80
Blender     Rumah Tangga  8056   2801243000          73.70
Rice Cooker Rumah Tangga  6234   2789195000          77.50
Headphone   Elektronik    6109   2713028000          81.20
Jaket       Fashion       6841   2398686000          84.40
Sepatu      Fashion       3722   2241360000          87.50
Tas         Fashion       7709   2152360000          90.40
```

- **7 dari 26 produk** (27%) menyumbang sekitar 80% pendapatan (prinsip Pareto).


## 5. Tren waktu

```
         Pendapatan  Pertumbuhan MoM (%)
Bulan                                   
2024-01  3732196000                  NaN
2024-02  5662341000                51.70
2024-03  8332596000                47.20
2024-04  4642110000               -44.30
2024-05  8355208000                80.00
2024-06  6263268000               -25.00
2024-07  6002356000                -4.20
2024-08  5220894000               -13.00
2024-09  6482908000                24.20
2024-10  6113735000                -5.70
2024-11  4819654000               -21.20
2024-12  7588149000                57.40
```

- Bulan puncak: **May 2024** | bulan terendah: **January 2024**.

- Tren linear: +65.9 juta Rp per bulan (R2 = 0.03, p 0.608).


## 6. Pola hari (weekday vs weekend)

```
        count   mean  median
Hari                        
Senin     137 137.98  137.00
Selasa    129 147.47  141.00
Rabu      149 138.89  138.00
Kamis     138 138.67  132.00
Jumat     138 134.40  134.50
Sabtu     138 167.33  166.00
Minggu    171 171.41  161.00
```

- Rata-rata unit/transaksi: akhir pekan **169.6** vs hari kerja **139.4** (Mann-Whitney p < 0.001).


## 7. Hubungan harga dan jumlah terjual

- Spearman harga vs jumlah: **-0.79** -> kuat (negatif) (p < 0.001).

- Regresi log-log: elastisitas harga = **-0.25** (naik harga 1% -> jumlah terjual berubah sekitar -0.25%), R2 = 0.78.

- Beda jumlah terjual antar kategori: Kruskal-Wallis H = 671.8 (p < 0.001), eta2 = 0.78.


## 8. Kesimpulan otomatis

- Kategori dengan pendapatan terbesar: **Elektronik** (76.3%).

- Produk dengan pendapatan terbesar: **Laptop**.

- Harga bersifat sangat miring ke kanan -> gunakan skala log / median, bukan hanya rata-rata.

- Produk murah terjual jauh lebih banyak per transaksi (elastisitas -0.25), tetapi produk mahal tetap bisa unggul di total pendapatan.
