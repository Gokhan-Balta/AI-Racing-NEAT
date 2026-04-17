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
git clone https://github.com/kullanici_adi/AI-Racing-NEAT.git
cd racing-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Pist Ekleme ve Başlangıç Noktalarının Belirleme. 

Pist yöneticisi ile yeni pistler ve noktalar kolaylıkla belirlenebilir. Burada başlangıç noktası ve yarış yönü gibi noktalar kaydedilir. Bu noktalar pist adı ile model dosyasında kullanılabilir. Bu sayede kolaylıkla pistler arasında geçiş yapılabilir ya da yeni başlangıç noktları belirlenebilir. 

```bash
python track_manager.py track_1
```

<img width="550" height="500" alt="image" src="https://github.com/user-attachments/assets/cf820d43-df91-4006-bf5b-74d366973112" />


## Çalıştırma

```bash
# Eğitimi başlat
python neat_runner.py
```

<img width="550" height="500" alt="image" src="https://github.com/user-attachments/assets/0ceb11a2-59be-498f-8e4c-a312986807d6" />


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
