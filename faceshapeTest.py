from matplotlib import pyplot as plt
import tensorflow as tf
import cv2
import numpy as np
import os

from faceDetection import detect_face, maskLandmarks

# Deshabilitar GPU - 
# Habilitar en caso de contar con una tarjeta compatible
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  

# Obtiene el directorio del archivo actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construye la ruta al directorio de datasets
model_dir = os.path.join(current_dir, 'faceshape_model.keras')

model = tf.keras.models.load_model(model_dir)

def categorize(path):
    try:
        
        # Detectar el rostro
        face_rect, face_crop = detect_face(path)

        if face_rect is None or face_crop is None:
            print(f"No se detectaron caras en la imagen {path}")
            return None
 
        # Convertir la imagen recortada a formato adecuado para el modelo
        img_normalized = face_crop.astype(float) / 255.0
        
        # Redimensionar la imagen si es necesario (depende del modelo)
        img_resized = cv2.resize(img_normalized, (480, 480))
        
        # Realizar la predicción
        prediction = model.predict(img_resized.reshape(-1, 480, 480, 3))
        
        # Obtener la clase predicha
        predicted_class = np.argmax(prediction[0], axis=-1)        
        plt.show()
        
        return predicted_class
    except Exception as e:
        print(f"Error durante la categorización: {e}")
        return None

# ['heart', 'oblong', 'oval', 'round', 'square']
# 0: heart
# 1: oblong  
# 2: oval
# 3: round
# 4: square    
test_file = os.path.join(current_dir, 'test/oval.jpg')
if (os.path.exists(test_file)):
    res = categorize(test_file)
    print(res)
else:
    print(f"El archivo {test_file} no existe.")
