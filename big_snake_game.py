import pygame as pg
from random import randrange
import math
from sprites import (
    ascii_head,
    ascii_body,
    ascii_tail,
    ascii_corner,
    ascii_apple,
    ascii_car,
)


# --- Basic constants ---
WINDOWS = 600
TILE_SIZE = 20
CAR_SIZE = TILE_SIZE * 7

# --- Pygame initialization ---
pg.init()
screen = pg.display.set_mode([WINDOWS]*2)
clock = pg.time.Clock()
pg.display.set_caption("ASCII Snake - Rotated Corners")
font_size = 9
font = pg.font.SysFont("Courier New", font_size)
line_height = 0.2
hud_font = pg.font.SysFont("Consolas", 18)

# --- Render ASCII into a tile ---
def render_ascii(ascii_text, color):
    lines = ascii_text.strip().splitlines()
    surfaces = [font.render(line, True, color) for line in lines]
    width = max(s.get_width() for s in surfaces)
    height = len(surfaces) * int(font_size*line_height)
    surf = pg.Surface((width, height), pg.SRCALPHA)
    surf.fill((0,0,0,0))
    for i, s in enumerate(surfaces):
        surf.blit(s, (0, i*int(font_size*line_height)))
    return pg.transform.smoothscale(surf, (TILE_SIZE, TILE_SIZE))

# --- Random position ---
def get_random_position():
    x = randrange(0, WINDOWS, TILE_SIZE)
    y = randrange(0, WINDOWS, TILE_SIZE)
    return (x + TILE_SIZE//2, y + TILE_SIZE//2)

# --- Rendered sprites ---
head_sprite_up = render_ascii(ascii_head, pg.Color("white"))
head_sprite_down = pg.transform.rotate(head_sprite_up, 180)
head_sprite_left = pg.transform.rotate(head_sprite_up, 90)
head_sprite_right = pg.transform.rotate(head_sprite_up, -90)

body_sprite_up = render_ascii(ascii_body, pg.Color("white"))
body_sprite_down = pg.transform.rotate(body_sprite_up, 180)
body_sprite_left = pg.transform.rotate(body_sprite_up, 90)
body_sprite_right = pg.transform.rotate(body_sprite_up, -90)

tail_sprite_up = render_ascii(ascii_tail, pg.Color("white"))
tail_sprite_down = pg.transform.rotate(tail_sprite_up, 180)
tail_sprite_left = pg.transform.rotate(tail_sprite_up, 90)
tail_sprite_right = pg.transform.rotate(tail_sprite_up, -90)

corner_ur_sprite = render_ascii(ascii_corner, pg.Color("white"))
corner_ul_sprite = pg.transform.rotate(corner_ur_sprite, 90)
corner_dl_sprite = pg.transform.rotate(corner_ur_sprite, 180)
corner_dr_sprite = pg.transform.rotate(corner_ur_sprite, -90)

apple_sprite = render_ascii(ascii_apple, pg.Color("red"))
car_sprite = pg.transform.smoothscale(render_ascii(ascii_car, pg.Color("white")), (CAR_SIZE, CAR_SIZE))

# --- Snake initialization ---
snake = pg.Rect(0, 0, TILE_SIZE-2, TILE_SIZE-2)
snake.center = get_random_position()
snake_dir = (TILE_SIZE, 0)
length = 3
segments = [
    snake.copy().move(-2 * TILE_SIZE, 0),
    snake.copy().move(-1 * TILE_SIZE, 0),
    snake.copy(),
]
time, time_step = 0, 220
food = snake.copy()
food.center = get_random_position()

last_dir = snake_dir
start_time = pg.time.get_ticks()
score = 0
game_state = "start"
final_time = "00:00"
final_score = 0
freeze_end_time = 0
car_active = False
car_rect = pg.Rect(0, 0, CAR_SIZE, CAR_SIZE)
next_car_time = pg.time.get_ticks() + randrange(9000, 17001)

def reset_game():
    global snake, snake_dir, length, segments, food, last_dir, start_time, score
    global car_active, car_rect, next_car_time
    snake = pg.Rect(0, 0, TILE_SIZE-2, TILE_SIZE-2)
    snake.center = get_random_position()
    snake_dir = (TILE_SIZE, 0)
    length = 3
    segments = [
        snake.copy().move(-2 * TILE_SIZE, 0),
        snake.copy().move(-1 * TILE_SIZE, 0),
        snake.copy(),
    ]
    food = snake.copy()
    food.center = get_random_position()
    last_dir = snake_dir
    start_time = pg.time.get_ticks()
    score = 0
    car_active = False
    car_rect = pg.Rect(0, 0, CAR_SIZE, CAR_SIZE)
    next_car_time = pg.time.get_ticks() + randrange(9000, 17001)

def draw_scene():
    screen.fill("black")
    screen.blit(apple_sprite, (food.x, food.y))
    if car_active:
        screen.blit(car_sprite, car_rect.topleft)
    elapsed_seconds = (pg.time.get_ticks() - start_time) // 1000
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    timer_surface = hud_font.render(f"{minutes:02d}:{seconds:02d}", True, pg.Color("white"))
    screen.blit(timer_surface, (8, 8))
    score_surface = hud_font.render(f"Score: {score}", True, pg.Color("white"))
    screen.blit(score_surface, (screen.get_width() - score_surface.get_width() - 8, 8))

    for i, segment in enumerate(segments):
        if i == len(segments)-1:  # Head
            if snake_dir == (0, -TILE_SIZE):
                screen.blit(head_sprite_up, segment.topleft)
            elif snake_dir == (0, TILE_SIZE):
                screen.blit(head_sprite_down, segment.topleft)
            elif snake_dir == (-TILE_SIZE, 0):
                screen.blit(head_sprite_left, segment.topleft)
            elif snake_dir == (TILE_SIZE, 0):
                screen.blit(head_sprite_right, segment.topleft)
            else:
                screen.blit(head_sprite_up, segment.topleft)
        elif i == 0:  # Tail
            tail_dir = (segments[i+1].x - segment.x, segments[i+1].y - segment.y)
            if tail_dir == (0, -TILE_SIZE):
                screen.blit(tail_sprite_up, segment.topleft)
            elif tail_dir == (0, TILE_SIZE):
                screen.blit(tail_sprite_down, segment.topleft)
            elif tail_dir == (-TILE_SIZE, 0):
                screen.blit(tail_sprite_left, segment.topleft)
            elif tail_dir == (TILE_SIZE, 0):
                screen.blit(tail_sprite_right, segment.topleft)
            else:
                screen.blit(tail_sprite_up, segment.topleft)
        else:  # Body and corners
            prev_seg = segments[i-1]
            next_seg = segments[i+1]

            dx_prev = segment.x - prev_seg.x
            dy_prev = segment.y - prev_seg.y
            dx_next = next_seg.x - segment.x
            dy_next = next_seg.y - segment.y

            # --- Horizontal ---
            if dy_prev == 0 and dy_next == 0:
                t = pg.time.get_ticks() / 200.0
                wave_offset = int(2 * math.sin(t + i*0.5))
                screen.blit(body_sprite_right, (segment.x, segment.y + wave_offset))
            # --- Vertical ---
            elif dx_prev == 0 and dx_next == 0:
                t = pg.time.get_ticks() / 200.0
                wave_offset = int(2 * math.sin(t + i*0.5))
                screen.blit(body_sprite_up, (segment.x + wave_offset, segment.y))
            # --- Corner pieces ---
            else:
                if (prev_seg.x < segment.x and next_seg.y < segment.y) or (next_seg.x < segment.x and prev_seg.y < segment.y):
                    screen.blit(corner_ul_sprite, segment.topleft)
                elif (prev_seg.x > segment.x and next_seg.y < segment.y) or (next_seg.x > segment.x and prev_seg.y < segment.y):
                    screen.blit(corner_ur_sprite, segment.topleft)
                elif (prev_seg.x < segment.x and next_seg.y > segment.y) or (next_seg.x < segment.x and prev_seg.y > segment.y):
                    screen.blit(corner_dl_sprite, segment.topleft)
                elif (prev_seg.x > segment.x and next_seg.y > segment.y) or (next_seg.x > segment.x and prev_seg.y > segment.y):
                    screen.blit(corner_dr_sprite, segment.topleft)

# --- Main loop ---
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN and game_state == "playing":
            if event.key in (pg.K_w, pg.K_UP) and snake_dir != (0, TILE_SIZE):
                snake_dir = (0, -TILE_SIZE)
                last_dir = snake_dir
            if event.key in (pg.K_s, pg.K_DOWN) and snake_dir != (0, -TILE_SIZE):
                snake_dir = (0, TILE_SIZE)
                last_dir = snake_dir
            if event.key in (pg.K_a, pg.K_LEFT) and snake_dir != (TILE_SIZE, 0):
                snake_dir = (-TILE_SIZE, 0)
                last_dir = snake_dir
            if event.key in (pg.K_d, pg.K_RIGHT) and snake_dir != (-TILE_SIZE, 0):
                snake_dir = (TILE_SIZE, 0)
                last_dir = snake_dir
        if event.type == pg.KEYDOWN and game_state == "start":
            if event.key == pg.K_SPACE:
                reset_game()
                game_state = "playing"
        if event.type == pg.KEYDOWN and game_state == "game_over":
            if event.key == pg.K_SPACE:
                reset_game()
                game_state = "playing"
            if event.key in (pg.K_ESCAPE, pg.K_q):
                running = False
        if event.type == pg.KEYDOWN and game_state == "freeze":
            if event.key in (pg.K_ESCAPE, pg.K_q):
                running = False

    if game_state == "start":
        screen.fill("black")
        title = hud_font.render("ASCII SNAKE", True, pg.Color("white"))
        line1 = hud_font.render("Use W/A/S/D or Arrow Keys to move", True, pg.Color("white"))
        line2 = hud_font.render("Eat apples to grow. Don't hit yourself.", True, pg.Color("white"))
        line3 = hud_font.render("Press SPACE to start", True, pg.Color("white"))
        center_x = screen.get_width() // 2
        screen.blit(title, (center_x - title.get_width() // 2, 120))
        screen.blit(line1, (center_x - line1.get_width() // 2, 180))
        screen.blit(line2, (center_x - line2.get_width() // 2, 210))
        screen.blit(line3, (center_x - line3.get_width() // 2, 260))
        pg.display.flip()
        clock.tick(60)
        continue

    if game_state == "game_over":
        screen.fill("black")
        center_x = screen.get_width() // 2
        over_title = pg.font.SysFont("Consolas", 36).render("GAME OVER", True, pg.Color("white"))
        time_line = hud_font.render(f"Time: {final_time}", True, pg.Color("white"))
        score_line = hud_font.render(f"Score: {final_score}", True, pg.Color("white"))
        msg_line = hud_font.render("Good luck in your next game!", True, pg.Color("white"))
        prompt_line = hud_font.render("Press SPACE to play again or ESC to exit", True, pg.Color("white"))
        screen.blit(over_title, (center_x - over_title.get_width() // 2, 110))
        screen.blit(time_line, (center_x - time_line.get_width() // 2, 170))
        screen.blit(score_line, (center_x - score_line.get_width() // 2, 200))
        screen.blit(msg_line, (center_x - msg_line.get_width() // 2, 235))
        screen.blit(prompt_line, (center_x - prompt_line.get_width() // 2, 270))
        pg.display.flip()
        clock.tick(60)
        continue

    if game_state == "freeze":
        if pg.time.get_ticks() >= freeze_end_time:
            game_state = "game_over"
            continue
        draw_scene()
        overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
        overlay.fill((200, 0, 0, 80))
        screen.blit(overlay, (0, 0))
        crash_text = pg.font.SysFont("Consolas", 28).render("CRASH!", True, pg.Color("white"))
        screen.blit(crash_text, (screen.get_width() // 2 - crash_text.get_width() // 2, 60))
        pg.display.flip()
        clock.tick(60)
        continue

    # --- Move the snake ---
    time_now = pg.time.get_ticks()
    if time_now - time > time_step:
        time = time_now
        snake.move_ip(snake_dir)
        if snake.centerx < TILE_SIZE // 2:
            snake.centerx = WINDOWS - TILE_SIZE // 2
        elif snake.centerx > WINDOWS - TILE_SIZE // 2:
            snake.centerx = TILE_SIZE // 2
        if snake.centery < TILE_SIZE // 2:
            snake.centery = WINDOWS - TILE_SIZE // 2
        elif snake.centery > WINDOWS - TILE_SIZE // 2:
            snake.centery = TILE_SIZE // 2
        segments.append(snake.copy())
        segments = segments[-length:]

        if car_active:
            car_rect.move_ip(0, TILE_SIZE)
            if car_rect.top >= WINDOWS:
                car_active = False
                next_car_time = pg.time.get_ticks() + randrange(9000, 17001)

    if not car_active and pg.time.get_ticks() >= next_car_time:
        car_active = True
        car_rect = pg.Rect(0, 0, CAR_SIZE, CAR_SIZE)
        car_x = randrange(CAR_SIZE // 2, WINDOWS - CAR_SIZE // 2 + TILE_SIZE, TILE_SIZE)
        car_rect.center = (car_x, -CAR_SIZE // 2)

    # --- Collisions ---
    self_eating = pg.Rect.collidelist(snake, segments[:-1]) != -1
    car_hit = car_active and car_rect.collidelist(segments) != -1
    if self_eating or car_hit:
        elapsed_seconds = (pg.time.get_ticks() - start_time) // 1000
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        final_time = f"{minutes:02d}:{seconds:02d}"
        final_score = score
        freeze_end_time = pg.time.get_ticks() + 1200
        game_state = "freeze"
        continue

    # --- Eat food ---
    if snake.center == food.center:
        food.center = get_random_position()
        length += 1
        score += 1

    # --- Drawing ---
    draw_scene()

    pg.display.flip()
    clock.tick(60)

pg.quit()

