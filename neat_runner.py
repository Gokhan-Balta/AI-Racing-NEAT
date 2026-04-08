import pygame
import neat
import pickle
import sys
import os
from car import Car
import json


# --- EKRAN BOYUTLARI ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# --- RENK ---
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Kaçıncı nesildeyiz? Ekranda göstereceğiz
generation = 0

# Başlangıç noktası trac için
#START_X = 400
#START_Y = 515

# Başlangıç noktası track_1 için
#START_X = 400
#START_Y = 455

# track_2 için başlangıç noktası
#START_X = 400
#START_Y = 433

# Hangi yolu kullanıyoruz
folder = "tracks"
track_name = "track_1"
# Dosya yolları
image_path = os.path.join(folder, f"{track_name}.png")
json_path = os.path.join(folder, f"{track_name}.json")



def eval_genomes(genomes, config):
    """
    NEAT'in her nesilde çağırdığı ana fonksiyon.

    'genomes' → o nesildeki tüm arabalar (genome = bir arabanın beyni)
    'config'  → config.txt'den okunan ayarlar

    NEAT bu fonksiyona bakarak şunu anlar:
    "Her genomun fitness skoru ne? Kim daha iyi?"
    Bizim görevimiz: her arabayı piste sal, ne kadar
    ilerlediğini ölç, genome.fitness'a yaz.
    """

    global generation
    generation += 1

    # --- PYGAME BAŞLAT ---
    # Her nesilde pygame'i sıfırdan başlatmıyoruz,
    # main bloğunda bir kez başlatıyoruz.
    # Ama ekranı ve pisti burada yeniden kullanıyoruz.
    screen = pygame.display.get_surface()
    clock  = pygame.time.Clock()

    # Pisti yükle
    track     = pygame.image.load(image_path).convert()
    track_mask = pygame.mask.from_threshold(
        track, (255, 255, 255), (30, 30, 30)
    )

    # --- NEURAL NETWORK VE ARABA OLUŞTUR ---
    # Her genome için:
    #   1. neat.nn.FeedForwardNetwork.create() → genomdan sinir ağı yap
    #   2. Car() → o sinir ağıyla kontrol edilecek arabayı yarat
    #
    # 'nets' listesi sinir ağlarını tutar
    # 'cars' listesi arabaları tutar
    # İkisi birbiriyle aynı sırada — nets[0] cars[0]'ı kontrol eder
    nets = []
    cars = []
    
    try:
        with open(json_path, "r") as file:
            track_data = json.load(file)
            START_X = track_data["x"]
            START_Y = track_data["y"]
            START_ANGLE = track_data["angle"]
            START_TOP_POINT = track_data["point_top"]
            START_BOTTOM_POINT = track_data["point_bottom"]
    except FileNotFoundError:
        print(f"Hata: {track_name} dosyaları '{folder}' klasöründe bulunamadı!")
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")


    for genome_id, genome in genomes:
        # Başlangıç fitness skoru 0
        genome.fitness = 0

        # Genomdan sinir ağı oluştur
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)

        # Arabayı oluştur — başlangıç noktası
        car = Car(x=START_X, y=START_Y)
        car.angle = START_ANGLE
        cars.append(car)

    # --- FONT (ekranda yazı için) ---
    font = pygame.font.SysFont("Arial", 20)

    # --- NESIL DÖNGÜSÜ ---
    # Bu döngü o nesildeki tüm arabalar ölene kadar devam eder
    running = True
    while running:

        # Pygame olayları — pencere kapatma
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Model kaydet ve çık
                pygame.quit()
                sys.exit()

        # --- HER ARABAY GÜNCELLE ---
        # Kaç araba hâlâ hayatta?
        alive_count = 0

        for i, car in enumerate(cars):

            if not car.alive:
                continue  # ölmüşse atla

            alive_count += 1

            # Arabayı güncelle (hareket + sensörler + çarpışma)
            car.update(track_mask)

            if not car.alive:
                continue

            # --- SİNİR AĞI KARAR VERİYOR ---
            # Sensör verilerini al (5 sayı, 0-1 arası normalize)
            inputs = car.get_sensor_data()

            # Sinir ağına ver, çıktısını al
            # output → 3 sayı (sol, düz, sağ için)
            # Her biri -1 ile +1 arasında (tanh aktivasyonu)
            output = nets[i].activate(inputs)

            # En yüksek çıktıyı seç → o yöne dön
            # Örnek: output = [0.2, 0.8, -0.3]
            # argmax → index 1 (düz git)
            decision = output.index(max(output))

            if decision == 0:
                car.angle += 5    # sola dön
            elif decision == 2:
                car.angle -= 5    # sağa dön
            # decision == 1 → düz git (açı değişmez)

            # --- FITNESS SKORU GÜNCELLE ---
            # Ne kadar ilerledi? distance değerini fitness'a ekle
            # Bu çok önemli bir tasarım kararı:
            # "Daha uzağa giden araba daha iyi" diyoruz
            genomes[i][1].fitness += car.distance * 0.01

            # --- TUR TAMAMLAMA ---
            # Araba başlangıç noktasına yakın mı?
            dist_to_start = ((car.x - START_X)**2 + (car.y - START_Y)**2) ** 0.5

            # Önce başlangıç noktasından uzaklaşmış olmalı
            if dist_to_start > 80:
                car.started = True

            # Uzaklaştıktan sonra geri dönerse tur tamamdır
            if car.started and dist_to_start < 40:
                car.lap_done = True
                car.alive = False
                genomes[i][1].fitness += 1000
                print(f"Nesil {generation} — araba {i} turu tamamladi!")


        # Tüm arabalar öldüyse nesli bitir
        if alive_count == 0:
            running = False

        # --- EKRANA ÇİZ ---
        screen.blit(track, (0, 0))

        # Başlangıç çizgisi trac için
        #pygame.draw.rect(screen, RED, (390, 445, 20, 96))
        # Başlangıç çizgisi track_1 için
        #pygame.draw.rect(screen, RED, (388, 450, 24, 59))
        #Test
        pygame.draw.line(screen, RED,
            tuple(track_data["point_top"]),
            tuple(track_data["point_bottom"]),
                20)


        # Arabaları çiz
        for car in cars:
            car.draw(screen)

        # Bilgi yazıları
        gen_text   = font.render(f"Nesil: {generation}", True, GREEN)
        alive_text = font.render(f"Hayatta: {alive_count}", True, GREEN)
        screen.blit(gen_text,   (10, 10))
        screen.blit(alive_text, (10, 35))

        pygame.display.flip()
        clock.tick(60)

    # --- NESİL BİTTİ: EN İYİ ARABAY KAYDET ---
    # Bu nesildeki en yüksek fitness'a sahip genomu bul
    best_genome = max(genomes, key=lambda x: x[1].fitness)[1]

    # pickle ile dosyaya yaz
    with open("best_model.pkl", "wb") as f:
        pickle.dump(best_genome, f)

    print(f"Nesil {generation} bitti. "
          f"En iyi fitness: {best_genome.fitness:.1f} | "
          f"Model kaydedildi.")


def run():
    """
    NEAT algoritmasını başlatan fonksiyon.
    Config dosyasını okur, popülasyonu oluşturur,
    eğitimi başlatır.
    """

    # Config dosyasının tam yolu
    # os.path.dirname(__file__) → bu dosyanın bulunduğu klasör
    # Böylece farklı bilgisayarlarda da çalışır
    config_path = os.path.join(
        os.path.dirname(__file__), "config.txt"
    )

    # Config'i yükle
    # neat.config.Config → NEAT'e "hangi sınıfları kullanacaksın?" der
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # Popülasyon oluştur
    # Bu nesil 1'deki tüm arabaları (genomları) hazırlar
    population = neat.Population(config)

    # İstatistikleri terminale yazdır
    # Her nesilde en iyi / ortalama fitness görünür
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Her 10 nesilde bir checkpoint kaydet
    # "checkpoint-" ile başlayan dosyalar oluşturur
    # Kaldığın yerden devam etmek istersen:
    # population = neat.Checkpointer.restore_checkpoint("checkpoint-49")
    population.add_reporter(
        neat.Checkpointer(10, filename_prefix="checkpoint-")
    )

    # Eğitimi başlat — 50 nesil çalıştır
    # Her nesilde eval_genomes fonksiyonu çağrılır
    winner = population.run(eval_genomes, 50)

    print("\nEğitim tamamlandı!")
    print(f"En iyi genome:\n{winner}")


# --- PROGRAM GİRİŞ NOKTASI ---
if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Racing AI — NEAT Eğitimi")

    run()