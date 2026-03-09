import pygame
pygame.init()

running = True

class Game:
        # init
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("ball video game")

        self.clock = pygame.time.Clock()

        self.gamer = self.Player(self.screen)
        self.ground1 = self.Ground(self.screen, 1)
        self.ground2 = self.Ground(self.screen, 2)

    def mainLoop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                global running
                running = False

            self.gamer.playerLoop(event)

        # Rendering code
        self.screen.fill("white")

        self.gamer.drawPlayer()
        self.ground1.drawGround()
        self.ground2.drawGround()

        pygame.display.flip()
        self.clock.tick(60)

    class Player: # The player object.
        def __init__(self, screen):
            self.y_vel = 0
            self.screen = screen
            self.hitbox = pygame.Rect(50, 480, 64, 64)

        def playerLoop(self, e):
            if e.type == pygame.KEYDOWN: # handle for presses
                if e.key == pygame.K_SPACE:
                    print("jump")
                
            if e.type == pygame.MOUSEBUTTONDOWN:
                print("jump")
 
                

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
        def __init__(self, sprite, x, y, hitbox_width=64, hitbox_height=64):
            self.sprite = sprite
            self.x_pos = x
            self.y_pos = y

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