import os

import pygame

dirname, scriptname = os.path.split(os.path.abspath(__file__))
THIS_DIRECTORY = f'{dirname}{os.sep}'

VERSION = '0.1'
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FONT = None
COLOURS = None
IMAGES = None

DIAL_POSITIONS = {
    'a':0,
    'b':0,
    'c':0
}
MOTOR_POSITIONS = {
    'a':0,
    'b':0,
    'c':0
}


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
        'logo':   pygame.image.load('assets/logo.png'),
        'disk_a': pygame.image.load('assets/disk_a.png'),
        'disk_b': pygame.image.load('assets/disk_b.png'),
        'disk_c': pygame.image.load('assets/disk_c.png')
    }

def rotate_image(surf, image, pos, originPos, angle):
    # from https://stackoverflow.com/a/54714144/12825882
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    surf.blit(rotated_image, rotated_image_rect)
  

def draw_dials(screen):
    dial_a = pygame.draw.circle(
        screen,
        COLOURS['primary'],
        (
            250,                # left
            SCREEN_HEIGHT - 75 # top
        ),
        50,                      # radius
        0                        # border thickness (0 = filled)
    )

    dial_b = pygame.draw.circle(
        screen,
        COLOURS['primary'],
        (
            int(round(SCREEN_WIDTH / 2, 0)),
            SCREEN_HEIGHT - 75 
        ),
        50,
        0
    )

    dial_c = pygame.draw.circle(
        screen,
        COLOURS['primary'],
        (
            int(round(SCREEN_WIDTH / 2, 0)) + 150,
            SCREEN_HEIGHT - 75 
        ),
        50,
        0
    )
    return dial_a, dial_b, dial_c

def draw_discs(screen):
    w, h = IMAGES['disk_a'].get_size()
    rotate_image(
        screen,
        IMAGES['disk_a'],
        (
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            
        ),
        (int(w/2), int(h/2)),
        DIAL_POSITIONS['a']
    )


def main():
    global DIAL_POSITIONS
    init()
    pygame.display.set_icon(IMAGES['logo'])
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f'Control Simulator | v{VERSION}')
    clock = pygame.time.Clock()

    lmb_pressed = False
    rmb_pressed = False
    running = True
    while running:
        screen.fill(COLOURS['white'])

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

        # Dials
        dial_a, dial_b, dial_c = draw_dials(screen)

        # Dial text


        # Disks
        draw_discs(screen)

        # Debug buttons
        reset = pygame.draw.rect(
            screen,
            COLOURS['primary'],         # colour
            pygame.Rect(
                SCREEN_WIDTH - 100,     # left
                SCREEN_HEIGHT - 80,     # top
                75,                     # width
                30                      # height
            )
        )
        text_width, text_height = FONT.size('RESET')
        screen.blit(
            FONT.render(
                'RESET',
                True,
                COLOURS['white']
            ),
            (
                SCREEN_WIDTH - 90,
                SCREEN_HEIGHT - 75
            )
        )


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                lmb_pressed = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                lmb_pressed = False

            if lmb_pressed:
                if dial_a.collidepoint(event.pos):
                    DIAL_POSITIONS['a'] += 1
                if dial_b.collidepoint(event.pos):
                    DIAL_POSITIONS['b'] += 1
                if dial_c.collidepoint(event.pos):
                    DIAL_POSITIONS['c'] += 1

        pygame.display.flip()
        clock.tick(10)


if __name__ == '__main__':
    main()
