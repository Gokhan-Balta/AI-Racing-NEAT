# Racing AI — NEAT ile Öğrenen Araba

Pygame ile oluşturulmuş bir yarış pisti üzerinde,  
NEAT algoritması kullanarak kendi kendine sürmeyi öğrenen bir yapay zeka.

## Nasıl çalışır?

Her nesilde 20 araba piste salınır. Duvara çarpanlar elenir.  
Hayatta kalanların beyinleri çaprazlanıp mutasyona uğratılır.  
Nesiller ilerledikçe arabalar pisti tamamlamayı öğrenir.

## Kullanılan teknolojiler

- Python 3.12
- Pygame — oyun motoru ve görselleştirme
- NEAT-Python — evrimsel sinir ağı algoritması
- Pillow — pist görsellerini işleme

## Kurulum

```bash
git clone https://github.com/kullanici_adi/racing-ai.git
cd racing-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
# Eğitimi başlat
python neat_runner.py

# Yeni pist ekle
python track_manager.py pist_adi
```

## Proje yapısı

```
racing_AI/
├── car.py            # Araba sınıfı ve sensörler
├── neat_runner.py    # NEAT eğitim döngüsü
├── track_manager.py  # Pist yönetim aracı
├── config.txt        # NEAT parametreleri
├── tracks/           # Pist PNG ve JSON dosyaları
└── requirements.txt
```