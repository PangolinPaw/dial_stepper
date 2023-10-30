import os

import pygame

VERSION = '0.1'
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FONT = None
COLOURS = None
IMAGES = None

dirname, scriptname = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'

def init():
    global FONT, COLOURS, IMAGES
    pygame.init()
    pygame.font.init()
    FONT = pygame.font.Font(f'{THIS_DIRECTORY}assets{os.sep}roboto.ttf', 18)
    COLOURS = {
        'black':    ( 27,  40,  50),
        'white':    (255, 255, 255),
        'muted':    (200, 200, 200),
        'border':   (237, 240, 243),
        'primary':  ( 16, 149, 193),
        'secondary':( 89, 107, 120),
        'error':    (193,  60,  16)
    }
    IMAGES = {
        'logo': pygame.image.load('assets/logo.png')
    }

def main():
    init()
    pygame.display.set_icon(IMAGES['logo'])
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f'Control Simulator | v{VERSION}')
    clock = pygame.time.Clock()

    running = True
    while running:
        screen.fill(COLOURS['black'])

        # Dial backboard
        pygame.draw.rect(
            screen,
            COLOURS['white'],           # colour
            pygame.Rect(
                0,                      # left
                SCREEN_HEIGHT - 150,    # top
                SCREEN_WIDTH,           # width
                150                     # height
            )
        )

        dial_a = pygame.draw.circle(
            screen,
            COLOURS['primary'],
            (SCREEN_HEIGHT - 100, 100),          # center
            50,                      # radius
            0                        # border thickness (0 = filled)
        )


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(10)


if __name__ == '__main__':
    main()
