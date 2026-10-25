# Bedah Kasus 3 - Dataset Pengamatan Cuaca


## 1. Struktur & kualitas data

- Jumlah baris: **1,000** | kolom asli: **4**

- Missing value: **0** | baris duplikat: **22**

**Skala pengukuran & visualisasi yang sesuai**

```
                       Tipe / Skala           Visualisasi
Kolom                                                    
Kota            Kategorik (Nominal)             Bar Chart
Suhu (°C)        Numerik - Interval  Histogram / Box Plot
Kelembapan (%)      Numerik - Rasio  Histogram / Box Plot
Kondisi         Kategorik (Nominal)       Bar / Pie Chart
```


## 2. Statistik deskriptif numerik

```
                      n  mean  median   std   min    Q1    Q3    max  CV (%)  skewness  kurtosis  outlier (IQR)  p normaltest
Suhu (°C)      1,000.00 29.60   30.10  3.32 18.50 27.40 32.10  36.00   11.22     -0.64     -0.05           6.00          0.00
Kelembapan (%) 1,000.00 75.94   75.00 10.69 47.00 67.00 84.00 100.00   14.08      0.15     -0.79           0.00          0.00
```

- **Suhu (°C)**: agak miring ke kiri, outlier IQR = 6 data.

- **Kelembapan (%)**: hampir simetris, outlier IQR = 0 data.


## 3. Profil per kota

```
              n  Suhu_rata  Suhu_std  Lembap_rata  Persen_Hujan
Kota                                                           
Surabaya    111      32.05      2.14        69.68         22.52
Makassar    126      31.79      2.17        72.16         28.57
Semarang    114      30.43      2.41        75.43         33.33
Medan       129      30.29      2.52        77.26         35.66
Jakarta     132      30.15      2.32        76.11         38.64
Denpasar    121      29.98      2.22        76.36         32.23
Yogyakarta  123      29.08      2.38        77.15         32.52
Bandung     144      24.15      2.20        81.77         48.61
```

- Beda suhu antar kota: ANOVA F = 156.0 (p < 0.001), eta2 = 0.52.


## 4. Profil per kondisi cuaca

```
               n  Suhu_rata  Lembap_rata
Kondisi                                 
Cerah        335      32.11        65.26
Berawan      320      30.16        74.76
Hujan        277      26.94        86.01
Hujan Lebat   68      25.46        93.12
```

- Suhu antar kondisi: F = 312.4 (p < 0.001), eta2 = 0.48.

- Kelembapan antar kondisi: F = 1050.8 (p < 0.001), eta2 = 0.76.


## 5. Hubungan suhu dan kelembapan

- Pearson r = **-0.69** -> kuat (negatif) (p < 0.001) | Spearman rho = -0.71.

- Regresi: Kelembapan = 142.0 + (-2.23) x Suhu, R2 = 0.48 (tiap +1 °C, kelembapan turun sekitar 2.2 poin persen).


## 6. Keterkaitan kota x kondisi

```
Kondisi     Cerah  Berawan  Hujan  Hujan Lebat
Kota                                          
Bandung        29       45     51           19
Denpasar       41       41     34            5
Jakarta        38       43     44            7
Makassar       54       36     30            6
Medan          43       40     35           11
Semarang       38       38     28           10
Surabaya       53       33     22            3
Yogyakarta     39       44     33            7
```

- Chi-square = 43.7, dof = 21, p 0.003, Cramer's V = 0.12.


## 7. Interval vs Rasio (inti Bedah Kasus 3)

- Suhu 20 °C vs 10 °C: rasio angka = 2.00, tetapi dalam Kelvin = 1.035 -> rasio suhu Celsius **tidak bermakna** (skala interval, nol tidak mutlak).

- Kelembapan 80% vs 40%: rasio = 2.00 dan tetap 2.00 pada satuan apa pun -> rasio **bermakna** (skala rasio, 0% = tidak ada uap air).


## 8. Kesimpulan otomatis

- Kota terpanas: **Surabaya** (32.0 °C); tersejuk: **Bandung** (24.2 °C).

- Kota dengan hari hujan terbanyak: **Bandung** (48.6%).

- Suhu dan kelembapan berkorelasi kuat (negatif); kondisi hujan identik dengan suhu lebih rendah & kelembapan tinggi.
