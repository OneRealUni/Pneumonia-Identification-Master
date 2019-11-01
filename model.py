
import tensorflow as tf
import cv2
import numpy as np

def initialize_model():
    model = tf.keras.models.load_model('./trained_model/v3_weights.h5')
    return model

def get_image(b_img):
    image = np.asarray(bytearray(b_img), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    img = cv2.resize(image, (224,224))
    img=img/255
    return img

def classify(b_img):

    img = get_image(b_img)
    model = initialize_model()
    prediction = model.predict_proba([[img]])
    print("\n\nin_model :\t --> \t{}\n\n".format(prediction))
    x = np.argmax(prediction)
    return "PNEUMONIA" if x == 1 else "NORMAL"
