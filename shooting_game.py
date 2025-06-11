import pygame
import sys
import random

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 640, 480
TOTAL_WIDTH = WIDTH * 3  # 全体は3画面分
CLICK_AREA_HEIGHT = HEIGHT + 50  # 画面全体+αをクリックエリアに
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooting Game")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (150, 75, 0)

# キャラクター設定
class Character:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = 50
        self.y = 50
        self.vel_x = 2  # 右に移動する速度
        self.vel_y = 0
        self.gravity = 0.05  # さらに緩やかな落下
        self.jump_power = -2  # 上昇距離をさらに小さく
        self.color = RED

    def update(self):
        # 重力の適用
        self.vel_y += self.gravity
        
        # 位置の更新
        self.x += self.vel_x
        self.y += self.vel_y
        
        # 画面下に落ちたらゲームオーバー
        if self.y > HEIGHT:
            return "gameover"
        
        # 画面上に出たらゲームオーバー
        if self.y < 0:
            return "gameover"
        
        # ゴールに到達したらクリア
        if self.x > TOTAL_WIDTH - 50:
            return "clear"
            
        return "playing"
    
    def draw(self, screen, camera_x):
        # カメラ位置を考慮して描画
        pygame.draw.rect(screen, self.color, (self.x - camera_x, self.y, self.width, self.height))
    
    def jump(self):
        self.vel_y = self.jump_power
        # 弾が当たった時は必ず右向きに進行方向を戻す
        self.vel_x = 2
    
    def knockback(self):
        # 障害物に当たった時の軽いノックバック
        self.vel_x = -1  # 少し後ろに下がる
        self.vel_y = -0.5  # 少し上に浮く

# 障害物クラス
class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = BROWN
    
    def draw(self, screen, camera_x):
        # カメラ位置を考慮して描画
        pygame.draw.rect(screen, self.color, (self.x - camera_x, self.y, self.width, self.height))
    
    def check_collision(self, character):
        # キャラクターとの衝突判定
        if (self.x < character.x + character.width and
            self.x + self.width > character.x and
            self.y < character.y + character.height and
            self.y + self.height > character.y):
            return True
        return False

# 弾の設定
class Bullet:
    def __init__(self, start_x, start_y, target_x, target_y):
        self.x = start_x
        self.y = start_y
        self.radius = 15  # キャラクターの半分ぐらいの大きさ
        self.color = BLUE
        self.speed = 10
        
        # 発射方向の計算
        dx = target_x - start_x
        dy = target_y - start_y
        distance = max(1, (dx**2 + dy**2)**0.5)  # ゼロ除算を防ぐ
        self.vel_x = (dx / distance) * self.speed
        self.vel_y = (dy / distance) * self.speed
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
    
    def draw(self, screen, camera_x):
        pygame.draw.circle(screen, self.color, (int(self.x - camera_x), int(self.y)), self.radius)
    
    def is_out_of_screen(self):
        return self.x < 0 or self.x > TOTAL_WIDTH or self.y < 0 or self.y > HEIGHT

# ゲームクラス
class Game:
    def __init__(self):
        self.character = Character()
        self.bullets = []
        self.obstacles = []
        self.camera_x = 0
        self.state = "playing"  # playing, gameover, clear
        
        # ゴールの位置
        self.goal_x = TOTAL_WIDTH - 30
        self.goal_y = HEIGHT - 100
        self.goal_width = 20
        self.goal_height = 100
        
        # 障害物の生成
        self.generate_obstacles()
    
    def generate_obstacles(self):
        # ランダムに障害物を配置
        num_obstacles = 10  # 障害物の数
        for _ in range(num_obstacles):
            # 画面の範囲内でランダムな位置に配置
            x = random.randint(WIDTH, TOTAL_WIDTH - 100)  # 最初の画面は避ける
            y = random.randint(50, HEIGHT - 100)  # 地面より上
            width = random.randint(30, 80)
            height = random.randint(30, 80)
            self.obstacles.append(Obstacle(x, y, width, height))
    
    def update(self):
        if self.state != "playing":
            return
            
        # キャラクターの更新
        result = self.character.update()
        if result != "playing":
            self.state = result
            return
        
        # 障害物との当たり判定
        for obstacle in self.obstacles:
            if obstacle.check_collision(self.character):
                self.character.knockback()  # ノックバック
        
        # 弾の更新と当たり判定
        bullets_to_remove = []
        for bullet in self.bullets:
            bullet.update()
            
            # 画面外に出た弾を削除リストに追加
            if bullet.is_out_of_screen():
                bullets_to_remove.append(bullet)
                continue
            
            # キャラクターとの当たり判定（弾の半径を考慮）
            if ((self.character.x - bullet.radius < bullet.x < self.character.x + self.character.width + bullet.radius) and
                (self.character.y - bullet.radius < bullet.y < self.character.y + self.character.height + bullet.radius)):
                self.character.jump()  # キャラクターを浮き上がらせる
                bullets_to_remove.append(bullet)
        
        # 削除リストの弾を削除
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
        
        # カメラの位置更新（キャラクターが中央に来るように）
        self.camera_x = max(0, min(self.character.x - WIDTH // 2, TOTAL_WIDTH - WIDTH))
    
    def draw(self, screen):
        screen.fill(WHITE)
        
        # クリックエリアの表示（薄い色で）
        pygame.draw.rect(screen, (200, 200, 255), (0, HEIGHT - CLICK_AREA_HEIGHT, WIDTH, CLICK_AREA_HEIGHT))
        
        # 地面の描画
        pygame.draw.rect(screen, GREEN, (0, HEIGHT - 10, WIDTH, 10))
        
        # 障害物の描画
        for obstacle in self.obstacles:
            obstacle.draw(screen, self.camera_x)
        
        # ゴールの描画（カメラ位置を考慮）
        if 0 <= self.goal_x - self.camera_x <= WIDTH:
            pygame.draw.rect(screen, GREEN, (self.goal_x - self.camera_x, self.goal_y, self.goal_width, self.goal_height))
        
        # 画面の境界線を描画
        for i in range(1, 3):
            x = i * WIDTH - self.camera_x
            if 0 <= x <= WIDTH:
                pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT), 2)
        
        # キャラクターの描画
        self.character.draw(screen, self.camera_x)
        
        # 弾の描画
        for bullet in self.bullets:
            bullet.draw(screen, self.camera_x)
        
        # ゲーム状態の表示
        font = pygame.font.SysFont(None, 36)
        if self.state == "gameover":
            text = font.render("GAME OVER - Press R to Restart", True, BLACK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        elif self.state == "clear":
            text = font.render("CLEAR! - Press R to Restart", True, BLACK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
    
    def shoot(self, target_x, target_y):
        if self.state == "playing":
            # クリックした位置を起点に、上方向に発射
            bullet = Bullet(target_x + self.camera_x, HEIGHT, target_x + self.camera_x, 0)
            self.bullets.append(bullet)
    
    def restart(self):
        self.__init__()

# メインループ
def main():
    clock = pygame.time.Clock()
    game = Game()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # マウスクリックで弾を発射（クリックエリア内のみ）
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_y >= HEIGHT - CLICK_AREA_HEIGHT:
                    game.shoot(mouse_x, mouse_y)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Rキーでリスタート
                    game.restart()
        
        game.update()
        game.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
