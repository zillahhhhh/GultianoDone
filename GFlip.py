import pygame
import sys
import math
import random

pygame.init()
pygame.mixer.init()

# ── Music ─────────────────────────────────────────────────────────────────────
try:
    pygame.mixer.music.load("gflp.mp3")
    pygame.mixer.music.set_volume(0.55)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"[Music] Could not load gflp.mp3: {e}")

SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("G FLIP")
clock = pygame.time.Clock()
FPS = 60

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PALETTE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BLACK       = (  0,   0,   0)
DARK_BG     = (  8,   6,  20)
NEON_PINK   = (255,   0, 180)
NEON_CYAN   = (  0, 230, 255)
NEON_YELLOW = (255, 220,   0)
NEON_GREEN  = ( 50, 255, 100)
NEON_PURPLE = (160,   0, 255)
NEON_ORANGE = (255, 140,   0)
WHITE       = (255, 255, 255)
DIM_WHITE   = (180, 180, 200)

BRICK_DARK   = ( 18,  12,  38)
BRICK_MID    = ( 38,  24,  68)
BRICK_LIGHT  = ( 68,  44, 108)
BRICK_MORTAR = ( 10,   8,  22)
CEIL_DARK    = ( 12,  28,  48)
CEIL_MID     = ( 24,  54,  88)
CEIL_LIGHT   = ( 40,  88, 128)
CEIL_MORTAR  = (  8,  16,  28)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  FONTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def pf(size, bold=True):
    for name in ("Courier New", "Lucida Console", "Consolas"):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            pass
    return pygame.font.Font(None, size)

f_title = pf(96)
f_sub   = pf(22)
f_body  = pf(24)
f_small = pf(18)
f_tiny  = pf(14)
f_hud   = pf(20)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BACKGROUND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
try:
    bg_raw = pygame.image.load("Starting-bg.jpg").convert()
    bg_raw = pygame.transform.scale(bg_raw, (SCREEN_W, SCREEN_H))
    HAS_BG = True
except Exception:
    HAS_BG = False

if HAS_BG:
    bg_dark = bg_raw.copy()
    dark_overlay = pygame.Surface((SCREEN_W, SCREEN_H))
    dark_overlay.fill((0, 0, 0))
    dark_overlay.set_alpha(130)
    bg_dark.blit(dark_overlay, (0, 0))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def draw_text_cx(surface, text, font, color, cy):
    img = font.render(text, True, color)
    surface.blit(img, (SCREEN_W // 2 - img.get_width() // 2, cy))

def draw_panel(surface, x, y, w, h, alpha=185, border1=NEON_PINK, border2=NEON_CYAN):
    p = pygame.Surface((w, h), pygame.SRCALPHA)
    p.fill((0, 0, 0, alpha))
    surface.blit(p, (x, y))
    pygame.draw.rect(surface, border1, (x,   y,   w,   h  ), 3)
    pygame.draw.rect(surface, border2, (x+3, y+3, w-6, h-6), 1)

def draw_glow_circle(surface, cx, cy, r, color, max_alpha=160):
    for radius in range(r + 8, 0, -1):
        a = int(max_alpha * (radius / (r + 8)))
        s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, a), (radius, radius), radius)
        surface.blit(s, (cx - radius, cy - radius))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PLATFORM DRAWING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BRICK_W = 48
BRICK_H = 16

def draw_formal_platform(surface, rect_x, rect_y, rect_w, rect_h,
                          dark, mid, light, mortar, edge_color,
                          scroll_offset=0, flip=False):
    pygame.draw.rect(surface, dark, (rect_x, rect_y, rect_w, rect_h))
    num_rows = rect_h // BRICK_H + 1
    for row in range(num_rows):
        by = rect_y + row * BRICK_H
        if by + BRICK_H < rect_y or by > rect_y + rect_h:
            continue
        row_offset = (BRICK_W // 2) if row % 2 == 0 else 0
        offset = int(scroll_offset) % BRICK_W
        bx = rect_x - offset - row_offset
        while bx < rect_x + rect_w:
            clipped_x = max(bx, rect_x)
            clipped_w = min(bx + BRICK_W - 1, rect_x + rect_w) - clipped_x
            clipped_y = max(by, rect_y)
            clipped_h = min(by + BRICK_H - 1, rect_y + rect_h) - clipped_y
            if clipped_w > 0 and clipped_h > 0:
                shade = 0.08 * ((bx // BRICK_W + row) % 3)
                col   = lerp_color(dark, mid, shade + 0.25)
                pygame.draw.rect(surface, col, (clipped_x, clipped_y, clipped_w, clipped_h))
                pygame.draw.line(surface, light, (clipped_x, clipped_y), (clipped_x + clipped_w - 1, clipped_y))
                pygame.draw.line(surface, light, (clipped_x, clipped_y), (clipped_x, clipped_y + clipped_h - 1))
                pygame.draw.line(surface, mortar, (clipped_x, clipped_y + clipped_h), (clipped_x + clipped_w, clipped_y + clipped_h))
                pygame.draw.line(surface, mortar, (clipped_x + clipped_w, clipped_y), (clipped_x + clipped_w, clipped_y + clipped_h))
            bx += BRICK_W
    glow_h = 4
    glow_y = rect_y if flip else rect_y + rect_h - glow_h
    glow_s = pygame.Surface((rect_w, glow_h), pygame.SRCALPHA)
    glow_s.fill((*edge_color, 180))
    surface.blit(glow_s, (rect_x, glow_y))
    outer_s = pygame.Surface((rect_w, 8), pygame.SRCALPHA)
    outer_s.fill((*edge_color, 60))
    outer_y = (rect_y + rect_h) if not flip else rect_y - 8
    surface.blit(outer_s, (rect_x, outer_y))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ASTRONAUT SPRITE SHEET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPRITE_W, SPRITE_H = 80, 100
ANIM_ROWS  = {"idle_ground":0,"idle_ceiling":1,"run_ground":2,"run_ceiling":3,"jump_flip":4}
ANIM_COUNT = {"idle_ground":4,"idle_ceiling":4,"run_ground":6,"run_ceiling":6,"jump_flip":5}
ANIM_FPS   = {"idle_ground":6,"idle_ceiling":6,"run_ground":10,"run_ceiling":10,"jump_flip":12}

try:
    _raw_sheet = pygame.image.load("astronaut_sheet.png").convert_alpha()
    HAS_SPRITES = True
except Exception as e:
    print(f"[Sprites] Could not load astronaut_sheet.png: {e}")
    HAS_SPRITES = False

def get_sprite_frame(anim_name, frame_index):
    if not HAS_SPRITES:
        return None
    row   = ANIM_ROWS[anim_name]
    count = ANIM_COUNT[anim_name]
    col   = frame_index % count
    rect  = pygame.Rect(col * SPRITE_W, row * SPRITE_H, SPRITE_W, SPRITE_H)
    return _raw_sheet.subsurface(rect)

CHAR_RENDER_W = SPRITE_W
CHAR_RENDER_H = SPRITE_H

CHAR_PIXELS = [
    "0000011110000000","0000111111000000","0001111111100000",
    "0001122211100000","0001111111100000","0000111111000000",
    "0000011110000000","0001111111100000","0001122211100000",
    "0001111111100000","0001111111100000","0001111111100000",
    "0000011110000000","0000111001110000","0000111001110000",
    "0000110000110000","0000110000110000","0000110000110000",
    "0000110000110000","0001110000111000",
]
CHAR_PAL_NORMAL = {"1": NEON_CYAN, "2": WHITE, "3": (0,100,140)}
CHAR_PAL_FLIP   = {"1": NEON_PINK, "2": WHITE, "3": (120,0,80)}

def draw_pixel_char(surface, ox, oy, scale=3, flipped=False):
    palette = CHAR_PAL_FLIP if flipped else CHAR_PAL_NORMAL
    rows    = list(reversed(CHAR_PIXELS)) if flipped else CHAR_PIXELS
    for row_i, row in enumerate(rows):
        for col_i, cell in enumerate(row):
            if cell == "0": continue
            col = palette.get(cell, NEON_CYAN)
            pygame.draw.rect(surface, col, (ox + col_i*scale, oy + row_i*scale, scale, scale))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ALIEN ENEMY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALIEN_W = 44
ALIEN_H = 44

GROUND_Y    = SCREEN_H - 70
CEILING_Y   = 50
PLATFORM_H  = 18
PLAY_TOP    = CEILING_Y + PLATFORM_H
PLAY_BOT    = GROUND_Y
PLAY_MID    = (PLAY_TOP + PLAY_BOT) // 2


class Alien:
    MOVE_PATROL  = "patrol"
    MOVE_DIVE    = "dive"
    MOVE_RETREAT = "retreat"

    def __init__(self, screen_x, world_speed, world_scroll):
        self.x          = float(screen_x)
        self.y          = float(random.randint(PLAY_TOP + 60, PLAY_BOT - 60))
        self.base_y     = self.y
        self.vx         = -(world_speed * 0.55 + random.uniform(0.4, 1.0))
        self.vy         = 0.0
        self.hp         = 3
        self.alive      = True
        self.phase      = random.uniform(0, math.pi * 2)
        self.wave_amp   = random.uniform(40, 90)
        self.wave_speed = random.uniform(0.03, 0.06)
        self.tick       = 0
        self.mode       = self.MOVE_PATROL
        self.mode_timer = 0
        self.hit_flash  = 0
        self.death_timer = 0
        self.score_value = 200
        self.tint = random.choice([NEON_GREEN, (0, 255, 120), (80, 255, 80)])
        self.eye_col = random.choice([NEON_YELLOW, NEON_PINK, WHITE])
        self.particles_spawned = False

    def update(self, player_x, player_y, world_speed):
        if not self.alive:
            self.death_timer += 1
            return
        self.tick += 1
        self.hit_flash = max(0, self.hit_flash - 1)
        self.x  += self.vx - world_speed * 0.18
        self.y   = self.base_y + math.sin(self.tick * self.wave_speed + self.phase) * self.wave_amp
        self.y = max(PLAY_TOP + ALIEN_H // 2 + 4, min(PLAY_BOT - ALIEN_H // 2 - 4, self.y))
        self.mode_timer += 1
        if self.mode == self.MOVE_PATROL and self.mode_timer > 90:
            if abs(self.x - player_x) < 320 and random.random() < 0.35:
                self.mode       = self.MOVE_DIVE
                self.mode_timer = 0
                self.base_y = player_y
        elif self.mode == self.MOVE_DIVE and self.mode_timer > 50:
            self.mode       = self.MOVE_PATROL
            self.mode_timer = 0
            self.base_y     = self.y

    def hit(self):
        self.hp       -= 1
        self.hit_flash = 10
        if self.hp <= 0:
            self.alive = False
            self.death_timer = 0
            return True
        return False

    def rect(self):
        hw = ALIEN_W // 2
        hh = ALIEN_H // 2
        return pygame.Rect(int(self.x) - hw + 4, int(self.y) - hh + 4, ALIEN_W - 8, ALIEN_H - 8)

    def draw(self, surface, tick):
        cx, cy = int(self.x), int(self.y)
        t = tick * 0.07 + self.phase
        pulse = (math.sin(t) + 1) / 2
        if self.hit_flash > 0:
            body_col = WHITE
        else:
            body_col = lerp_color(self.tint, (20, 60, 20), 0.35 - 0.2 * pulse)
        glow_r = int(26 + 6 * pulse)
        gs = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        glow_a = int(55 + 35 * pulse)
        pygame.draw.circle(gs, (*self.tint, glow_a), (glow_r, glow_r), glow_r)
        surface.blit(gs, (cx - glow_r, cy - glow_r))
        dome_rect = pygame.Rect(cx - 14, cy - 20, 28, 18)
        pygame.draw.ellipse(surface, lerp_color(body_col, WHITE, 0.25), dome_rect)
        disc_rect = pygame.Rect(cx - 22, cy - 8, 44, 18)
        pygame.draw.ellipse(surface, body_col, disc_rect)
        under_rect = pygame.Rect(cx - 18, cy + 4, 36, 10)
        pygame.draw.ellipse(surface, lerp_color(body_col, BLACK, 0.45), under_rect)
        for i in range(5):
            angle = math.radians(tick * 6 + i * 72 + self.phase * 30)
            lx = cx + int(math.cos(angle) * 14)
            ly = cy + int(math.sin(angle) * 5) + 2
            light_col = self.tint if i % 2 == 0 else NEON_YELLOW
            pygame.draw.circle(surface, light_col, (lx, ly), 2)
        eye_r = int(5 + 1.5 * pulse)
        pygame.draw.circle(surface, self.eye_col, (cx, cy - 10), eye_r)
        pygame.draw.circle(surface, BLACK, (cx, cy - 10), eye_r - 2)
        pygame.draw.circle(surface, self.eye_col, (cx + 2, cy - 13), 2)
        bar_w = 34
        bar_x = cx - bar_w // 2
        bar_y = cy - 28
        pygame.draw.rect(surface, (40, 0, 0), (bar_x, bar_y, bar_w, 5))
        hp_col = NEON_GREEN if self.hp == 3 else (NEON_YELLOW if self.hp == 2 else NEON_PINK)
        pygame.draw.rect(surface, hp_col, (bar_x, bar_y, int(bar_w * self.hp / 3), 5))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, 5), 1)
        beam_alpha = int(60 + 40 * pulse)
        beam_surf = pygame.Surface((20, 30), pygame.SRCALPHA)
        for brow in range(30):
            fade = int(beam_alpha * (1 - brow / 30))
            width = int(20 * (1 - brow / 30))
            if width > 0:
                beam_surf.fill((*self.tint, fade), (10 - width // 2, brow, width, 1))
        surface.blit(beam_surf, (cx - 10, cy + 12))
        pygame.draw.line(surface, self.tint, (cx, cy - 20), (cx + 4, cy - 28), 2)
        pygame.draw.circle(surface, NEON_YELLOW, (cx + 4, cy - 28), int(2 + pulse))
        outline_col = lerp_color(self.tint, WHITE, 0.5 + 0.3 * pulse)
        pygame.draw.ellipse(surface, outline_col, disc_rect, 2)
        pygame.draw.ellipse(surface, outline_col, dome_rect, 1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BOSS ALIEN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOSS_W = 120
BOSS_H = 100
BOSS_MAX_HP = 20
BOSS_PHASE_THRESHOLD = 10


class BossAlien:
    def __init__(self):
        self.x          = float(SCREEN_W - 160)
        self.y          = float(PLAY_MID)
        self.base_y     = float(PLAY_MID)
        self.hp         = BOSS_MAX_HP
        self.alive      = True
        self.phase      = 1
        self.tick       = 0
        self.hit_flash  = 0
        self.death_timer = 0
        self.vx         = 0.0
        self.vy         = 0.0
        self.wave_amp   = 80
        self.wave_speed = 0.022
        self.phase_angle = 0.0
        self.orbs: list = []
        # FIX: large initial cooldown so boss doesn't fire the instant it spawns
        self.orb_cooldown = 150
        self.orb_interval = 90
        self.dashing     = False
        self.dash_timer  = 0
        self.dash_vx     = 0.0
        self.dash_vy     = 0.0
        self.enrage_announced = False
        self.score_value = 2000
        self.spin_angle  = 0.0
        self.tint        = (180, 0, 255)
        self.eye_col     = NEON_PINK
        # FIX: spawn delay — boss won't move or shoot until this reaches 0
        self.spawn_delay = 180

    def update(self, player_x, player_y):
        if not self.alive:
            self.death_timer += 1
            self._update_orbs()
            return

        self.tick       += 1
        self.hit_flash   = max(0, self.hit_flash - 1)
        self.spin_angle  = (self.spin_angle + (3 if self.phase == 1 else 5)) % 360

        # FIX: honour spawn delay — freeze movement and shooting
        if self.spawn_delay > 0:
            self.spawn_delay -= 1
            self._update_orbs()
            return

        self.orb_cooldown = max(0, self.orb_cooldown - 1)
        self.phase_angle += self.wave_speed

        # Phase 2 trigger
        if self.hp <= BOSS_PHASE_THRESHOLD and self.phase == 1:
            self.phase = 2
            self.enrage_announced = True
            self.wave_amp   = 110
            self.wave_speed = 0.038
            self.orb_interval = 55
            self.tint  = (255, 40, 80)
            self.eye_col = NEON_YELLOW

        # Movement
        if self.dashing:
            self.x += self.dash_vx
            self.y += self.dash_vy
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False
        else:
            target_x = SCREEN_W * 0.68
            self.x += (target_x - self.x) * 0.012
            self.y = self.base_y + math.sin(self.phase_angle) * self.wave_amp
            # Phase 2 dash
            if self.phase == 2 and self.tick % 120 == 0:
                dx = player_x - self.x
                dy = player_y - self.y
                dist = max(1, math.hypot(dx, dy))
                speed = 7.0
                self.dash_vx    = dx / dist * speed
                self.dash_vy    = dy / dist * speed
                self.dash_timer = 14
                self.dashing    = True

        # Clamp
        self.x = max(SCREEN_W * 0.35, min(SCREEN_W - BOSS_W // 2 - 10, self.x))
        self.y = max(PLAY_TOP + BOSS_H // 2 + 8, min(PLAY_BOT - BOSS_H // 2 - 8, self.y))

        # Shoot
        if self.orb_cooldown == 0:
            self._shoot(player_x, player_y)
            self.orb_cooldown = self.orb_interval

        self._update_orbs()

    def _shoot(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = max(1, math.hypot(dx, dy))
        speed = 3.5 if self.phase == 1 else 4.5

        if self.phase == 1:
            self.orbs.append({
                "x": self.x - BOSS_W // 2,
                "y": self.y,
                "vx": dx / dist * speed,
                "vy": dy / dist * speed,
                "life": 180,
                "r": 9,
                "col": NEON_PURPLE,
            })
        else:
            for spread in (-18, 0, 18):
                angle = math.atan2(dy, dx) + math.radians(spread)
                self.orbs.append({
                    "x": self.x - BOSS_W // 2,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 180,
                    "r": 7,
                    "col": NEON_PINK,
                })

    def _update_orbs(self):
        for orb in self.orbs:
            orb["x"] += orb["vx"]
            orb["y"] += orb["vy"]
            orb["life"] -= 1
        # FIX: remove orbs that go off the LEFT edge (x < 0) so they can't
        # hit the player invisibly after scrolling past them
        self.orbs = [o for o in self.orbs
                     if o["life"] > 0
                     and 0 < o["x"] < SCREEN_W + 30
                     and PLAY_TOP < o["y"] < PLAY_BOT]

    def hit(self):
        self.hp       -= 1
        self.hit_flash = 8
        if self.hp <= 0:
            self.alive       = False
            self.death_timer = 0
            return True
        return False

    def rect(self):
        hw = BOSS_W // 2 - 8
        hh = BOSS_H // 2 - 8
        return pygame.Rect(int(self.x) - hw, int(self.y) - hh, hw * 2, hh * 2)

    def orb_rects(self):
        # FIX: shrink hitbox by 3px per side — fairer collision detection
        return [pygame.Rect(int(o["x"]) - o["r"] + 3, int(o["y"]) - o["r"] + 3,
                            max(2, o["r"] * 2 - 6), max(2, o["r"] * 2 - 6))
                for o in self.orbs]

    def draw(self, surface, tick):
        cx, cy = int(self.x), int(self.y)
        t      = tick * 0.05
        pulse  = (math.sin(t) + 1) / 2

        # Draw orbs behind boss
        for orb in self.orbs:
            ox, oy = int(orb["x"]), int(orb["y"])
            r      = orb["r"]
            gs = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*orb["col"], 80), (r * 2, r * 2), r * 2)
            surface.blit(gs, (ox - r * 2, oy - r * 2))
            pygame.draw.circle(surface, orb["col"], (ox, oy), r)
            pygame.draw.circle(surface, WHITE,       (ox, oy), max(1, r - 3))

        if not self.alive:
            return

        body_col = WHITE if self.hit_flash > 0 else lerp_color(
            self.tint, (10, 0, 30), 0.3 - 0.15 * pulse
        )

        # Outer glow
        glow_r = int(60 + 14 * pulse)
        gs = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*self.tint, int(40 + 25 * pulse)), (glow_r, glow_r), glow_r)
        surface.blit(gs, (cx - glow_r, cy - glow_r))

        # Body
        dome = pygame.Rect(cx - 40, cy - 55, 80, 50)
        pygame.draw.ellipse(surface, lerp_color(body_col, WHITE, 0.3), dome)
        disc = pygame.Rect(cx - 60, cy - 22, 120, 44)
        pygame.draw.ellipse(surface, body_col, disc)
        under = pygame.Rect(cx - 48, cy + 14, 96, 26)
        pygame.draw.ellipse(surface, lerp_color(body_col, BLACK, 0.5), under)

        # Spinning ring lights
        for i in range(8):
            angle = math.radians(self.spin_angle + i * 45)
            lx = cx + int(math.cos(angle) * 42)
            ly = cy + int(math.sin(angle) * 14) + 2
            c  = self.tint if i % 2 == 0 else NEON_YELLOW
            pygame.draw.circle(surface, c, (lx, ly), 3)

        # Eye
        eye_r = int(10 + 3 * pulse)
        pygame.draw.circle(surface, self.eye_col, (cx, cy - 28), eye_r)
        pygame.draw.circle(surface, BLACK,         (cx, cy - 28), eye_r - 3)
        pygame.draw.circle(surface, self.eye_col,  (cx + 2, cy - 31), 3)

        # Phase 2 extra eyes
        if self.phase == 2:
            for ex, ey_off in [(-28, -10), (28, -10)]:
                pygame.draw.circle(surface, NEON_YELLOW, (cx + ex, cy + ey_off), 5)
                pygame.draw.circle(surface, BLACK,        (cx + ex, cy + ey_off), 3)

        # Tractor beam
        beam_alpha = int(70 + 50 * pulse)
        beam_surf  = pygame.Surface((50, 60), pygame.SRCALPHA)
        for row in range(60):
            fade = int(beam_alpha * (1 - row / 60))
            w    = int(50 * (1 - row / 60))
            if w > 0:
                beam_surf.fill((*self.tint, fade), (25 - w // 2, row, w, 1))
        surface.blit(beam_surf, (cx - 25, cy + 24))

        # Antenna
        pygame.draw.line(surface, self.tint, (cx, cy - 55), (cx + 10, cy - 70), 3)
        pygame.draw.circle(surface, NEON_YELLOW, (cx + 10, cy - 70), int(4 + 2 * pulse))
        if self.phase == 2:
            pygame.draw.line(surface, NEON_PINK, (cx, cy - 55), (cx - 10, cy - 68), 2)
            pygame.draw.circle(surface, NEON_PINK, (cx - 10, cy - 68), int(3 + pulse))

        # Outlines
        outline = lerp_color(self.tint, WHITE, 0.4 + 0.3 * pulse)
        pygame.draw.ellipse(surface, outline, disc, 2)
        pygame.draw.ellipse(surface, outline, dome, 2)

        # HP bar above boss
        bar_w = 110
        bar_x = cx - bar_w // 2
        bar_y = cy - 75
        pygame.draw.rect(surface, (50, 0, 0), (bar_x - 2, bar_y - 2, bar_w + 4, 14))
        hp_frac = max(0, self.hp / BOSS_MAX_HP)
        hp_col  = lerp_color(NEON_PINK, NEON_GREEN, hp_frac)
        pygame.draw.rect(surface, hp_col, (bar_x, bar_y, int(bar_w * hp_frac), 10))
        pygame.draw.rect(surface, WHITE,  (bar_x, bar_y, bar_w, 10), 1)
        boss_lbl = f_tiny.render("◆ BOSS", True, NEON_YELLOW)
        surface.blit(boss_lbl, (bar_x + bar_w + 6, bar_y))

        # FIX: draw countdown ring when spawn_delay is active
        if self.spawn_delay > 0:
            warn = f_small.render("BOSS CHARGING...", True, NEON_YELLOW)
            ws = pygame.Surface((warn.get_width() + 16, warn.get_height() + 8), pygame.SRCALPHA)
            ws.fill((0, 0, 0, 160))
            surface.blit(ws, (cx - ws.get_width() // 2, cy - 100))
            surface.blit(warn, (cx - warn.get_width() // 2, cy - 96))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SPACE CRYSTAL SPIKE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPIKE_W, SPIKE_H = 20, 24

_spike_pulse_tick = 0

def tick_spikes():
    global _spike_pulse_tick
    _spike_pulse_tick += 1

def draw_space_spike(surface, x, y, point_up=True, idx=0):
    t      = _spike_pulse_tick * 0.07 + idx * 0.9
    pulse  = (math.sin(t) + 1) / 2
    pulse2 = (math.sin(t * 1.7 + 1.1) + 1) / 2

    if idx % 3 == 0:
        core_col  = lerp_color((180,  0, 255), (255,  80, 255), pulse)
        glow_col  = (120,   0, 200)
        edge_col  = lerp_color(NEON_PINK, (255, 160, 255), pulse2)
    elif idx % 3 == 1:
        core_col  = lerp_color((  0, 180, 255), ( 80, 255, 255), pulse)
        glow_col  = (  0, 100, 180)
        edge_col  = lerp_color(NEON_CYAN, (160, 255, 255), pulse2)
    else:
        core_col  = lerp_color((200, 100, 255), (255, 200, 255), pulse)
        glow_col  = ( 80,   0, 160)
        edge_col  = lerp_color(NEON_PURPLE, (220, 180, 255), pulse2)

    half  = SPIKE_W // 2
    if point_up:
        base_y = y + SPIKE_H
        tip_y  = y
        pts_outer = [(x, base_y), (x + half, tip_y), (x + SPIKE_W, base_y)]
        facet_pts = [(x + half, tip_y), (x + half - 3, tip_y + SPIKE_H * 0.45),
                     (x + half + 3, tip_y + SPIKE_H * 0.45)]
        left_facet  = [(x + half, tip_y), (x + half - 4, base_y - 4)]
        right_facet = [(x + half, tip_y), (x + half + 4, base_y - 4)]
        orb_cx, orb_cy = x + half, base_y - 5
        beam_x, beam_y1, beam_y2 = x + half, tip_y - 2, tip_y - int(6 + 4 * pulse)
    else:
        base_y = y
        tip_y  = y + SPIKE_H
        pts_outer = [(x, base_y), (x + half, tip_y), (x + SPIKE_W, base_y)]
        facet_pts = [(x + half, tip_y), (x + half - 3, tip_y - SPIKE_H * 0.45),
                     (x + half + 3, tip_y - SPIKE_H * 0.45)]
        left_facet  = [(x + half, tip_y), (x + half - 4, base_y + 4)]
        right_facet = [(x + half, tip_y), (x + half + 4, base_y + 4)]
        orb_cx, orb_cy = x + half, base_y + 5
        beam_x, beam_y1, beam_y2 = x + half, tip_y + 2, tip_y + int(6 + 4 * pulse)

    glow_r = int(16 + 4 * pulse)
    glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
    glow_alpha = int(55 + 35 * pulse)
    pygame.draw.circle(glow_s, (*glow_col, glow_alpha), (glow_r, glow_r), glow_r)
    surface.blit(glow_s, (x + half - glow_r, (base_y if not point_up else tip_y) - glow_r // 2 * (1 if not point_up else -1)))

    shadow_col = lerp_color(glow_col, (5, 3, 15), 0.75)
    pygame.draw.polygon(surface, shadow_col, pts_outer)

    mid_x = x + half
    mid_y = (base_y + tip_y) // 2
    if point_up:
        lit_pts = [(x, base_y), (x + half, tip_y), (mid_x, mid_y)]
    else:
        lit_pts = [(x, base_y), (x + half, tip_y), (mid_x, mid_y)]
    lit_col = lerp_color(glow_col, (230, 220, 255), 0.5 + 0.3 * pulse)
    if len(lit_pts) >= 3:
        pygame.draw.polygon(surface, lit_col, lit_pts)

    inner_col = lerp_color(core_col, WHITE, 0.3 + 0.3 * pulse2)
    if len(facet_pts) >= 3:
        pygame.draw.polygon(surface, inner_col, facet_pts)
    pygame.draw.line(surface, inner_col, left_facet[0],  left_facet[1],  1)
    pygame.draw.line(surface, inner_col, right_facet[0], right_facet[1], 1)

    pygame.draw.polygon(surface, edge_col, pts_outer, 2)

    tip_glow = pygame.Surface((10, 10), pygame.SRCALPHA)
    tip_a = int(180 + 70 * pulse)
    pygame.draw.circle(tip_glow, (*core_col, tip_a), (5, 5), 5)
    surface.blit(tip_glow, (x + half - 5, tip_y - 5))
    pygame.draw.circle(surface, WHITE, (x + half, tip_y), int(2 + pulse))

    beam_s = pygame.Surface((3, abs(beam_y2 - beam_y1) + 1), pygame.SRCALPHA)
    beam_s.fill((*core_col, int(120 * pulse)))
    if beam_y2 < beam_y1:
        surface.blit(beam_s, (beam_x - 1, beam_y2))
    else:
        surface.blit(beam_s, (beam_x - 1, beam_y1))

    spark_angle = _spike_pulse_tick * 0.12 + idx * 1.3
    sr = int(5 + 2 * pulse)
    spark_x = int(x + half + math.cos(spark_angle) * sr)
    spark_y = int(tip_y   + math.sin(spark_angle) * sr * 0.4)
    pygame.draw.circle(surface, WHITE, (spark_x, spark_y), 1)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SCANLINE OVERLAY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
scanline_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
for _sy in range(0, SCREEN_H, 3):
    scanline_surf.fill((0, 0, 0, 38), (0, _sy, SCREEN_W, 1))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ROCK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROCK_SPEED   = 1.1
ROCK_MIN_GAP = 320

_ROCK_SHAPES = [
    [(-18,-8),(-10,-18),(4,-20),(16,-10),(20,2),(14,14),(0,18),(-14,12),(-20,2)],
    [(-14,-18),(0,-22),(18,-10),(22,4),(10,20),(-4,16),(-20,8),(-22,-6)],
    [(-12,-20),(4,-22),(18,-12),(22,2),(16,16),(2,22),(-14,16),(-22,4),(-20,-10)],
]
_ROCK_SIZES = [22, 28, 34, 20, 26]


class Rock:
    def __init__(self, x):
        self.x         = float(x)
        self.y         = float(random.randint(PLAY_TOP + 44, PLAY_BOT - 44))
        self.rot       = random.uniform(0, 360)
        self.rot_spd   = random.uniform(-0.55, 0.55)
        self.shape     = random.choice(_ROCK_SHAPES)
        self.size      = random.choice(_ROCK_SIZES)
        self.wobble_ph = random.uniform(0, math.pi * 2)
        self.base_col  = random.choice([
            (110, 90, 160), (90, 110, 140), (130, 100, 170), (80, 80, 120)
        ])
        self.edge_col   = lerp_color(self.base_col, (210, 195, 255), 0.55)
        self.shadow_col = lerp_color(self.base_col, (8, 6, 20), 0.55)

    def update(self):
        self.x   -= ROCK_SPEED
        self.rot  = (self.rot + self.rot_spd) % 360
        self.y   += math.sin(pygame.time.get_ticks() * 0.0009 + self.wobble_ph) * 0.22

    def rect(self):
        r = self.size - 6
        return pygame.Rect(int(self.x) - r, int(self.y) - r, r * 2, r * 2)

    def _rotated_pts(self):
        rad = math.radians(self.rot)
        cos_r, sin_r = math.cos(rad), math.sin(rad)
        pts = []
        for (ox, oy) in self.shape:
            sx = ox * self.size / 22
            sy = oy * self.size / 22
            pts.append((int(self.x + sx * cos_r - sy * sin_r),
                        int(self.y + sx * sin_r + sy * cos_r)))
        return pts

    def draw(self, surface):
        pts = self._rotated_pts()
        gs = self.size + 10
        glow = pygame.Surface((gs * 2, gs * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.base_col, 28), (gs, gs), gs)
        surface.blit(glow, (int(self.x) - gs, int(self.y) - gs))
        pygame.draw.polygon(surface, self.base_col, pts)
        mid = len(pts) // 2
        hi_col = lerp_color(self.base_col, (230, 220, 255), 0.50)
        if len(pts[:mid]) >= 3:
            pygame.draw.polygon(surface, hi_col, pts[:mid])
        if len(pts[mid:]) >= 3:
            pygame.draw.polygon(surface, self.shadow_col, pts[mid:])
        pygame.draw.polygon(surface, self.edge_col, pts, 2)
        for i in range(0, len(pts), 2):
            cx = (pts[i][0] + int(self.x)) // 2
            cy = (pts[i][1] + int(self.y)) // 2
            pygame.draw.circle(surface, lerp_color(self.base_col, (0, 0, 0), 0.45), (cx, cy), 2)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BULLET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BULLET_SPEED = 14
BULLET_W     = 16
BULLET_H     = 5

class Bullet:
    def __init__(self, x, y):
        self.x    = float(x)
        self.y    = float(y)
        self.life = 90
        self.trail = []

    def update(self):
        self.trail.insert(0, (int(self.x), int(self.y)))
        if len(self.trail) > 6:
            self.trail.pop()
        self.x   += BULLET_SPEED
        self.life -= 1

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y) - BULLET_H // 2, BULLET_W, BULLET_H)

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            alpha  = max(0, 120 - i * 22)
            length = max(2, BULLET_W - i * 2)
            s = pygame.Surface((length, BULLET_H), pygame.SRCALPHA)
            s.fill((*NEON_ORANGE, alpha))
            surface.blit(s, (tx - length, ty - BULLET_H // 2))
        bx, by = int(self.x), int(self.y) - BULLET_H // 2
        gs = pygame.Surface((BULLET_W + 10, BULLET_H + 10), pygame.SRCALPHA)
        gs.fill((*NEON_YELLOW, 60))
        surface.blit(gs, (bx - 5, by - 5))
        pygame.draw.rect(surface, NEON_YELLOW, (bx, by, BULLET_W, BULLET_H), border_radius=2)
        pygame.draw.rect(surface, WHITE, (bx + 2, by + 1, BULLET_W - 4, BULLET_H - 2), border_radius=1)
        pygame.draw.circle(surface, WHITE, (bx + BULLET_W, by + BULLET_H // 2), 3)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  START SCREEN ASSETS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class ScrollLayer:
    def __init__(self, count, speed, color, size_range):
        self.speed = speed
        self.items = [{"x": random.randint(0, SCREEN_W),
                       "y": random.randint(80, SCREEN_H-80),
                       "s": random.randint(*size_range),
                       "a": random.randint(60, 180),
                       "c": color} for _ in range(count)]
    def update(self):
        for item in self.items:
            item["x"] -= self.speed
            if item["x"] < -10:
                item["x"] = SCREEN_W + 10
                item["y"] = random.randint(80, SCREEN_H-80)
    def draw(self, surface):
        for item in self.items:
            s = pygame.Surface((item["s"], item["s"]), pygame.SRCALPHA)
            s.fill((*item["c"], item["a"]))
            surface.blit(s, (item["x"], item["y"]))

menu_layers = [ScrollLayer(40, 0.4, NEON_CYAN,   (1,2)),
               ScrollLayer(25, 0.8, NEON_PINK,   (2,3)),
               ScrollLayer(15, 1.5, NEON_YELLOW, (1,2))]

class MenuOrb:
    def __init__(self):
        self.x     = random.randint(60, SCREEN_W-60)
        self.y     = random.randint(110, SCREEN_H-110)
        self.r     = random.randint(3,7)
        self.color = random.choice([NEON_PINK, NEON_CYAN, NEON_YELLOW, NEON_PURPLE])
        self.phase = random.uniform(0, math.pi*2)
        self.speed = random.uniform(0.02, 0.05)
    def draw(self, surface, tick):
        dy = int(math.sin(tick*self.speed+self.phase)*12)
        draw_glow_circle(surface, self.x, self.y+dy, self.r, self.color, 140)

menu_orbs = [MenuOrb() for _ in range(18)]

MENU_PLATFORM_H = 22
MENU_GROUND_Y   = SCREEN_H - 80
MENU_CEILING_Y  = 75

def draw_menu_platform(surface, y, color, tick):
    is_ceil = (y == MENU_CEILING_Y)
    if is_ceil:
        draw_formal_platform(surface, 0, y, SCREEN_W, MENU_PLATFORM_H,
                             CEIL_DARK, CEIL_MID, CEIL_LIGHT, CEIL_MORTAR,
                             NEON_PURPLE, scroll_offset=tick*0.8, flip=True)
    else:
        draw_formal_platform(surface, 0, y, SCREEN_W, MENU_PLATFORM_H,
                             BRICK_DARK, BRICK_MID, BRICK_LIGHT, BRICK_MORTAR,
                             NEON_CYAN, scroll_offset=tick*0.8, flip=False)

def draw_spike_row_menu(surface, y, point_up, tick):
    offset = int(tick * 0.8) % SPIKE_W
    x, i = -offset, 0
    while x < SCREEN_W + SPIKE_W:
        draw_space_spike(surface, x, y, point_up=point_up, idx=i)
        x += SPIKE_W; i += 1

def draw_corner_deco(surface, tick):
    pulse = int(180+75*math.sin(tick*0.06))
    size  = 30
    for cx, cy in [(5,5),(SCREEN_W-35,5),(5,SCREEN_H-35),(SCREEN_W-35,SCREEN_H-35)]:
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        col = (*NEON_PINK, pulse)
        pygame.draw.rect(s, col, (0, 0, size, 3))
        pygame.draw.rect(s, col, (0, 0, 3, size))
        pygame.draw.rect(s, col, (0, size-3, size, 3))
        pygame.draw.rect(s, col, (size-3, 0, 3, size))
        surface.blit(s, (cx, cy))

def draw_menu_title(surface, tick):
    t  = (math.sin(tick*0.04)+1)/2
    c1 = lerp_color(NEON_PINK,  (255,100,255), t)
    c2 = lerp_color(NEON_CYAN,  (100,255,255), t)
    for r, a in [(14,15),(9,35),(5,60)]:
        gi = f_title.render("G  FLIP", True, c1)
        for dx in [-r,0,r]:
            for dy in [-r,0,r]:
                gs = pygame.Surface(gi.get_size(), pygame.SRCALPHA)
                gs.blit(gi,(0,0)); gs.set_alpha(a)
                surface.blit(gs, (SCREEN_W//2-gs.get_width()//2+dx, 145+dy))
    sh = f_title.render("G  FLIP", True, BLACK)
    sh.set_alpha(80)
    surface.blit(sh, (SCREEN_W//2-sh.get_width()//2+5, 150))
    letters = "G  FLIP"
    total   = f_title.size(letters)[0]
    cx      = SCREEN_W//2 - total//2
    for idx, ch in enumerate(letters):
        lw, _ = f_title.size(ch)
        col   = c1 if idx%2==0 else c2
        img   = f_title.render(ch, True, col)
        bob   = int(math.sin(tick*0.05+idx*0.6)*4) if ch!=" " else 0
        surface.blit(img, (cx, 145+bob)); cx += lw
    sub_c = lerp_color(NEON_CYAN, NEON_YELLOW, (math.sin(tick*0.03+1)+1)/2)
    draw_text_cx(surface, "─── A GRAVITY FLIP ADVENTURE ───", f_sub, sub_c, 258)

class MenuChar:
    def __init__(self, x, y, flipped=False):
        self.x, self.y, self.flipped = x, y, flipped
        self.dir = -1 if flipped else 1
    def update(self):
        self.x += 1.2*self.dir
        if self.x > SCREEN_W-100: self.dir = -1
        if self.x < 60:           self.dir =  1
    def draw(self, surface, tick):
        bob = int(math.sin(tick*0.15)*4)*(-1 if self.flipped else 1)
        bx  = int(self.x)
        if HAS_SPRITES:
            anim = "run_ceiling" if self.flipped else "run_ground"
            frame_idx = (tick // 6) % ANIM_COUNT[anim]
            sprite = get_sprite_frame(anim, frame_idx)
            if sprite:
                surface.blit(sprite, (bx, int(self.y)+bob))
        else:
            draw_pixel_char(surface, bx, int(self.y)+bob, scale=3, flipped=self.flipped)

menu_char_ground  = MenuChar(200, MENU_GROUND_Y-60)
menu_char_ceiling = MenuChar(550, MENU_CEILING_Y+MENU_PLATFORM_H, flipped=True)

def draw_neon_lines(surface, tick):
    for i in range(3):
        y = (tick*(1+i*0.4)*2+i*200) % SCREEN_H
        ls = pygame.Surface((SCREEN_W,2), pygame.SRCALPHA)
        ls.fill((*NEON_CYAN, 55))
        surface.blit(ls, (0,int(y)))

def draw_lightning(surface, tick):
    if (tick//8)%3!=0: return
    seg_y=[160,170,180,165,175]; seg_xl=[90,95,88,92,85]; seg_xr=[710,705,712,708,715]
    for i in range(len(seg_y)-1):
        s = pygame.Surface((SCREEN_W,SCREEN_H), pygame.SRCALPHA)
        a = random.randint(80,180)
        pygame.draw.line(s,(*NEON_YELLOW,a),(seg_xl[i],seg_y[i]),(seg_xl[i+1],seg_y[i+1]),2)
        pygame.draw.line(s,(*NEON_YELLOW,a),(seg_xr[i],seg_y[i]),(seg_xr[i+1],seg_y[i+1]),2)
        surface.blit(s,(0,0))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GUIDE SCREEN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GUIDE_SECTIONS = [
    {"title":"  GRAVITY FLIP","icon":"↕","color":NEON_CYAN,
     "lines":["Hold or tap SPACE to switch","between ground and ceiling."]},
    {"title":"  OBSTACLES",   "icon":"▲","color":NEON_PINK,
     "lines":["Dodge plasma crystals, rocks,","and deadly aliens!"]},
    {"title":"  SHOOT",       "icon":"▶","color":NEON_ORANGE,
     "lines":["Press E to fire bullets.","Hit aliens 3x to destroy them!"]},
    {"title":"  DIFFICULTY",  "icon":"▶▶","color":NEON_GREEN,
     "lines":["Speed increases every 300pts.","How far can you survive?"]},
]
CONTROLS = [("SPACE","Hold or tap to Flip",NEON_CYAN),
            ("E","Shoot bullet",NEON_ORANGE),
            ("ENTER","Start / Confirm",NEON_YELLOW),
            ("ESC","Pause / Back",NEON_PINK)]

def draw_guide(surface, tick):
    if HAS_BG:
        d = pygame.Surface((SCREEN_W,SCREEN_H), pygame.SRCALPHA)
        d.fill((0,0,0,165)); surface.blit(d,(0,0))
    draw_panel(surface,30,20,SCREEN_W-60,SCREEN_H-40,alpha=210)
    bar = pygame.Surface((SCREEN_W-66,44), pygame.SRCALPHA)
    bar.fill((*NEON_PINK,80)); surface.blit(bar,(33,22))
    hc = lerp_color(NEON_PINK, NEON_CYAN, (math.sin(tick*0.05)+1)/2)
    draw_text_cx(surface,"◈  HOW  TO  PLAY  ◈",f_body,hc,30)
    cell_w, cell_h = (SCREEN_W-80)//2, 128
    for i, sec in enumerate(GUIDE_SECTIONS):
        cx = 40+(i%2)*(cell_w+8); cy = 78+(i//2)*(cell_h+8)
        cs = pygame.Surface((cell_w,cell_h), pygame.SRCALPHA)
        cs.fill((0,0,0,140)); surface.blit(cs,(cx,cy))
        pygame.draw.rect(surface, sec["color"], (cx,cy,cell_w,cell_h), 2)
        ib = pygame.Surface((34,34), pygame.SRCALPHA)
        ib.fill((*sec["color"],80)); surface.blit(ib,(cx+6,cy+6))
        surface.blit(f_body.render(sec["icon"],True,sec["color"]), (cx+8,cy+8))
        surface.blit(f_small.render(sec["title"],True,sec["color"]), (cx+46,cy+10))
        for li, line in enumerate(sec["lines"]):
            surface.blit(f_tiny.render(line,True,DIM_WHITE), (cx+8,cy+50+li*22))
    ctrl_y = 78+2*(cell_h+8)+4
    draw_panel(surface,40,ctrl_y,SCREEN_W-80,66,alpha=150,border1=NEON_YELLOW,border2=NEON_CYAN)
    kx = 40
    for key,action,color in CONTROLS:
        kb = pygame.Surface((80,26), pygame.SRCALPHA)
        kb.fill((*color,90)); surface.blit(kb,(kx,ctrl_y+8))
        pygame.draw.rect(surface,color,(kx,ctrl_y+8,80,26),2)
        surface.blit(f_small.render(key,True,WHITE),(kx+4,ctrl_y+13))
        surface.blit(f_tiny.render(action,True,DIM_WHITE),(kx+86,ctrl_y+15))
        kx += 175
    if (tick//30)%2==0:
        fp = f_small.render("ENTER  →  Start Game      ESC  →  Back",True,NEON_YELLOW)
        surface.blit(fp,(SCREEN_W//2-fp.get_width()//2,SCREEN_H-42))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SHARED LEVEL BASE CONSTANTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GRAVITY     = 0.55
FLIP_VEL    = -10.0
PLAYER_W    = CHAR_RENDER_W
PLAYER_H    = CHAR_RENDER_H
FLIP_HOLD_INTERVAL = 14
BASE_WORLD_SPEED   = 3.4

def get_world_speed(score):
    return BASE_WORLD_SPEED

GEM_FIRST_WORLD_X = 4500
GEM_RESPAWN_AHEAD = 1200
LEVEL1_LENGTH     = 6000

ROCK_SPAWN_WORLD_XS = [
    700, 1050, 1400, 1750, 2100,
    2500, 2850, 3200, 3600, 3950,
    4300, 4700, 5100, 5500,
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PLAYER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x               = 120
        self.y               = float(PLAY_BOT - PLAYER_H)
        self.vy              = 0.0
        self.on_ground       = True
        self.flipped         = False
        self.alive           = True
        self.flip_cooldown   = 0
        self.hold_flip_timer = 0
        self.trail           = []
        self.anim_tick       = 0
        self.is_flipping     = False
        self.flip_anim_timer = 0

    def flip(self):
        if self.flip_cooldown > 0:
            return
        self.flipped         = not self.flipped
        self.vy              = FLIP_VEL if self.flipped else -FLIP_VEL
        self.flip_cooldown   = 12
        self.hold_flip_timer = 0
        self.is_flipping     = True
        self.flip_anim_timer = 20

    def update(self, space_held=False):
        if not self.alive:
            return
        if self.flip_cooldown > 0:
            self.flip_cooldown -= 1
        if space_held:
            self.hold_flip_timer += 1
            if self.hold_flip_timer >= FLIP_HOLD_INTERVAL:
                self.flip()
        else:
            self.hold_flip_timer = 0
        grav_dir = -1 if self.flipped else 1
        self.vy += GRAVITY * grav_dir
        self.vy  = max(-14, min(14, self.vy))
        self.y  += self.vy
        if not self.flipped and self.y + PLAYER_H >= PLAY_BOT:
            self.y  = float(PLAY_BOT - PLAYER_H)
            self.vy = 0
        if self.flipped and self.y <= PLAY_TOP:
            self.y  = float(PLAY_TOP)
            self.vy = 0
        self.trail.insert(0, (int(self.x), int(self.y)))
        if len(self.trail) > 6:
            self.trail.pop()
        self.anim_tick += 1
        if self.flip_anim_timer > 0:
            self.flip_anim_timer -= 1
            self.is_flipping = self.flip_anim_timer > 0

    def rect(self):
        return pygame.Rect(int(self.x)+4, int(self.y)+4, PLAYER_W-8, PLAYER_H-8)

    def _get_anim(self):
        if self.is_flipping:   return "jump_flip"
        if self.flipped:       return "run_ceiling"
        return "run_ground"

    def draw(self, surface):
        col = NEON_PINK if self.flipped else NEON_CYAN
        cx_off = PLAYER_W // 2
        cy_off = PLAYER_H // 2
        for i, (tx, ty) in enumerate(self.trail[1:]):
            alpha  = max(0, 60 - i * 18)
            radius = max(2, 8 - i * 2)
            gs = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*col, alpha), (radius, radius), radius)
            surface.blit(gs, (tx + cx_off - radius, ty + cy_off - radius))
        ox, oy = int(self.x), int(self.y)
        if HAS_SPRITES:
            anim      = self._get_anim()
            fps       = ANIM_FPS[anim]
            frame_idx = (self.anim_tick // max(1, 60 // fps)) % ANIM_COUNT[anim]
            sprite    = get_sprite_frame(anim, frame_idx)
            if sprite:
                surface.blit(sprite, (ox, oy))
        else:
            draw_pixel_char(surface, ox, oy, scale=3, flipped=self.flipped)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GEM / PORTAL / SPIKE / PARTICLE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class Gem:
    def __init__(self, world_x, y):
        self.world_x   = world_x
        self.x         = 0
        self.y         = y
        self.collected = False
        self.anim      = 0

    def update(self):
        self.anim += 1

    def rect(self):
        return pygame.Rect(self.x - 14, self.y - 14, 28, 28)

class Portal:
    def __init__(self, world_x):
        self.world_x    = world_x
        self.x          = 0
        self.y          = PLAY_MID
        self.active     = False
        self.suck_timer = 0
        self.spin       = 0

    def update(self, tick):
        self.spin = tick * 3

    def rect(self):
        return pygame.Rect(self.x - 30, self.y - 60, 60, 120)

    def draw(self, surface, tick):
        if not self.active:
            s = pygame.Surface((60, 120), pygame.SRCALPHA)
            s.fill((30, 0, 60, 80))
            surface.blit(s, (self.x - 30, self.y - 60))
            lt = f_tiny.render("?", True, (80, 60, 100))
            surface.blit(lt, (self.x - lt.get_width()//2, self.y - lt.get_height()//2))
            return
        for i in range(6, 0, -1):
            r_outer = int(30 * i / 6)
            r_inner = max(4, r_outer - 4)
            alpha   = int(200 * (1 - i / 6)) + 40
            angle   = math.radians(self.spin + i * 30)
            cx = self.x + int(math.cos(angle) * 4)
            cy = self.y + int(math.sin(angle) * 4)
            col = lerp_color(NEON_PURPLE, BLACK, i / 6)
            s = pygame.Surface((r_outer*2, r_outer*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*col, alpha), (r_outer, r_outer), r_outer)
            pygame.draw.circle(s, (0, 0, 0, 255), (r_outer, r_outer), r_inner)
            surface.blit(s, (cx - r_outer, cy - r_outer))
        pygame.draw.circle(surface, BLACK, (self.x, self.y), 10)
        for i in range(8):
            sx = self.x + random.randint(-28, 28)
            sy = self.y + random.randint(-55, 55)
            streak_s = pygame.Surface((2, 6), pygame.SRCALPHA)
            streak_s.fill((*NEON_PURPLE, random.randint(60, 160)))
            surface.blit(streak_s, (sx, sy))
        lbl = f_tiny.render("NEXT LEVEL ▶", True, NEON_YELLOW)
        surface.blit(lbl, (self.x - lbl.get_width()//2, self.y - 80))

class Spike:
    def __init__(self, x, on_ground=True, idx=0):
        self.x         = x
        self.on_ground = on_ground
        self.idx       = idx

    def update(self, world_speed):
        self.x -= world_speed

    def rect(self):
        if self.on_ground:
            return pygame.Rect(int(self.x) + 4, PLAY_BOT - SPIKE_H + 4, SPIKE_W - 8, SPIKE_H - 8)
        else:
            return pygame.Rect(int(self.x) + 4, PLAY_TOP + 4, SPIKE_W - 8, SPIKE_H - 8)

    def draw(self, surface):
        if self.on_ground:
            draw_space_spike(surface, int(self.x), PLAY_BOT - SPIKE_H, point_up=True, idx=self.idx)
        else:
            draw_space_spike(surface, int(self.x), PLAY_TOP, point_up=False, idx=self.idx)

class Particle:
    def __init__(self, x, y, color):
        self.x        = float(x)
        self.y        = float(y)
        self.vx       = random.uniform(-3, 3)
        self.vy       = random.uniform(-5, 1)
        self.life     = random.randint(20, 45)
        self.max_life = self.life
        self.color    = color
        self.size     = random.randint(2, 5)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.2
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        a = int(255 * self.life / self.max_life)
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((*self.color, a))
        surface.blit(s, (int(self.x), int(self.y)))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LEVEL 1
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def make_level1():
    spike_defs = [
        (500,  True),  (800,  False), (1100, True),  (1400, False),
        (1700, True),  (1900, False), (2150, True),  (2350, False),
        (2600, True),  (2800, False), (2950, True),  (3100, False),
        (3250, True),  (3400, False),
    ]
    gem    = Gem(GEM_FIRST_WORLD_X, PLAY_MID)
    portal = Portal(LEVEL1_LENGTH - 200)
    return spike_defs, gem, portal

class Level1:
    def __init__(self):
        self.reset()

    def reset(self):
        self.scroll        = 0.0
        self.player        = Player()
        self.spike_defs, self.gem, self.portal = make_level1()
        self.spawned       = set()
        self.spikes        = []
        self.particles     = []
        self.score         = 0
        self.gem_collected = False
        self.suck_timer    = 0
        self.transition    = False
        self.trans_timer   = 0
        self.dead          = False
        self.dead_timer    = 0
        self.paused        = False
        self.bg_scroll     = 0.0
        self.rocks              = []
        self.rock_spawn_index   = 0
        self._last_rock_sx      = -9999
        self.bullets            = []
        self.rocks_destroyed    = 0
        self._spike_idx_counter = 0

    def spawn_spikes(self):
        screen_right_world = self.scroll + SCREEN_W + 100
        for i, (wx, on_g) in enumerate(self.spike_defs):
            if i not in self.spawned and wx < screen_right_world:
                self.spikes.append(Spike(wx - self.scroll + SCREEN_W, on_g,
                                         idx=self._spike_idx_counter))
                self._spike_idx_counter += 1
                self.spawned.add(i)

    def spawn_rocks(self):
        while self.rock_spawn_index < len(ROCK_SPAWN_WORLD_XS):
            wx = ROCK_SPAWN_WORLD_XS[self.rock_spawn_index]
            screen_wx = wx - self.scroll
            if screen_wx > SCREEN_W + 40:
                break
            if screen_wx > -40:
                self.rocks.append(Rock(SCREEN_W + 40))
            self.rock_spawn_index += 1

    def world_to_screen(self, wx):
        return wx - self.scroll

    def shoot(self):
        bx = int(self.player.x) + PLAYER_W
        by = int(self.player.y) + PLAYER_H // 2
        self.bullets.append(Bullet(bx, by))

    def update(self, keys):
        if self.paused or self.transition or self.dead:
            if self.transition: self.trans_timer += 1
            if self.dead:       self.dead_timer  += 1
            return

        tick_spikes()
        world_speed = get_world_speed(self.score)
        self.scroll    += world_speed
        self.bg_scroll += world_speed * 0.3

        self.spawn_spikes()
        self.spawn_rocks()

        space_held = keys[pygame.K_SPACE]
        self.player.update(space_held=space_held)

        for sp in self.spikes:
            sp.update(world_speed)
        self.spikes = [sp for sp in self.spikes if sp.x > -60]

        for rock in self.rocks:
            rock.update()

        for bullet in self.bullets:
            bullet.update()

        rocks_to_remove   = set()
        bullets_to_remove = set()
        for bi, bullet in enumerate(self.bullets):
            if bullet.life <= 0 or bullet.x > SCREEN_W + 50:
                bullets_to_remove.add(bi)
                continue
            br = bullet.rect()
            for ri, rock in enumerate(self.rocks):
                if ri in rocks_to_remove:
                    continue
                if br.colliderect(rock.rect()):
                    for _ in range(22):
                        self.particles.append(
                            Particle(rock.x, rock.y,
                                     random.choice([rock.base_col, NEON_ORANGE, NEON_YELLOW, WHITE]))
                        )
                    rocks_to_remove.add(ri)
                    bullets_to_remove.add(bi)
                    self.score += 50
                    self.rocks_destroyed += 1
                    break

        self.rocks   = [r for i, r in enumerate(self.rocks)   if i not in rocks_to_remove]
        self.bullets = [b for i, b in enumerate(self.bullets) if i not in bullets_to_remove]
        self.rocks   = [r for r in self.rocks if r.x > -80]

        self.gem.update()
        self.portal.update(int(self.scroll))

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        pr = self.player.rect()

        for sp in self.spikes:
            if pr.colliderect(sp.rect()):
                self.kill_player(); return

        for rock in self.rocks:
            if pr.colliderect(rock.rect()):
                for _ in range(18):
                    self.particles.append(
                        Particle(rock.x, rock.y,
                                 random.choice([rock.base_col, NEON_ORANGE, WHITE]))
                    )
                self.kill_player(); return

        gem_sx = self.world_to_screen(self.gem.world_x)
        self.gem.x = gem_sx

        if not self.gem_collected:
            gem_rect = pygame.Rect(gem_sx - 14, self.gem.y - 14, 28, 28)
            if pr.colliderect(gem_rect):
                self.gem_collected  = True
                self.portal.active  = True
                self.portal.world_x = self.scroll + 900
                self.score         += 500
                for _ in range(30):
                    self.particles.append(Particle(gem_sx, self.gem.y, NEON_YELLOW))
            elif gem_sx < -60:
                self.gem.world_x = self.scroll + GEM_RESPAWN_AHEAD
                self.gem.x       = self.world_to_screen(self.gem.world_x)

        self.portal.x = self.world_to_screen(self.portal.world_x)
        portal_sx     = self.portal.x

        if self.portal.active and self.scroll > 0:
            portal_rect = pygame.Rect(portal_sx - 55, PLAY_TOP, 110, PLAY_BOT - PLAY_TOP)
            if pr.colliderect(portal_rect):
                self.suck_timer += 1
                if self.suck_timer > 10:
                    self.transition  = True
                    self.trans_timer = 0
                    for _ in range(50):
                        self.particles.append(Particle(portal_sx, self.portal.y, NEON_PURPLE))
            else:
                self.suck_timer = 0
                if portal_sx < -60:
                    self.portal.world_x = self.scroll + 600

        if self.player.y > SCREEN_H + 20 or self.player.y < -SCREEN_H:
            self.kill_player()

        self.score += 1

    def kill_player(self):
        self.dead       = True
        self.dead_timer = 0
        self.player.alive = False
        pygame.mixer.music.stop()
        for _ in range(40):
            self.particles.append(Particle(int(self.player.x)+24,
                                           int(self.player.y)+30, NEON_PINK))

    def draw(self, surface, tick):
        if HAS_BG:
            surface.blit(bg_dark, (0, 0))
        else:
            surface.fill(DARK_BG)

        offset = int(self.bg_scroll) % 60
        for gx in range(-offset, SCREEN_W, 60):
            pygame.draw.line(surface, (20, 16, 50), (gx, 0), (gx, SCREEN_H))
        for gy in range(0, SCREEN_H, 60):
            pygame.draw.line(surface, (20, 16, 50), (0, gy), (SCREEN_W, gy))

        portal_sx = self.portal.x

        draw_formal_platform(surface, 0, 0, SCREEN_W, CEILING_Y + PLATFORM_H,
                             CEIL_DARK, CEIL_MID, CEIL_LIGHT, CEIL_MORTAR,
                             NEON_PURPLE, scroll_offset=self.bg_scroll, flip=True)
        draw_formal_platform(surface, 0, GROUND_Y, SCREEN_W, SCREEN_H - GROUND_Y,
                             BRICK_DARK, BRICK_MID, BRICK_LIGHT, BRICK_MORTAR,
                             NEON_CYAN, scroll_offset=self.bg_scroll, flip=False)

        if self.portal.active:
            hole_w = 70
            pygame.draw.rect(surface, DARK_BG,
                             (portal_sx - hole_w//2, 0, hole_w, CEILING_Y + PLATFORM_H + 2))
            pygame.draw.rect(surface, DARK_BG,
                             (portal_sx - hole_w//2, GROUND_Y - 2, hole_w, SCREEN_H - GROUND_Y + 2))

        for sp in self.spikes:
            sp.draw(surface)
        for rock in self.rocks:
            rock.draw(surface)
        for bullet in self.bullets:
            bullet.draw(surface)

        if not self.gem_collected:
            gem_sx = self.gem.x
            spin   = math.sin(tick * 0.08)
            w      = max(4, int(28 * abs(spin)))
            pulse  = (math.sin(tick * 0.1) + 1) / 2
            color  = lerp_color(NEON_YELLOW, NEON_CYAN, pulse)
            draw_glow_circle(surface, gem_sx, self.gem.y, 16, color, 100)
            pygame.draw.polygon(surface, color, [
                (gem_sx,        self.gem.y - 14),
                (gem_sx + w//2, self.gem.y),
                (gem_sx,        self.gem.y + 14),
                (gem_sx - w//2, self.gem.y),
            ])
            pygame.draw.polygon(surface, WHITE, [
                (gem_sx,        self.gem.y - 7),
                (gem_sx + w//4, self.gem.y),
                (gem_sx,        self.gem.y + 7),
                (gem_sx - w//4, self.gem.y),
            ])
            lbl = f_tiny.render("◆ COLLECT", True, NEON_YELLOW)
            surface.blit(lbl, (gem_sx - lbl.get_width()//2, self.gem.y - 28))

        self.portal.draw(surface, tick)

        for p in self.particles:
            p.draw(surface)

        self.player.draw(surface)
        self.draw_hud(surface, tick)
        surface.blit(scanline_surf, (0, 0))

        if self.dead:
            alpha = min(200, self.dead_timer * 5)
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, alpha))
            surface.blit(ov, (0, 0))
            if self.dead_timer > 20:
                draw_text_cx(surface, "GAME OVER", f_title, NEON_PINK, 220)
                draw_text_cx(surface, f"SCORE:  {self.score}", f_body, NEON_YELLOW, 330)
                draw_text_cx(surface, f"ROCKS DESTROYED: {self.rocks_destroyed}", f_small, NEON_ORANGE, 365)
                draw_text_cx(surface, "ENTER → Retry     ESC → Menu", f_small, DIM_WHITE, 400)

        if self.transition:
            alpha = min(255, self.trans_timer * 6)
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((60, 0, 120, alpha))
            surface.blit(ov, (0, 0))
            if self.trans_timer > 30:
                draw_text_cx(surface, "LEVEL  COMPLETE!", f_body, NEON_YELLOW, 220)
                draw_text_cx(surface, f"SCORE:  {self.score}", f_sub, NEON_CYAN, 260)
                draw_text_cx(surface, f"ROCKS DESTROYED: {self.rocks_destroyed}", f_small, NEON_ORANGE, 295)
                draw_text_cx(surface, "ENTERING LEVEL 2...", f_small, NEON_GREEN, 335)
                draw_text_cx(surface, "ENTER → Continue     ESC → Menu", f_small, DIM_WHITE, 375)

    def draw_hud(self, surface, tick):
        bar = pygame.Surface((SCREEN_W, 40), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 140))
        surface.blit(bar, (0, 0))
        lvl_t = f_hud.render("LEVEL  01", True, NEON_CYAN)
        surface.blit(lvl_t, (10, 8))
        sc_t = f_hud.render(f"SCORE  {self.score:06d}", True, NEON_YELLOW)
        surface.blit(sc_t, (SCREEN_W - sc_t.get_width() - 10, 8))
        gem_x = SCREEN_W // 2 - 60
        if self.gem_collected:
            pygame.draw.polygon(surface, NEON_YELLOW,
                                [(gem_x+10,2),(gem_x+18,10),(gem_x+10,18),(gem_x+2,10)])
            gt = f_tiny.render("GEM ✓", True, NEON_YELLOW)
        else:
            gt = f_tiny.render("GEM: collect ◆", True, DIM_WHITE)
        surface.blit(gt, (gem_x + 22, 10))
        if self.gem_collected:
            pt = f_tiny.render("◈ PORTAL OPEN", True, NEON_PURPLE)
        else:
            pt = f_tiny.render("◈ PORTAL LOCKED", True, (60, 50, 80))
        surface.blit(pt, (gem_x + 22, 24))
        prog  = min(1.0, self.scroll / LEVEL1_LENGTH)
        bar_w = 200
        bar_x = SCREEN_W // 2 - bar_w // 2
        bar_y = SCREEN_H - 18
        pygame.draw.rect(surface, (30, 30, 60), (bar_x, bar_y, bar_w, 8))
        fill_c = lerp_color(NEON_CYAN, NEON_PINK, prog)
        pygame.draw.rect(surface, fill_c, (bar_x, bar_y, int(bar_w * prog), 8))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, 8), 1)
        prog_t = f_tiny.render(f"{int(prog*100)}%", True, WHITE)
        surface.blit(prog_t, (bar_x + bar_w + 4, bar_y - 1))
        hint = f_tiny.render("SPACE=Flip  E=Shoot", True, (80, 80, 100))
        surface.blit(hint, (8, SCREEN_H - 18))
        rd_t = f_tiny.render(f"ROCKS ✕ {self.rocks_destroyed}", True, NEON_ORANGE)
        surface.blit(rd_t, (SCREEN_W - rd_t.get_width() - 8, SCREEN_H - 18))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LEVEL 2
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LEVEL2_LENGTH       = 7000
LEVEL2_WORLD_SPEED  = 4.0

ALIEN_SPAWN_WORLD_XS = [
    500, 900, 1300, 1700,
    2100, 2400, 2700, 3000,
    3400, 3700, 4000, 4300,
    4700, 5000, 5300, 5600, 5900,
]

LEVEL2_SPIKE_DEFS = [
    (400,  True),  (650,  False), (900,  True),  (1150, False),
    (1400, True),  (1600, False), (1800, True),  (2000, False),
    (2200, True),  (2400, False), (2600, True),  (2800, False),
    (3000, True),  (3200, False), (3500, True),  (3700, False),
    (4000, True),  (4200, False), (4500, True),  (4700, False),
    (5000, True),  (5200, False), (5500, True),  (5700, False),
    (6000, True),  (6200, False), (6500, True),  (6700, False),
]

L2_BG_COLOR   = (5, 3, 18)
L2_GRID_COLOR = (18, 10, 45)

class Level2:
    def __init__(self, carry_score=0):
        self.reset(carry_score)

    def reset(self, carry_score=0):
        self.scroll             = 0.0
        self.player             = Player()
        self.spikes             = []
        self.spike_defs         = list(LEVEL2_SPIKE_DEFS)
        self.spawned_spikes     = set()
        self.particles          = []
        self.score              = carry_score
        self.gem                = Gem(LEVEL2_LENGTH // 2, PLAY_MID)
        self.gem_collected      = False
        self.portal             = Portal(LEVEL2_LENGTH - 200)
        self.suck_timer         = 0
        self.transition         = False
        self.trans_timer        = 0
        self.dead               = False
        self.dead_timer         = 0
        self.paused             = False
        self.bg_scroll          = 0.0
        self.bullets            = []
        self.aliens             = []
        self.alien_spawn_index  = 0
        self.aliens_destroyed   = 0
        self.rocks              = []
        self.rock_spawn_index   = 0
        self._spike_idx_counter = 0
        self._tick              = 0
        self.stars = [
            {"x": random.uniform(0, SCREEN_W),
             "y": random.uniform(PLAY_TOP, PLAY_BOT),
             "r": random.choice([1, 1, 1, 2]),
             "speed": random.uniform(0.5, 2.0),
             "col": random.choice([NEON_CYAN, NEON_PURPLE, WHITE, (200,180,255)])}
            for _ in range(80)
        ]

    def world_to_screen(self, wx):
        return wx - self.scroll

    def shoot(self):
        bx = int(self.player.x) + PLAYER_W
        by = int(self.player.y) + PLAYER_H // 2
        self.bullets.append(Bullet(bx, by))

    def spawn_spikes(self):
        screen_right_world = self.scroll + SCREEN_W + 100
        for i, (wx, on_g) in enumerate(self.spike_defs):
            if i not in self.spawned_spikes and wx < screen_right_world:
                self.spikes.append(Spike(wx - self.scroll + SCREEN_W, on_g,
                                         idx=self._spike_idx_counter))
                self._spike_idx_counter += 1
                self.spawned_spikes.add(i)

    def spawn_aliens(self):
        while self.alien_spawn_index < len(ALIEN_SPAWN_WORLD_XS):
            wx = ALIEN_SPAWN_WORLD_XS[self.alien_spawn_index]
            screen_wx = wx - self.scroll
            if screen_wx > SCREEN_W + 60:
                break
            self.aliens.append(Alien(SCREEN_W + 60, LEVEL2_WORLD_SPEED, self.scroll))
            self.alien_spawn_index += 1

    def spawn_rocks(self):
        l2_rock_xs = [800, 1600, 2400, 3200, 4000, 4800, 5600]
        while self.rock_spawn_index < len(l2_rock_xs):
            wx = l2_rock_xs[self.rock_spawn_index]
            if wx - self.scroll > SCREEN_W + 40:
                break
            if wx - self.scroll > -40:
                self.rocks.append(Rock(SCREEN_W + 40))
            self.rock_spawn_index += 1

    def update(self, keys):
        if self.paused or self.transition or self.dead:
            if self.transition: self.trans_timer += 1
            if self.dead:       self.dead_timer  += 1
            return

        self._tick += 1
        tick_spikes()

        world_speed = LEVEL2_WORLD_SPEED
        self.scroll    += world_speed
        self.bg_scroll += world_speed * 0.25

        self.spawn_spikes()
        self.spawn_aliens()
        self.spawn_rocks()

        for star in self.stars:
            star["x"] -= star["speed"]
            if star["x"] < 0:
                star["x"] = SCREEN_W + 2
                star["y"] = random.uniform(PLAY_TOP, PLAY_BOT)

        space_held = keys[pygame.K_SPACE]
        self.player.update(space_held=space_held)

        for sp in self.spikes:
            sp.update(world_speed)
        self.spikes = [sp for sp in self.spikes if sp.x > -60]

        for al in self.aliens:
            al.update(self.player.x, self.player.y, world_speed)

        for rock in self.rocks:
            rock.update()

        for bullet in self.bullets:
            bullet.update()

        bullets_to_remove = set()
        aliens_to_remove  = set()
        rocks_to_remove   = set()

        for bi, bullet in enumerate(self.bullets):
            if bullet.life <= 0 or bullet.x > SCREEN_W + 50:
                bullets_to_remove.add(bi)
                continue
            br = bullet.rect()
            for ai, al in enumerate(self.aliens):
                if ai in aliens_to_remove or not al.alive:
                    continue
                if br.colliderect(al.rect()):
                    killed = al.hit()
                    bullets_to_remove.add(bi)
                    if killed:
                        aliens_to_remove.add(ai)
                        self.score += al.score_value
                        self.aliens_destroyed += 1
                        for _ in range(35):
                            self.particles.append(
                                Particle(al.x, al.y,
                                         random.choice([al.tint, NEON_GREEN, NEON_YELLOW, WHITE]))
                            )
                    else:
                        for _ in range(8):
                            self.particles.append(
                                Particle(al.x, al.y, random.choice([WHITE, NEON_GREEN]))
                            )
                    break
            if bi in bullets_to_remove:
                continue
            for ri, rock in enumerate(self.rocks):
                if ri in rocks_to_remove:
                    continue
                if br.colliderect(rock.rect()):
                    for _ in range(18):
                        self.particles.append(
                            Particle(rock.x, rock.y,
                                     random.choice([rock.base_col, NEON_ORANGE, NEON_YELLOW, WHITE]))
                        )
                    rocks_to_remove.add(ri)
                    bullets_to_remove.add(bi)
                    self.score += 50
                    break

        self.aliens  = [a for i, a in enumerate(self.aliens)
                        if i not in aliens_to_remove and a.x > -100]
        self.rocks   = [r for i, r in enumerate(self.rocks)
                        if i not in rocks_to_remove and r.x > -80]
        self.bullets = [b for i, b in enumerate(self.bullets)
                        if i not in bullets_to_remove]

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        self.gem.update()
        self.portal.update(int(self.scroll))

        pr = self.player.rect()

        for sp in self.spikes:
            if pr.colliderect(sp.rect()):
                self.kill_player(); return

        for al in self.aliens:
            if al.alive and pr.colliderect(al.rect()):
                self.kill_player(); return

        for rock in self.rocks:
            if pr.colliderect(rock.rect()):
                self.kill_player(); return

        gem_sx = self.world_to_screen(self.gem.world_x)
        self.gem.x = gem_sx
        if not self.gem_collected:
            gem_rect = pygame.Rect(gem_sx - 14, self.gem.y - 14, 28, 28)
            if pr.colliderect(gem_rect):
                self.gem_collected  = True
                self.portal.active  = True
                self.portal.world_x = self.scroll + 900
                self.score         += 500
                for _ in range(30):
                    self.particles.append(Particle(gem_sx, self.gem.y, NEON_YELLOW))
            elif gem_sx < -60:
                self.gem.world_x = self.scroll + GEM_RESPAWN_AHEAD
                self.gem.x       = self.world_to_screen(self.gem.world_x)

        self.portal.x = self.world_to_screen(self.portal.world_x)
        portal_sx     = self.portal.x

        if self.portal.active and self.scroll > 0:
            portal_rect = pygame.Rect(portal_sx - 55, PLAY_TOP, 110, PLAY_BOT - PLAY_TOP)
            if pr.colliderect(portal_rect):
                self.suck_timer += 1
                if self.suck_timer > 10:
                    self.transition  = True
                    self.trans_timer = 0
                    for _ in range(50):
                        self.particles.append(Particle(portal_sx, self.portal.y, NEON_PURPLE))
            else:
                self.suck_timer = 0
                if portal_sx < -60:
                    self.portal.world_x = self.scroll + 600

        if self.player.y > SCREEN_H + 20 or self.player.y < -SCREEN_H:
            self.kill_player()

        self.score += 1

    def kill_player(self):
        self.dead       = True
        self.dead_timer = 0
        self.player.alive = False
        pygame.mixer.music.stop()
        for _ in range(40):
            self.particles.append(Particle(int(self.player.x)+24,
                                           int(self.player.y)+30, NEON_PINK))

    def draw(self, surface, tick):
        surface.fill(L2_BG_COLOR)
        offset = int(self.bg_scroll) % 60
        for gx in range(-offset, SCREEN_W, 60):
            pygame.draw.line(surface, L2_GRID_COLOR, (gx, 0), (gx, SCREEN_H))
        for gy in range(0, SCREEN_H, 60):
            pygame.draw.line(surface, L2_GRID_COLOR, (0, gy), (SCREEN_W, gy))
        for star in self.stars:
            sx, sy = int(star["x"]), int(star["y"])
            r = star["r"]
            col = star["col"]
            if r == 1:
                surface.set_at((sx, sy), col)
            else:
                pygame.draw.circle(surface, col, (sx, sy), r)
        draw_formal_platform(surface, 0, 0, SCREEN_W, CEILING_Y + PLATFORM_H,
                             (28, 8, 48), (58, 14, 88), (88, 24, 128), (12, 4, 24),
                             NEON_PINK, scroll_offset=self.bg_scroll, flip=True)
        draw_formal_platform(surface, 0, GROUND_Y, SCREEN_W, SCREEN_H - GROUND_Y,
                             BRICK_DARK, BRICK_MID, BRICK_LIGHT, BRICK_MORTAR,
                             NEON_GREEN, scroll_offset=self.bg_scroll, flip=False)
        if self.portal.active:
            hole_w = 70
            portal_sx = self.portal.x
            pygame.draw.rect(surface, L2_BG_COLOR,
                             (portal_sx - hole_w//2, 0, hole_w, CEILING_Y + PLATFORM_H + 2))
            pygame.draw.rect(surface, L2_BG_COLOR,
                             (portal_sx - hole_w//2, GROUND_Y - 2, hole_w, SCREEN_H - GROUND_Y + 2))
        for sp in self.spikes:
            sp.draw(surface)
        for rock in self.rocks:
            rock.draw(surface)
        for al in self.aliens:
            al.draw(surface, tick)
        for bullet in self.bullets:
            bullet.draw(surface)
        if not self.gem_collected:
            gem_sx = self.gem.x
            spin   = math.sin(tick * 0.08)
            w      = max(4, int(28 * abs(spin)))
            pulse  = (math.sin(tick * 0.1) + 1) / 2
            color  = lerp_color(NEON_YELLOW, NEON_GREEN, pulse)
            draw_glow_circle(surface, gem_sx, self.gem.y, 16, color, 100)
            pygame.draw.polygon(surface, color, [
                (gem_sx,        self.gem.y - 14),
                (gem_sx + w//2, self.gem.y),
                (gem_sx,        self.gem.y + 14),
                (gem_sx - w//2, self.gem.y),
            ])
            pygame.draw.polygon(surface, WHITE, [
                (gem_sx,        self.gem.y - 7),
                (gem_sx + w//4, self.gem.y),
                (gem_sx,        self.gem.y + 7),
                (gem_sx - w//4, self.gem.y),
            ])
            lbl = f_tiny.render("◆ COLLECT", True, NEON_YELLOW)
            surface.blit(lbl, (gem_sx - lbl.get_width()//2, self.gem.y - 28))
        self.portal.draw(surface, tick)
        for p in self.particles:
            p.draw(surface)
        self.player.draw(surface)
        self.draw_hud(surface, tick)
        surface.blit(scanline_surf, (0, 0))
        if self.dead:
            alpha = min(200, self.dead_timer * 5)
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, alpha))
            surface.blit(ov, (0, 0))
            if self.dead_timer > 20:
                draw_text_cx(surface, "GAME OVER", f_title, NEON_PINK, 200)
                draw_text_cx(surface, f"SCORE:  {self.score}", f_body, NEON_YELLOW, 315)
                draw_text_cx(surface, f"ALIENS DESTROYED: {self.aliens_destroyed}", f_small, NEON_GREEN, 350)
                draw_text_cx(surface, "ENTER → Retry Level 2     ESC → Menu", f_small, DIM_WHITE, 390)
        if self.transition:
            alpha = min(255, self.trans_timer * 6)
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 60, 20, alpha))
            surface.blit(ov, (0, 0))
            if self.trans_timer > 30:
                draw_text_cx(surface, "LEVEL 2  COMPLETE!", f_body, NEON_GREEN, 210)
                draw_text_cx(surface, f"SCORE:  {self.score}", f_sub, NEON_YELLOW, 255)
                draw_text_cx(surface, f"ALIENS DESTROYED: {self.aliens_destroyed}", f_small, NEON_CYAN, 290)
                draw_text_cx(surface, "ENTERING LEVEL 3...", f_small, NEON_PURPLE, 335)
                draw_text_cx(surface, "ENTER → Continue     ESC → Menu", f_small, DIM_WHITE, 375)

    def draw_hud(self, surface, tick):
        bar = pygame.Surface((SCREEN_W, 40), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 140))
        surface.blit(bar, (0, 0))
        lvl_t = f_hud.render("LEVEL  02", True, NEON_GREEN)
        surface.blit(lvl_t, (10, 8))
        sc_t = f_hud.render(f"SCORE  {self.score:06d}", True, NEON_YELLOW)
        surface.blit(sc_t, (SCREEN_W - sc_t.get_width() - 10, 8))
        gem_x = SCREEN_W // 2 - 60
        if self.gem_collected:
            pygame.draw.polygon(surface, NEON_YELLOW,
                                [(gem_x+10,2),(gem_x+18,10),(gem_x+10,18),(gem_x+2,10)])
            gt = f_tiny.render("GEM ✓", True, NEON_YELLOW)
        else:
            gt = f_tiny.render("GEM: collect ◆", True, DIM_WHITE)
        surface.blit(gt, (gem_x + 22, 10))
        if self.gem_collected:
            pt = f_tiny.render("◈ PORTAL OPEN", True, NEON_PURPLE)
        else:
            pt = f_tiny.render("◈ PORTAL LOCKED", True, (60, 50, 80))
        surface.blit(pt, (gem_x + 22, 24))
        prog  = min(1.0, self.scroll / LEVEL2_LENGTH)
        bar_w = 200
        bar_x = SCREEN_W // 2 - bar_w // 2
        bar_y = SCREEN_H - 18
        pygame.draw.rect(surface, (30, 30, 60), (bar_x, bar_y, bar_w, 8))
        fill_c = lerp_color(NEON_GREEN, NEON_PINK, prog)
        pygame.draw.rect(surface, fill_c, (bar_x, bar_y, int(bar_w * prog), 8))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, 8), 1)
        prog_t = f_tiny.render(f"{int(prog*100)}%", True, WHITE)
        surface.blit(prog_t, (bar_x + bar_w + 4, bar_y - 1))
        hint = f_tiny.render("SPACE=Flip  E=Shoot", True, (80, 80, 100))
        surface.blit(hint, (8, SCREEN_H - 18))
        ad_t = f_tiny.render(f"ALIENS ✕ {self.aliens_destroyed}", True, NEON_GREEN)
        surface.blit(ad_t, (SCREEN_W - ad_t.get_width() - 8, SCREEN_H - 18))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LEVEL 3  ── Boss Fight
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LEVEL3_LENGTH      = 8000
LEVEL3_WORLD_SPEED = 4.6

LEVEL3_ALIEN_XS = [
    600, 950, 1300, 1650, 2000,
    2350, 2700, 3050, 3400, 3750,
    4100, 4450, 4800, 5150, 5500, 5850,
]

LEVEL3_SPIKE_DEFS = [
    (350, True),  (580, False), (810, True),  (1040, False),
    (1270, True), (1500, False),(1730, True), (1960, False),
    (2200, True), (2430, False),(2660, True), (2890, False),
    (3120, True), (3350, False),(3600, True), (3830, False),
    (4060, True), (4300, False),(4540, True), (4780, False),
    (5020, True), (5260, False),(5500, True), (5740, False),
    (6000, True), (6240, False),(6480, True), (6720, False),
    (7000, True), (7240, False),(7480, True),
]

L3_BG_COLOR   = (3, 2, 14)
L3_GRID_COLOR = (12, 6, 38)


class Level3:
    def __init__(self, carry_score=0):
        self.reset(carry_score)

    def reset(self, carry_score=0):
        self.scroll              = 0.0
        self.player              = Player()
        self.spikes              = []
        self.spike_defs          = list(LEVEL3_SPIKE_DEFS)
        self.spawned_spikes      = set()
        self.particles           = []
        self.score               = carry_score
        self.gem                 = Gem(LEVEL3_LENGTH // 2, PLAY_MID)
        self.gem_collected       = False
        self.portal              = Portal(LEVEL3_LENGTH - 200)
        self.portal.active       = False
        self.suck_timer          = 0
        self.transition          = False
        self.trans_timer         = 0
        self.dead                = False
        self.dead_timer          = 0
        self.paused              = False
        self.bg_scroll           = 0.0
        self.bullets             = []
        self.aliens              = []
        self.alien_spawn_index   = 0
        self.aliens_destroyed    = 0
        self.rocks               = []
        self.rock_spawn_index    = 0
        self._spike_idx_counter  = 0
        self._tick               = 0
        self.boss                = None
        self.boss_spawned        = False
        self.boss_defeated       = False
        self.boss_announce_timer = 0
        self.stars = [
            {"x": random.uniform(0, SCREEN_W),
             "y": random.uniform(PLAY_TOP, PLAY_BOT),
             "r": random.choice([1, 1, 2]),
             "speed": random.uniform(0.4, 2.2),
             "col": random.choice([NEON_PURPLE, (180,100,255), WHITE, NEON_CYAN])}
            for _ in range(100)
        ]
        self._l3_rock_xs = [900, 1800, 2700, 3600, 4500, 5400, 6300]

    def world_to_screen(self, wx):
        return wx - self.scroll

    def shoot(self):
        bx = int(self.player.x) + PLAYER_W
        by = int(self.player.y) + PLAYER_H // 2
        self.bullets.append(Bullet(bx, by))

    def spawn_spikes(self):
        screen_right = self.scroll + SCREEN_W + 100
        for i, (wx, on_g) in enumerate(self.spike_defs):
            if i not in self.spawned_spikes and wx < screen_right:
                self.spikes.append(Spike(wx - self.scroll + SCREEN_W, on_g,
                                         idx=self._spike_idx_counter))
                self._spike_idx_counter += 1
                self.spawned_spikes.add(i)

    def spawn_aliens(self):
        if self.boss_spawned:
            return
        while self.alien_spawn_index < len(LEVEL3_ALIEN_XS):
            wx = LEVEL3_ALIEN_XS[self.alien_spawn_index]
            if wx - self.scroll > SCREEN_W + 60:
                break
            self.aliens.append(Alien(SCREEN_W + 60, LEVEL3_WORLD_SPEED, self.scroll))
            self.alien_spawn_index += 1

    def spawn_rocks(self):
        while self.rock_spawn_index < len(self._l3_rock_xs):
            wx = self._l3_rock_xs[self.rock_spawn_index]
            if wx - self.scroll > SCREEN_W + 40:
                break
            if wx - self.scroll > -40:
                self.rocks.append(Rock(SCREEN_W + 40))
            self.rock_spawn_index += 1

    def _spawn_boss(self):
        self.boss = BossAlien()
        self.boss_spawned = True
        self.boss_announce_timer = 180
        # spawn_delay is already set in BossAlien.__init__ to 180

    def update(self, keys):
        if self.paused or self.transition or self.dead:
            if self.transition: self.trans_timer += 1
            if self.dead:       self.dead_timer  += 1
            return

        self._tick += 1
        tick_spikes()

        world_speed     = LEVEL3_WORLD_SPEED
        self.scroll    += world_speed
        self.bg_scroll += world_speed * 0.22

        if self.boss_announce_timer > 0:
            self.boss_announce_timer -= 1

        self.spawn_spikes()
        self.spawn_aliens()
        self.spawn_rocks()

        for star in self.stars:
            star["x"] -= star["speed"]
            if star["x"] < 0:
                star["x"] = SCREEN_W + 2
                star["y"] = random.uniform(PLAY_TOP, PLAY_BOT)

        space_held = keys[pygame.K_SPACE]
        self.player.update(space_held=space_held)

        for sp in self.spikes:
            sp.update(world_speed)
        self.spikes = [sp for sp in self.spikes if sp.x > -60]

        for al in self.aliens:
            al.update(self.player.x, self.player.y, world_speed)

        for rock in self.rocks:
            rock.update()

        for bullet in self.bullets:
            bullet.update()

        # Boss update — always call so orbs keep moving even during spawn_delay
        if self.boss and self.boss.alive:
            self.boss.update(self.player.x, self.player.y)
        elif self.boss and not self.boss.alive and not self.boss_defeated:
            self.boss_defeated   = True
            self.portal.active   = True
            self.portal.world_x  = self.scroll + 600
            self.score          += self.boss.score_value
            for _ in range(80):
                self.particles.append(
                    Particle(int(self.boss.x), int(self.boss.y),
                             random.choice([NEON_PURPLE, NEON_PINK, NEON_YELLOW,
                                            WHITE, (255, 100, 255)]))
                )

        bullets_to_remove = set()
        aliens_to_remove  = set()
        rocks_to_remove   = set()

        for bi, bullet in enumerate(self.bullets):
            if bullet.life <= 0 or bullet.x > SCREEN_W + 50:
                bullets_to_remove.add(bi)
                continue
            br = bullet.rect()

            # vs boss
            if (self.boss and self.boss.alive
                    and bi not in bullets_to_remove
                    and br.colliderect(self.boss.rect())):
                killed = self.boss.hit()
                bullets_to_remove.add(bi)
                for _ in range(10):
                    self.particles.append(
                        Particle(int(self.boss.x), int(self.boss.y),
                                 random.choice([NEON_YELLOW, WHITE, NEON_PINK]))
                    )
                continue

            for ai, al in enumerate(self.aliens):
                if ai in aliens_to_remove or not al.alive:
                    continue
                if br.colliderect(al.rect()):
                    killed = al.hit()
                    bullets_to_remove.add(bi)
                    if killed:
                        aliens_to_remove.add(ai)
                        self.score           += al.score_value
                        self.aliens_destroyed += 1
                        for _ in range(28):
                            self.particles.append(
                                Particle(al.x, al.y,
                                         random.choice([al.tint, NEON_GREEN, NEON_YELLOW, WHITE]))
                            )
                    else:
                        for _ in range(6):
                            self.particles.append(
                                Particle(al.x, al.y, random.choice([WHITE, NEON_GREEN]))
                            )
                    break

            if bi in bullets_to_remove:
                continue

            for ri, rock in enumerate(self.rocks):
                if ri in rocks_to_remove:
                    continue
                if br.colliderect(rock.rect()):
                    for _ in range(18):
                        self.particles.append(
                            Particle(rock.x, rock.y,
                                     random.choice([rock.base_col, NEON_ORANGE, NEON_YELLOW, WHITE]))
                        )
                    rocks_to_remove.add(ri)
                    bullets_to_remove.add(bi)
                    self.score += 50
                    break

        self.aliens  = [a for i, a in enumerate(self.aliens)
                        if i not in aliens_to_remove and a.x > -100]
        self.rocks   = [r for i, r in enumerate(self.rocks)
                        if i not in rocks_to_remove and r.x > -80]
        self.bullets = [b for i, b in enumerate(self.bullets)
                        if i not in bullets_to_remove]

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        self.gem.update()
        self.portal.update(self._tick)

        pr = self.player.rect()

        for sp in self.spikes:
            if pr.colliderect(sp.rect()):
                self.kill_player(); return

        for al in self.aliens:
            if al.alive and pr.colliderect(al.rect()):
                self.kill_player(); return

        for rock in self.rocks:
            if pr.colliderect(rock.rect()):
                self.kill_player(); return

        # Boss body collision — only active once spawn_delay has expired
        if (self.boss and self.boss.alive
                and self.boss.spawn_delay <= 0
                and pr.colliderect(self.boss.rect())):
            self.kill_player(); return

        # Boss orb collision — only orbs that are on-screen (x > 0 already enforced
        # in _update_orbs, but double-check here too)
        if self.boss:
            for orb_rect in self.boss.orb_rects():
                if orb_rect.x > 0 and pr.colliderect(orb_rect):
                    self.kill_player(); return

        gem_sx = self.world_to_screen(self.gem.world_x)
        self.gem.x = gem_sx
        if not self.gem_collected:
            gem_rect = pygame.Rect(gem_sx - 14, self.gem.y - 14, 28, 28)
            if pr.colliderect(gem_rect):
                self.gem_collected = True
                self.score        += 500
                for _ in range(30):
                    self.particles.append(Particle(gem_sx, self.gem.y, NEON_YELLOW))
                self._spawn_boss()
            elif gem_sx < -60:
                self.gem.world_x = self.scroll + GEM_RESPAWN_AHEAD
                self.gem.x       = self.world_to_screen(self.gem.world_x)

        self.portal.x = self.world_to_screen(self.portal.world_x)
        portal_sx     = self.portal.x

        if self.portal.active and self.scroll > 0:
            portal_rect = pygame.Rect(portal_sx - 55, PLAY_TOP, 110, PLAY_BOT - PLAY_TOP)
            if pr.colliderect(portal_rect):
                self.suck_timer += 1
                if self.suck_timer > 10:
                    self.transition  = True
                    self.trans_timer = 0
                    for _ in range(50):
                        self.particles.append(Particle(portal_sx, self.portal.y, NEON_PURPLE))
            else:
                self.suck_timer = 0
                if portal_sx < -60:
                    self.portal.world_x = self.scroll + 600

        if self.player.y > SCREEN_H + 20 or self.player.y < -SCREEN_H:
            self.kill_player()

        self.score += 1

    def kill_player(self):
        self.dead        = True
        self.dead_timer  = 0
        self.player.alive = False
        pygame.mixer.music.stop()
        for _ in range(40):
            self.particles.append(Particle(int(self.player.x) + 24,
                                           int(self.player.y) + 30, NEON_PINK))

    def draw(self, surface, tick):
        surface.fill(L3_BG_COLOR)

        offset = int(self.bg_scroll) % 60
        for gx in range(-offset, SCREEN_W, 60):
            pygame.draw.line(surface, L3_GRID_COLOR, (gx, 0), (gx, SCREEN_H))
        for gy in range(0, SCREEN_H, 60):
            pygame.draw.line(surface, L3_GRID_COLOR, (0, gy), (SCREEN_W, gy))

        for star in self.stars:
            sx, sy = int(star["x"]), int(star["y"])
            r = star["r"]
            if r == 1:
                surface.set_at((sx, sy), star["col"])
            else:
                pygame.draw.circle(surface, star["col"], (sx, sy), r)

        draw_formal_platform(
            surface, 0, 0, SCREEN_W, CEILING_Y + PLATFORM_H,
            (30, 4, 60), (60, 8, 100), (90, 16, 140), (12, 2, 24),
            NEON_PINK, scroll_offset=self.bg_scroll, flip=True
        )
        draw_formal_platform(
            surface, 0, GROUND_Y, SCREEN_W, SCREEN_H - GROUND_Y,
            (20, 4, 50), (45, 10, 85), (70, 18, 120), (10, 2, 20),
            NEON_PURPLE, scroll_offset=self.bg_scroll, flip=False
        )

        if self.portal.active:
            hole_w    = 70
            portal_sx = self.portal.x
            pygame.draw.rect(surface, L3_BG_COLOR,
                             (portal_sx - hole_w // 2, 0, hole_w, CEILING_Y + PLATFORM_H + 2))
            pygame.draw.rect(surface, L3_BG_COLOR,
                             (portal_sx - hole_w // 2, GROUND_Y - 2, hole_w, SCREEN_H - GROUND_Y + 2))

        for sp in self.spikes:
            sp.draw(surface)
        for rock in self.rocks:
            rock.draw(surface)
        for al in self.aliens:
            al.draw(surface, tick)
        if self.boss:
            self.boss.draw(surface, tick)
        for bullet in self.bullets:
            bullet.draw(surface)

        if not self.gem_collected:
            gem_sx = self.gem.x
            spin   = math.sin(tick * 0.08)
            w      = max(4, int(28 * abs(spin)))
            pulse  = (math.sin(tick * 0.1) + 1) / 2
            color  = lerp_color(NEON_YELLOW, NEON_PURPLE, pulse)
            draw_glow_circle(surface, gem_sx, self.gem.y, 16, color, 100)
            pygame.draw.polygon(surface, color, [
                (gem_sx,        self.gem.y - 14),
                (gem_sx + w//2, self.gem.y),
                (gem_sx,        self.gem.y + 14),
                (gem_sx - w//2, self.gem.y),
            ])
            pygame.draw.polygon(surface, WHITE, [
                (gem_sx,        self.gem.y - 7),
                (gem_sx + w//4, self.gem.y),
                (gem_sx,        self.gem.y + 7),
                (gem_sx - w//4, self.gem.y),
            ])
            lbl = f_tiny.render("◆ COLLECT", True, NEON_YELLOW)
            surface.blit(lbl, (gem_sx - lbl.get_width()//2, self.gem.y - 28))

        if self.gem_collected and self.boss and self.boss.alive:
            warn_col = lerp_color(NEON_PINK, NEON_YELLOW, (math.sin(tick * 0.12) + 1) / 2)
            warn_t   = f_body.render("◆ DEFEAT THE BOSS TO OPEN PORTAL ◆", True, warn_col)
            ws = pygame.Surface((warn_t.get_width() + 20, warn_t.get_height() + 8), pygame.SRCALPHA)
            ws.fill((0, 0, 0, 130))
            surface.blit(ws, (SCREEN_W // 2 - ws.get_width() // 2, 48))
            surface.blit(warn_t, (SCREEN_W // 2 - warn_t.get_width() // 2, 52))

        if self.boss_announce_timer > 0:
            alpha = min(255, self.boss_announce_timer * 5)
            at = f_body.render("⚠  BOSS  INCOMING  ⚠", True, NEON_YELLOW)
            s  = pygame.Surface((at.get_width() + 32, at.get_height() + 14), pygame.SRCALPHA)
            s.fill((120, 0, 0, min(180, alpha)))
            surface.blit(s, (SCREEN_W // 2 - s.get_width() // 2, SCREEN_H // 2 - 30))
            at.set_alpha(alpha)
            surface.blit(at, (SCREEN_W // 2 - at.get_width() // 2, SCREEN_H // 2 - 24))

        if self.boss_defeated and not self.transition:
            dt = f_small.render("BOSS DEFEATED!  ◈ ENTER PORTAL", True, NEON_GREEN)
            ds = pygame.Surface((dt.get_width() + 20, dt.get_height() + 8), pygame.SRCALPHA)
            ds.fill((0, 0, 0, 140))
            surface.blit(ds, (SCREEN_W // 2 - ds.get_width() // 2, 48))
            surface.blit(dt, (SCREEN_W // 2 - dt.get_width() // 2, 52))

        self.portal.draw(surface, tick)

        for p in self.particles:
            p.draw(surface)

        self.player.draw(surface)
        self.draw_hud(surface, tick)
        surface.blit(scanline_surf, (0, 0))

        if self.dead:
            alpha = min(200, self.dead_timer * 5)
            ov    = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, alpha))
            surface.blit(ov, (0, 0))
            if self.dead_timer > 20:
                draw_text_cx(surface, "GAME OVER",            f_title, NEON_PINK,   200)
                draw_text_cx(surface, f"SCORE:  {self.score}", f_body, NEON_YELLOW, 315)
                draw_text_cx(surface, f"ALIENS DESTROYED: {self.aliens_destroyed}",
                             f_small, NEON_GREEN, 350)
                draw_text_cx(surface, "ENTER → Retry Level 3     ESC → Menu",
                             f_small, DIM_WHITE, 390)

        if self.transition:
            alpha = min(255, self.trans_timer * 6)
            ov    = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((60, 0, 80, alpha))
            surface.blit(ov, (0, 0))
            if self.trans_timer > 30:
                draw_text_cx(surface, "LEVEL 3  COMPLETE!",    f_body,  NEON_PURPLE, 200)
                draw_text_cx(surface, f"SCORE:  {self.score}", f_sub,   NEON_YELLOW, 248)
                draw_text_cx(surface, f"ALIENS DESTROYED: {self.aliens_destroyed}",
                             f_small, NEON_CYAN, 286)
                draw_text_cx(surface, "YOU WIN!  Thanks for playing G FLIP",
                             f_small, NEON_GREEN, 330)
                draw_text_cx(surface, "ESC → Menu", f_small, NEON_PINK, 374)

    def draw_hud(self, surface, tick):
        bar = pygame.Surface((SCREEN_W, 40), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 140))
        surface.blit(bar, (0, 0))

        lvl_t = f_hud.render("LEVEL  03", True, NEON_PURPLE)
        surface.blit(lvl_t, (10, 8))

        sc_t = f_hud.render(f"SCORE  {self.score:06d}", True, NEON_YELLOW)
        surface.blit(sc_t, (SCREEN_W - sc_t.get_width() - 10, 8))

        gem_x = SCREEN_W // 2 - 60
        if self.gem_collected:
            pygame.draw.polygon(surface, NEON_YELLOW,
                                [(gem_x+10,2),(gem_x+18,10),(gem_x+10,18),(gem_x+2,10)])
            gt = f_tiny.render("GEM ✓", True, NEON_YELLOW)
        else:
            gt = f_tiny.render("GEM: collect ◆", True, DIM_WHITE)
        surface.blit(gt, (gem_x + 22, 10))

        if self.boss and self.boss.alive:
            pt = f_tiny.render("◈ DEFEAT BOSS", True, NEON_PINK)
        elif self.boss_defeated:
            pt = f_tiny.render("◈ PORTAL OPEN", True, NEON_PURPLE)
        elif self.gem_collected:
            pt = f_tiny.render("◈ BOSS INCOMING", True, NEON_ORANGE)
        else:
            pt = f_tiny.render("◈ PORTAL LOCKED", True, (60, 50, 80))
        surface.blit(pt, (gem_x + 22, 24))

        if self.boss and self.boss.alive:
            bbar_w = 300
            bbar_x = SCREEN_W // 2 - bbar_w // 2
            bbar_y = SCREEN_H - 32
            pygame.draw.rect(surface, (50, 0, 0),    (bbar_x - 2, bbar_y - 2, bbar_w + 4, 18))
            hp_frac = max(0, self.boss.hp / BOSS_MAX_HP)
            hp_col  = lerp_color(NEON_PINK, NEON_GREEN, hp_frac)
            pygame.draw.rect(surface, hp_col,        (bbar_x, bbar_y, int(bbar_w * hp_frac), 14))
            pygame.draw.rect(surface, WHITE,          (bbar_x, bbar_y, bbar_w, 14), 1)
            bl = f_tiny.render(f"BOSS  HP  {self.boss.hp}/{BOSS_MAX_HP}", True, WHITE)
            surface.blit(bl, (bbar_x + bbar_w // 2 - bl.get_width() // 2, bbar_y + 1))
        else:
            prog  = min(1.0, self.scroll / LEVEL3_LENGTH)
            bar_w = 200
            bar_x = SCREEN_W // 2 - bar_w // 2
            bar_y = SCREEN_H - 18
            pygame.draw.rect(surface, (30, 30, 60), (bar_x, bar_y, bar_w, 8))
            fill_c = lerp_color(NEON_PURPLE, NEON_PINK, prog)
            pygame.draw.rect(surface, fill_c,       (bar_x, bar_y, int(bar_w * prog), 8))
            pygame.draw.rect(surface, WHITE,         (bar_x, bar_y, bar_w, 8), 1)
            prog_t = f_tiny.render(f"{int(prog*100)}%", True, WHITE)
            surface.blit(prog_t, (bar_x + bar_w + 4, bar_y - 1))

        hint  = f_tiny.render("SPACE=Flip  E=Shoot", True, (80, 80, 100))
        surface.blit(hint, (8, SCREEN_H - 18))

        ad_t = f_tiny.render(f"ALIENS ✕ {self.aliens_destroyed}", True, NEON_GREEN)
        surface.blit(ad_t, (SCREEN_W - ad_t.get_width() - 8, SCREEN_H - 18))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STATE MACHINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ST_START  = "start"
ST_GUIDE  = "guide"
ST_LEVEL1 = "level1"
ST_LEVEL2 = "level2"
ST_LEVEL3 = "level3"

state  = ST_START
tick   = 0
level1 = None
level2 = None
level3 = None

def start_level1():
    global level1
    level1 = Level1()
    _play_music()

def start_level2(carry_score=0):
    global level2
    level2 = Level2(carry_score)
    _play_music()

def start_level3(carry_score=0):
    global level3
    level3 = Level3(carry_score)
    _play_music()

def _play_music():
    try:
        pygame.mixer.music.load("gflp.mp3")
        pygame.mixer.music.set_volume(0.55)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"[Music] Could not restart gflp.mp3: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN LOOP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
running = True
while running:
    clock.tick(FPS)
    tick += 1
    keys = pygame.key.get_pressed()

    tick_spikes()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if state == ST_START:
                if event.key == pygame.K_RETURN:
                    state = ST_GUIDE
                elif event.key == pygame.K_ESCAPE:
                    running = False

            elif state == ST_GUIDE:
                if event.key == pygame.K_RETURN:
                    start_level1()
                    state = ST_LEVEL1
                elif event.key == pygame.K_ESCAPE:
                    state = ST_START

            elif state == ST_LEVEL1:
                if level1.dead:
                    if event.key == pygame.K_RETURN:
                        start_level1()
                    elif event.key == pygame.K_ESCAPE:
                        state = ST_START
                elif level1.transition:
                    if event.key == pygame.K_RETURN:
                        start_level2(level1.score)
                        state = ST_LEVEL2
                    elif event.key == pygame.K_ESCAPE:
                        state = ST_START
                elif level1.paused:
                    if event.key == pygame.K_ESCAPE:
                        level1.paused = False
                        pygame.mixer.music.unpause()
                    elif event.key == pygame.K_q:
                        state = ST_START
                else:
                    if event.key == pygame.K_SPACE:
                        level1.player.flip()
                    elif event.key == pygame.K_ESCAPE:
                        level1.paused = True
                        pygame.mixer.music.pause()
                    elif event.key == pygame.K_e:
                        level1.shoot()

            elif state == ST_LEVEL2:
                if level2.dead:
                    if event.key == pygame.K_RETURN:
                        start_level2()
                    elif event.key == pygame.K_ESCAPE:
                        state = ST_START
                elif level2.transition:
                    if event.key == pygame.K_RETURN:
                        start_level3(level2.score)
                        state = ST_LEVEL3
                    elif event.key == pygame.K_ESCAPE:
                        state = ST_START
                elif level2.paused:
                    if event.key == pygame.K_ESCAPE:
                        level2.paused = False
                        pygame.mixer.music.unpause()
                    elif event.key == pygame.K_q:
                        state = ST_START
                else:
                    if event.key == pygame.K_SPACE:
                        level2.player.flip()
                    elif event.key == pygame.K_ESCAPE:
                        level2.paused = True
                        pygame.mixer.music.pause()
                    elif event.key == pygame.K_e:
                        level2.shoot()

            elif state == ST_LEVEL3:
                if level3.dead:
                    if event.key == pygame.K_RETURN:
                        start_level3()
                    elif event.key == pygame.K_ESCAPE:
                        state = ST_START
                elif level3.transition:
                    if event.key == pygame.K_ESCAPE:
                        state = ST_START
                elif level3.paused:
                    if event.key == pygame.K_ESCAPE:
                        level3.paused = False
                        pygame.mixer.music.unpause()
                    elif event.key == pygame.K_q:
                        state = ST_START
                else:
                    if event.key == pygame.K_SPACE:
                        level3.player.flip()
                    elif event.key == pygame.K_ESCAPE:
                        level3.paused = True
                        pygame.mixer.music.pause()
                    elif event.key == pygame.K_e:
                        level3.shoot()

    # Hold-E shooting
    if state == ST_LEVEL1 and level1 and not level1.dead and not level1.paused and not level1.transition:
        if keys[pygame.K_e]:
            level1.shoot()
    if state == ST_LEVEL2 and level2 and not level2.dead and not level2.paused and not level2.transition:
        if keys[pygame.K_e]:
            level2.shoot()
    if state == ST_LEVEL3 and level3 and not level3.dead and not level3.paused and not level3.transition:
        if keys[pygame.K_e]:
            level3.shoot()

    # ── Backgrounds ──────────────────────────────────────────────────────────
    if state in (ST_START, ST_GUIDE):
        if HAS_BG:
            screen.blit(bg_raw, (0, 0))
        else:
            screen.fill(DARK_BG)
            for gx in range(0, SCREEN_W, 50):
                pygame.draw.line(screen, (18,14,40),(gx,0),(gx,SCREEN_H))
            for gy in range(0, SCREEN_H, 50):
                pygame.draw.line(screen, (18,14,40),(0,gy),(SCREEN_W,gy))

    # ── Start screen ─────────────────────────────────────────────────────────
    if state == ST_START:
        for layer in menu_layers:
            layer.update(); layer.draw(screen)
        draw_neon_lines(screen, tick)
        draw_menu_platform(screen, MENU_CEILING_Y, NEON_PURPLE, tick)
        draw_menu_platform(screen, MENU_GROUND_Y,  NEON_CYAN,   tick)
        draw_spike_row_menu(screen, MENU_CEILING_Y + MENU_PLATFORM_H, False, tick)
        draw_spike_row_menu(screen, MENU_GROUND_Y  - SPIKE_H,         True,  tick)
        for orb in menu_orbs:
            orb.draw(screen, tick)
        menu_char_ground.update();  menu_char_ground.draw(screen,  tick)
        menu_char_ceiling.update(); menu_char_ceiling.draw(screen, tick)
        draw_lightning(screen, tick)
        draw_menu_title(screen, tick)

        lvl = f_tiny.render("LEVEL  01", True, NEON_CYAN)
        screen.blit(lvl, (10,6))
        sc  = f_tiny.render("SCORE  000000", True, NEON_YELLOW)
        screen.blit(sc, (SCREEN_W - sc.get_width()-10, 6))

        if (tick//35)%2==0:
            t2 = (math.sin(tick*0.06)+1)/2
            pc = lerp_color(NEON_YELLOW, NEON_PINK, t2)
            pe = f_sub.render("▶  PRESS  ENTER  TO  START  ◀", True, pc)
            gb = pygame.Surface((pe.get_width()+24, pe.get_height()+10), pygame.SRCALPHA)
            gb.fill((*pc, 30))
            screen.blit(gb, (SCREEN_W//2-gb.get_width()//2, 500))
            screen.blit(pe, (SCREEN_W//2-pe.get_width()//2, 503))
        esc_t = f_tiny.render("ESC  →  Quit", True, (90,90,120))
        screen.blit(esc_t, (SCREEN_W//2 - esc_t.get_width()//2, 542))
        draw_corner_deco(screen, tick)
        screen.blit(scanline_surf, (0,0))

    # ── Guide screen ─────────────────────────────────────────────────────────
    elif state == ST_GUIDE:
        draw_guide(screen, tick)
        screen.blit(scanline_surf, (0,0))

    # ── Level 1 ──────────────────────────────────────────────────────────────
    elif state == ST_LEVEL1:
        level1.update(keys)
        level1.draw(screen, tick)

        if level1.paused:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0,0,0,170)); screen.blit(ov,(0,0))
            draw_panel(screen, 200, 180, 400, 200)
            draw_text_cx(screen, "PAUSED",            f_body,  NEON_CYAN,   210)
            draw_text_cx(screen, "ESC  →  Resume",    f_small, NEON_YELLOW, 270)
            draw_text_cx(screen, "Q    →  Main Menu", f_small, DIM_WHITE,   310)

    # ── Level 2 ──────────────────────────────────────────────────────────────
    elif state == ST_LEVEL2:
        level2.update(keys)
        level2.draw(screen, tick)

        if level2.paused:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0,0,0,170)); screen.blit(ov,(0,0))
            draw_panel(screen, 200, 180, 400, 200)
            draw_text_cx(screen, "PAUSED",            f_body,  NEON_GREEN,  210)
            draw_text_cx(screen, "ESC  →  Resume",    f_small, NEON_YELLOW, 270)
            draw_text_cx(screen, "Q    →  Main Menu", f_small, DIM_WHITE,   310)

    # ── Level 3 ──────────────────────────────────────────────────────────────
    elif state == ST_LEVEL3:
        level3.update(keys)
        level3.draw(screen, tick)

        if level3.paused:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0,0,0,170)); screen.blit(ov,(0,0))
            draw_panel(screen, 200, 180, 400, 200)
            draw_text_cx(screen, "PAUSED",            f_body,  NEON_PURPLE, 210)
            draw_text_cx(screen, "ESC  →  Resume",    f_small, NEON_YELLOW, 270)
            draw_text_cx(screen, "Q    →  Main Menu", f_small, DIM_WHITE,   310)

    pygame.display.flip()

pygame.quit()
sys.exit()