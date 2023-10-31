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
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        'disk_a': pygame.image.load('assets/disk_a.png').convert_alpha(),
        'dial_a': pygame.image.load('assets/dial_a.png').convert_alpha(),
        'disk_b': pygame.image.load('assets/disk_b.png').convert_alpha(),
        'dial_b': pygame.image.load('assets/dial_b.png').convert_alpha(),
        'disk_c': pygame.image.load('assets/disk_c.png').convert_alpha(),
        'dial_c': pygame.image.load('assets/dial_c.png').convert_alpha()
    }
    return screen

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
    w, h = IMAGES['dial_a'].get_size()
    dial_a = pygame.draw.circle(
        screen,
        COLOURS['white'],
        (
            250,                # left
            SCREEN_HEIGHT - 75 # top
        ),
        50,                      # radius
        0                        # border thickness (0 = filled)
    )
    rotate_image(
        screen,
        IMAGES['dial_a'],
        (
            250,
            520,
            
        ),
        (int(w/2), int(h/2)),
        DIAL_POSITIONS['a']
    )

    dial_b = pygame.draw.circle(
        screen,
        COLOURS['white'],
        (
            int(round(SCREEN_WIDTH / 2, 0)),
            SCREEN_HEIGHT - 75 
        ),
        50,
        0
    )
    rotate_image(
        screen,
        IMAGES['dial_b'],
        (
            395,
            520,
            
        ),
        (int(w/2), int(h/2)),
        DIAL_POSITIONS['b']
    )

    dial_c = pygame.draw.circle(
        screen,
        COLOURS['white'],
        (
            int(round(SCREEN_WIDTH / 2, 0)) + 150,
            SCREEN_HEIGHT - 75 
        ),
        50,
        0
    )
    rotate_image(
        screen,
        IMAGES['dial_c'],
        (
            550,
            520,
            
        ),
        (int(w/2), int(h/2)),
        DIAL_POSITIONS['c']
    )
    return dial_a, dial_b, dial_c

def draw_discs(screen):

    if MOTOR_POSITIONS['a'] > DIAL_POSITIONS['a']:
        MOTOR_POSITIONS['a'] -= 1.8
    if MOTOR_POSITIONS['a'] < DIAL_POSITIONS['a']:
        MOTOR_POSITIONS['a'] += 1.8
        
    w, h = IMAGES['disk_a'].get_size()

    rotate_image(
        screen,
        IMAGES['disk_a'],
        (
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            
        ),
        (int(w/2), int(h/2)),
        MOTOR_POSITIONS['a']
    )

    if MOTOR_POSITIONS['b'] > DIAL_POSITIONS['b']:
        MOTOR_POSITIONS['b'] -= 1.8
    if MOTOR_POSITIONS['b'] < DIAL_POSITIONS['b']:
        MOTOR_POSITIONS['b'] += 1.8
    rotate_image(
        screen,
        IMAGES['disk_b'],
        (
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            
        ),
        (int(w/2), int(h/2)),
        MOTOR_POSITIONS['b']
    )

    if MOTOR_POSITIONS['c'] > DIAL_POSITIONS['c']:
        MOTOR_POSITIONS['c'] -= 1.8
    if MOTOR_POSITIONS['c'] < DIAL_POSITIONS['c']:
        MOTOR_POSITIONS['c'] += 1.8
    rotate_image(
        screen,
        IMAGES['disk_c'],
        (
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            
        ),
        (int(w/2), int(h/2)),
        MOTOR_POSITIONS['c']
    )


def main():
    global DIAL_POSITIONS
    screen = init()
    pygame.display.set_icon(IMAGES['logo'])
    
    pygame.display.set_caption(f'Control Simulator | v{VERSION}')
    clock = pygame.time.Clock()

    turn_a = None
    turn_b = None
    turn_c = None
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

        # Disks
        draw_discs(screen)

        # Disk text
        position = str(int(round(MOTOR_POSITIONS['a'] / 1.8,0)))
        text_width, _ = FONT.size(position)
        screen.blit(
            FONT.render(
                position,
                True,
                COLOURS['black']
            ),
            (
                (SCREEN_WIDTH / 2 - text_width / 2) - 25,
                SCREEN_HEIGHT / 2 - 150
            )
        )
        position = str(int(round(MOTOR_POSITIONS['b'] / 1.8,0)))
        text_width, _ = FONT.size(position)
        screen.blit(
            FONT.render(
                position,
                True,
                COLOURS['black']
            ),
            (
                SCREEN_WIDTH / 2 - text_width / 2,
                (SCREEN_HEIGHT / 2 - 150) - 25
            )
        )
        position = str(int(round(MOTOR_POSITIONS['c'] / 1.8,0)))
        text_width, _ = FONT.size(position)
        screen.blit(
            FONT.render(
                position,
                True,
                COLOURS['black']
            ),
            (
                (SCREEN_WIDTH / 2 - text_width / 2) + 25,
                (SCREEN_HEIGHT / 2 - 150) - 50
            )
        )

        # Dials
        dial_a, dial_b, dial_c = draw_dials(screen)

        # Dial text
        position = str(int(DIAL_POSITIONS['a'] / 15))
        text_width, _ = FONT.size(position)
        screen.blit(
            FONT.render(
                position,
                True,
                COLOURS['black']
            ),
            (
                250 - text_width / 2,
                450
            )
        )
        position = str(int(DIAL_POSITIONS['b'] / 15))
        text_width, _ = FONT.size(position)
        screen.blit(
            FONT.render(
                position,
                True,
                COLOURS['black']
            ),
            (
                395 - text_width / 2,
                450
            )
        )
        position = str(int(DIAL_POSITIONS['c'] / 15))
        text_width, _ = FONT.size(position)
        screen.blit(
            FONT.render(
                position,
                True,
                COLOURS['black']
            ),
            (
                550 - text_width / 2,
                450
            )
        )


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    direction = 'counterclocwise'
                else:
                    direction = 'clockwise'
                if dial_a.collidepoint(event.pos):
                    turn_a = direction
                if dial_b.collidepoint(event.pos):
                    turn_b = direction
                if dial_c.collidepoint(event.pos):
                    turn_c = direction
            if event.type == pygame.MOUSEBUTTONUP:
                turn_a = None
                turn_b = None
                turn_c = None

        if turn_a == 'clockwise':
            DIAL_POSITIONS['a'] -= 15 # 360 deg / 24 steps = 15 deg
            if DIAL_POSITIONS['a'] < 0:
                DIAL_POSITIONS['a'] = 360 - 15
        elif turn_a == 'counterclocwise':
            DIAL_POSITIONS['a'] += 15
            if DIAL_POSITIONS['a'] >= 360:
                DIAL_POSITIONS['a'] = 0

        if turn_b == 'clockwise':
            DIAL_POSITIONS['b'] -= 15 # 360 deg / 24 steps = 15 deg
            if DIAL_POSITIONS['b'] < 0:
                DIAL_POSITIONS['b'] = 360 - 15
        elif turn_b == 'counterclocwise':
            DIAL_POSITIONS['b'] += 15
            if DIAL_POSITIONS['b'] >= 360:
                DIAL_POSITIONS['b'] = 0

        if turn_c == 'clockwise':
            DIAL_POSITIONS['c'] -= 15 # 360 deg / 24 steps = 15 deg
            if DIAL_POSITIONS['c'] < 0:
                DIAL_POSITIONS['c'] = 360 - 15
        elif turn_c == 'counterclocwise':
            DIAL_POSITIONS['c'] += 15
            if DIAL_POSITIONS['c'] >= 360:
                DIAL_POSITIONS['c'] = 0

        pygame.display.flip()
        clock.tick(10)


if __name__ == '__main__':
    main()
