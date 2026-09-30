import pygame
from game.maze import generate_maze, CELL
from game.entities import Player, Enemy

COLS, ROWS = 13, 11
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 110
FPS = 60
SPEED_UP_MS = 15000  # enemies speed up every 15 seconds
SPEED_STEP = 2
MIN_MOVE_INTERVAL = 5
FREEZE_FRAMES = 300  # 5 seconds at 60 FPS
PELLET_CELL = (ROWS//2, COLS//4)

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Chase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont("monospace", 38, bold=True)
        self.reset()

    def reset(self):
        self.walls = generate_maze(COLS, ROWS)
        self.player = Player(0, 0)
        self.enemies = [Enemy(ROWS-1, COLS-1), Enemy(0, COLS-1), Enemy(ROWS-1, 0)]
        self.exit_rect = pygame.Rect((COLS//2)*CELL+5, (ROWS//2)*CELL+5, CELL-10, CELL-10)
        self.caught = False
        self.won = False
        self.start_ticks = pygame.time.get_ticks()
        self.speed_tier = 1
        pr, pc = PELLET_CELL
        self.pellet_rect = pygame.Rect(pc*CELL+CELL//2-9, pr*CELL+CELL//2-9, 18, 18)
        self.pellet_active = True
        self.freeze_timer = 0
        self.score = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset()
        return True

    def update(self):
        if self.caught or self.won: return
        self.score += 1
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, ROWS, COLS)
        elapsed = pygame.time.get_ticks() - self.start_ticks
        target_tier = elapsed // SPEED_UP_MS + 1
        while self.speed_tier < target_tier and any(e.move_interval > MIN_MOVE_INTERVAL for e in self.enemies):
            self.speed_tier += 1
            for enemy in self.enemies:
                enemy.move_interval = max(MIN_MOVE_INTERVAL, enemy.move_interval - SPEED_STEP)
        if self.pellet_active and self.player.rect.colliderect(self.pellet_rect):
            self.pellet_active = False
            self.freeze_timer = FREEZE_FRAMES
            for enemy in self.enemies:
                enemy.frozen = True
        for enemy in self.enemies:
            enemy.update(self.walls, self.player, ROWS, COLS)
            if self.player.rect.colliderect(enemy.rect):
                self.caught = True
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            if self.freeze_timer == 0:
                for enemy in self.enemies:
                    enemy.frozen = False
        if self.player.rect.colliderect(self.exit_rect):
            self.won = True

    def draw(self):
        self.screen.fill((230, 220, 210))
        wc=(50,40,60)
        for r in range(ROWS):
            for c in range(COLS):
                x,y=c*CELL,r*CELL
                w=self.walls[r][c]
                if w[0]: pygame.draw.line(self.screen,wc,(x,y),(x+CELL,y),3)
                if w[1]: pygame.draw.line(self.screen,wc,(x,y+CELL),(x+CELL,y+CELL),3)
                if w[2]: pygame.draw.line(self.screen,wc,(x+CELL,y),(x+CELL,y+CELL),3)
                if w[3]: pygame.draw.line(self.screen,wc,(x,y),(x,y+CELL),3)
        pygame.draw.rect(self.screen,(80,200,80),self.exit_rect,border_radius=4)
        lbl=self.font.render("EXIT",True,(20,80,20))
        self.screen.blit(lbl,(self.exit_rect.x+2,self.exit_rect.y+6))
        if self.pellet_active:
            pygame.draw.circle(self.screen,(255,220,0),self.pellet_rect.center,9)
            pygame.draw.circle(self.screen,(160,120,0),self.pellet_rect.center,9,2)
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        hud=pygame.Rect(0,ROWS*CELL,WIDTH,110)
        pygame.draw.rect(self.screen,(30,30,50),hud)
        info=self.font.render("Reach EXIT before the enemy catches you!  R=Restart",True,(200,200,200))
        self.screen.blit(info,(8,ROWS*CELL+14))
        maxed = all(e.move_interval <= MIN_MOVE_INTERVAL for e in self.enemies)
        tier=self.font.render(f"Enemy Speed: Tier {self.speed_tier}"+(" (MAX)" if maxed else ""),True,(255,200,80))
        self.screen.blit(tier,(8,ROWS*CELL+46))
        if self.freeze_timer > 0:
            frz=self.font.render(f"FROZEN: {(self.freeze_timer+59)//60}s",True,(120,200,255))
            self.screen.blit(frz,(WIDTH-frz.get_width()-8,ROWS*CELL+46))
        surv=self.font.render(f"Survived: {self.score//60}s",True,(200,200,200))
        self.screen.blit(surv,(8,ROWS*CELL+78))
        if self.caught:
            self._overlay("CAUGHT!", (220,60,60))
        if self.won:
            self._overlay("ESCAPED!", (80,220,80))
        pygame.display.flip()

    def _overlay(self, text, color):
        surf=pygame.Surface((WIDTH,ROWS*CELL),pygame.SRCALPHA)
        surf.fill((0,0,0,140))
        self.screen.blit(surf,(0,0))
        msg=self.big_font.render(text,True,color)
        sub=self.font.render("Press R to Restart",True,(200,200,200))
        self.screen.blit(msg,(WIDTH//2-msg.get_width()//2,ROWS*CELL//2-30))
        self.screen.blit(sub,(WIDTH//2-sub.get_width()//2,ROWS*CELL//2+20))
        res=self.font.render(f"Final Score: {self.score}  (Survived: {self.score//60}s)",True,(255,255,255))
        self.screen.blit(res,(WIDTH//2-res.get_width()//2,ROWS*CELL//2+52))

    def run(self):
        running=True
        while running:
            running=self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()