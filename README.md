# Bedah Kasus 1-3: Data Sintesis, Analisis Python, Dashboard Streamlit

## Struktur
- `generate_data.py` : membuat 3 dataset sintesis (1000 baris/kasus) -> folder `data/`
- `utils.py`         : loader data + fungsi statistik bersama
- `analisis.py`      : analisis detail -> `output/laporan_kasus*.md` dan `output/figures/*.png`
- `app.py`           : dashboard Streamlit interaktif

## Cara menjalankan
```bash
pip install -r requirements.txt
python generate_data.py      # 1) buat data sintesis
python analisis.py           # 2) analisis detail + laporan + grafik
streamlit run app.py         # 3) buka dashboard di http://localhost:8501
```

## Catatan data
2 baris pertama tiap dataset = contoh asli dari soal; 998 baris sisanya sintesis (seed 42, reproducible).
Pola yang sengaja dibangun: harga naik -> jumlah terjual turun, lonjakan akhir pekan & akhir tahun (Kasus 1);
IPK naik tipis seiring semester, outlier usia & IPK rendah (Kasus 2); hujan -> suhu turun & kelembapan naik,
Bandung lebih sejuk (Kasus 3).
