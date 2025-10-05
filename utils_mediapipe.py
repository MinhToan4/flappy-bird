###############################################################################
### Wrapper cho Google MediaPipe hand pose estimation
### https://github.com/google/mediapipe
###############################################################################

# Import các thư viện cần thiết
import cv2  # Thư viện xử lý hình ảnh
import numpy as np  # Thư viện xử lý mảng số
import mediapipe as mp  # Thư viện MediaPipe cho AI

# Lớp MediaPipeHand - wrapper cho nhận diện tay của MediaPipe
class MediaPipeHand:
    def __init__(self, static_image_mode=True, max_num_hands=1):
        # Gọi constructor của lớp cha
        super(MediaPipeHand, self).__init__()
        # Số lượng tay tối đa để nhận diện
        self.max_num_hands = max_num_hands

        # Truy cập MediaPipe Solutions Python API
        mp_hands = mp.solutions.hands

        # Khởi tạo MediaPipe Hands
        # static_image_mode:
        #   Cho xử lý video đặt thành False:
        #   Sẽ sử dụng frame trước để định vị tay, giảm độ trễ
        #   Cho hình ảnh không liên quan đặt thành True:
        #   Cho phép nhận diện tay chạy trên mọi hình ảnh đầu vào
        
        # max_num_hands:
        #   Số lượng tay tối đa để nhận diện
        
        # min_detection_confidence:
        #   Giá trị confidence [0,1] từ model nhận diện tay
        #   để việc nhận diện được coi là thành công
        
        # min_tracking_confidence:
        #   Giá trị confidence tối thiểu [0,1] từ model theo dõi landmark
        #   để landmark tay được coi là được theo dõi thành công,
        #   nếu không thì nhận diện tay sẽ được gọi tự động ở frame tiếp theo.
        #   Đặt cao hơn có thể tăng độ robust nhưng tăng độ trễ.
        #   Bỏ qua nếu static_image_mode là true, khi đó nhận diện tay chạy trên mọi hình ảnh.

        self.pipe = mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

        # Định nghĩa các tham số của tay
        self.param = []
        for i in range(max_num_hands):
            p = {
                'keypt'   : np.zeros((21,2)), # Điểm then chốt 2D trong tọa độ hình ảnh (pixel)
                'joint'   : np.zeros((21,3)), # Khớp 3D trong tọa độ tương đối
                'joint_3d': np.zeros((21,3)), # Khớp 3D trong tọa độ tuyệt đối (m)
                'class'   : None, # Tay trái / phải
                'score'   : 0, # Xác suất dự đoán tay thuận (luôn >0.5, tay ngược=1-score)
                'angle'   : np.zeros(15), # Góc khớp
                'gesture' : None, # Loại cử chỉ tay
                'fps'     : -1, # Số khung hình mỗi giây
                # https://github.com/google/mediapipe/issues/1351
                # 'visible' : np.zeros(21), # Tầm nhìn: Xác suất [0,1] có thể nhìn thấy (có mặt và không bị che) trong hình ảnh
                # 'presence': np.zeros(21), # Sự hiện diện: Xác suất [0,1] có mặt trong hình ảnh hoặc nằm ngoài hình ảnh
            }
            self.param.append(p)

        # Định nghĩa cây động học liên kết các điểm then chốt để tạo khung xương
        self.ktree = [0,          # Cổ tay
                      0,1,2,3,    # Ngón cái
                      0,5,6,7,    # Ngón trỏ
                      0,9,10,11,  # Ngón giữa
                      0,13,14,15, # Ngón áp út
                      0,17,18,19] # Ngón út

        # Định nghĩa màu cho 21 điểm then chốt
        self.color = [[0,0,0], # Cổ tay đen
                      [255,0,0],[255,60,0],[255,120,0],[255,180,0], # Ngón cái
                      [0,255,0],[60,255,0],[120,255,0],[180,255,0], # Ngón trỏ
                      [0,255,0],[0,255,60],[0,255,120],[0,255,180], # Ngón giữa
                      [0,0,255],[0,60,255],[0,120,255],[0,180,255], # Ngón áp út
                      [0,0,255],[60,0,255],[120,0,255],[180,0,255]] # Ngón út
        self.color = np.asarray(self.color)
        self.color_ = self.color / 255 # Cho Open3D RGB
        self.color[:,[0,2]] = self.color[:,[2,0]] # Cho OpenCV BGR
        self.color = self.color.tolist()            


    def result_to_param(self, result, img):
        # Chuyển đổi kết quả tay MediaPipe thành tham số của riêng mình
        img_height, img_width, _ = img.shape

        # Reset tham số
        for p in self.param:
            p['class'] = None

        if result.multi_hand_landmarks is not None:
            # Duyệt qua các tay khác nhau
            for i, res in enumerate(result.multi_handedness):
                if i>self.max_num_hands-1: break # Lưu ý: Cần kiểm tra nếu vượt quá số tay tối đa
                self.param[i]['class'] = res.classification[0].label
                self.param[i]['score'] = res.classification[0].score

            # Duyệt qua các tay khác nhau
            for i, res in enumerate(result.multi_hand_landmarks):
                if i>self.max_num_hands-1: break # Lưu ý: Cần kiểm tra nếu vượt quá số tay tối đa
                # Duyệt qua 21 landmark cho mỗi tay
                for j, lm in enumerate(res.landmark):
                    self.param[i]['keypt'][j,0] = lm.x * img_width # Chuyển tọa độ chuẩn hóa thành pixel [0,1] -> [0,width]
                    self.param[i]['keypt'][j,1] = lm.y * img_height # Chuyển tọa độ chuẩn hóa thành pixel [0,1] -> [0,height]

                    self.param[i]['joint'][j,0] = lm.x
                    self.param[i]['joint'][j,1] = lm.y
                    self.param[i]['joint'][j,2] = lm.z

                    # Bỏ qua https://github.com/google/mediapipe/issues/1320
                    # self.param[i]['visible'][j] = lm.visibility
                    # self.param[i]['presence'][j] = lm.presence

                # Chuyển đổi khớp 3D tương đối thành góc
                self.param[i]['angle'] = self.convert_3d_joint_to_angle(self.param[i]['joint'])

        return self.param


    def convert_3d_joint_to_angle(self, joint):
        # Lấy vector hướng của xương từ parent đến child
        v1 = joint[[0,1,2,3,0,5,6,7,0,9,10,11,0,13,14,15,0,17,18,19],:] # Khớp parent
        v2 = joint[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],:] # Khớp child
        v = v2 - v1 # [20,3]
        # Chuẩn hóa v
        v = v/np.linalg.norm(v, axis=1)[:, np.newaxis]

        # Lấy góc sử dụng arcos của tích vô hướng
        angle = np.arccos(np.einsum('nt,nt->n',
            v[[0,1,2,4,5,6,8,9,10,12,13,14,16,17,18],:], 
            v[[1,2,3,5,6,7,9,10,11,13,14,15,17,18,19],:])) # [15,]

        return np.degrees(angle) # Chuyển radian thành độ


    def draw2d(self, img, param):
        # Lấy kích thước hình ảnh
        img_height, img_width, _ = img.shape

        # Duyệt qua các tay khác nhau
        for p in param:
            if p['class'] is not None:
                # # Gắn nhãn tay trái hoặc phải
                # x = int(p['keypt'][0,0]) - 30
                # y = int(p['keypt'][0,1]) + 40
                # # cv2.putText(img, '%s %.3f' % (p['class'], p['score']), (x, y), 
                # cv2.putText(img, '%s' % (p['class']), (x, y), 
                #     cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2) # Đỏ
                
                # Gắn nhãn góc trung bình
                x = int(p['keypt'][0,0]) - 30
                y = int(p['keypt'][0,1]) + 40
                # cv2.putText(img, '%s %.3f' % (p['class'], p['score']), (x, y), 
                cv2.putText(img, 'Góc TB %d độ' % (np.mean(p['angle'])), (x, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2) # Đỏ
                
                # Duyệt qua điểm then chốt cho mỗi tay
                for i in range(21):
                    x = int(p['keypt'][i,0])
                    y = int(p['keypt'][i,1])
                    if x>0 and y>0 and x<img_width and y<img_height:
                        # Vẽ khung xương
                        start = p['keypt'][self.ktree[i],:]
                        x_ = int(start[0])
                        y_ = int(start[1])
                        if x_>0 and y_>0 and x_<img_width and y_<img_height:
                            cv2.line(img, (x_, y_), (x, y), self.color[i], 2) 

                        # Vẽ điểm then chốt
                        cv2.circle(img, (x, y), 5, self.color[i], -1)
                        # cv2.circle(img, (x, y), 3, self.color[i], -1)

                        # # Đánh số điểm then chốt
                        # cv2.putText(img, '%d' % (i), (x, y), 
                        #     cv2.FONT_HERSHEY_SIMPLEX, 1, self.color[i])

                        # # Gắn nhãn tầm nhìn và sự hiện diện
                        # cv2.putText(img, '%.1f, %.1f' % (p['visible'][i], p['presence'][i]),
                        #     (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, self.color[i])
                
                # Gắn nhãn cử chỉ
                if p['gesture'] is not None:
                    size = cv2.getTextSize(p['gesture'].upper(), 
                        # cv2.FONT_HERSHEY_SIMPLEX, 2, 2)[0]
                        cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                    x = int((img_width-size[0]) / 2)
                    cv2.putText(img, p['gesture'].upper(),
                        # (x, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 2)
                        (x, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

                    # Gắn nhãn góc khớp
                    self.draw_joint_angle(img, p)

            # Gắn nhãn fps
            if p['fps']>0:
                cv2.putText(img, 'FPS: %.1f' % (p['fps']),
                    (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)   

        return img


    def forward(self, img):
        # Tiền xử lý hình ảnh
        # img = cv2.flip(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Trích xuất kết quả tay
        result = self.pipe.process(img)

        # Chuyển đổi kết quả tay thành tham số của riêng mình
        param = self.result_to_param(result, img)

        return param

