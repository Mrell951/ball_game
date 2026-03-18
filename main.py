import pygame
import sys
pygame.init()
pygame.mixer.init()

running = True

IMAGES = {
    "Background": "images/background.png",
    "Player": "images/ball.png",
    "Spike": "images/spike.png",
    "Block": "images/block.png"
}
SOUNDS = {
    "Game Over": pygame.mixer.Sound("Audio/sega-rally-15-game-over-yeah1.mp3")
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
                grid_lines = [line.strip() for line in lines[1:] if line.strip()]
                    
                for y, line in enumerate(grid_lines):
                    # Split by comma and process each cell
                    cells = line.split(',')
                    for x, cell in enumerate(cells):
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

        # init
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        self.scroll_x = 0
        
        self.isDead = False
        self.game_over_sound = True

        pygame.display.set_caption("ball video game")

        self.clock = pygame.time.Clock()

        self.gamer = self.Player(self.screen)
        self.ground1 = self.Ground(self.screen, 1)
        self.ground2 = self.Ground(self.screen, 2)

        self.BLOCKS = []
        self.OBSTICALES = []

        self.LevelLoader("level.data", self.BLOCKS, self.OBSTICALES).load_level("level.data")
        
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
        

        self.bg = self.Background(0)
        self.bg1 = self.Background(511)
        self.bg2 = self.Background(511 * 2)

    def mainLoop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global running
                running = False

            self.gamer.playerLoop(event)
        
        fps = self.clock.get_fps()
        pygame.display.set_caption(f"ball video game - FPS: {fps:.2f}")

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

        self.ground1.drawGround()
        self.ground2.drawGround()

        if self.isDead:
            if self.game_over_sound:
                SOUNDS["Game Over"].play()
                self.game_over_sound = False
            # Animate the game over video frame by frame at the top-left corner
            if not hasattr(self, 'game_over_frame_idx'):
                self.game_over_frame_idx = 0
            if self.game_over_frame_idx < len(self.video_frames):
                self.screen.blit(self.video_frames[round(self.game_over_frame_idx)], (0, 0))
                self.game_over_frame_idx += 0.7575757575757576
            else:
                self.screen.blit(self.video_frames[-1], (0, 0))
            
            print(self.game_over_frame_idx)
            if round(self.game_over_frame_idx) > 189:
                running = False
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        self.clock.tick(60)

        # display the fps
        fps = self.clock.get_fps()
        pygame.display.set_caption(f"ball video game - FPS: {fps:.1f}")

    class Player: # The player object.
        def __init__(self, screen):
            self.y_vel = 0
            self.gravity_side = 1
            self.falling = 0
            self.screen = screen

            self.overlap_x = 0
            self.overlap_y = 0

            self.rotate_amount = 0
            self.cached_rotations = {}  # Cache for rotated images to reduce lag

            self.player_img = pygame.image.load(IMAGES["Player"])

            self.hitbox = pygame.Rect(50, 400, 64, 64)

        def playerLoop(self, e):

            if e.type == pygame.KEYDOWN: # handle for presses
                if self.falling < 3:
                    if e.key == pygame.K_SPACE:
                        self.gravity_side *= -1
                
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.falling < 3:
                    self.gravity_side *= -1

        def PlayerColision(self, block):
            if self.hitbox.colliderect(block):
                # Calculate overlaps to determine collision direction

                self.overlap_x = min(self.hitbox.right, block.right) - max(self.hitbox.left, block.left)
                self.overlap_y = min(self.hitbox.bottom, block.bottom) - max(self.hitbox.top, block.top)
                
                # Vertical collision
                self.hitbox.y -= self.y_vel
                self.falling = 0
                self.y_vel = 0
            else:
                self.falling += 1

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
            self.y_vel += 1 * self.gravity_side
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
        pass

    class Pause_menu: # The pause menu.
        def __init__(self):
            pass

    class Bot(Player): # Background bot that competes the level with you. (also inherits stuff from the player)
        def __init__(self):
            super().__init__()

    class Effects: # Other cool effects.
        pass

if __name__ == "__main__":
    g = Game()
    while running:
        g.mainLoop()
    pygame.quit()
    exit()