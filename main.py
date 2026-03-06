import pygame
pygame.init()

class Game:

    class Player: # The player object.
        def __init__(self):
            self.y_vel = 0

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
        pass

    class Block_transition_obj: # Fade in and out effects
        def __init__(self, border):
            self.border = border

    class Particle_obj: # Particle object. It can only be spawned once.
        def __init__(self, x, y, gravity_enabled, gravity_amount):
            pass

    class End_wall: # End wall for completing the level.
        pass

    class Pause_menu: # The pause menu.
        pass

    class Bot: # Background bot that competes the level with you.
        pass

    class Effects: # Other cool effects.
        pass

    # init
    def __init__(self):
        pass