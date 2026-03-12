import pygame
pygame.init()

running = True

class Game:
        # init
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        self.scroll_x = 0
        pygame.display.set_caption("ball video game")

        self.clock = pygame.time.Clock()

        self.gamer = self.Player(self.screen)
        self.ground1 = self.Ground(self.screen, 1)
        self.ground2 = self.Ground(self.screen, 2)

        self.block = self.Solid_object_template(16, 90, True)

    def mainLoop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global running
                running = False

            self.gamer.playerLoop(event)

        self.scroll_x += 7.3
        self.gamer.PlayerPhysics()

        self.gamer.PlayerColision(self.ground1.hitbox)
        self.gamer.PlayerColision(self.ground2.hitbox)

        self.block.run_loop(self.scroll_x)

        # Rendering code
        self.screen.fill("white")

        self.gamer.drawPlayer()

        self.block.draw(self.screen)

        self.ground1.drawGround()
        self.ground2.drawGround()

        pygame.display.flip()
        self.clock.tick(60)

    class Player: # The player object.
        def __init__(self, screen):
            self.y_vel = 0
            self.gravity_side = 1
            self.falling = 0
            self.screen = screen
            self.hitbox = pygame.Rect(50, 400, 64, 64)

        def playerLoop(self, e):

            if e.type == pygame.KEYDOWN: # handle for presses
                if self.falling < 3:
                    if e.key == pygame.K_SPACE:
                        self.gravity_side *= -1
                
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.falling < 3:
                    self.gravity_side *= -1
            
            print(self.falling)

        def PlayerColision(self, block):
            if self.hitbox.colliderect(block):
                self.hitbox.y -= self.y_vel
                self.falling = 0
                self.y_vel = 0
            else:
                self.falling += 1
                
        def PlayerPhysics(self):
            self.y_vel += 1 * self.gravity_side
            self.hitbox.y += self.y_vel

        def drawPlayer(self):
            pygame.draw.rect(self.screen, (255, 0, 0), self.hitbox)
        
    class Background: # Background object
        def __init__(self):
            self.paralax_amount = 0

    class Ground: # Ground object
        def __init__(self, screen, side=1): # side can be 1 or 2.
            self.side = side
            self.screen = screen

            if side == 1:
                self.hitbox = pygame.Rect(0, -75, 800, 128)
            elif side == 2:
                self.hitbox = pygame.Rect(0, 550, 800, 128)

        def drawGround(self):
            pygame.draw.rect(self.screen, (125, 125, 125), self.hitbox)

    class Solid_object_template: # Object template for solid objects.
        def __init__(self, x, y, snap, hitbox_width=64, hitbox_height=64):
            # self.sprite = sprite
            self.x_pos = x
            self.y_pos = y

            self.hitbox_width = hitbox_width
            self.hitbox_height = hitbox_height

            if snap:
                grid_x = self.x_pos // self.hitbox_width
                grid_y = self.y_pos // self.hitbox_height


                self.snapped_x = grid_x * self.hitbox_width
                self.snapped_y = grid_y * self.hitbox_height


                self.hitbox = pygame.Rect(self.snapped_x, self.snapped_y, self.hitbox_width, self.hitbox_height)
            else:
                self.hitbox = pygame.Rect(self.x_pos, self.y_pos, self.hitbox_width, self.hitbox_height)
        
        def run_loop(self, scroll_amount):
            self.hitbox.x = (scroll_amount * -1) + self.x_pos
        
        def draw(self, screen):
            pygame.draw.rect(screen, (64, 64, 100), self.hitbox)

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
    exit()