import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np

BaseOptions = mp.tasks.BaseOptions
ImageSegmenter = mp.tasks.vision.ImageSegmenter
ImageSegmenterOptions = mp.tasks.vision.ImageSegmenterOptions
VisionRunningMode = mp.tasks.vision.RunningMode

model_path = os.path.join(os.path.dirname(__file__), 'hair_segmenter.tflite')
base_options = BaseOptions(model_asset_path=model_path)

# Create a image segmenter instance with the image mode:
options = ImageSegmenterOptions(
    base_options=base_options,
    running_mode=VisionRunningMode.IMAGE,
    output_category_mask=True,
    output_confidence_masks=True
    )

def segment_hair(image_path, color, output_path):
    # Load the input image from an image file.
    with python.vision.ImageSegmenter.create_from_options(options) as segmenter:
        image = mp.Image.create_from_file(image_path)
        segmentation_result = segmenter.segment(image)
        category_mask = segmentation_result.category_mask
        image_data = cv2.cvtColor(image.numpy_view(), cv2.COLOR_BGR2RGB)
        preprocessed = process_segmentation_result(image_data, segmentation_result)
        final_result = recolor_hair(preprocessed, color)
        if (output_path != ''):
          save_final_image(final_result, output_path)
        

def process_segmentation_result(image, result):
    height, width = image.shape[:2]
    mask = result.category_mask.numpy_view()
    mask_binary = np.where(mask == 1, 255, 0).astype(np.uint8)
    return {
        'original_image': image,
        'mask': mask_binary,
        'width': width,
        'height': height
    }

def recolor_hair(result, hex_color):
        rgb = hex_to_rgb(hex_color)
        
        src = result['original_image']
        mask = result['mask']
        
        # Convert to LAB color space
        lab_img = cv2.cvtColor(src, cv2.COLOR_RGB2LAB)
        
        # Create a color image in LAB
        # Crear un array 2D de un solo pixel
        # Invertimos de rgb a bgr por motivo de opencv
        rgb_list_color = rgb[:3]
        rgb_list_color.reverse()
        rgb_color = np.uint8([[rgb_list_color]])  

        lab_color = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2LAB)  # Convertir a LAB
        color_lab = np.full(src.shape, lab_color, dtype=np.uint8)  # Crear la imagen llena
        
        # Combine the original L channel with new a and b channels
        new_lab = lab_img.copy()
        new_lab[:,:,1:] = cv2.addWeighted(lab_img[:,:,1:], 0.2, color_lab[:,:,1:], 0.8, 0)
        
        # Convert back to RGB
        dst = cv2.cvtColor(new_lab, cv2.COLOR_LAB2RGB)
        
        # Apply the mask
        mask_3d = np.repeat(mask[:,:,np.newaxis], 3, axis=2)
        final_result = np.where(mask_3d == 255, dst, src)
        
        return final_result

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)] + [255]

def save_final_image(image, output_path):
    cv2.imwrite(output_path + '/recolor_hair.jpg', image)
        
