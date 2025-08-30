import cv2
import sys # We will use sys.exit to exit the program
import random # For generating random numbers
import pygame
import numpy as np

from pygame.locals import * # Basic pygame imports

# Try to import real MediaPipe wrapper; fallback to mock
using_mock = False
try:
    from utils_mediapipe import MediaPipeHand
except Exception as e:
    from utils_mediapipe_mock import MediaPipeHand
    using_mock = True
    print("[INFO] Using mock MediaPipe hand tracking (real mediapipe not available):", e)


# Global Variables for the game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
IS_MUTED = True  # Mute all sounds if True
GOD_MODE = True   # If True, bird never dies
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'

# Load Classes for Hand Tracking
# Try to find an available camera, starting from index 0
cap = None
for i in range(5):  # Try cameras 0-4
    test_cap = cv2.VideoCapture(i)
    if test_cap.isOpened():
        ret, frame = test_cap.read()
        if ret:
            cap = test_cap
            print(f"Found camera at index {i}")
            break
        else:
            test_cap.release()
    else:
        test_cap.release()

if cap is None:
    print("No camera found - running in keyboard-only mode")

hand = MediaPipeHand(static_image_mode=False, max_num_hands=2)

def welcomeScreen():
    """
    Shows welcome images on the screen
    """
    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    messagey = int(SCREENHEIGHT*0.13)
    basex = 0
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT or (event.type==KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # If the user presses space or up key, start the game for them
            elif event.type==KEYDOWN and (event.key==K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
                SCREEN.blit(GAME_SPRITES['message'], (messagex,messagey ))
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def mainGame():
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENWIDTH/2)
    basex = 0

    # Create 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # my List of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
    ]
    # my List of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -8 # velocity while flapping
    playerFlapped = False # It is true only when the bird is flapping
    GESTURE_THRESHOLD = 55  # angle (deg) above which we trigger a flap
    prev_angle_above = [False, False]  # cho 2 tay

    while True:
        angles = [None, None]  # Reset mỗi frame cho 2 tay
        if cap is not None:
            ret, img = cap.read()
            if ret:
                img = cv2.flip(img, 1)
                try:
                    param = hand.forward(img)
                except Exception as err:
                    print("[ERROR] Hand forward error:", err)
                    param = []
                # Vẽ và lấy góc cho từng tay
                for i in range(min(2, len(param))):
                    if param[i]['class'] is not None:
                        angles[i] = float(np.mean(param[i]['angle']))
                img = hand.draw2d(img.copy(), param)
                # Hiển thị góc của 2 tay
                cv2.putText(img, f"Angle L: {angles[0] if angles[0] is not None else -1:.1f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
                cv2.putText(img, f"Angle R: {angles[1] if angles[1] is not None else -1:.1f}", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
                cv2.imshow('Hand', img)
                cv2.waitKey(1)
        # Nếu không có camera hoặc dùng mock, chỉ lấy tay đầu tiên
        if (cap is None or using_mock) and 'param' not in locals():
            try:
                param = hand.forward(np.zeros((480,640,3), dtype=np.uint8))
                angles[0] = float(np.mean(param[0]['angle']))
            except Exception:
                angles[0] = None

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    if not IS_MUTED: GAME_SOUNDS['wing'].play()

        # Gesture-based flap (cho 2 tay, chỉ cần 1 tay vượt ngưỡng là nhảy)
        if cap is not None and not using_mock:
            for i in range(2):
                if angles[i] is not None:
                    angle_above = angles[i] > GESTURE_THRESHOLD
                    if angle_above and not prev_angle_above[i] and playery > 0:
                        playerVelY = playerFlapAccv
                        playerFlapped = True
                        if not IS_MUTED: GAME_SOUNDS['wing'].play()
                    prev_angle_above[i] = angle_above

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes) # This function will return true if the player is crashed
        if crashTest and not GOD_MODE:
            return

        #check for score
        playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
            if pipeMidPos<= playerMidPos < pipeMidPos +4:
                score +=1
                print(f"Your score is {score}")
                if not IS_MUTED: GAME_SOUNDS['point'].play()
        # Apply gravity / velocity AFTER scoring loop (once per frame)
        if playerVelY <playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        # Physics update only (remove direct angle->y mapping)
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)
        # Clamp playery inside screen
        if playery < 0: playery = 0
        if playery > GROUNDY - playerHeight: playery = GROUNDY - playerHeight

        # move pipes to the left
        for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0<upperPipes[0]['x']<5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # if the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Lets blit our sprites now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width)/2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery> GROUNDY - 25  or playery<0:
        if not GOD_MODE and not IS_MUTED: GAME_SOUNDS['hit'].play()
        return not GOD_MODE

    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            if not GOD_MODE and not IS_MUTED: GAME_SOUNDS['hit'].play()
            return not GOD_MODE

    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            if not GOD_MODE and not IS_MUTED: GAME_SOUNDS['hit'].play()
            return not GOD_MODE

    return False


def getRandomPipe():
    """
    Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT/3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1}, #upper Pipe
        {'x': pipeX, 'y': y2} #lower Pipe
    ]
    return pipe


if __name__ == "__main__":
    # This will be the main point from where our game will start
    pygame.init() # Initialize all pygame's modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird by CodeWithHarry')
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),
    )

    GAME_SPRITES['message'] =pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] =pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] =(pygame.transform.rotate(pygame.image.load( PIPE).convert_alpha(), 180),
    pygame.image.load(PIPE).convert_alpha()
    )

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    while True:
        welcomeScreen() # Shows welcome screen to the user until he presses a button
        mainGame() # This is the main game function
