import pygame
import math

# Renkler
WHITE = (255, 255, 255)
RED   = (200, 50, 50)
YELLOW = (255, 255, 0)

class Car:
    """
    Bir arabayı temsil eden sınıf.
    """

    def __init__(self, x, y):
        # Konum
        self.x = x
        self.y = y

        # Tur
        self.lap_done = False
        self.started = False
        
        # Açı (derece cinsinden)
        # 0 = sağa bakıyor, 90 = yukarı, 180 = sola, 270 = aşağı
        self.angle = 0

        # Hız
        self.speed = 3

        # Araba hayatta mı?
        self.alive = True

        # Araba kaç piksel ilerledi- fitness skoru için
        self.distance = 0

        # Sensörler — 5 adet ışın fırlatır
        # Her biri bir yönde duvara olan mesafeyi ölçer
        self.sensors = []

    def update(self, track_mask):
        
        """
        Arabayı hareket ettirir, sensörleri günceller,
        çarpışma kontrolü yapar.
        """

        if not self.alive:
            return  

        # --- HAREKET ---
        # Bu yüzden math.radians() radyan çevrilir.
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y -= math.sin(math.radians(self.angle)) * self.speed
        # Not: y eksenini tersine alınır çünkü pygame'de
        # y aşağı gidince artar (matematik koordinatının tersi)

        self.distance += self.speed

        # --- ÇARPIŞMA KONTROLÜ ---
        # Arabanın bulunduğu piksel siyah mı?
        cx = int(self.x)
        cy = int(self.y)

        # Ekran dışına çıktı mı?
        if cx < 0 or cx >= 800 or cy < 0 or cy >= 600:
            self.alive = False
            return

        # Track mask'a sor: bu nokta yolda mı?
        if track_mask.get_at((cx, cy)) == 0:
            self.alive = False  
            return

        # --- SENSÖRLER ---
        self.sensors = []

        # 5 farklı açıda ışın fırlatıyoruz
        # -90 ile +90 derece arası 
        sensor_angles = [-90, -45, 0, 45, 90]

        for sensor_angle in sensor_angles:
            distance = self._cast_ray(sensor_angle, track_mask)
            self.sensors.append(distance)

    def _cast_ray(self, relative_angle, track_mask):
        """
        Belirli bir açıda ışın fırlatır, duvara olan mesafeyi döndürür.
        
        relative_angle: arabanın yönüne göre kaç derece sapma
        
        Nasıl çalışır?
        Arabanın bulunduğu noktadan dışarı doğru adım adım ilerleriz.
        Her adımda "bu nokta hâlâ yolda mı?" diye sorarız.
        Siyah piksele çarptığımızda durur, kaç adım attığımızı döndürürüz.
        """

        # Işının gerçek açısı = arabanın açısı + sensörün sapması
        angle = math.radians(self.angle + relative_angle)

        # Adım adım ilerle
        for distance in range(1, 200):  # en fazla 200 piksel bak
            # Bu adımdaki koordinat
            rx = int(self.x + math.cos(angle) * distance)
            ry = int(self.y - math.sin(angle) * distance)

            # Ekran dışına çıktı mı?
            if rx < 0 or rx >= 800 or ry < 0 or ry >= 600:
                return distance

            # Duvara çarptı mı?
            if track_mask.get_at((rx, ry)) == 0:
                return distance  # Mesafeyi döndür

        return 200  # 200 piksel içinde duvar bulunamadı

    def draw(self, screen):
        """
        Arabayı ve sensörleri ekrana çizer.
        """

        if not self.alive:
            return

        # Arabayı küçük bir daire olarak çiz
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 8)

        # Sensör ışınlarını çiz (sarı çizgiler)
        sensor_angles = [-90, -45, 0, 45, 90]

        for i, sensor_angle in enumerate(sensor_angles):
            angle = math.radians(self.angle + sensor_angle)
            distance = self.sensors[i] if self.sensors else 0

            # Işının bitiş noktası
            end_x = int(self.x + math.cos(angle) * distance)
            end_y = int(self.y - math.sin(angle) * distance)

            pygame.draw.line(screen, YELLOW,
                           (int(self.x), int(self.y)),
                           (end_x, end_y), 1)

    def get_sensor_data(self):
        """
        NEAT algoritmasına verilecek input değerleri.
        5 sensör mesafesini 0-1 arasına normalize eder.
        
        Neden normalize?
        Neural network'ler küçük sayılarla daha iyi çalışır.
        150 piksel demek yerine 0.75 deriz (150/200 = 0.75)
        """
        if not self.sensors:
            return [0, 0, 0, 0, 0]

        return [s / 200.0 for s in self.sensors]