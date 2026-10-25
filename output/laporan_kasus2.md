# Bedah Kasus 2 - Dataset Profil Mahasiswa


## 1. Struktur & kualitas data

- Jumlah baris: **1,000** | kolom asli: **4**

- Missing value: **0** | baris duplikat: **32**

**Skala pengukuran & visualisasi yang sesuai**

```
                 Tipe / Skala           Visualisasi
Kolom                                              
Jurusan   Kategorik (Nominal)             Bar Chart
Semester  Kategorik (Ordinal)   Bar Chart berurutan
IPK           Numerik Kontinu  Histogram / Box Plot
Usia          Numerik Kontinu  Histogram / Box Plot
```


## 2. Statistik deskriptif numerik

```
            n  mean  median  std   min    Q1    Q3   max  CV (%)  skewness  kurtosis  outlier (IQR)  p normaltest
IPK  1,000.00  3.23    3.23 0.36  2.03  3.02  3.48  4.00   11.02     -0.27      0.24          12.00          0.00
Usia 1,000.00 19.87   20.00 1.59 18.00 19.00 21.00 29.00    8.00      1.53      4.38          20.00          0.00
```

- **IPK**: hampir simetris, outlier IQR = 12 data, normaltest p 0.001.

- **Usia**: sangat miring ke kanan, outlier IQR = 20 data, normaltest p < 0.001.


## 3. Sebaran kategorik

```
                  Jumlah  Persen (%)
Jurusan                             
Sistem Informasi     213       21.30
Manajemen            171       17.10
Informatika          161       16.10
Akuntansi            133       13.30
Psikologi             89        8.90
Teknik Sipil          88        8.80
Hukum                 83        8.30
Ilmu Komunikasi       62        6.20
```

```
          Jumlah  Persen (%)
Semester                    
1            185       18.50
2            134       13.40
3            177       17.70
4            133       13.30
5            139       13.90
6             97        9.70
7             77        7.70
8             58        5.80
```

```
              Jumlah  Persen (%)
Kategori IPK                    
< 2.75            73        7.30
2.75 - 3.24      451       45.10
3.25 - 3.49      239       23.90
>= 3.50          237       23.70
```


## 4. IPK per jurusan

```
                  count  mean  median  std  min  max
Jurusan                                             
Psikologi            89  3.31    3.29 0.39 2.22 4.00
Sistem Informasi    213  3.30    3.31 0.34 2.04 4.00
Akuntansi           133  3.23    3.24 0.35 2.31 4.00
Ilmu Komunikasi      62  3.23    3.23 0.36 2.44 3.97
Manajemen           171  3.22    3.22 0.34 2.37 4.00
Informatika         161  3.20    3.19 0.33 2.21 4.00
Hukum                83  3.14    3.17 0.40 2.03 4.00
Teknik Sipil         88  3.10    3.15 0.34 2.19 3.80
```

- ANOVA: F = 4.62, p < 0.001 | Kruskal-Wallis p < 0.001 | eta2 = 0.032.

- Ada perbedaan IPK yang signifikan antar jurusan, namun ukuran efeknya kecil (eta2 0.032).


## 5. IPK dan usia menurut semester (ordinal -> Spearman)

```
            n  IPK_rata  IPK_std  Usia_rata
Semester                                   
1         185      3.13     0.34      18.66
2         134      3.18     0.31      18.88
3         177      3.18     0.36      19.67
4         133      3.28     0.35      19.61
5         139      3.24     0.36      20.66
6          97      3.37     0.34      20.77
7          77      3.32     0.35      21.68
8          58      3.33     0.40      21.45
```

- Semester vs IPK: rho = **0.22** -> lemah (positif) (p < 0.001).

- Semester vs Usia: rho = **0.77** -> kuat (positif) (p < 0.001).

- IPK vs Usia (Pearson): r = **0.12** -> sangat lemah (positif) (p < 0.001).


## 6. Keterkaitan jurusan x semester

```
Semester           1   2   3   4   5   6   7   8
Jurusan                                         
Akuntansi         24  24  20  13  18  13  12   9
Hukum             18   9  16  12  12   5   5   6
Ilmu Komunikasi   19   5   7  11   9   7   2   2
Informatika       35  21  25  21  18  15  15  11
Manajemen         29  29  30  25  24  20   8   6
Psikologi         14   9  20  10  10  13   5   8
Sistem Informasi  31  28  48  29  30  15  23   9
Teknik Sipil      15   9  11  12  18   9   7   7
```

- Chi-square = 50.4, dof = 49, p 0.418, Cramer's V = 0.08 -> tidak ada asosiasi signifikan antara jurusan dan semester.


## 7. Kesimpulan otomatis

- Jurusan ber-IPK rata-rata tertinggi: **Psikologi** (3.31); terendah: **Teknik Sipil** (3.10).

- Mahasiswa ber-IPK >= 3.50: **23.7%**; ber-IPK < 2.75: **7.3%**.

- IPK cenderung naik seiring semester (rho 0.22); usia naik seiring semester (rho 0.77).

- Outlier usia = mahasiswa dewasa / kelas karyawan; outlier IPK = IPK rendah. Keduanya terlihat jelas di Box Plot.
