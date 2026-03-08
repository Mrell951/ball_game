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

    def mainLoop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Rendering code
        self.screen.fill("white")

        self.gamer.drawPlayer()

        pygame.display.update()
        self.clock.tick(60)

    class Player: # The player object.
        def __init__(self, screen):
            self.y_vel = 0
            self.screen = screen
            self.hitbox = pygame.Rect(640, 480, 64, 64)

        def playerLoop(self):
            pass

        def drawPlayer(self):
            pygame.draw.rect(self.screen, (255, 0, 0), self.hitbox)
    class Background: # Background object
        def __init__(self):
            self.paralax_amount = 0

    class Ground: # Ground object
        def __init__(self, side):
            self.side = side

    class Solid_object_template: # Object template for solid objects.
        def __init__(self, sprite, x, y):
            self.sprite = sprite
            self.x_pos = x
            self.y_pos = y

    class Obsticale(Solid_object_template): # bad objects >:( (inherits from Solid_object_template)
        def __init__(self, sprite, x, y):
            super().__init__(sprite, x, y)

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