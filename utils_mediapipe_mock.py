#### Import các thư viện cần thiết
import cv2  # Thư viện xử lý hình ảnh
import numpy as np  # Thư viện xử lý mảng số

# Lớp MediaPipeHand mock - giả lập chức năng nhận diện tay
class MediaPipeHand:
    def __init__(self, static_image_mode=True, max_num_hands=1):
        # Gọi constructor của lớp cha
        super(MediaPipeHand, self).__init__()
        # Số lượng tay tối đa để nhận diện
        self.max_num_hands = max_num_hands
        
        # Định nghĩa các tham số của tay
        self.param = []
        for i in range(max_num_hands):
            p = {
                'keypt'   : np.zeros((21,2)), # Điểm then chốt 2D trong tọa độ hình ảnh (pixel)
                'joint'   : np.zeros((21,3)), # Khớp 3D trong tọa độ tương đối
                'joint_3d': np.zeros((21,3)), # Khớp 3D trong tọa độ tuyệt đối (m)
                'class'   : 'Right', # Tay trái / phải
                'score'   : 0.9, # Xác suất dự đoán tay thuận
                'angle'   : np.ones(15) * 45, # Góc khớp - mặc định 45 độ
                'gesture' : None, # Loại cử chỉ tay
                'fps'     : -1, # Số khung hình mỗi giây
            }
            self.param.append(p)

    def forward(self, img):
        """
        Hàm forward mock giả lập việc nhận diện tay
        Trả về các tham số tay mock tĩnh (không tự động vỗ cánh)
        """
        # Trả về góc tĩnh dưới ngưỡng để ngăn tự động vỗ cánh
        # Người dùng chỉ có thể điều khiển qua bàn phím (SPACE/UP)
        static_angle = 30  # Dưới GESTURE_THRESHOLD là 55

        # Cập nhật góc mock thành giá trị tĩnh
        self.param[0]['angle'] = np.ones(15) * static_angle

        return self.param

    def draw2d(self, img, param):
        """
        Hàm vẽ mock hiển thị văn bản thay vì landmark của tay
        """
        # Nếu có tham số tay và tay được nhận diện
        if len(param) > 0 and param[0]['class'] is not None:
            # Hiển thị thông tin hand tracking mock
            cv2.putText(img, 'Mock Hand Tracking', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(img, f'Góc: {param[0]["angle"][0]:.1f}', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(img, 'Nhấn SPACE để vỗ cánh!', (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        return img
