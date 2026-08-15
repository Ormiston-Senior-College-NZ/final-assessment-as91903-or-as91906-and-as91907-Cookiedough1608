import pygame
import random
import math
import os

# ============================================================
# PARTY RUN — Subway Surfers style endless runner
# 3 lanes, jump / slide, pseudo-3D perspective, coins, power-ups
# ============================================================

pygame.init()

WIDTH = 900
HEIGHT = 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Party Run")

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont("arial", 40, bold=True)
big_font = pygame.font.SysFont("arial", 70, bold=True)
small_font = pygame.font.SysFont("arial", 24, bold=True)
tiny_font = pygame.font.SysFont("arial", 18, bold=True)

# ---------------- Colours ----------------
WHITE = (255, 255, 255)
BLACK = (15, 15, 18)
GREY = (120, 120, 130)

SKY_TOP = (60, 170, 255)
SKY_BOTTOM = (200, 235, 255)
SUN = (255, 220, 90)

BUILDING = (95, 105, 135)
WINDOW = (255, 235, 130)

ROAD_DARK = (55, 55, 62)
ROAD_LIGHT = (72, 72, 80)
CURB = (230, 230, 235)

TRAIN_BODY = (235, 70, 70)
TRAIN_STRIPE = (255, 255, 255)
BARRIER_YELLOW = (255, 200, 40)
BARRIER_BLACK = (30, 30, 30)

COIN_GOLD = (255, 205, 55)
COIN_SHADE = (200, 150, 20)

MEDICAL_RED = (230, 60, 60)
FOOD_RED = (220, 50, 50)
FOOD_LEAF = (70, 170, 70)
CANDY_PINK = (255, 110, 170)
CANDY_STRIPE = (255, 255, 255)

PILL_RED = (230, 70, 70)
PILL_WHITE = (250, 250, 250)
BOTTLE_GLASS = (70, 90, 60)
BOTTLE_LABEL = (245, 240, 225)

SKIN = (255, 205, 165)
SHIRT_BLUE = (60, 130, 255)
SHIRT_BOOST = (60, 220, 130)
SHIRT_SHIELD = (255, 210, 60)
PANTS = (40, 45, 60)

POLICE_RED = (230, 50, 50)
POLICE_BLUE = (50, 90, 230)

MAGNET_PURPLE = (170, 100, 255)
MULT_ORANGE = (255, 140, 40)
SHIELD_CYAN = (70, 220, 230)

# ---------------- Perspective helpers ----------------
HORIZON_Y = 230
GROUND_Y = 600
LANE_HALF_NEAR = 230
LANE_HALF_FAR = 6
SCALE_NEAR = 1.0
SCALE_FAR = 0.08

LANE_OFFSETS = [-1, 0, 1]  # left, centre, right


def lane_half_width(d):
    return LANE_HALF_FAR + (LANE_HALF_NEAR - LANE_HALF_FAR) * (1 - d)


def persp_x(lane_offset, d):
    return WIDTH / 2 + lane_offset * lane_half_width(d)


def persp_y(d):
    return HORIZON_Y + (GROUND_Y - HORIZON_Y) * (1 - d)


def persp_scale(d):
    return SCALE_FAR + (SCALE_NEAR - SCALE_FAR) * (1 - d)


# ---------------- Player ----------------
PLAYER_D = 0.015
JUMP_DURATION = 34
JUMP_HEIGHT = 150
SLIDE_DURATION = 34
LANE_LERP_SPEED = 0.28

player_lane = 1          # 0=left, 1=centre, 2=right (index into LANE_OFFSETS)
player_visual_offset = 0.0  # current smoothed world lane offset

jumping = False
jump_t = 0
sliding = False
slide_t = 0

run_cycle = 0.0

# ---------------- Power-ups ----------------
magnet_timer = 0
mult_timer = 0
shield_timer = 0
MAGNET_DURATION = 420
MULT_DURATION = 420
SHIELD_DURATION = 300

score = 0
coins_collected = 0
game_over = False
lose_reason = ""
score_recorded = False

distance_speed = 0.0048      # base "depth units per frame" obstacles travel
MIN_DEPTH_SPEED = 0.0048
MAX_DEPTH_SPEED = 0.0135

# ---------------- World objects ----------------
obstacles = []   # {lane, d, type, resolved}          -- trains / barriers
coins = []       # {lane, d, collected, kind, high}    -- good items: medical / food / candy
bad_items = []   # {lane, d, resolved, kind}           -- bad items: drugs / alcohol
powerups = []    # {lane, d, kind, taken}

spawn_timer = 0
SPAWN_INTERVAL_MIN = 95
SPAWN_INTERVAL_MAX = 135
next_spawn_in = random.randint(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)
frames_since_full_block = 999
FULL_BLOCK_COOLDOWN = 150  # min frames between lane-blocking waves (train/low/high walls)

# lane-divider dash scroll
dash_scroll = 0.0

stars = [[random.randint(0, WIDTH), random.randint(0, HORIZON_Y)] for _ in range(60)]
clouds = [[random.randint(0, WIDTH), random.randint(20, 150)] for _ in range(5)]

BUILDING_UNIT_WIDTH = 110
NUM_BUILDINGS = 12
building_scroll = 0.0
random.seed(7)
BUILDING_HEIGHTS = [random.randint(90, 220) for _ in range(NUM_BUILDINGS)]
random.seed()

LEADERBOARD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaderboard.txt")


def load_leaderboard():
    scores = []
    try:
        with open(LEADERBOARD_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if line.isdigit():
                    scores.append(int(line))
    except FileNotFoundError:
        pass
    return sorted(scores, reverse=True)[:5]


def save_leaderboard(scores):
    try:
        with open(LEADERBOARD_PATH, "w") as f:
            for s in scores:
                f.write(f"{s}\n")
    except OSError:
        pass


def record_score(new_score):
    global leaderboard
    leaderboard.append(new_score)
    leaderboard = sorted(leaderboard, reverse=True)[:5]
    save_leaderboard(leaderboard)


leaderboard = load_leaderboard()


# ============================================================
# BACKGROUND
# ============================================================

def draw_sky_and_skyline(speed):
    global building_scroll

    for y in range(0, HORIZON_Y + 40):
        t = y / (HORIZON_Y + 40)
        r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    pygame.draw.circle(screen, SUN, (WIDTH - 120, 80), 40)

    for s in stars:
        pygame.draw.circle(screen, WHITE, s, 1)

    for c in clouds:
        pygame.draw.ellipse(screen, (250, 250, 250), (c[0], c[1], 100, 40))
        pygame.draw.ellipse(screen, (250, 250, 250), (c[0] + 18, c[1] - 8, 60, 32))
        c[0] -= 0.6
        if c[0] < -120:
            c[0] = WIDTH + random.randint(40, 240)
            c[1] = random.randint(20, 140)

    building_scroll += speed * 0.9
    offset = building_scroll % BUILDING_UNIT_WIDTH

    for i in range(-1, NUM_BUILDINGS + 1):
        x = i * BUILDING_UNIT_WIDTH - offset
        h = BUILDING_HEIGHTS[i % NUM_BUILDINGS]
        base_y = HORIZON_Y + 10
        pygame.draw.rect(screen, BUILDING, (x, base_y - h, 82, h))
        for row in range(int(h // 26)):
            for col in range(3):
                wx = x + 12 + col * 22
                wy = base_y - h + 10 + row * 26
                pygame.draw.rect(screen, WINDOW, (wx, wy, 9, 13))


def draw_road():
    # ground strip below horizon, before road trapezoid, blend colour
    pygame.draw.rect(screen, (80, 150, 80), (0, HORIZON_Y, WIDTH, GROUND_Y - HORIZON_Y + 60))

    far_left = persp_x(-1.6, 1.0)
    far_right = persp_x(1.6, 1.0)
    near_left = persp_x(-1.6, 0.0)
    near_right = persp_x(1.6, 0.0)

    pygame.draw.polygon(
        screen, ROAD_DARK,
        [(far_left, persp_y(1.0)), (far_right, persp_y(1.0)),
         (near_right, persp_y(0.0)), (near_left, persp_y(0.0))]
    )

    # lane divider dashes (between lane -1/0 and 0/1)
    for boundary in (-0.5, 0.5):
        d = dash_scroll % 0.08
        while d < 1.0:
            x = persp_x(boundary, d)
            y = persp_y(d)
            w = max(2, int(6 * persp_scale(d)))
            h = max(6, int(26 * persp_scale(d)))
            pygame.draw.rect(screen, ROAD_LIGHT, (x - w / 2, y, w, h))
            d += 0.08

    # curb edges
    pygame.draw.line(screen, CURB, (far_left, persp_y(1.0)), (near_left, persp_y(0.0)), 4)
    pygame.draw.line(screen, CURB, (far_right, persp_y(1.0)), (near_right, persp_y(0.0)), 4)


# ============================================================
# OBSTACLES / COINS / POWER-UPS
# ============================================================

GOOD_KINDS = ["medical", "food", "candy"]
BAD_KINDS = ["drugs", "alcohol"]


def spawn_wave():
    global frames_since_full_block

    full_block_ready = frames_since_full_block >= FULL_BLOCK_COOLDOWN

    if full_block_ready:
        pattern = random.choice(["one_train", "two_train", "low_all", "high_all", "coin_lane"])
    else:
        # a lane-blocking wave is still in flight -- keep it simple so we never
        # stack two "avoid every lane" walls on top of each other
        pattern = random.choice(["coin_lane", "coin_lane", "one_train"])

    if pattern in ("two_train", "low_all", "high_all"):
        frames_since_full_block = 0

    if pattern == "one_train":
        lane = random.randint(0, 2)
        obstacles.append({"lane": lane, "d": 1.0, "type": "train", "resolved": False})
        for l in range(3):
            if l != lane:
                spawn_coin_line(l)

    elif pattern == "two_train":
        open_lane = random.randint(0, 2)
        for l in range(3):
            if l != open_lane:
                obstacles.append({"lane": l, "d": 1.0, "type": "train", "resolved": False})
        spawn_coin_line(open_lane)

    elif pattern == "low_all":
        for l in range(3):
            obstacles.append({"lane": l, "d": 1.0, "type": "low", "resolved": False})
        for l in range(3):
            coins.append({"lane": l, "d": 1.0, "collected": False, "high": True, "kind": random.choice(GOOD_KINDS)})

    elif pattern == "high_all":
        for l in range(3):
            obstacles.append({"lane": l, "d": 1.0, "type": "high", "resolved": False})

    elif pattern == "coin_lane":
        lane = random.randint(0, 2)
        spawn_coin_line(lane)

    # occasionally sprinkle a line of bad items (drugs/alcohol) into a lane that
    # isn't already blocked by a train -- the player has to dodge sideways to avoid it
    if random.random() < 0.3:
        free_lanes = [l for l in range(3) if not any(
            o["lane"] == l and o["type"] == "train" and o["d"] > 0.5 for o in obstacles)]
        if free_lanes:
            spawn_bad_line(random.choice(free_lanes))

    if random.random() < 0.12:
        lane = random.randint(0, 2)
        kind = random.choice(["magnet", "mult", "shield"])
        powerups.append({"lane": lane, "d": 1.0, "kind": kind, "taken": False})


def spawn_coin_line(lane):
    kind = random.choice(GOOD_KINDS)
    for i in range(6):
        coins.append({"lane": lane, "d": 1.0 + i * 0.035, "collected": False, "high": False, "kind": kind})


def spawn_bad_line(lane):
    kind = random.choice(BAD_KINDS)
    for i in range(4):
        bad_items.append({"lane": lane, "d": 1.05 + i * 0.045, "resolved": False, "kind": kind})


def draw_train(x, y, scale):
    w, h = 150 * scale, 190 * scale
    rect = pygame.Rect(x - w / 2, y - h, w, h)
    pygame.draw.rect(screen, TRAIN_BODY, rect, border_radius=int(10 * scale))
    stripe_h = max(2, int(10 * scale))
    pygame.draw.rect(screen, TRAIN_STRIPE, (rect.x, rect.y + h * 0.55, w, stripe_h))
    win_w = w * 0.22
    for i in range(3):
        wx = rect.x + w * 0.12 + i * (w * 0.3)
        pygame.draw.rect(screen, (150, 220, 255), (wx, rect.y + h * 0.18, win_w, h * 0.22), border_radius=int(3 * scale))


def draw_low_barrier(x, y, scale):
    w, h = 130 * scale, 46 * scale
    rect = pygame.Rect(x - w / 2, y - h, w, h)
    stripes = 6
    sw = w / stripes
    for i in range(stripes):
        col = BARRIER_YELLOW if i % 2 == 0 else BARRIER_BLACK
        pygame.draw.rect(screen, col, (rect.x + i * sw, rect.y, sw, h))
    pygame.draw.rect(screen, BLACK, rect, max(1, int(2 * scale)), border_radius=2)


def draw_high_barrier(x, y, scale):
    w = 150 * scale
    bar_h = 26 * scale
    bar_y = y - 170 * scale
    post_w = 10 * scale
    pygame.draw.rect(screen, GREY, (x - w / 2, bar_y, post_w, 170 * scale - bar_h))
    pygame.draw.rect(screen, GREY, (x + w / 2 - post_w, bar_y, post_w, 170 * scale - bar_h))
    stripes = 6
    sw = w / stripes
    for i in range(stripes):
        col = BARRIER_YELLOW if i % 2 == 0 else BARRIER_BLACK
        pygame.draw.rect(screen, col, (x - w / 2 + i * sw, bar_y, sw, bar_h))


def draw_good_icon(cx, cy, r, kind):
    cx, cy = int(cx), int(cy)

    if kind == "medical":
        s = r * 1.6
        rect = pygame.Rect(cx - s / 2, cy - s / 2, s, s)
        pygame.draw.rect(screen, WHITE, rect, border_radius=max(1, int(s * 0.2)))
        pygame.draw.rect(screen, MEDICAL_RED, rect, max(1, int(s * 0.12)), border_radius=max(1, int(s * 0.2)))
        bar_w = s * 0.55
        bar_h = s * 0.16
        pygame.draw.rect(screen, MEDICAL_RED, (cx - bar_w / 2, cy - bar_h / 2, bar_w, bar_h))
        pygame.draw.rect(screen, MEDICAL_RED, (cx - bar_h / 2, cy - bar_w / 2, bar_h, bar_w))

    elif kind == "food":
        pygame.draw.circle(screen, FOOD_RED, (cx, cy + int(r * 0.1)), r)
        pygame.draw.circle(screen, (255, 180, 180), (cx - int(r * 0.35), cy - int(r * 0.25)), max(1, int(r * 0.3)))
        pygame.draw.line(screen, (110, 70, 40), (cx, cy - r), (cx + int(r * 0.15), cy - int(r * 1.4)), max(1, int(r * 0.18)))
        leaf_pts = [(cx + int(r * 0.15), cy - int(r * 1.2)), (cx + int(r * 0.8), cy - int(r * 1.3)), (cx + int(r * 0.3), cy - int(r * 0.85))]
        pygame.draw.polygon(screen, FOOD_LEAF, leaf_pts)

    else:  # candy
        pygame.draw.circle(screen, CANDY_PINK, (cx, cy), r)
        for ang in (0, 60, 120):
            rad = math.radians(ang)
            x1 = cx - math.cos(rad) * r
            y1 = cy - math.sin(rad) * r
            x2 = cx + math.cos(rad) * r
            y2 = cy + math.sin(rad) * r
            pygame.draw.line(screen, CANDY_STRIPE, (x1, y1), (x2, y2), max(1, int(r * 0.28)))
        pts_l = [(cx - r, cy), (cx - r * 1.8, cy - r * 0.6), (cx - r * 1.8, cy + r * 0.6)]
        pts_r = [(cx + r, cy), (cx + r * 1.8, cy - r * 0.6), (cx + r * 1.8, cy + r * 0.6)]
        pygame.draw.polygon(screen, CANDY_PINK, pts_l)
        pygame.draw.polygon(screen, CANDY_PINK, pts_r)


def draw_good_item(x, y, scale, kind, high):
    yy = y - (95 if high else 22) * scale
    r = max(3, int(15 * scale))
    draw_good_icon(x, yy, r, kind)


def draw_bad_icon(cx, cy, r, kind, show_x=True):
    cx, cy = int(cx), int(cy)

    if kind == "drugs":
        w, h = r * 1.9, r * 0.9
        rect = pygame.Rect(cx - w / 2, cy - h / 2, w, h)
        pygame.draw.rect(screen, PILL_WHITE, rect, border_radius=max(1, int(h * 0.5)))
        half = pygame.Rect(cx, cy - h / 2, w / 2, h)
        pygame.draw.rect(screen, PILL_RED, half, border_radius=max(1, int(h * 0.5)))
        pygame.draw.rect(screen, BLACK, rect, max(1, int(h * 0.12)), border_radius=max(1, int(h * 0.5)))

    else:  # alcohol
        body_w, body_h = r * 1.1, r * 1.6
        neck_w, neck_h = r * 0.5, r * 0.8
        body = pygame.Rect(cx - body_w / 2, cy - body_h / 2 + neck_h * 0.3, body_w, body_h)
        neck = pygame.Rect(cx - neck_w / 2, cy - body_h / 2 - neck_h + neck_h * 0.3, neck_w, neck_h)
        pygame.draw.rect(screen, BOTTLE_GLASS, body, border_radius=max(1, int(r * 0.25)))
        pygame.draw.rect(screen, BOTTLE_GLASS, neck)
        label = pygame.Rect(body.x + body_w * 0.12, body.y + body_h * 0.25, body_w * 0.76, body_h * 0.4)
        pygame.draw.rect(screen, BOTTLE_LABEL, label)

    if show_x:
        # small warning cross to make "avoid me" unmistakable during fast gameplay
        pygame.draw.line(screen, BLACK, (cx - r * 1.1, cy - r * 1.1), (cx + r * 1.1, cy + r * 1.1), max(1, int(r * 0.22)))
        pygame.draw.line(screen, BLACK, (cx - r * 1.1, cy + r * 1.1), (cx + r * 1.1, cy - r * 1.1), max(1, int(r * 0.22)))


def draw_bad_item(x, y, scale, kind):
    yy = y - 22 * scale
    r = max(3, int(15 * scale))
    draw_bad_icon(x, yy, r, kind)


def draw_top_legend():
    panel_w = 560
    panel_h = 60
    panel_x = WIDTH / 2 - panel_w / 2
    panel_y = 70

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 0, 0, 140), (0, 0, panel_w, panel_h), border_radius=14)
    screen.blit(panel, (panel_x, panel_y))

    icon_r = 15
    row1_y = panel_y + 18
    row2_y = panel_y + 44

    avoid_label = tiny_font.render("AVOID:", True, POLICE_RED)
    screen.blit(avoid_label, (panel_x + 12, row1_y - 10))
    draw_bad_icon(panel_x + 96, row1_y, icon_r, "drugs", show_x=False)
    drug_lbl = tiny_font.render("Drugs", True, WHITE)
    screen.blit(drug_lbl, (panel_x + 112, row1_y - 9))
    draw_bad_icon(panel_x + 190, row1_y, icon_r, "alcohol", show_x=False)
    alc_lbl = tiny_font.render("Alcohol", True, WHITE)
    screen.blit(alc_lbl, (panel_x + 206, row1_y - 9))

    grab_label = tiny_font.render("GRAB:", True, FOOD_LEAF)
    screen.blit(grab_label, (panel_x + 12, row2_y - 10))
    draw_good_icon(panel_x + 92, row2_y, icon_r, "medical")
    med_lbl = tiny_font.render("Medical", True, WHITE)
    screen.blit(med_lbl, (panel_x + 108, row2_y - 9))
    draw_good_icon(panel_x + 190, row2_y, icon_r, "food")
    food_lbl = tiny_font.render("Food", True, WHITE)
    screen.blit(food_lbl, (panel_x + 206, row2_y - 9))
    draw_good_icon(panel_x + 262, row2_y, icon_r, "candy")
    candy_lbl = tiny_font.render("Candy", True, WHITE)
    screen.blit(candy_lbl, (panel_x + 280, row2_y - 9))

    sep_x = panel_x + 340
    pygame.draw.line(screen, (255, 255, 255, 80), (sep_x, panel_y + 8), (sep_x, panel_y + panel_h - 8), 1)

    tip = tiny_font.render("Grab good items for points.", True, WHITE)
    tip2 = tiny_font.render("A bad item ends your run!", True, WHITE)
    screen.blit(tip, (sep_x + 12, row1_y - 10))
    screen.blit(tip2, (sep_x + 12, row2_y - 10))


def draw_powerup(x, y, scale, kind):
    yy = y - 40 * scale
    r = max(6, int(20 * scale))
    colors = {"magnet": MAGNET_PURPLE, "mult": MULT_ORANGE, "shield": SHIELD_CYAN}
    labels = {"magnet": "M", "mult": "x2", "shield": "S"}
    pygame.draw.circle(screen, colors[kind], (int(x), int(yy)), r)
    pygame.draw.circle(screen, WHITE, (int(x), int(yy)), r, max(1, int(r * 0.15)))
    if scale > 0.35:
        lbl = tiny_font.render(labels[kind], True, WHITE)
        screen.blit(lbl, (x - lbl.get_width() / 2, yy - lbl.get_height() / 2))


# ============================================================
# PLAYER
# ============================================================

def draw_player():
    x = persp_x(player_visual_offset, PLAYER_D)
    base_y = persp_y(PLAYER_D)
    scale = persp_scale(PLAYER_D)

    jump_offset = 0
    if jumping:
        jump_offset = JUMP_HEIGHT * math.sin(math.pi * (jump_t / JUMP_DURATION)) * scale

    body_h = 130 * scale
    body_w = 66 * scale
    if sliding:
        body_h *= 0.5

    y = base_y - jump_offset

    shirt_color = SHIRT_BLUE
    if shield_timer > 0:
        shirt_color = SHIRT_SHIELD
    elif mult_timer > 0:
        shirt_color = SHIRT_BOOST

    # shadow on ground (fades a bit when jumping)
    shadow_alpha_w = body_w * (0.9 if not jumping else 0.6)
    pygame.draw.ellipse(screen, (30, 60, 30), (x - shadow_alpha_w / 2, base_y - 6 * scale, shadow_alpha_w, 12 * scale))

    if shield_timer > 0:
        pygame.draw.circle(screen, SHIELD_CYAN, (int(x), int(y - body_h * 0.55)), int(body_w * 0.95), max(1, int(3 * scale)))

    # legs (running animation, skip while jumping/sliding for a cleaner pose)
    leg_w = 16 * scale
    leg_h = (46 if not sliding else 20) * scale
    swing = math.sin(run_cycle) * (14 * scale) if (not jumping and not sliding) else 0
    pygame.draw.rect(screen, PANTS, (x - body_w / 2 + 6 * scale, y - leg_h + swing, leg_w, leg_h), border_radius=int(4 * scale))
    pygame.draw.rect(screen, PANTS, (x + body_w / 2 - 6 * scale - leg_w, y - leg_h - swing, leg_w, leg_h), border_radius=int(4 * scale))

    # torso
    torso_rect = pygame.Rect(x - body_w / 2, y - body_h, body_w, body_h - leg_h * 0.6)
    pygame.draw.rect(screen, shirt_color, torso_rect, border_radius=int(12 * scale))

    # head
    head_r = 20 * scale
    head_y = torso_rect.y - head_r * 0.6
    pygame.draw.circle(screen, SKIN, (int(x), int(head_y)), int(head_r))
    eye_dx = 7 * scale
    pygame.draw.circle(screen, WHITE, (int(x - eye_dx), int(head_y - 2 * scale)), max(1, int(4 * scale)))
    pygame.draw.circle(screen, WHITE, (int(x + eye_dx), int(head_y - 2 * scale)), max(1, int(4 * scale)))
    pygame.draw.circle(screen, BLACK, (int(x - eye_dx), int(head_y - 2 * scale)), max(1, int(2 * scale)))
    pygame.draw.circle(screen, BLACK, (int(x + eye_dx), int(head_y - 2 * scale)), max(1, int(2 * scale)))

    return x, y, body_w, body_h, scale


# ============================================================
# GAME RESET
# ============================================================

def reset_game():
    global score, coins_collected, game_over, lose_reason, score_recorded
    global player_lane, player_visual_offset, jumping, jump_t, sliding, slide_t
    global magnet_timer, mult_timer, shield_timer, distance_speed, dash_scroll
    global spawn_timer, next_spawn_in, frames_since_full_block

    score = 0
    coins_collected = 0
    game_over = False
    lose_reason = ""
    score_recorded = False

    player_lane = 1
    player_visual_offset = 0.0
    jumping = False
    jump_t = 0
    sliding = False
    slide_t = 0

    magnet_timer = 0
    mult_timer = 0
    shield_timer = 0
    distance_speed = MIN_DEPTH_SPEED
    dash_scroll = 0.0

    spawn_timer = 0
    next_spawn_in = random.randint(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)
    frames_since_full_block = 999  # let the very first wave be anything

    obstacles.clear()
    coins.clear()
    bad_items.clear()
    powerups.clear()


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    player_lane = max(0, player_lane - 1)
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    player_lane = min(2, player_lane + 1)
                if event.key in (pygame.K_UP, pygame.K_SPACE, pygame.K_w) and not jumping and not sliding:
                    jumping = True
                    jump_t = 0
                if event.key in (pygame.K_DOWN, pygame.K_s) and not sliding and not jumping:
                    sliding = True
                    slide_t = 0
            if event.key == pygame.K_r and game_over:
                reset_game()

    if not game_over:
        distance_speed = min(MAX_DEPTH_SPEED, MIN_DEPTH_SPEED + score / 2200000)

        draw_sky_and_skyline(6 + distance_speed * 900)
        draw_road()

        # --- lane lerp ---
        target_offset = LANE_OFFSETS[player_lane]
        player_visual_offset += (target_offset - player_visual_offset) * LANE_LERP_SPEED

        # --- jump / slide timers ---
        if jumping:
            jump_t += 1
            if jump_t >= JUMP_DURATION:
                jumping = False
                jump_t = 0
        if sliding:
            slide_t += 1
            if slide_t >= SLIDE_DURATION:
                sliding = False
                slide_t = 0

        run_cycle += 0.35 + distance_speed * 20

        # --- spawn ---
        spawn_timer += 1
        frames_since_full_block += 1
        if spawn_timer >= next_spawn_in:
            spawn_timer = 0
            next_spawn_in = random.randint(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)
            spawn_wave()

        dash_scroll -= distance_speed

        COLLIDE_D = 0.045

        # --- obstacles ---
        for obs in obstacles[:]:
            obs["d"] -= distance_speed
            if not obs["resolved"] and obs["d"] <= COLLIDE_D:
                obs["resolved"] = True
                if obs["lane"] == player_lane:
                    hit = False
                    if obs["type"] == "train":
                        hit = True
                    elif obs["type"] == "low":
                        hit = not jumping
                    elif obs["type"] == "high":
                        hit = not sliding

                    if hit:
                        if shield_timer > 0:
                            shield_timer = 0  # shield absorbs one hit
                        else:
                            game_over = True
                            lose_reason = "Hit by a train!" if obs["type"] == "train" else "You didn't dodge in time!"
            if obs["d"] < -0.15:
                obstacles.remove(obs)

        # --- good items (medical / food / candy) ---
        for coin in coins[:]:
            coin["d"] -= distance_speed
            magnet_active = magnet_timer > 0
            lane_match = coin["lane"] == player_lane or (magnet_active and abs(coin["lane"] - player_lane) <= 1)
            if not coin["collected"] and coin["d"] <= COLLIDE_D and lane_match:
                coin["collected"] = True
                coins_collected += 1
                score += 20 * (2 if mult_timer > 0 else 1)
            if coin["d"] < -0.15 or coin["collected"]:
                coins.remove(coin)

        # --- bad items (drugs / alcohol) ---
        for bad in bad_items[:]:
            bad["d"] -= distance_speed
            if not bad["resolved"] and bad["d"] <= COLLIDE_D:
                bad["resolved"] = True
                if bad["lane"] == player_lane:
                    if shield_timer > 0:
                        shield_timer = 0  # shield absorbs one hit
                    else:
                        game_over = True
                        lose_reason = "Drugs stopped your run!" if bad["kind"] == "drugs" else "Alcohol stopped your run!"
            if bad["d"] < -0.15:
                bad_items.remove(bad)

        # --- power-ups ---
        for pu in powerups[:]:
            pu["d"] -= distance_speed
            if not pu["taken"] and pu["d"] <= COLLIDE_D and pu["lane"] == player_lane:
                pu["taken"] = True
                if pu["kind"] == "magnet":
                    magnet_timer = MAGNET_DURATION
                elif pu["kind"] == "mult":
                    mult_timer = MULT_DURATION
                elif pu["kind"] == "shield":
                    shield_timer = SHIELD_DURATION
            if pu["d"] < -0.15 or pu["taken"]:
                powerups.remove(pu)

        if magnet_timer > 0:
            magnet_timer -= 1
        if mult_timer > 0:
            mult_timer -= 1
        if shield_timer > 0:
            shield_timer -= 1

        if game_over and not score_recorded:
            record_score(score)
            score_recorded = True

        if not game_over:
            # --- draw world objects, far to near ---
            drawables = []
            for obs in obstacles:
                drawables.append(("obs", obs))
            for coin in coins:
                drawables.append(("coin", coin))
            for bad in bad_items:
                drawables.append(("bad", bad))
            for pu in powerups:
                drawables.append(("pu", pu))
            drawables.sort(key=lambda t: -t[1]["d"])

            for kind, obj in drawables:
                d = max(0.0, min(1.0, obj["d"]))
                x = persp_x(LANE_OFFSETS[obj["lane"]], d)
                y = persp_y(d)
                scale = persp_scale(d)
                if kind == "obs":
                    if obj["type"] == "train":
                        draw_train(x, y, scale)
                    elif obj["type"] == "low":
                        draw_low_barrier(x, y, scale)
                    elif obj["type"] == "high":
                        draw_high_barrier(x, y, scale)
                elif kind == "coin":
                    draw_good_item(x, y, scale, obj["kind"], obj["high"])
                elif kind == "bad":
                    draw_bad_item(x, y, scale, obj["kind"])
                elif kind == "pu":
                    draw_powerup(x, y, scale, obj["kind"])

            draw_player()

            score += 1 + (1 if mult_timer > 0 else 0)

            # --- HUD ---
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (20, 16))
            coin_text = small_font.render(f"Good items: {coins_collected}", True, FOOD_LEAF)
            screen.blit(coin_text, (20, 62))
            draw_top_legend()

            badge_x = WIDTH - 40
            if magnet_timer > 0:
                t = small_font.render("MAGNET", True, MAGNET_PURPLE)
                screen.blit(t, (badge_x - t.get_width(), 16))
                badge_x -= t.get_width() + 14
            if mult_timer > 0:
                t = small_font.render("x2 SCORE", True, MULT_ORANGE)
                screen.blit(t, (badge_x - t.get_width(), 16))
                badge_x -= t.get_width() + 14
            if shield_timer > 0:
                t = small_font.render("SHIELD", True, SHIELD_CYAN)
                screen.blit(t, (badge_x - t.get_width(), 16))

            controls = tiny_font.render("<- -> move   UP/SPACE jump   DOWN slide", True, WHITE)
            screen.blit(controls, (20, HEIGHT - 30))

    else:
        screen.fill(BLACK)

        over_text = big_font.render("GAME OVER", True, TRAIN_BODY)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 40))

        if lose_reason:
            reason_text = font.render(lose_reason, True, WHITE)
            screen.blit(reason_text, (WIDTH // 2 - reason_text.get_width() // 2, 115))

        score_text = font.render(f"Score: {score}   Coins: {coins_collected}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 165))

        lb_title = font.render("Leaderboard", True, WHITE)
        screen.blit(lb_title, (WIDTH // 2 - lb_title.get_width() // 2, 220))

        for i, entry in enumerate(leaderboard):
            entry_text = small_font.render(f"{i + 1}. {entry}", True, WHITE)
            screen.blit(entry_text, (WIDTH // 2 - entry_text.get_width() // 2, 270 + i * 30))

        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 460))

    pygame.display.flip()

pygame.quit()