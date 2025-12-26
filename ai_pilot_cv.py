import pygame
import cv2
import numpy as np
import math
import random
import json
import os
import time

"""Formula AI Ultimate - Q-Learning Racing Simulation.

このプログラムは、強化学習（Q学習）を用いてAIが自律走行するレースシミュレーションです。
AIは画面上の黄色い線を認識し、最適なハンドル操作を学習します。
"""

# --- 設定 ---
DATA_FILE = "formula_ai_ultimate_best.json"
WHITE, BLACK, ROAD_GRAY, YELLOW = (255, 255, 255), (15, 15, 15), (70, 70, 70), (255, 255, 0)
BRIGHT_RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
CYAN = (0, 255, 255)
DARK_GRAY = (30, 30, 30)

def save_brain(data, best_total):
    """学習済みのQテーブルとベストタイムをJSONファイルに保存します。

    Args:
        data (dict): 保存するQテーブル。
        best_total (float): 記録されたベストタイム。
    """
    serializable_data = {str(k): v for k, v in data.items()}
    with open(DATA_FILE, "w") as f:
        json.dump({"brain": serializable_data, "best_total": best_total}, f)

def load_brain():
    """JSONファイルからQテーブルとベストタイムを読み込みます。

    Returns:
        tuple: (Qテーブル(dict), ベストタイム(float)) のタプル。
            ファイルがない場合は空の辞書と999.9を返します。
    """
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                raw_data = json.load(f)
                brain = {eval(k): v for k, v in raw_data["brain"].items()}
                return brain, raw_data.get("best_total", 999.9)
        except: pass
    return {}, 999.9

def draw_checker_line(surface, x, y, w, h):
    """スタート/ゴール地点にチェッカーフラッグ模様の線を描画します。

    Args:
        surface (pygame.Surface): 描画対象のサーフェス。
        x (int): 描画開始X座標。
        y (int): 描画開始Y座標。
        w (int): 線の幅。
        h (int): 線の高さ。
    """
    sq_size = 10
    for row in range(h // sq_size):
        for col in range(w // sq_size):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(surface, color, (x + col*sq_size, y + row*sq_size, sq_size, sq_size))

def draw_cool_car(surface, x, y, angle, color):
    """指定された座標と角度で、F1スタイルの自車を描画します。

    Args:
        surface (pygame.Surface): 描画対象のサーフェス。
        x (float): 車の中心X座標。
        y (float): 車の中心Y座標。
        angle (float): 車の回転角度（ラジアン）。
        color (tuple): 車体の色(RGB)。
    """
    car_width, car_length = 20, 36
    body_surf = pygame.Surface((car_length, car_width), pygame.SRCALPHA)
    pygame.draw.rect(body_surf, color, (0, 2, 8, 16), border_radius=2)
    pygame.draw.rect(body_surf, color, (5, 5, 26, 10), border_radius=4)
    pygame.draw.polygon(body_surf, color, [(30, 5), (36, 8), (36, 12), (30, 15)])
    tire_color = (10, 10, 10)
    pygame.draw.rect(body_surf, tire_color, (6, 0, 8, 4))
    pygame.draw.rect(body_surf, tire_color, (6, 16, 8, 4))
    pygame.draw.rect(body_surf, tire_color, (24, 0, 6, 4))
    pygame.draw.rect(body_surf, tire_color, (24, 16, 6, 4))
    pygame.draw.circle(body_surf, YELLOW, (18, 10), 3)
    rotated_car = pygame.transform.rotate(body_surf, math.degrees(-angle))
    surface.blit(rotated_car, (x - rotated_car.get_width()//2, y - rotated_car.get_height()//2))

def start_pilot():
    """メインループ：物理演算、Q学習、描画処理のすべてを管理します。"""
    pygame.init()
    WIDTH, HEIGHT = 1100, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    ai_canvas = pygame.Surface((WIDTH, 720)) 
    font = pygame.font.SysFont("Arial", 18, bold=True)
    big_font = pygame.font.SysFont("Arial", 100, bold=True)
    clock = pygame.time.Clock()
    
    L, R, track_width = 400, 130, 110
    center_x, center_y = 550, 360
    total_len = 2 * L + 2 * math.pi * R
    
    brain_data, best_total_time = load_brain()
    steer_acts = [(-3.0, -1.0), (-1.0, 0.1), (0.0, 0.5), (1.0, 0.1), (3.0, -1.0)]

    def get_pos(d, off):
        """コース距離とオフセットから画面座標を算出します。

        Args:
            d (float): 走行距離。
            off (float): コース中心からの左右オフセット。

        Returns:
            tuple: (x, y, angle) の座標情報。
        """
        td = d % total_len
        if td <= L/2: bx, by, ang = center_x + td, center_y + R, 0
        elif td <= L/2 + math.pi*R:
            a = (td - L/2) / R
            bx, by, ang = center_x + L/2 + R * math.sin(a), center_y + R * math.cos(a), -a
        elif td <= 1.5*L + math.pi*R: bx, by, ang = center_x + L/2 - (td - (L/2 + math.pi*R)), center_y - R, math.pi
        elif td <= 1.5*L + 2*math.pi*R:
            a = (td - (1.5*L + math.pi*R)) / R
            bx, by, ang = center_x - L/2 - R * math.sin(a), center_y - R * math.cos(a), math.pi - a
        else: bx, by, ang = center_x - L/2 + (td - (1.5*L + 2*math.pi*R)), center_y + R, 0
        return bx + math.cos(ang + math.pi/2) * off, by + math.sin(ang + math.pi/2) * off, ang

    def add_log(msg):
        """ログを端末（コンソール）に出力します。

        Args:
            msg (str): 出力するメッセージ。
        """
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] {msg}")

    def reset_race():
        """リセット時の初期状態を返します。

        Returns:
            tuple: 初期化された各変数のタプル。
        """
        now = time.time()
        return 0.0, 0.0, 0.0, 0, now, False, 3, None, None

    dist, offset, speed, lap, start_time, finished, countdown, last_state, last_action_idx = reset_race()
    goal_time = 0.0
    img_rgb = np.zeros((200, 200, 3), dtype=np.uint8)

    while True:
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: save_brain(brain_data, best_total_time); pygame.quit(); return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                save_brain(brain_data, best_total_time)
                dist, offset, speed, lap, start_time, finished, countdown, last_state, last_action_idx = reset_race()
                add_log("Race Reset.")

        # --- 1. コース描画 ---
        ai_canvas.fill(BLACK)
        pygame.draw.rect(ai_canvas, ROAD_GRAY, (center_x-L//2, center_y-R-track_width//2, L, 2*R+track_width))
        pygame.draw.circle(ai_canvas, ROAD_GRAY, (center_x-L//2, center_y), R+track_width//2)
        pygame.draw.circle(ai_canvas, ROAD_GRAY, (center_x+L//2, center_y), R+track_width//2)
        pygame.draw.rect(ai_canvas, BLACK, (center_x-L//2, center_y-R+track_width//2, L, 2*R-track_width))
        pygame.draw.circle(ai_canvas, BLACK, (center_x-L//2, center_y), R-track_width//2)
        pygame.draw.circle(ai_canvas, BLACK, (center_x+L//2, center_y), R-track_width//2)
        draw_checker_line(ai_canvas, center_x - 10, center_y + R - track_width//2, 20, track_width)
        pygame.draw.arc(ai_canvas, YELLOW, (center_x+L//2-R, center_y-R, 2*R, 2*R), -math.pi/2, math.pi/2, 5)
        pygame.draw.arc(ai_canvas, YELLOW, (center_x-L//2-R, center_y-R, 2*R, 2*R), math.pi/2, 3*math.pi/2, 5)
        pygame.draw.line(ai_canvas, YELLOW, (center_x-L//2, center_y-R), (center_x+L//2, center_y-R), 5)
        pygame.draw.line(ai_canvas, YELLOW, (center_x-L//2, center_y+R), (center_x+L//2, center_y+R), 5)

        cx, cy, ang = get_pos(dist, offset)

        # --- 2. 画像処理 ---
        rx, ry = max(0, min(WIDTH-200, int(cx-100))), max(0, min(720-200, int(cy-100)))
        sub = ai_canvas.subsurface((rx, ry, 200, 200))
        img_rgb = np.transpose(pygame.surfarray.array3d(sub), (1, 0, 2)).copy()
        
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([40, 255, 255]))
        M = cv2.moments(mask)
        err = (int(M["m10"] / M["m00"]) - 100) if M["m00"] > 0 else 0
        cv2.circle(img_rgb, (err+100, 100), 6, BRIGHT_RED, -1)

        # --- 3. 学習と物理演算 ---
        if countdown > 0:
            if current_time - start_time > 1.0:
                countdown -= 1; start_time = current_time
                if countdown == 0: add_log("GO!!")
        elif not finished:
            current_state = (round(err / 8),)
            reward = (100 - abs(err)) + (speed * 3.0) 
            if abs(offset) > 48: reward -= 2000
            
            if last_state is not None:
                if current_state not in brain_data: brain_data[current_state] = [0.0] * 5
                brain_data[last_state][last_action_idx] += 0.2 * (reward + 0.9 * max(brain_data[current_state]) - brain_data[last_state][last_action_idx])
            
            if current_state not in brain_data: brain_data[current_state] = [0.0] * 5
            action_idx = brain_data[current_state].index(max(brain_data[current_state])) if random.random() > 0.1 else random.randint(0, 4)
            
            steer_val, accel_val = steer_acts[action_idx]
            offset += steer_val * (speed * 0.02); speed = max(10.0, min(30.0, speed + accel_val)) * 0.995 
            prev_dist = dist; dist += speed * 0.5
            last_state, last_action_idx = current_state, action_idx

            if int(dist / total_len) > int(prev_dist / total_len):
                lap += 1
                if lap >= 8:
                    finished = True; goal_time = current_time - start_time
                    if goal_time < best_total_time: best_total_time = goal_time; add_log(f"NEW RECORD! {best_total_time:.2f}s")
                    add_log(f"GOAL!! Total: {goal_time:.2f}s"); save_brain(brain_data, best_total_time)
            if abs(offset) > 52:
                add_log("CRASH!"); dist, offset, speed, lap, start_time, finished, countdown, last_state, last_action_idx = reset_race()

        # --- 4. 最終描画 ---
        screen.fill(DARK_GRAY)
        screen.blit(ai_canvas, (0, 0))
        draw_cool_car(screen, int(cx), int(cy), ang, BRIGHT_RED)
        
        mon_surf = pygame.surfarray.make_surface(np.transpose(img_rgb, (1, 0, 2)))
        screen.blit(mon_surf, (890, 10))
        pygame.draw.rect(screen, WHITE, (890, 10, 200, 200), 2)
 
        # 表示速度の決定：カウントダウン中、またはゴール後は表示速度を0にする
        display_speed = 0 if (countdown > 0 or finished) else int(speed * 20)

        race_time = current_time - start_time if not finished and countdown == 0 else (goal_time if finished else 0)

        hud_texts = [
            f"LAP: {min(lap + 1, 8)} / 8", 
            f"TIME: {race_time:.2f} s", 
            f"BEST: {best_total_time:.2f} s" if best_total_time < 900 else "BEST: --.-- s", 
            f"SPEED: {display_speed} km/h"
        ]
        for i, t in enumerate(hud_texts): 
            screen.blit(font.render(t, True, WHITE), (20, 20 + i*25))

        if countdown > 0:
            txt = big_font.render(str(countdown), True, YELLOW); screen.blit(txt, (WIDTH//2 - 50, 310))
        if finished:
            txt = big_font.render("GOAL!!", True, GREEN); screen.blit(txt, (WIDTH//2 - 150, 310))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    start_pilot()