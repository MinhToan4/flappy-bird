# 🎮 Flappy Bird với Điều Khiển Bằng Cử Chỉ Tay - MediaPipe Hand Tracking

![Flappy Bird Game](doc/flappy.gif)
![MediaPipe Hand Tracking](doc/mediapipe.gif)

## 📖 Mô Tả

Đây là phiên bản đặc biệt của game Flappy Bird được điều khiển bằng cử chỉ tay thông qua công nghệ **MediaPipe Hand Tracking** của Google. Game hỗ trợ điều khiển bằng cả hai tay và có nhiều tính năng thú vị!

## ✨ Tính Năng Chính

### 🎯 Điều Khiển Đa Dạng
- **Điều khiển bằng cử chỉ tay**: Sử dụng MediaPipe để nhận diện cử chỉ tay qua camera
- **Hỗ trợ 2 tay**: Có thể điều khiển bằng một hoặc cả hai tay
- **Điều khiển bàn phím**: Phím Space hoặc mũi tên lên để nhảy
- **Tự động fallback**: Nếu không có camera hoặc MediaPipe, tự động chuyển sang chế độ bàn phím

### 🎮 Chế Độ Game
- **God Mode**: Chế độ bất tử (có thể bật/tắt)
- **Tắt tiếng**: Có thể tắt/bật âm thanh game
- **Hiển thị góc tay**: Hiển thị realtime góc cử chỉ của cả hai tay

### 🖐️ Cách Điều Khiển Bằng Tay
- **Ngưỡng góc**: 55 độ (có thể điều chỉnh)
- **Cách hoạt động**: Khi góc trung bình của các ngón tay vượt quá 55 độ, chim sẽ nhảy lên
- **Hỗ trợ 2 tay**: Chỉ cần một trong hai tay vượt ngưỡng là chim nhảy

## 🚀 Cài Đặt và Chạy Game

### 📋 Yêu Cầu Hệ Thống
- Python 3.7 trở lên (khuyến nghị Python 3.11)
- Camera web (không bắt buộc, có thể chơi bằng bàn phím)
- Windows/Linux/MacOS

### 📦 Cài Đặt Dependencies

#### Cách 1: Sử dụng Virtual Environment (Khuyến nghị)
```bash
# Tạo virtual environment
python -m venv .venv

# Kích hoạt virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Cài đặt các thư viện
pip install --upgrade pip
pip install -r requirements.txt
```

#### Cách 2: Cài Đặt Trực Tiếp
```bash
pip install mediapipe==0.10.14 opencv-python pygame numpy
```

#### Cách 3: Sử dụng Conda
```bash
conda create -n flappy-game python=3.11
conda activate flappy-game
pip install -r requirements.txt
```

### 🎯 Chạy Game
```bash
python main.py
```

## 🎮 Hướng Dẫn Chơi

### 🖱️ Điều Khiển Cơ Bản
- **Space** hoặc **↑**: Làm chim nhảy lên
- **ESC**: Thoát game

### 🖐️ Điều Khiển Bằng Tay
1. **Đặt tay trước camera**: Game sẽ tự động nhận diện đến 2 tay
2. **Cử chỉ nhảy**: Mở bàn tay rộng (góc > 55°) để làm chim nhảy
3. **Cử chỉ bình thường**: Nắm tay lại (góc < 55°) để chim rơi tự nhiên
4. **Theo dõi góc**: Xem góc realtime của từng tay trên cửa sổ camera

### 🎯 Mục Tiêu
- Điều khiển chim bay qua các ống nước
- Ghi điểm mỗi khi vượt qua một cặp ống
- Tránh va chạm với ống nước và mặt đất

## ⚙️ Cấu Hình Game

### 🔧 Các Tham Số Có Thể Điều Chỉnh

Trong file `main.py`, bạn có thể thay đổi:

```python
# Cài đặt âm thanh
IS_MUTED = True    # True: Tắt tiếng, False: Bật tiếng

# Chế độ bất tử
GOD_MODE = True    # True: Không chết, False: Chế độ bình thường

# Ngưỡng cử chỉ tay
GESTURE_THRESHOLD = 55  # Góc (độ) để kích hoạt nhảy

# Cài đặt game
FPS = 32                # Tốc độ khung hình
SCREENWIDTH = 289       # Độ rộng màn hình
SCREENHEIGHT = 511      # Độ cao màn hình
```

## 🛠️ Xử Lý Sự Cố

### ❌ Lỗi "ModuleNotFoundError: No module named 'mediapipe'"

**Giải pháp:**
```bash
# Cài đặt lại mediapipe
pip install --upgrade pip
pip install mediapipe==0.10.14

# Hoặc thử phiên bản khác
pip install mediapipe
```

### ❌ Lỗi "ModuleNotFoundError: No module named 'cv2'"

**Giải pháp:**
```bash
pip install opencv-python
```

### ❌ Không Tìm Thấy Camera

Game sẽ tự động:
- Thử tìm camera từ index 0-4
- Nếu không tìm thấy, chuyển sang chế độ bàn phím
- Hiển thị thông báo: "No camera found - running in keyboard-only mode"

### ❌ MediaPipe Không Hoạt Động

Game sẽ tự động:
- Chuyển sang chế độ mock (giả lập)
- Hiển thị: "[INFO] Using mock MediaPipe hand tracking"
- Vẫn có thể chơi bằng bàn phím

### ❌ Lỗi IndentationError

**Nguyên nhân:** File code bị lỗi định dạng
**Giải pháp:** Kiểm tra và sửa lại indentation trong file `main.py`

## 📁 Cấu Trúc Project

```
flappy-mediapipe/
├── main.py                 # File chính của game
├── utils_mediapipe.py      # MediaPipe hand tracking thật
├── utils_mediapipe_mock.py # MediaPipe giả lập (fallback)
├── requirements.txt        # Danh sách thư viện cần thiết
├── README.md              # File hướng dẫn này
├── doc/                   # Thư mục tài liệu
│   ├── flappy.gif        # Demo game
│   └── mediapipe.gif     # Demo hand tracking
└── gallery/              # Tài nguyên game
    ├── audio/           # File âm thanh
    │   ├── die.wav
    │   ├── hit.wav
    │   ├── point.wav
    │   ├── swoosh.wav
    │   └── wing.wav
    └── sprites/         # Hình ảnh game
        ├── background.png
        ├── base.png
        ├── bird.png
        ├── message.png
        ├── pipe.png
        └── 0.png - 9.png  # Số điểm
```

## 🔬 Chi Tiết Kỹ Thuật

### 🖐️ MediaPipe Hand Tracking
- **Framework**: Google MediaPipe
- **Số tay hỗ trợ**: Tối đa 2 tay
- **Thuật toán**: Tính góc trung bình của các khớp ngón tay
- **Ngưỡng mặc định**: 55 độ
- **Tần số xử lý**: 32 FPS

### 🎮 Game Engine
- **Framework**: Pygame
- **Vật lý**: Gravity-based với tốc độ và gia tốc
- **Collision Detection**: AABB (Axis-Aligned Bounding Box)
- **Rendering**: 2D sprite-based

### 📹 Camera Processing
- **Tự động tìm camera**: Quét từ index 0-4
- **Image processing**: Flip horizontal để mirror effect
- **Realtime display**: Hiển thị góc tay trên video

## 🤝 Đóng Góp

Chào mừng mọi đóng góp! Bạn có thể:
1. Fork project
2. Tạo feature branch
3. Commit changes
4. Push và tạo Pull Request

## 📄 Giấy Phép

Project này được phát triển cho mục đích học tập và giải trí.

## 🆘 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra phần "Xử Lý Sự Cố" ở trên
2. Đảm bảo đã cài đúng tất cả dependencies
3. Thử chạy trong virtual environment
4. Kiểm tra camera có hoạt động không

---

**Chúc bạn chơi game vui vẻ! 🎮✨**
Team Python CT01