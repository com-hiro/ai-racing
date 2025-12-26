import pygame
import sys
import ai_pilot_cv as ai_pilot  # 最新のOpenCV+Q学習ファイルを指定

"""
AI Driving Research Center - Launcher Menu
このプログラムは、AI走行シミュレーションのランチャー（起動メニュー）です。
ユーザーにミッションの概要を提示し、メインのAI学習プログラムを安全に呼び出す役割を持ちます。
"""

# --- 設定 ---
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 650
WHITE, BLACK, GRAY = (255, 255, 255), (20, 20, 20), (100, 100, 100)
BLUE, GREEN = (50, 120, 255), (46, 204, 113)

def main_menu():
    """
    メインメニュー画面を表示し、ユーザーの入力を待ち受けます。
    STARTボタンが押されると、AIパイロットプログラム（学習走行）を起動します。
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("AI Driving Research Center")
    
    # 日本語表示にも対応できるよう、一般的なフォントを指定（環境に合わせてフォントサイズを拡大）
    font_title = pygame.font.SysFont("hiraginosans", 60, bold=True)
    font_btn = pygame.font.SysFont("hiraginosans", 32)
    font_desc = pygame.font.SysFont("hiraginosans", 24)

    while True:
        screen.fill(BLACK)
        
        # --- タイトル表示 ---
        title_surf = font_title.render("AI AUTONOMOUS LAB", True, WHITE)
        screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 100))
        
        # --- ミッション説明文の描画 ---
        desc_text = [
            "• Computer Vision (OpenCV) Lane Detection",
            "• Q-Learning Autonomous Driving Policy",
            "• 8-Lap Training Mission Simulator"
        ]        

        for i, text in enumerate(desc_text):
            d_surf = font_desc.render(text, True, GRAY)
            screen.blit(d_surf, (SCREEN_WIDTH//2 - 200, 220 + i*40))

        # --- スタートボタンの描画とホバー判定 ---
        mouse_pos = pygame.mouse.get_pos()
        btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 420, 300, 80)
        
        # マウスがボタン上にあるか（ホバー）で色を変化させる
        btn_color = GREEN if btn_rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=15)
        
        btn_text = font_btn.render("START MISSION", True, WHITE)
        screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2, btn_rect.centery - btn_text.get_height()//2))

        # --- イベント処理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(mouse_pos):
                    # 【重要】AIパイロット（学習プログラム）の起動
                    # 外部ファイル ai_pilot_cv.py の start_pilot() 関数を呼び出します
                    ai_pilot.start_pilot()
                    
                    # AIパイロット終了後、メニュー画面の解像度を再設定して戻る
                    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.flip()

if __name__ == "__main__":
    # このスクリプトが直接実行された場合にメニューを起動します
    main_menu()