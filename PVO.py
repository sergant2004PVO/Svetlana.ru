import pygame
import sys
import random

# --- Константы ---
WIDTH, HEIGHT = 900, 600
GROUND_Y = 520

TANK_SPEED = 5
ROCKET_SPEED = -10
HELI_SPEED_MIN = 3
HELI_SPEED_MAX = 6

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ПВО: танк + ПЗРК 'Игла'")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 24)

# --- Цвета ---
SKY = (40, 40, 80)
GROUND = (50, 120, 50)
WHITE = (255, 255, 255)
TANK_COLOR = (0, 200, 0)
HELI_COLOR = (200, 200, 0)
ROCKET_COLOR = (255, 80, 80)


# --- Классы объектов ---
class Tank:
    def __init__(self):
        self.width = 80
        self.height = 40
        self.x = WIDTH // 2
        self.y = GROUND_Y - self.height
        self.speed = TANK_SPEED

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction):
        if direction == "left":
            self.x -= self.speed
        elif direction == "right":
            self.x += self.speed

        # Ограничение по краям экрана
        if self.x < 0:
            self.x = 0
        if self.x + self.width > WIDTH:
            self.x = WIDTH - self.width

    def draw(self, surf):
        # корпус танка
        pygame.draw.rect(surf, TANK_COLOR, self.rect)
        # башня (побольше прямоугольник сверху)
        turret_rect = pygame.Rect(
            self.x + self.width // 4,
            self.y - 15,
            self.width // 2,
            15
        )
        pygame.draw.rect(surf, TANK_COLOR, turret_rect)
        # ствол ПЗРК вверх (условно)
        pygame.draw.rect(
            surf,
            TANK_COLOR,
            (self.x + self.width // 2 - 3, self.y - 40, 6, 25)
        )

    def get_rocket_start_pos(self):
        # Точка вылета ракеты — конец ствола
        return self.x + self.width // 2, self.y - 40


class Rocket:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.speed_y = ROCKET_SPEED
        self.active = True

    @property
    def rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def update(self):
        if not self.active:
            return
        self.y += self.speed_y
        # если улетела за экран — деактивируем
        if self.y < -10:
            self.active = False

    def draw(self, surf):
        if not self.active:
            return
        pygame.draw.circle(surf, ROCKET_COLOR, (int(self.x), int(self.y)), self.radius)


class Helicopter:
    def __init__(self):
        self.width = 80
        self.height = 30
        self.reset()

    def reset(self):
        # С вероятностью 50/50 летит слева направо или справа налево
        side = random.choice(["left", "right"])
        self.y = random.randint(80, 200)
        speed = random.randint(HELI_SPEED_MIN, HELI_SPEED_MAX)
        if side == "left":
            self.x = -self.width
            self.vx = speed
        else:
            self.x = WIDTH
            self.vx = -speed

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x += self.vx
        # если улетел за экран — респавним
        if self.x > WIDTH + self.width or self.x < -self.width:
            self.reset()

    def draw(self, surf):
        # корпус
        pygame.draw.rect(surf, HELI_COLOR, self.rect)
        # винт
        pygame.draw.line(
            surf,
            HELI_COLOR,
            (self.x, self.y),
            (self.x + self.width, self.y),
            4
        )


def draw_ground():
    pygame.draw.rect(screen, GROUND, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))


def draw_hud(score):
    text = font.render(f"Сбитых целей: {score}", True, WHITE)
    screen.blit(text, (10, 10))


def main():
    tank = Tank()
    heli = Helicopter()
    rocket = None
    score = 0

    while True:
        # --- Обработка событий ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Стрельба
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # стреляем, только если ракеты сейчас нет
                    if rocket is None or not rocket.active:
                        rx, ry = tank.get_rocket_start_pos()
                        rocket = Rocket(rx, ry)

        # --- Управление танком ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            tank.move("left")
        if keys[pygame.K_RIGHT]:
            tank.move("right")

        # --- Логика ---
        heli.update()
        if rocket is not None:
            rocket.update()
            # Проверка попадания
            if rocket.active and rocket.rect.colliderect(heli.rect):
                rocket.active = False
                score += 1
                heli.reset()

        # --- Рисование ---
        screen.fill(SKY)
        draw_ground()
        tank.draw(screen)
        heli.draw(screen)
        if rocket is not None:
            rocket.draw(screen)
        draw_hud(score)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
