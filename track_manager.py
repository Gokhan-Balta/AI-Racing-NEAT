import pygame
import json
import math
import os
from PIL import Image

SCREEN_W = 800
SCREEN_H = 600


def resize_track(image_path):
    img = Image.open(image_path)
    if img.size != (SCREEN_W, SCREEN_H):
        img = img.resize((SCREEN_W, SCREEN_H), Image.LANCZOS)
        img.save(image_path)
        print(f"Boyut duzeltildi: {image_path}")


def find_start(image_path):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Sol tik x2: cizgi ust/alt | Sag tik: yon | S: kaydet")

    track = pygame.image.load(image_path).convert()
    font  = pygame.font.SysFont("Arial", 18)

    point_top    = None
    point_bottom = None
    mid_point    = None
    angle_point  = None
    angle        = None

    print("\nTalimatlar:")
    print("1. Sol tik: Baslangic cizgisinin UST noktasi")
    print("2. Sol tik: Baslangic cizgisinin ALT noktasi")
    print("3. Sag tik: Yon noktasi")
    print("4. S: Kaydet\n")

    running = True
    while running:
        screen.blit(track, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if point_top is None:
                        point_top = event.pos
                        print(f"Ust nokta: {point_top}")
                    elif point_bottom is None:
                        point_bottom = event.pos
                        mid_x = round((point_top[0] + point_bottom[0]) / 2)
                        mid_y = round((point_top[1] + point_bottom[1]) / 2)
                        mid_point = (mid_x, mid_y)
                        print(f"Alt nokta: {point_bottom}")
                        print(f"Orta nokta: {mid_point}")

                elif event.button == 3:
                    angle_point = event.pos
                    if mid_point:
                        dx = angle_point[0] - mid_point[0]
                        dy = angle_point[1] - mid_point[1]
                        angle = round(math.degrees(math.atan2(-dy, dx)), 1)
                        print(f"Yon: {angle_point} | Aci: {angle}")

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and mid_point and angle is not None:
                    running = False

        # Ust nokta — mavi
        if point_top:
            pygame.draw.circle(screen, (0, 150, 255), point_top, 7)
            screen.blit(font.render("UST", True, (0, 150, 255)), (point_top[0]+10, point_top[1]-10))

        # Alt nokta — turuncu
        if point_bottom:
            pygame.draw.circle(screen, (255, 150, 0), point_bottom, 7)
            screen.blit(font.render("ALT", True, (255, 150, 0)), (point_bottom[0]+10, point_bottom[1]-10))
        
        # Orta nokta — kırmızı
        if mid_point:
            pygame.draw.line(screen, (255, 255, 255), point_top, point_bottom, 2)
            pygame.draw.circle(screen, (255, 0, 0), mid_point, 8)
            pygame.draw.circle(screen, (255, 255, 0), mid_point, 4)

        # Yön çizgisi ve noktası — yeşil
        if angle_point and mid_point:
            pygame.draw.line(screen, (0, 255, 0), mid_point, angle_point, 2)
            pygame.draw.circle(screen, (0, 255, 0), angle_point, 7)

        # Talimat yazısı
        if point_top is None:
            msg = "1. Sol tik: Cizginin UST noktasi"
        elif point_bottom is None:
            msg = "2. Sol tik: Cizginin ALT noktasi"
        elif angle is None:
            msg = "3. Sag tik: Yon noktasi sec"
        else:
            msg = "S tusuna bas: Kaydet"

        screen.blit(font.render(msg, True, (255, 255, 0)), (10, 10))
        screen.blit(font.render(str(pygame.mouse.get_pos()), True, (150, 150, 150)), (10, 35))

        if mid_point:
            screen.blit(font.render(f"Orta: {mid_point}", True, (255, 255, 0)), (10, 60))
        if angle is not None:
            screen.blit(font.render(f"Aci: {angle}", True, (100, 255, 100)), (10, 85))

        pygame.display.flip()

    pygame.quit()

    return {
        "point_top":    list(point_top),
        "point_bottom": list(point_bottom),
        "x":            mid_point[0],
        "y":            mid_point[1],
        "angle":        angle,
        "angle_point":  list(angle_point)
    }


def save_track_config(track_name, config_data):
    os.makedirs("tracks", exist_ok=True)
    path = os.path.join("tracks", f"{track_name}.json")
    with open(path, "w") as f:
        json.dump(config_data, f, indent=2)
    print(f"Kaydedildi: {path}")


def load_track_config(track_name):
    path = os.path.join("tracks", f"{track_name}.json")
    with open(path, "r") as f:
        return json.load(f)


def setup_new_track(track_name):
    image_path = os.path.join("tracks", f"{track_name}.png")

    if not os.path.exists(image_path):
        print(f"HATA: {image_path} bulunamadi!")
        print("Pist PNG dosyasini tracks/ klasorune koy.")
        return

    resize_track(image_path)

    print(f"\n'{track_name}' pisti icin baslangic noktasi seciliyor...")
    config = find_start(image_path)

    if config:
        save_track_config(track_name, config)
        print(f"\nTamamlandi!")
        print(f"  Ust nokta : {config['point_top']}")
        print(f"  Alt nokta : {config['point_bottom']}")
        print(f"  Orta nokta: x={config['x']}, y={config['y']}")
        print(f"  Aci       : {config['angle']}")
    else:
        print("Iptal edildi.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Kullanim: python track_manager.py <pist_adi>")
        print("Ornek   : python track_manager.py oval")
    else:
        setup_new_track(sys.argv[1])