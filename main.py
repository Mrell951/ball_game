import pygame
import sys
import cProfile
import psutil
import os

pygame.init()
pygame.mixer.init()

running = True
paused = False
debug = False

IMAGES = {
    "Background": "images/background.png",
    "Player": "images/ball.png",
    "Spike": "images/spike.png",
    "Half-Spike": "images/spikehalf.png",
    "Block": "images/block.png",
    "End Wall": "images/endWall.png",
    "End Screen": "images/endScreen.png"
}
SOUNDS = {
    "Game Over": pygame.mixer.Sound("Audio/sega-rally-15-game-over-yeah1.mp3"),
    "Swoosh": pygame.mixer.Sound("Audio/swoosh.wav")
}
class Game:
    class LevelLoader:
        def __init__(self, filepath, blocks=[], obstacles=[]):
            self.blocks = blocks
            self.obstacles = obstacles
            self.level_length = 0
            self.load_level(filepath)

        def load_level(self, filepath):
            try:
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                    
                    # First line is level length
                    self.level_length = int(lines[0].strip())
                    
                    # Parse the grid
                    grid_lines = [line.strip().split(',') for line in lines[1:] if line.strip()]
                    
                    for y, line in enumerate(grid_lines):
                        # Split by comma and process each cell
                        for x, cell in enumerate(line):
                            cell = cell.strip()
                            
                            if not cell or cell == '0':
                                continue
                            
                            # Parse cell with optional parameters
                            rotation = 0
                            if '[' in cell:
                                base_cell = cell[:cell.index('[')]
                                params = cell[cell.index('[')+1:cell.index(']')]
                                if params.startswith('rot'):
                                    rotation = int(params.split('-')[1])
                            else:
                                base_cell = cell
                            
                            base_cell = int(base_cell)
                            
                            # 1 = regular block, 3 = spike, 4 = half-spike
                            if base_cell == 1:
                                self.blocks.append({"x": x, "y": y, "rotation": rotation})
                            elif base_cell == 3:
                                self.obstacles.append({"x": x, "y": y, "rotation": rotation, "type": "spike"})
                            elif base_cell == 4:
                                self.obstacles.append({"x": x, "y": y, "rotation": rotation, "type": "half-spike"})
            except FileNotFoundError:
                print(f"Error: Could not find level file at {filepath}")
            except Exception as e:
                print(f"Error loading level: {e}")
        
        def return_length(self):
            return self.level_length

        # init
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600), vsync=1)
        self.has_won = False
        self.scroll_x = 0

        # loading screen
        self.screen.fill((0, 0, 0)) # Fill background with black
        self.font = pygame.font.SysFont('Arial', 40)
        self.loading_text = self.font.render("Loading...", True, (255, 255, 255))
        self.text_rect = self.loading_text.get_rect(center=(700, 550))
        self.screen.blit(self.loading_text, self.text_rect)
        pygame.display.flip()

        self.isDead = False
        self.game_over_sound = True

        self.process = psutil.Process(os.getpid())

        pygame.display.set_caption("ball video game")

        self.clock = pygame.time.Clock()

        self.end_screen = self.End_level_screen()

        self.gamer = self.Player(self.screen)

        self.ground1 = self.Ground(self.screen, 1)
        self.ground2 = self.Ground(self.screen, 2)

        self.BLOCKS = []
        self.OBSTICALES = []

        self.level_data = self.LevelLoader("level.data", self.BLOCKS, self.OBSTICALES)
        self.level_data.load_level("level.data")
        self.length = self.level_data.return_length()

        self.pause = self.Pause_menu()

        self.end = self.End_wall(self.length, self.screen)
        # Convert loaded block dictionaries to Solid_object_template objects
        self.BLOCKS = [self.Solid_object_template(IMAGES["Block"], b["x"], b["y"], True) for b in self.BLOCKS]
        
        # Convert loaded obstacle dictionaries to Obsticale objects
        self.OBSTICALES = [self.Obsticale(IMAGES["Spike"], o["x"], o["y"], True, rotation=o["rotation"]) for o in self.OBSTICALES]

        # game over vid
        self.video_frames = []
        for i in range(12, 211):
            frame_path = f"GameOverVid/game over/img_{i:06}.png"
            try:
                img = pygame.image.load(frame_path)
                self.video_frames.append(img)
            except pygame.error:
                print(f"Could not load {frame_path}")

        pygame.mixer.music.load("Audio/105753.mp3")
        pygame.mixer.music.play(-1)


        self.bg = self.Background(0)
        self.bg1 = self.Background(511)
        self.bg2 = self.Background(511 * 2)

    def mainLoop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global running
                running = False

            if not paused:
                self.gamer.playerLoop(event)

            self.pause.do_menu(event)
        
        fps = self.clock.get_fps()
        pygame.display.set_caption(f"ball video game - FPS: {fps:.2f}")

        if not paused:
            self.end.interact(x_scroll=self.scroll_x)
            self.has_won = self.end.has_won(self.gamer.hitbox)

            if not self.isDead:
                self.scroll_x += 7.3
                self.gamer.PlayerPhysics()

                for i in self.BLOCKS:
                    self.gamer.PlayerColision(i.hitbox)
                    self.isDead = self.gamer.isDead(i.hitbox, i)
                
                for i in self.OBSTICALES:
                    if self.gamer.hitbox.colliderect(i.hitbox):
                        self.isDead = self.gamer.kill()

                self.gamer.PlayerColision(self.ground1.hitbox)
                self.gamer.PlayerColision(self.ground2.hitbox)

            for i in self.BLOCKS:
                i.run_loop(self.scroll_x)

            for i in self.OBSTICALES:
                i.run_loop(self.scroll_x)

            if not self.isDead:
                self.bg.run_loop()
                self.bg1.run_loop()
                self.bg2.run_loop()


        # Rendering code
        self.screen.fill("white")

        self.bg.drawLoop(self.screen)
        self.bg1.drawLoop(self.screen)
        self.bg2.drawLoop(self.screen)
        self.gamer.drawPlayer()

        for i in self.BLOCKS:
            i.draw(self.screen)
        
        for i in self.OBSTICALES:
            i.draw(self.screen)

        self.end.draw_wall()

        self.ground1.drawGround()
        self.ground2.drawGround()

        if self.isDead:
            if self.game_over_sound:
                SOUNDS["Game Over"].play()
                pygame.mixer.music.stop()
                self.game_over_sound = False
            # Animate the game over video frame by frame at the top-left corner
            if not hasattr(self, 'game_over_frame_idx'):
                self.game_over_frame_idx = 0
            if self.game_over_frame_idx < len(self.video_frames):
                self.screen.blit(self.video_frames[round(self.game_over_frame_idx)], (0, 0))
                self.game_over_frame_idx += 0.7575757575757576
            else:
                self.screen.blit(self.video_frames[-1], (0, 0))
            
            if round(self.game_over_frame_idx) > 189:
                running = False
                pygame.quit()
                sys.exit()

        if self.has_won:
            self.end_screen.appear(self.has_won, self.screen)

        self.pause.draw_menu(self.screen)
        pygame.display.flip()
        self.clock.tick(60)

        # display the fps
        fps = self.clock.get_fps()
        pygame.display.set_caption(f"ball video game - FPS: {fps:.1f}")

    def debug(self):
        mem_bytes = self.process.memory_info().rss
        mem_mib = mem_bytes / (1024 * 1024) 
        cpu_usage = psutil.cpu_percent(interval=1) 

        print(f"Ram useage: {mem_mib:.2f}")
        print(f"CPU useage (for the whole system): {cpu_usage}")
        print("Player's falling variable:", self.gamer.falling)

    class Player: # The player object.
        def __init__(self, screen):
            self.y_vel = 0
            self.max_y_vel = 20
            self.gravity_strength = 1
            self.gravity_side = 1
            self.falling = 0
            self.on_surface = False
            self.screen = screen

            self.overlap_x = 0
            self.overlap_y = 0

            self.rotate_amount = 0
            self.cached_rotations = {}  # Cache for rotated images to reduce lag

            self.player_img = pygame.image.load(IMAGES["Player"])

            self.hitbox = pygame.Rect(50, 400, 64, 64)
            self.jump_pressed = False

        def playerLoop(self, e):
            keys = pygame.key.get_pressed()

            jump_requested = keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]

            if jump_requested and not self.jump_pressed and self.on_surface:
                SOUNDS["Swoosh"].play()
                self.gravity_side *= -1
                self.y_vel = 0
                self.on_surface = False
                self.falling = 1

            self.jump_pressed = jump_requested

        def begin_physics_step(self):
            if self.on_surface:
                self.falling = 0
            else:
                self.falling += 1

            self.on_surface = False

             
        def PlayerColision(self, block):
            if self.hitbox.colliderect(block):
                # Calculate overlaps to determine collision direction

                self.overlap_x = min(self.hitbox.right, block.right) - max(self.hitbox.left, block.left)
                self.overlap_y = min(self.hitbox.bottom, block.bottom) - max(self.hitbox.top, block.top)

                if self.overlap_y <= self.overlap_x:
                    if self.y_vel * self.gravity_side >= 0:
                        if self.gravity_side > 0:
                            self.hitbox.bottom = block.top
                        else:
                            self.hitbox.top = block.bottom
                        self.on_surface = True
                        self.falling = 0
                        self.y_vel = 0
                else:
                    if self.hitbox.centerx < block.centerx:
                        self.hitbox.right = block.left
                    else:
                        self.hitbox.left = block.right

        def isDead(self, block, obj=None): # NOTE: always call this function after the colision or the game will crash (+ this is only for regular blocks) 
            if self.overlap_x < self.overlap_y and self.hitbox.right > block.right:
                # Left side collision only
                game_over_state = True
                return game_over_state
            return False
        
        def kill(self): # the most evil function 😈😈😈
            game_over_state = True
            return game_over_state 

        def PlayerPhysics(self):
            self.begin_physics_step()
            self.y_vel += self.gravity_strength * self.gravity_side
            self.y_vel = max(-self.max_y_vel, min(self.max_y_vel, self.y_vel))
            self.hitbox.y += self.y_vel

        def drawPlayer(self):

            self.rotate_amount -= 7 / ((self.falling / 12) + 1)
            self.rotate_amount %= 360

            angle_key = round(self.rotate_amount, 1)
            
            if angle_key not in self.cached_rotations:
                self.cached_rotations[angle_key] = pygame.transform.rotate(self.player_img, angle_key)
                # Optional: Limit cache size to prevent memory issues
                if len(self.cached_rotations) > 50:
                    farthest_key = max(self.cached_rotations.keys(), key=lambda k: abs(k - self.rotate_amount))
                    del self.cached_rotations[farthest_key]

            rotated_image = self.cached_rotations[angle_key]
            new_rect = rotated_image.get_rect(center = self.player_img.get_rect(topleft=(self.hitbox.topleft)).center)

            # pygame.draw.rect(self.screen, (255, 0, 0), self.hitbox)
            if self.isDead(pygame.Rect(0, 0, 0, 0)):
                return
            self.screen.blit(rotated_image, new_rect)
            
        
    class Background: # Background object
        def __init__(self, x_offset):
            self.paralax_amount = 2
            self.hitbox = pygame.Rect(x_offset, 0, 800, 600)
            self.background_image = pygame.image.load(IMAGES["Background"])
        
        def run_loop(self):
            self.hitbox.x -= self.paralax_amount
            if self.hitbox.x <= -600:
                self.hitbox.x = 800

        def drawLoop(self, screen):
            screen.blit(self.background_image, self.hitbox)

    class Ground: # Ground object
        def __init__(self, screen, side=1): # side can be 1 or 2.
            self.side = side
            self.screen = screen

            if side == 1:
                self.hitbox = pygame.Rect(0, -64, 800, 128)
            elif side == 2:
                self.hitbox = pygame.Rect(0, 512, 800, 128)

        def drawGround(self):
            pygame.draw.rect(self.screen, (125, 125, 125), self.hitbox)

    class Solid_object_template: # Object template for solid objects.
        def __init__(self, sprite, x, y, snap, hitbox_width=64, hitbox_height=64):
            self.hitbox_width = hitbox_width
            self.sprite = pygame.image.load(sprite)
            self.hitbox_height = hitbox_height
            grid_size = hitbox_width

            if snap:
                # Snap x and y to nearest grid position
                self.x_pos = x * grid_size
                self.y_pos = y * grid_size
            else:
                self.x_pos = x
                self.y_pos = y

            self.hitbox = pygame.Rect(self.x_pos, self.y_pos, self.hitbox_width, self.hitbox_height)
        
        def run_loop(self, scroll_amount):
            self.hitbox.x = (scroll_amount * -1) + self.x_pos
        
        def draw(self, screen):
            # pygame.draw.rect(screen, (64, 64, 100), self.hitbox)
            screen.blit(self.sprite, self.hitbox)

    class Obsticale(Solid_object_template): # bad objects >:( (inherits from Solid_object_template)
        def __init__(self, sprite, x, y, snap, hitbox_width=64, hitbox_height=64, rotation=0):
            super().__init__(sprite, x, y, snap, hitbox_width, hitbox_height)
            self.hitbox_width = hitbox_width
            self.sprite = pygame.transform.scale(pygame.image.load(sprite), (hitbox_width, hitbox_height))
            self.sprite = pygame.transform.rotate(self.sprite, rotation * 90)
            self.hitbox_height = hitbox_height
            grid_size = hitbox_width

            if snap:
                # Snap x and y to nearest grid position
                self.x_pos = x * grid_size
                self.y_pos = y * grid_size
            else:
                self.x_pos = x
                self.y_pos = y


    class Block_transition_obj: # Fade in and out effects
        def __init__(self, border):
            self.border = border

    class Particle_obj: # Particle object. It can only be spawned once.
        def __init__(self, x, y, gravity_enabled, gravity_amount):
            pass

    class End_wall: # End wall for completing the level.
        def __init__(self, end_pos, screen):
            self.image = pygame.image.load(IMAGES["End Wall"])
            self.end_pos = end_pos
            self.screen = screen
            self.hitbox = pygame.Rect(end_pos, 0, 512, 600)

        def draw_wall(self):
            self.screen.blit(self.image, self.hitbox)

        def interact(self, x_scroll):
            self.hitbox.x = (x_scroll * -1) + self.end_pos
            
        def has_won(self, player_rect):
            if self.hitbox.colliderect(player_rect):
                won = True
                return won
    class Pause_menu: # The pause menu.
        def __init__(self):
            self.hitbox = pygame.Rect(0, 0, 800, 600)
            self.is_menu_visible = False
            self.transparent_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
            self.transparent_surface.fill((0, 0, 0, 128))
            self.font = pygame.font.SysFont('Arial', 48)
            self.small_font = pygame.font.SysFont('Arial', 28)
            self.title_text = self.font.render("Paused...", True, (255, 255, 255))
            self.resume_text = self.small_font.render("Press ESC to resume...", True, (255, 255, 255))
        
        def do_menu(self, e):
            global paused
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.is_menu_visible = not self.is_menu_visible
                    if self.is_menu_visible:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                    paused = not paused
        
        def draw_menu(self, screen):
            if self.is_menu_visible:
                screen.blit(self.transparent_surface, (0, 0))
                title_rect = self.title_text.get_rect(center=(400, 250))
                resume_rect = self.resume_text.get_rect(center=(400, 320))
                screen.blit(self.title_text, title_rect)
                screen.blit(self.resume_text, resume_rect)

    class Bot(Player): # Background bot that competes the level with you. (also inherits stuff from the player)
        def __init__(self):
            super().__init__()

    class Effects: # Other cool effects.
        pass

    class End_level_screen():
        def __init__(self):
            self.repeats = 0
            self.image = pygame.image.load(IMAGES["End Screen"])
            self.hitbox = pygame.Rect(0, 0, 800, 600)

            self.alpha = 0
            self.image.set_alpha(self.alpha)

        def appear(self, win_state, screen):
            screen.blit(self.image, self.hitbox)

            if win_state:
                if self.alpha < 255:
                    self.alpha += 5

                    if self.alpha >= 255:
                        pygame.quit()
                        exit()
                        
                    self.image.set_alpha(self.alpha)

if __name__ == "__main__":
    g = Game()
    while running:
        g.mainLoop()
        if debug:
            cProfile.run("g.mainLoop()")

    pygame.quit()
    exit()
