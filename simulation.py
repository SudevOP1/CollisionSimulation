import pygame as py
import csv
from settings import *

paused = PAUSED_AT_START
edge_l = WALL_BORDER_PADDING + WALL_WIDTH
edge_r = WINDOW_WIDTH - WALL_BORDER_PADDING - WALL_WIDTH
l_wall_rect = py.Rect(edge_l - WALL_WIDTH, INITIAL_CENTER_Y - WALL_HEIGHT // 2, WALL_WIDTH, WALL_HEIGHT)
r_wall_rect = py.Rect(edge_r, INITIAL_CENTER_Y - WALL_HEIGHT // 2, WALL_WIDTH, WALL_HEIGHT)
collision_count = 0
elapsed_time = 0

# swap if needed
if (LARGE_MASS_ON_RIGHT and M2 < M1) or ((not LARGE_MASS_ON_RIGHT) and M1 > M2):
    M1, M2 = M2, M1
    V1, V2 = V2, V1
left_m_side_len  = SMALL_M_SIDE_LEN if LARGE_MASS_ON_RIGHT else LARGE_M_SIDE_LEN
right_m_side_len = LARGE_M_SIDE_LEN if LARGE_MASS_ON_RIGHT else SMALL_M_SIDE_LEN

objs = [{
        "m": M1,
        "v": abs(V1),
        "side_len": left_m_side_len,
        "color": M1_COLOR,
        "rect": py.Rect(
            edge_l,
            INITIAL_CENTER_Y - left_m_side_len // 2,
            left_m_side_len,
            left_m_side_len,
        ),
    }, {
        "m": M2,
        "v": -abs(V2),
        "side_len": right_m_side_len,
        "color": M2_COLOR,
        "rect": py.Rect(
            edge_r - right_m_side_len,
            INITIAL_CENTER_Y - right_m_side_len // 2,
            right_m_side_len,
            right_m_side_len,
        ),
    }
]

with open(f"{LOGS_FILENAME}.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["v1", "v2", "t", "m1", "m2"])
    writer.writerow([V1, V2, 0, M1, M2])

    py.init()
    window = py.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = py.time.Clock()
    running = True
    dt = 0
    py.font.init()
    py.mixer.init()
    font = py.font.SysFont(FONT, FONT_SIZE)
    collision_sound = py.mixer.Sound(COLLISION_SOUND_FILENAME)

    def get_seconds_passed():
        global elapsed_time
        return round(elapsed_time, ROUND_DIGITS)

    def play_collision_sound():
        if PLAY_COLLISION_SOUND: collision_sound.play()

    def update_stuff():
        global objs, collision_count

        for obj in objs:
            
            # update positions
            obj["rect"].centerx += obj["v"] * dt
            
            # check edges
            if obj["rect"].left < edge_l:
                obj["rect"].left = edge_l
                obj["v"] *= -1
                play_collision_sound()
            elif obj["rect"].right > edge_r:
                obj["rect"].right = edge_r
                obj["v"] *= -1
                play_collision_sound()

        # objs collision
        if objs[0]["rect"].right >= objs[1]["rect"].left:
            collision_count += 1
            play_collision_sound()
            
            # move objects away
            diff = abs(objs[0]["rect"].right - objs[1]["rect"].left)
            objs[0]["rect"].centerx -= diff // 2
            objs[1]["rect"].centerx += diff // 2

            # calculate new vels
            m1 = objs[0]["m"]
            m2 = objs[1]["m"]
            v1 = objs[0]["v"]
            v2 = objs[1]["v"]
            m_sum = m1 + m2
            new_v1 = (v1*(m1-m2) + 2*m2*v2) / m_sum
            new_v2 = (v2*(m2-m1) + 2*m1*v1) / m_sum
            new_v1 = round(new_v1, ROUND_DIGITS)
            new_v2 = round(new_v2, ROUND_DIGITS)

            # set vels
            objs[0]["v"] = new_v1
            objs[1]["v"] = new_v2

            # log new velocities
            time = get_seconds_passed()
            writer.writerow([new_v1, new_v2, time])

    def draw_stuff():
        
        # bg
        window.fill(BG_COLOR)
        
        # walls
        py.draw.rect(window, WALL_COLOR, l_wall_rect)
        py.draw.rect(window, WALL_COLOR, r_wall_rect)
        
        # objs
        for obj in objs:
            py.draw.rect(window, obj["color"], obj["rect"])
        
        # text
        text_surfs = [
            font.render(f"m1 = {objs[0]["m"]}", True, objs[0]["color"]),
            font.render(f"v1 = {objs[0]["v"]}", True, objs[0]["color"]),
            font.render(f"m2 = {objs[1]["m"]}", True, objs[1]["color"]),
            font.render(f"v2 = {objs[1]["v"]}", True, objs[1]["color"]),
            font.render(f"Collisions = {collision_count}", True, WALL_COLOR),
            font.render(f"Time = {int(get_seconds_passed())} s", True, WALL_COLOR),
        ]
        text_rects = [
            (FONT_XPAD, FONT_YPAD),
            (FONT_XPAD, 2 * FONT_YPAD + text_surfs[0].get_height()),
            (WINDOW_WIDTH - FONT_XPAD - text_surfs[2].get_width(), FONT_YPAD),
            (WINDOW_WIDTH - FONT_XPAD - text_surfs[3].get_width(), 2 * FONT_YPAD + text_surfs[2].get_height()),
            (WINDOW_WIDTH // 2 - text_surfs[4].get_width() // 2, FONT_YPAD),
            (WINDOW_WIDTH // 2 - text_surfs[4].get_width() // 2, 2 * FONT_YPAD + text_surfs[4].get_height()),
        ]
        for surf, rect in zip(text_surfs, text_rects):
            window.blit(surf, rect)

    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                paused = not paused

        if not paused:
            update_stuff()
            elapsed_time += dt
        draw_stuff()

        py.display.flip()
        dt = clock.tick(60) / 1000 # limit fps to 60 with fps independent physics.

    py.quit()