import os
import cv2
from django.test import TestCase

from beautyai.faceDetection import detect_face, detect_landmarks
from beautyai.prediction import RecognitionError

# Create your tests here.
class BeautyAiTestCase(TestCase):
    def test_draw_face_landmarks(self):
        image_path = os.path.join(os.path.dirname(__file__), '..', 'beautyai/test', 'test1.jpg')
        face_rect, face_crop = detect_face(image_path)
        if face_rect is None or face_crop is None:
            raise RecognitionError("No se detectaron rostros en la imagen")
        landmarksImg, valid, _ = detect_landmarks(image_path)
        self.assertEqual(valid, True)
        cv2.imshow('Face landmarks', landmarksImg)
        cv2.waitKey(0)