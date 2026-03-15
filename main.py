import pygame
import cv2
pygame.init()

running = True

IMAGES = {
    "Background": "images/background.png",
    "Player": "images/ball.png",
    "Spike": "images/spike.png",
    "Block": "images/block.png"
}

class Game:
        # init
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        self.scroll_x = 0

        self.game_over = False

        pygame.display.set_caption("ball video game")

        self.clock = pygame.time.Clock()

        self.gamer = self.Player(self.screen)
        self.ground1 = self.Ground(self.screen, 1)
        self.ground2 = self.Ground(self.screen, 2)

        self.BLOCKS = [
            self.Solid_object_template(IMAGES["Block"], 9, 1, True),
            self.Solid_object_template(IMAGES["Block"], 15, 7, True)
        ]

        # game over vid
        video_path = 'gameOver.wmv' # Ensure the file is accessible
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print("video not workie :(")
            exit()

        success, img = self.cap.read()
        if not success:
            print("video not workie. (could not read the file :( )")
            exit()
        
        # set up the shape
        self.shape = img.shape[1::-1]

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

        self.scroll_x += 7.3
        self.gamer.PlayerPhysics()

        for i in self.BLOCKS:
            self.gamer.PlayerColision(i.hitbox)
        self.gamer.PlayerColision(self.ground1.hitbox)
        self.gamer.PlayerColision(self.ground2.hitbox)

        for i in self.BLOCKS:
            i.run_loop(self.scroll_x)

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
        

        self.ground1.drawGround()
        self.ground2.drawGround()

        if self.game_over:
            success, img = self.cap.read()
            if success:
                # Convert the OpenCV image (BGR) to Pygame surface (RGB)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                surf = pygame.surfarray.make_surface(img)
                # OpenCV reads top-to-bottom, Pygame surface is bottom-to-top by default, so we flip
                surf = pygame.transform.rotate(surf, -90) 
                surf = pygame.transform.flip(surf, True, False)

                self.screen.blit(surf, (0, 0))

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
                overlap_x = min(self.hitbox.right, block.right) - max(self.hitbox.left, block.left)
                overlap_y = min(self.hitbox.bottom, block.bottom) - max(self.hitbox.top, block.top)
                
                if overlap_x < overlap_y:
                    # Side collision (horizontal)
                    pass  # Do something special here later
                else:
                    # Vertical collision
                    self.hitbox.y -= self.y_vel
                    self.falling = 0
                    self.y_vel = 0
            else:
                self.falling += 1
                
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
                if len(self.cached_rotations) > 50:  # Keep only 50 rotations, remove farthest from current
                    farthest_key = max(self.cached_rotations.keys(), key=lambda k: abs(k - self.rotate_amount))
                    del self.cached_rotations[farthest_key]

            rotated_image = self.cached_rotations[angle_key]
            new_rect = rotated_image.get_rect(center = self.player_img.get_rect(topleft=(self.hitbox.topleft)).center)

            # pygame.draw.rect(self.screen, (255, 0, 0), self.hitbox)
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

            print("grid size:", x * grid_size)

            self.hitbox = pygame.Rect(self.x_pos, self.y_pos, self.hitbox_width, self.hitbox_height)
        
        def run_loop(self, scroll_amount):
            self.hitbox.x = (scroll_amount * -1) + self.x_pos
        
        def draw(self, screen):
            pygame.draw.rect(screen, (64, 64, 100), self.hitbox)
            screen.blit(self.sprite, self.hitbox)

    class Obsticale(Solid_object_template): # bad objects >:( (inherits from Solid_object_template)
        def __init__(self, sprite, x, y, hitbox_width=64, hitbox_height=64):
            super().__init__(sprite, x, y, hitbox_width, hitbox_height)

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
    g.cap.release()
    exit()