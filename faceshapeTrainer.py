import tensorflow as tf
import os
import datetime


batch_size = 32
img_height = 480
img_width = 480

# Obtiene el directorio del archivo actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construye la ruta al directorio de datasets
dataset_dir = os.path.join(current_dir, 'processed_dataset/faceshape')

train_ds = tf.keras.utils.image_dataset_from_directory(
  dataset_dir,
  validation_split=0.2,
  subset="training",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

val_ds = tf.keras.utils.image_dataset_from_directory(
  dataset_dir,
  validation_split=0.2,
  subset="validation",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

class_names = train_ds.class_names

# RED NEURONAL
""" 
  Este modelo parece funcionar mejor con una limitada
  cantidad de datos, esto debido a que previamente se
  han preprocesado las imágenes para enfocarlas únicamente
  en el rostro
"""
""" model = tf.keras.Sequential([
    tf.keras.layers.Flatten(input_shape=(480, 480, 3)), # a negro
    tf.keras.layers.Dense(50, activation=tf.nn.relu),
    tf.keras.layers.Dense(50, activation=tf.nn.relu),
    tf.keras.layers.Dense(50, activation=tf.nn.relu),
    tf.keras.layers.Dense(50, activation=tf.nn.relu),
    tf.keras.layers.Dense(50, activation=tf.nn.relu),
    tf.keras.layers.Dense(5, activation='softmax')
])  """

""" 
  # RED CONVOLUCIONAL
  # Añadir Dropout en el modelo
  Si se decide utilizar este modelo probablemente se deba aumentar 
  la cantidad de datos de entrenamiento, teniendo en cuenta que este tiene
  un costo computacional mayor
"""

model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(480, 480, 3)),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(5, activation='softmax')
])

# PARA EVITAR SOBREAJUSTE
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Guardar solo el mejor modelo
model_checkpoint = tf.keras.callbacks.ModelCheckpoint(
  os.path.join(current_dir, 'faceshape_model.keras'),
  monitor='val_loss',  # Métrica a monitorear
  save_best_only=True,  # Guardar solo el mejor modelo
  mode='min'  # El modo 'min' guarda el modelo cuando la métrica monitorizada disminuye
)
log_dir = os.path.join(current_dir, "logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)


model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy'],
)

#Entrenar
epochs = 30
history = model.fit(
  train_ds, epochs=epochs, batch_size=batch_size,
  validation_data=val_ds,
  callbacks=[tensorboard_callback]
  # callbacks=[early_stopping, model_checkpoint]
)
  
model.save(os.path.join(current_dir, 'faceshape_model.keras'))