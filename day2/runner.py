"""
Runner — простой платформер-бегалка в стиле Mario.

Герой бежит вправо, прыгает по платформам, собирает монетки и
ПРЫГАЕТ НА ВРАГОВ СВЕРХУ, чтобы их раздавить (как в Mario). Налетел на
врага сбоку — теряешь жизнь.

Управление:
  - ПРОБЕЛ / СТРЕЛКА ВВЕРХ — прыжок (можно двойной прыжок).
  - Esc — выход.
  - ENTER — начать заново после проигрыша.

Графика и звуки — бесплатные ассеты Kenney (CC0), лежат в day2/assets/.
Если файлы ассетов не найдены, игра рисует простые фигуры — работает в
любом случае. См. assets/CREDITS.txt.

Запуск:
  venv/bin/python day2/runner.py
"""

import os
import random
import sys

import pygame

# ---------------------------------------------------------------------------
# Настройки (можно менять на уроке)
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 900, 500
FPS = 60
GROUND_Y = HEIGHT - 70          # уровень земли (верх травы)
GRAVITY = 0.8
JUMP_SPEED = -15
STOMP_BOUNCE = -11              # подскок после того, как раздавил врага
SCROLL_SPEED = 5                # скорость бега (мир едет влево)

START_LIVES = 3

# ---------------------------------------------------------------------------
# УРОВНИ. Теперь игру можно ПРОЙТИ: у каждого уровня есть конечная длина и
# флаг-финиш. Дошёл до флага — уровень пройден, дальше следующий (сложнее).
# Прошёл все уровни — победа!
# ---------------------------------------------------------------------------
LEVELS = [
    # name        длина (в пикселях прокрутки)  скорость  доля врагов
    {"name": "Зелёные холмы",   "length": 4200, "speed": 5, "enemy_mult": 1.0},
    {"name": "Каменная тропа",  "length": 5200, "speed": 6, "enemy_mult": 1.3},
    {"name": "Небесные башни",  "length": 6000, "speed": 7, "enemy_mult": 1.6},
]

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# Цвета (R, G, B) — используются для фона и как запасной вариант рисования
SKY_TOP = (135, 206, 250)
SKY_BOTTOM = (200, 235, 255)
GROUND_GREEN = (96, 187, 70)
GROUND_BROWN = (134, 89, 45)
PLATFORM_TOP = (120, 200, 90)
PLATFORM_SIDE = (134, 89, 45)
HERO_COLOR = (220, 50, 50)
HERO_DARK = (150, 30, 30)
ENEMY_COLOR = (90, 60, 40)
ENEMY_DARK = (60, 40, 25)
TEXT_DARK = (40, 40, 40)
WHITE = (255, 255, 255)
GOLD = (255, 200, 0)
GOLD_DARK = (200, 150, 0)
RED = (200, 40, 40)


# ---------------------------------------------------------------------------
# Загрузка ассетов (картинки и звуки). Всё с запасным вариантом.
# ---------------------------------------------------------------------------
IMAGES = {}
SOUNDS = {}


def load_image(name, size=None):
    """Загрузить картинку из assets/images/. Вернуть None, если нет файла."""
    path = os.path.join(ASSETS_DIR, "images", name)
    if not os.path.exists(path):
        return None
    img = pygame.image.load(path).convert_alpha()
    if size is not None:
        img = pygame.transform.smoothscale(img, size)
    return img


def load_sound(name):
    """Загрузить звук из assets/sounds/. Вернуть None, если нет/нет аудио."""
    path = os.path.join(ASSETS_DIR, "sounds", name)
    if not os.path.exists(path):
        return None
    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        return None


def load_assets():
    """Заполнить словари IMAGES и SOUNDS. Безопасно при отсутствии файлов."""
    # картинки масштабируем под игровые размеры
    IMAGES["player_walk1"] = load_image("player_walk1.png", (40, 54))
    IMAGES["player_walk2"] = load_image("player_walk2.png", (40, 54))
    IMAGES["player_stand"] = load_image("player_stand.png", (40, 54))
    IMAGES["player_jump"] = load_image("player_jump.png", (40, 54))
    IMAGES["coin"] = load_image("coin.png", (28, 28))
    IMAGES["grass"] = load_image("grass.png", (36, 36))
    IMAGES["enemy_walk"] = load_image("enemy_walk.png", (46, 30))
    IMAGES["enemy_squashed"] = load_image("enemy_squashed.png", (46, 18))

    SOUNDS["coin"] = load_sound("coin.ogg")
    SOUNDS["jump"] = load_sound("jump.ogg")
    SOUNDS["hurt"] = load_sound("hurt.ogg")
    SOUNDS["stomp"] = load_sound("stomp.ogg")


def play(name):
    s = SOUNDS.get(name)
    if s is not None:
        s.play()


class Hero:
    """Герой. Прыгает и падает под действием гравитации, стоит на
    платформах и на земле."""

    def __init__(self):
        self.w = 38
        self.h = 50
        self.x = 140
        self.y = GROUND_Y - self.h
        self.vy = 0
        self.on_ground = True
        self.jumps_left = 2          # двойной прыжок
        self.run_frame = 0

    def jump(self):
        if self.jumps_left > 0:
            self.vy = JUMP_SPEED
            self.on_ground = False
            self.jumps_left -= 1
            play("jump")

    def update(self, platforms):
        self.vy += GRAVITY
        self.y += self.vy
        self.on_ground = False

        if self.y >= GROUND_Y - self.h:
            self.y = GROUND_Y - self.h
            self.vy = 0
            self.on_ground = True

        if self.vy >= 0:
            for p in platforms:
                if (self.rect.right > p.x and self.rect.left < p.x + p.w
                        and p.y <= self.rect.bottom <= p.y + 28
                        and self.rect.bottom - self.vy <= p.y + 1):
                    self.y = p.y - self.h
                    self.vy = 0
                    self.on_ground = True

        if self.on_ground:
            self.jumps_left = 2

        self.run_frame = (self.run_frame + 1) % 20

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, screen):
        r = self.rect
        # выбор спрайта по состоянию
        if not self.on_ground and IMAGES.get("player_jump"):
            img = IMAGES["player_jump"]
        elif IMAGES.get("player_walk1"):
            img = (IMAGES["player_walk1"] if (self.run_frame // 10) == 0
                   else IMAGES["player_walk2"])
        else:
            img = None

        if img is not None:
            screen.blit(img, (r.x - 1, r.y - 4))
            return

        # запасной вариант — простая фигурка
        pygame.draw.rect(screen, HERO_COLOR, r, border_radius=8)
        pygame.draw.rect(screen, HERO_DARK, (r.x - 2, r.y - 8, r.w + 4, 12),
                         border_radius=6)
        pygame.draw.circle(screen, WHITE, (r.x + 27, r.y + 16), 6)
        pygame.draw.circle(screen, TEXT_DARK, (r.x + 29, r.y + 16), 3)
        leg = 6 if (self.run_frame // 10) == 0 else -6
        if self.on_ground:
            pygame.draw.rect(screen, HERO_DARK, (r.x + 6, r.bottom - 2, 9, 8))
            pygame.draw.rect(screen, HERO_DARK,
                             (r.x + 22 + leg // 2, r.bottom - 2, 9, 8))


class Platform:
    """Парящая платформа, по которой можно прыгать."""

    def __init__(self, x, y, w):
        self.x = x
        self.y = y
        self.w = w
        self.h = 24

    def move(self, dx):
        self.x += dx

    def off_screen(self):
        return self.x + self.w < -10

    def draw(self, screen):
        grass = IMAGES.get("grass")
        if grass is not None:
            tile = grass.get_width()
            x = self.x
            while x < self.x + self.w:
                screen.blit(grass, (x, self.y))
                x += tile
            return
        pygame.draw.rect(screen, PLATFORM_SIDE,
                         (self.x, self.y, self.w, self.h), border_radius=6)
        pygame.draw.rect(screen, PLATFORM_TOP, (self.x, self.y, self.w, 8),
                         border_radius=6)


class Coin:
    """Монетка. Собирается при касании героем."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 13
        self.collected = False
        self.spin = random.randint(0, 30)

    def move(self, dx):
        self.x += dx

    def off_screen(self):
        return self.x + self.r < -10

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.r), int(self.y - self.r),
                           self.r * 2, self.r * 2)

    def update(self):
        self.spin += 1

    def draw(self, screen):
        img = IMAGES.get("coin")
        if img is not None:
            # лёгкое «вращение» — сжимаем спрайт по ширине
            phase = (self.spin % 40) / 40.0
            scale = abs(pygame.math.Vector2(1, 0).rotate(phase * 360).x)
            w = max(4, int(img.get_width() * scale))
            squished = pygame.transform.smoothscale(img, (w, img.get_height()))
            screen.blit(squished, (int(self.x - w / 2),
                                   int(self.y - img.get_height() / 2)))
            return
        phase = (self.spin % 40) / 40.0
        w = abs(pygame.math.Vector2(self.r, 0).rotate(phase * 360).x) + 3
        rect = (int(self.x - w), int(self.y - self.r), int(w * 2), self.r * 2)
        pygame.draw.ellipse(screen, GOLD, rect)
        pygame.draw.ellipse(screen, GOLD_DARK, rect, 2)


class Enemy:
    """Враг, ползущий по земле. Прыгни на него сверху, чтобы раздавить."""

    def __init__(self, x):
        self.w = 44
        self.h = 30
        self.x = x
        self.y = GROUND_Y - self.h
        self.wobble = random.randint(0, 20)
        self.squashed = False
        self.squash_timer = 0          # сколько кадров показывать «блин»

    def move(self, dx):
        self.x += dx

    def off_screen(self):
        return self.x + self.w < -10

    def squash(self):
        self.squashed = True
        self.squash_timer = 25
        self.h = 16
        self.y = GROUND_Y - self.h

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self):
        self.wobble += 1
        if self.squashed:
            self.squash_timer -= 1

    def gone(self):
        return self.off_screen() or (self.squashed and self.squash_timer <= 0)

    def draw(self, screen):
        r = self.rect
        key = "enemy_squashed" if self.squashed else "enemy_walk"
        img = IMAGES.get(key)
        if img is not None:
            screen.blit(img, (r.x, r.y))
            return

        if self.squashed:
            pygame.draw.ellipse(screen, ENEMY_DARK, r)
            return
        pygame.draw.ellipse(screen, ENEMY_COLOR, r)
        pygame.draw.ellipse(screen, ENEMY_DARK, r, 3)
        pygame.draw.circle(screen, WHITE, (r.x + 12, r.y + 12), 5)
        pygame.draw.circle(screen, WHITE, (r.x + 28, r.y + 12), 5)
        pygame.draw.circle(screen, TEXT_DARK, (r.x + 13, r.y + 12), 2)
        pygame.draw.circle(screen, TEXT_DARK, (r.x + 29, r.y + 12), 2)
        off = 3 if (self.wobble // 10) == 0 else -3
        pygame.draw.line(screen, ENEMY_DARK, (r.x + 8, r.bottom),
                         (r.x + 8 + off, r.bottom + 6), 3)
        pygame.draw.line(screen, ENEMY_DARK, (r.right - 8, r.bottom),
                         (r.right - 8 - off, r.bottom + 6), 3)


class Goal:
    """Флаг-финиш в конце уровня. Коснулся — уровень пройден."""

    def __init__(self, x):
        self.x = x
        self.w = 14
        self.h = 180
        self.y = GROUND_Y - self.h

    def move(self, dx):
        self.x += dx

    @property
    def rect(self):
        # ловим героя по всей высоте флагштока
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, screen):
        # столб
        pygame.draw.rect(screen, (90, 90, 100),
                         (int(self.x), int(self.y), self.w, self.h),
                         border_radius=4)
        pygame.draw.circle(screen, GOLD, (int(self.x + self.w / 2),
                                          int(self.y)), 9)
        # флаг
        flag = [
            (self.x + self.w, self.y + 6),
            (self.x + self.w + 56, self.y + 22),
            (self.x + self.w, self.y + 40),
        ]
        pygame.draw.polygon(screen, RED, [(int(a), int(b)) for a, b in flag])
        pygame.draw.polygon(screen, (140, 20, 20),
                            [(int(a), int(b)) for a, b in flag], 2)


def draw_background(screen, scroll_x):
    for y in range(HEIGHT):
        t = y / HEIGHT
        col = (
            int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t),
            int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t),
            int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t),
        )
        pygame.draw.line(screen, col, (0, y), (WIDTH, y))

    hill_off = -(scroll_x // 3) % (WIDTH + 200)
    for base in (-200, hill_off - 200, hill_off):
        pygame.draw.circle(screen, (120, 200, 110), (base + 150, GROUND_Y), 120)
        pygame.draw.circle(screen, (120, 200, 110), (base + 450, GROUND_Y), 160)

    cloud_off = -(scroll_x // 2) % (WIDTH + 300)
    for base in (cloud_off - 300, cloud_off, cloud_off + 300):
        for dx, dy, r in ((0, 0, 22), (28, 6, 28), (60, 0, 22)):
            pygame.draw.circle(screen, WHITE, (base + 100 + dx, 90 + dy), r)

    # земля: плиткой травы, если есть спрайт
    grass = IMAGES.get("grass")
    if grass is not None:
        tile = grass.get_width()
        x = -(scroll_x % tile)
        while x < WIDTH:
            screen.blit(grass, (x, GROUND_Y))
            x += tile
        pygame.draw.rect(screen, GROUND_BROWN,
                         (0, GROUND_Y + tile, WIDTH, HEIGHT))
    else:
        pygame.draw.rect(screen, GROUND_GREEN, (0, GROUND_Y, WIDTH, 18))
        pygame.draw.rect(screen, GROUND_BROWN,
                         (0, GROUND_Y + 18, WIDTH, HEIGHT - GROUND_Y - 18))


def draw_hud(screen, font, score, lives, level_name="", progress=0.0):
    screen.blit(font.render(f"Монетки: {score}", True, TEXT_DARK), (16, 14))

    # название уровня по центру сверху
    if level_name:
        lbl = font.render(level_name, True, TEXT_DARK)
        screen.blit(lbl, lbl.get_rect(midtop=(WIDTH // 2, 12)))

    # прогресс-бар до финиша (чтобы видеть цель уровня)
    bar_w, bar_h = 260, 14
    bx = (WIDTH - bar_w) // 2
    by = 44
    pygame.draw.rect(screen, (255, 255, 255), (bx, by, bar_w, bar_h),
                     border_radius=7)
    pygame.draw.rect(screen, (120, 200, 90),
                     (bx, by, int(bar_w * max(0.0, min(1.0, progress))), bar_h),
                     border_radius=7)
    pygame.draw.rect(screen, TEXT_DARK, (bx, by, bar_w, bar_h), 2,
                     border_radius=7)
    # флажок на конце бара
    pygame.draw.polygon(screen, RED, [
        (bx + bar_w + 4, by - 4), (bx + bar_w + 18, by + 2),
        (bx + bar_w + 4, by + 8)])

    coin = IMAGES.get("coin")
    for i in range(lives):
        cx = WIDTH - 40 - i * 36
        cy = 30
        pygame.draw.circle(screen, RED, (cx - 7, cy), 9)
        pygame.draw.circle(screen, RED, (cx + 7, cy), 9)
        pygame.draw.polygon(screen, RED,
                            [(cx - 15, cy + 4), (cx + 15, cy + 4), (cx, cy + 22)])


def _coins_on_platform(p):
    """Разложить монетки ровным рядком поверх платформы."""
    coins = []
    n = max(1, p.w // 40)
    for i in range(n):
        coins.append(Coin(p.x + 22 + i * 40, p.y - 26))
    return coins


def spawn_chunk(start_x, enemy_mult=1.0):
    """Сгенерировать кусок уровня. Случайно выбираем одну из «комнат»:
    ступеньки, этажи-башня, мостик через пропасть, парящая платформа или
    дуга монеток. enemy_mult увеличивает шанс врагов на сложных уровнях.
    Возвращает (platforms, coins, enemies, next_x)."""
    platforms, coins, enemies = [], [], []

    def maybe_enemy(chance, x):
        if random.random() < chance * enemy_mult:
            enemies.append(Enemy(x))

    kind = random.choice([
        "stairs", "stairs", "tower", "gap", "platform", "arc",
    ])

    if kind == "stairs":
        # лесенка вверх (или вниз) из небольших ступенек
        steps = random.randint(3, 4)
        step_w = 64
        step_h = 46
        going_up = random.random() < 0.6
        for i in range(steps):
            level = i if going_up else (steps - 1 - i)
            px = start_x + i * step_w
            py = GROUND_Y - 40 - level * step_h
            p = Platform(px, py, step_w)
            platforms.append(p)
            coins.append(Coin(px + step_w // 2, py - 26))
        width_used = steps * step_w
        maybe_enemy(0.4, start_x + width_used + 20)
        next_x = start_x + width_used + random.randint(80, 160)

    elif kind == "tower":
        # «этажи» — несколько платформ друг над другом со сдвигом
        floors = random.randint(2, 3)
        pw = random.randint(120, 160)
        for i in range(floors):
            shift = random.randint(-30, 30)
            px = start_x + shift
            py = GROUND_Y - 80 - i * 95
            p = Platform(px, py, pw)
            platforms.append(p)
            coins += _coins_on_platform(p)
        maybe_enemy(0.5, start_x + random.randint(60, 180))
        next_x = start_x + pw + random.randint(160, 240)

    elif kind == "gap":
        # пропасть с маленькими «островками»-ступеньками для перепрыгивания
        islands = random.randint(2, 3)
        gap = 95
        isl_w = 70
        for i in range(islands):
            px = start_x + i * (isl_w + gap)
            py = GROUND_Y - random.randint(50, 110)
            p = Platform(px, py, isl_w)
            platforms.append(p)
            coins.append(Coin(px + isl_w // 2, py - 26))
        next_x = start_x + islands * (isl_w + gap) + random.randint(60, 140)

    elif kind == "platform":
        # одна широкая парящая платформа (как раньше)
        pw = random.randint(120, 200)
        py = GROUND_Y - random.randint(90, 170)
        p = Platform(start_x, py, pw)
        platforms.append(p)
        coins += _coins_on_platform(p)
        maybe_enemy(0.5, start_x + random.randint(120, 240))
        next_x = start_x + random.randint(280, 360)

    else:  # arc — дуга монеток над землёй (награда за прыжок)
        n = random.randint(3, 5)
        for i in range(n):
            arc = -abs((i - (n - 1) / 2)) * 22 + 70
            coins.append(Coin(start_x + 30 + i * 45, GROUND_Y - 60 - arc))
        maybe_enemy(0.6, start_x + random.randint(120, 240))
        next_x = start_x + random.randint(280, 360)

    return platforms, coins, enemies, next_x


def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        pass  # без звуковой карты играем молча
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Runner — собирай монетки, прыгай на врагов!")
    clock = pygame.time.Clock()

    load_assets()

    font = pygame.font.SysFont("Arial", 24, bold=True)
    font_big = pygame.font.SysFont("Arial", 36, bold=True)
    font_huge = pygame.font.SysFont("Arial", 64, bold=True)

    def start_level(state, level_index):
        """Загрузить уровень: сбросить мир, поставить флаг-финиш в конце.
        Сохраняем общий счёт и жизни между уровнями."""
        level = LEVELS[level_index]
        state["level_index"] = level_index
        state["hero"] = Hero()
        state["platforms"] = []
        state["coins"] = []
        state["enemies"] = []
        state["goal"] = None
        state["scroll"] = 0
        state["next_x"] = WIDTH + 100
        state["invuln"] = 0
        state["popups"] = []
        state["speed"] = level["speed"]
        state["length"] = level["length"]
        state["enemy_mult"] = level["enemy_mult"]
        state["banner"] = level["name"]
        state["banner_timer"] = 120
        return state

    def new_game():
        state = {
            "score": 0,
            "lives": START_LIVES,
            "game_over": False,
            "level_done": False,
            "won": False,
        }
        return start_level(state, 0)

    state = new_game()

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif state["game_over"] or state["won"]:
                    if event.key == pygame.K_RETURN:
                        state = new_game()
                elif state["level_done"]:
                    if event.key == pygame.K_RETURN:
                        state["level_done"] = False
                        start_level(state, state["level_index"] + 1)
                elif event.key in (pygame.K_SPACE, pygame.K_UP):
                    state["hero"].jump()

        active = not (state["game_over"] or state["level_done"]
                      or state["won"])
        if active:
            hero = state["hero"]
            speed = state["speed"]
            dx = -speed
            state["scroll"] += speed

            # координата финиша уровня в текущей системе мира
            goal_world_x = WIDTH + 100 + (state["length"] - state["scroll"])

            state["next_x"] += dx
            # генерируем комнаты, пока не дошли до места под флаг-финиш
            while state["next_x"] <= WIDTH and state["next_x"] < goal_world_x:
                p, c, e, nx = spawn_chunk(state["next_x"],
                                          state["enemy_mult"])
                state["platforms"] += p
                state["coins"] += c
                state["enemies"] += e
                state["next_x"] = nx

            # поставить флаг, когда он входит в зону видимости
            if state["goal"] is None and goal_world_x <= WIDTH + 80:
                state["goal"] = Goal(goal_world_x)

            for p in state["platforms"]:
                p.move(dx)
            for c in state["coins"]:
                c.move(dx)
                c.update()
            for e in state["enemies"]:
                e.move(dx)
                e.update()
            if state["goal"] is not None:
                state["goal"].move(dx)

            hero.update(state["platforms"])

            # дошёл до флага — уровень пройден!
            if (state["goal"] is not None
                    and hero.rect.colliderect(state["goal"].rect)):
                play("coin")
                if state["level_index"] + 1 < len(LEVELS):
                    state["level_done"] = True
                else:
                    state["won"] = True

            # сбор монеток
            for c in state["coins"]:
                if not c.collected and c.rect.colliderect(hero.rect):
                    c.collected = True
                    state["score"] += 1
                    play("coin")
                    state["popups"].append(
                        {"x": c.x, "y": c.y, "text": "+1",
                         "color": GOLD_DARK, "life": 30})

            # столкновение с врагами: сверху -> раздавить, сбоку -> урон
            for e in state["enemies"]:
                if e.squashed:
                    continue
                if not e.rect.colliderect(hero.rect):
                    continue
                falling = hero.vy > 0
                from_above = hero.rect.bottom - hero.vy <= e.rect.top + 12
                if falling and from_above:
                    # РАЗДАВИЛ врага сверху
                    e.squash()
                    hero.vy = STOMP_BOUNCE       # подскок
                    hero.jumps_left = 1
                    state["score"] += 5
                    play("stomp")
                    state["popups"].append(
                        {"x": e.x + e.w / 2, "y": e.y - 10, "text": "+5",
                         "color": (40, 170, 70), "life": 35})
                elif state["invuln"] == 0:
                    state["lives"] -= 1
                    state["invuln"] = 90
                    play("hurt")
                    state["popups"].append(
                        {"x": hero.x + 20, "y": hero.y - 20, "text": "Ой!",
                         "color": RED, "life": 40})
                    if state["lives"] <= 0:
                        state["game_over"] = True

            if state["invuln"] > 0:
                state["invuln"] -= 1

            state["platforms"] = [p for p in state["platforms"]
                                  if not p.off_screen()]
            state["coins"] = [c for c in state["coins"]
                              if not c.collected and not c.off_screen()]
            state["enemies"] = [e for e in state["enemies"] if not e.gone()]

            for pp in state["popups"]:
                pp["y"] -= 1
                pp["x"] += dx
                pp["life"] -= 1
            state["popups"] = [pp for pp in state["popups"] if pp["life"] > 0]

        # ---------------- отрисовка ----------------
        draw_background(screen, state["scroll"])
        for p in state["platforms"]:
            p.draw(screen)
        for c in state["coins"]:
            c.draw(screen)
        for e in state["enemies"]:
            e.draw(screen)
        if state["goal"] is not None:
            state["goal"].draw(screen)

        if state["invuln"] == 0 or (state["invuln"] // 5) % 2 == 0:
            state["hero"].draw(screen)

        for pp in state["popups"]:
            surf = font.render(pp["text"], True, pp["color"])
            screen.blit(surf, surf.get_rect(center=(int(pp["x"]), int(pp["y"]))))

        progress = state["scroll"] / state["length"] if state["length"] else 0
        level_name = (f"Уровень {state['level_index'] + 1}: "
                      f"{LEVELS[state['level_index']]['name']}")
        draw_hud(screen, font, state["score"], state["lives"],
                 level_name, progress)

        # баннер с названием уровня в начале
        if state.get("banner_timer", 0) > 0 and not state["game_over"]:
            state["banner_timer"] -= 1
            txt = font_big.render(level_name, True, WHITE)
            box = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
            bg = box.inflate(40, 24)
            overlay = pygame.Surface(bg.size, pygame.SRCALPHA)
            overlay.fill((20, 20, 40, 170))
            screen.blit(overlay, bg)
            screen.blit(txt, box)

        if state["scroll"] < 240 and not state["game_over"]:
            hint = font.render(
                "ПРОБЕЛ — прыжок. Прыгни на врага СВЕРХУ, чтобы раздавить!",
                True, TEXT_DARK)
            screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 22)))

        if state["game_over"]:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((20, 20, 40))
            screen.blit(overlay, (0, 0))
            over = font_huge.render("Игра окончена", True, WHITE)
            screen.blit(over, over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
            sc = font_big.render(f"Очки: {state['score']}", True, GOLD)
            screen.blit(sc, sc.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))
            again = font.render("Нажми ENTER, чтобы играть снова", True, WHITE)
            screen.blit(again, again.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

        if state["level_done"]:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((20, 40, 20))
            screen.blit(overlay, (0, 0))
            done = font_huge.render("Уровень пройден!", True, GOLD)
            screen.blit(done, done.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 - 50)))
            sc = font_big.render(f"Очки: {state['score']}", True, WHITE)
            screen.blit(sc, sc.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))
            nxt = font.render("Нажми ENTER — следующий уровень", True, WHITE)
            screen.blit(nxt, nxt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

        if state["won"]:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(190)
            overlay.fill((40, 30, 10))
            screen.blit(overlay, (0, 0))
            win = font_huge.render("ПОБЕДА!", True, GOLD)
            screen.blit(win, win.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
            sub = font_big.render("Ты прошёл все уровни!", True, WHITE)
            screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            sc = font_big.render(f"Итог: {state['score']} очков", True, GOLD)
            screen.blit(sc, sc.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))
            again = font.render("Нажми ENTER, чтобы играть снова", True, WHITE)
            screen.blit(again, again.get_rect(
                center=(WIDTH // 2, HEIGHT // 2 + 100)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
