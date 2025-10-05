"""
================================================================================
                            FLAPPY BIRD GAME - TỔNG QUAN
================================================================================

MÔ TẢ CHUNG:
------------
Đây là game Flappy Bird được điều khiển bằng tay (hand tracking) sử dụng MediaPipe,
hoặc có thể chơi bằng bàn phím. Game được viết bằng Python với thư viện Pygame.

CÁCH CHƠI:
----------
- Chim bay qua các ống mà không va chạm
- Điều khiển chim vỗ cánh để bay lên
- Ghi điểm khi đi qua ống thành công
- Game kết thúc khi va chạm với ống hoặc mặt đất

CÁCH ĐIỀU KHIỂN:
---------------
1. BÀN PHÍM:
   - Nhấn SPACE hoặc mũi tên LÊN để vỗ cánh

2. HAND TRACKING (nếu có camera):
   - Giơ tay lên cao (góc > 55 độ) để vỗ cánh
   - Hỗ trợ 2 tay, chỉ cần 1 tay là đủ

TÍNH NĂNG CHÍNH:
---------------
- Hand tracking với MediaPipe (hoặc mock nếu không có)
- Hệ thống âm thanh có thể tắt/bật
- Chế độ GOD MODE (chim không chết)
- Hiển thị góc tay trên camera
- Đồ họa 2D đơn giản với sprite

CẤU TRÚC CODE:
--------------
- welcomeScreen(): Màn hình chào mừng
- mainGame(): Logic game chính
- isCollide(): Kiểm tra va chạm
- getRandomPipe(): Tạo ống ngẫu nhiên
- main: Khởi tạo và vòng lặp chính

THƯ VIỆN SỬ DỤNG:
---------------
- pygame: Đồ họa và âm thanh game
- cv2 (OpenCV): Xử lý camera
- mediapipe: Hand tracking (hoặc mock)
- numpy: Xử lý mảng số

================================================================================
"""

# Import các thư viện cần thiết
import cv2  # Thư viện xử lý hình ảnh và camera
import sys  # Sử dụng sys.exit để thoát chương trình
import random  # Tạo số ngẫu nhiên
import pygame  # Thư viện game chính
import numpy as np  # Thư viện xử lý mảng số

from pygame.locals import *  # Import các hằng số cơ bản của pygame

# Thử import MediaPipe thật; nếu không được thì dùng mock
using_mock = False
try:
    from utils_mediapipe import MediaPipeHand
except Exception as e:
    from utils_mediapipe_mock import MediaPipeHand
    using_mock = True
    print("[INFO] Sử dụng mock MediaPipe hand tracking (MediaPipe thật không khả dụng):", e)

# Biến toàn cục cho game
FPS = 32  # Số khung hình mỗi giây
SCREENWIDTH = 289  # Chiều rộng màn hình
SCREENHEIGHT = 511  # Chiều cao màn hình
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))  # Tạo cửa sổ game
GROUNDY = SCREENHEIGHT * 0.8  # Vị trí Y của mặt đất
GAME_SPRITES = {}  # Từ điển chứa các sprite (hình ảnh) của game
GAME_SOUNDS = {}  # Từ điển chứa các âm thanh của game
IS_MUTED = False  # Tắt tất cả âm thanh nếu True
GOD_MODE = False  # Nếu True, chim không bao giờ chết
PLAYER = 'gallery/sprites/bird.png'  # Đường dẫn đến hình chim
BACKGROUND = 'gallery/sprites/background.png'  # Đường dẫn đến hình nền
PIPE = 'gallery/sprites/pipe.png'  # Đường dẫn đến hình ống

# Khởi tạo camera và MediaPipe
# Thử tìm camera khả dụng, bắt đầu từ index 0
cap = None
for i in range(5):  # Thử camera 0-4
    test_cap = cv2.VideoCapture(i)
    if test_cap.isOpened():
        ret, frame = test_cap.read()
        if ret:
            cap = test_cap
            print(f"Tìm thấy camera tại index {i}")
            break
        else:
            test_cap.release()
    else:
        test_cap.release()

if cap is None:
    print("Không tìm thấy camera - chạy ở chế độ chỉ bàn phím")

# Khởi tạo đối tượng MediaPipe cho hand tracking
hand = MediaPipeHand(static_image_mode=False, max_num_hands=2)

def welcomeScreen():
    """
    Hiển thị màn hình chào mừng với hình ảnh hướng dẫn
    """
    # Vị trí ban đầu của chim trên màn hình
    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
    # Vị trí của thông điệp chào mừng
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    messagey = int(SCREENHEIGHT*0.13)
    basex = 0  # Vị trí X của mặt đất
    while True:
        # Xử lý các sự kiện pygame
        for event in pygame.event.get():
            # Nếu người dùng nhấn nút đóng hoặc ESC, thoát game
            if event.type == QUIT or (event.type==KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # Nếu người dùng nhấn SPACE hoặc UP, bắt đầu game
            elif event.type==KEYDOWN and (event.key==K_SPACE or event.key == K_UP):
                return
            else:
                # Vẽ nền, chim, thông điệp và mặt đất
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
                SCREEN.blit(GAME_SPRITES['message'], (messagex,messagey ))
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                pygame.display.update()  # Cập nhật màn hình
                FPSCLOCK.tick(FPS)  # Giữ tốc độ khung hình


def mainGame():
    # Khởi tạo điểm số và vị trí chim
    score = 0
    playerx = int(SCREENWIDTH/5)  # Vị trí X của chim
    playery = int(SCREENWIDTH/2)  # Vị trí Y ban đầu của chim
    basex = 0  # Vị trí X của mặt đất

    # Tạo 2 ống ngẫu nhiên cho màn hình
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # Danh sách các ống trên (upper pipes)
    upperPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
    ]
    # Danh sách các ống dưới (lower pipes)
    lowerPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
    ]

    # Tốc độ di chuyển của ống
    pipeVelX = -4

    # Các thông số vật lý của chim
    playerVelY = -9  # Tốc độ Y ban đầu
    playerMaxVelY = 10  # Tốc độ Y tối đa
    playerMinVelY = -8  # Tốc độ Y tối thiểu
    playerAccY = 1  # Gia tốc Y

    playerFlapAccv = -8  # Tốc độ khi vỗ cánh
    playerFlapped = False  # True khi chim đang vỗ cánh
    GESTURE_THRESHOLD = 55  # Ngưỡng góc (độ) để kích hoạt vỗ cánh
    prev_angle_above = [False, False]  # Theo dõi trạng thái góc của 2 tay

    while True:
        # Reset góc cho 2 tay mỗi frame
        angles = [None, None]
        # Nếu có camera, xử lý hình ảnh để nhận diện tay
        if cap is not None:
            ret, img = cap.read()
            if ret:
                img = cv2.flip(img, 1)  # Lật hình ảnh ngang
                try:
                    param = hand.forward(img)  # Xử lý hand tracking
                except Exception as err:
                    print("[ERROR] Lỗi xử lý tay:", err)
                    param = []
                # Lấy góc cho từng tay (tối đa 2 tay)
                for i in range(min(2, len(param))):
                    if param[i]['class'] is not None:
                        angles[i] = float(np.mean(param[i]['angle']))
                img = hand.draw2d(img.copy(), param)  # Vẽ kết quả lên hình ảnh
                # Hiển thị góc của 2 tay trên hình ảnh
                cv2.putText(img, f"Góc trái: {angles[0] if angles[0] is not None else -1:.1f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
                cv2.putText(img, f"Góc phải: {angles[1] if angles[1] is not None else -1:.1f}", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
                cv2.imshow('Tay', img)  # Hiển thị cửa sổ camera
                cv2.waitKey(1)
        # Nếu không có camera hoặc dùng mock, chỉ lấy tay đầu tiên
        if (cap is None or using_mock) and 'param' not in locals():
            try:
                param = hand.forward(np.zeros((480,640,3), dtype=np.uint8))
                angles[0] = float(np.mean(param[0]['angle']))
            except Exception:
                angles[0] = None

        # Xử lý sự kiện pygame
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv  # Đặt tốc độ vỗ cánh
                    playerFlapped = True
                    if not IS_MUTED: GAME_SOUNDS['wing'].play()  # Phát âm thanh vỗ cánh

        # Xử lý cử chỉ tay để vỗ cánh (cho 2 tay, chỉ cần 1 tay vượt ngưỡng là nhảy)
        if cap is not None and not using_mock:
            for i in range(2):
                if angles[i] is not None:
                    angle_above = angles[i] > GESTURE_THRESHOLD  # Kiểm tra góc có vượt ngưỡng
                    if angle_above and not prev_angle_above[i] and playery > 0:
                        playerVelY = playerFlapAccv  # Đặt tốc độ vỗ cánh
                        playerFlapped = True
                        if not IS_MUTED: GAME_SOUNDS['wing'].play()  # Phát âm thanh vỗ cánh
                    prev_angle_above[i] = angle_above  # Cập nhật trạng thái trước

        # Kiểm tra va chạm
        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest and not GOD_MODE:
            return  # Kết thúc game nếu va chạm và không phải chế độ god

        # Kiểm tra điểm số
        playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2  # Vị trí giữa của chim
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2  # Vị trí giữa của ống
            if pipeMidPos<= playerMidPos < pipeMidPos +4:  # Chim đi qua ống
                score +=1
                print(f"Điểm của bạn là {score}")
                if not IS_MUTED: GAME_SOUNDS['point'].play()  # Phát âm thanh ghi điểm

        # Áp dụng trọng lực / tốc độ SAU vòng lặp ghi điểm (một lần mỗi frame)
        if playerVelY <playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY  # Tăng tốc độ do trọng lực
        if playerFlapped:
            playerFlapped = False  # Reset trạng thái vỗ cánh
        playerHeight = GAME_SPRITES['player'].get_height()
        # Cập nhật vật lý (loại bỏ ánh xạ trực tiếp từ góc sang Y)
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)
        # Giữ chim trong màn hình
        if playery < 0: playery = 0
        if playery > GROUNDY - playerHeight: playery = GROUNDY - playerHeight

        # Di chuyển ống sang trái
        for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Thêm ống mới khi ống đầu tiên sắp ra khỏi màn hình bên trái
        if 0<upperPipes[0]['x']<5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # Nếu ống ra khỏi màn hình, xóa nó
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Vẽ các sprite lên màn hình
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))  # Vẽ nền
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))  # Vẽ ống trên
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))  # Vẽ ống dưới

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))  # Vẽ mặt đất
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))  # Vẽ chim
        # Hiển thị điểm số
        myDigits = [int(x) for x in list(str(score))]  # Chuyển điểm thành danh sách chữ số
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()  # Tính tổng chiều rộng
        Xoffset = (SCREENWIDTH - width)/2  # Căn giữa

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))  # Vẽ từng chữ số
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()  # Cập nhật màn hình
        FPSCLOCK.tick(FPS)  # Giữ tốc độ khung hình


def isCollide(playerx, playery, upperPipes, lowerPipes):
    # Kiểm tra va chạm với mặt đất hoặc trần nhà
    if playery> GROUNDY - 25  or playery<0:
        if not GOD_MODE and not IS_MUTED: GAME_SOUNDS['hit'].play()  # Phát âm thanh va chạm
        return not GOD_MODE  # Trả về True nếu không phải chế độ god

    # Kiểm tra va chạm với ống trên
    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            if not GOD_MODE and not IS_MUTED: GAME_SOUNDS['hit'].play()  # Phát âm thanh va chạm
            return not GOD_MODE  # Trả về True nếu không phải chế độ god

    # Kiểm tra va chạm với ống dưới
    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            if not GOD_MODE and not IS_MUTED: GAME_SOUNDS['hit'].play()  # Phát âm thanh va chạm
            return not GOD_MODE  # Trả về True nếu không phải chế độ god

    return False  # Không có va chạm


def getRandomPipe():
    """
    Tạo vị trí của hai ống (một ống thẳng dưới và một ống xoay trên) để vẽ lên màn hình
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()  # Chiều cao của ống
    offset = SCREENHEIGHT/3  # Khoảng cách offset
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))  # Vị trí Y của ống dưới
    pipeX = SCREENWIDTH + 10  # Vị trí X ban đầu của ống
    y1 = pipeHeight - y2 + offset  # Vị trí Y của ống trên
    pipe = [
        {'x': pipeX, 'y': -y1}, # Ống trên (xoay 180 độ)
        {'x': pipeX, 'y': y2} # Ống dưới
    ]
    return pipe


if __name__ == "__main__":
    # Đây là điểm bắt đầu chính của game
    pygame.init()  # Khởi tạo tất cả các module của pygame
    FPSCLOCK = pygame.time.Clock()  # Đồng hồ để kiểm soát FPS
    pygame.display.set_caption('Flappy Bird by CodeWithHarry')  # Tiêu đề cửa sổ
    # Tải các sprite số (0-9)
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

    # Tải các sprite khác
    GAME_SPRITES['message'] =pygame.image.load('gallery/sprites/message.png').convert_alpha()  # Thông điệp chào mừng
    GAME_SPRITES['base'] =pygame.image.load('gallery/sprites/base.png').convert_alpha()  # Mặt đất
    GAME_SPRITES['pipe'] =(pygame.transform.rotate(pygame.image.load( PIPE).convert_alpha(), 180),  # Ống trên (xoay)
    pygame.image.load(PIPE).convert_alpha()  # Ống dưới
    )

    # Tải âm thanh game
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')  # Âm thanh chết
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')  # Âm thanh va chạm
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')  # Âm thanh ghi điểm
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')  # Âm thanh swoosh
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')  # Âm thanh vỗ cánh

    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()  # Nền game
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()  # Chim player

    # Vòng lặp chính của game
    while True:
        welcomeScreen()  # Hiển thị màn hình chào mừng cho đến khi người dùng nhấn nút
        mainGame()  # Chạy hàm game chính
