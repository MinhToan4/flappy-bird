###############################################################################
### Mock wrapper for Google MediaPipe hand pose estimation
### This is a temporary solution for Python 3.13.5 compatibility
###############################################################################

import cv2
import numpy as np


class MediaPipeHand:
    def __init__(self, static_image_mode=True, max_num_hands=1):
        super(MediaPipeHand, self).__init__()
        self.max_num_hands = max_num_hands
        
        # Define hand parameter
        self.param = []
        for i in range(max_num_hands):
            p = {
                'keypt'   : np.zeros((21,2)), # 2D keypt in image coordinate (pixel)
                'joint'   : np.zeros((21,3)), # 3D joint in relative coordinate
                'joint_3d': np.zeros((21,3)), # 3D joint in absolute coordinate (m)
                'class'   : 'Right', # Left / right hand
                'score'   : 0.9, # Probability of predicted handedness
                'angle'   : np.ones(15) * 45, # Joint angles - default to 45 degrees
                'gesture' : None, # Type of hand gesture
                'fps'     : -1, # Frame per sec
            }
            self.param.append(p)

    def forward(self, img):
        """
        Mock forward function that simulates hand detection
        Returns static mock hand parameters (no auto-flapping)
        """
        # Return static angle below threshold to prevent auto-flapping
        # Users can only control via keyboard (SPACE/UP)
        static_angle = 30  # Below GESTURE_THRESHOLD of 55

        # Update the mock angle to static value
        self.param[0]['angle'] = np.ones(15) * static_angle

        return self.param

    def draw2d(self, img, param):
        """
        Mock draw function that displays text instead of hand landmarks
        """
        if len(param) > 0 and param[0]['class'] is not None:
            # Display mock hand tracking info
            cv2.putText(img, 'Mock Hand Tracking', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(img, f'Angle: {param[0]["angle"][0]:.1f}', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(img, 'Press SPACE to flap!', (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        return img
