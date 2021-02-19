from django.contrib import messages
from django.shortcuts import render, redirect
import os
from django.core.files.storage import FileSystemStorage
from pathlib import Path

from .models import *
from django.contrib.auth.decorators import login_required


import tensorflow as tf
from keras.models import load_model
from keras.preprocessing import image
from keras.preprocessing.image import img_to_array, load_img
import numpy as np
import json

BASE_DIR = Path(__file__).resolve().parent.parent
model_path = os.path.join(BASE_DIR, 'models/tb_diagnosis_model.h5')

model = load_model(model_path)


def home(request):
    text = "Home Page"
    context = {'text': text}
    return render(request, 'main/home.html', context)


def label_remarks(prediction):
    max_prob_val = np.argsort(prediction)[-1][-1]
    remarks = ' '
    if max_prob_val == 0:
        remarks = "Sorry, you have been infected with Tuberculosis."
    elif max_prob_val == 1:
        remarks = "You are not infected with Tuberculosis, but your lungs is not healthy."
    elif max_prob_val == 2:
        remarks = "You are not infected with tuberculosis, and your lungs is healthy."
    return remarks


def turn_predictions_to_labels(prediction):
    predection = int(prediction)
    if prediction == 0:
        label = "Tuberculosis"
    elif prediction == 1:
        label = "Sick"
    elif prediction == 2:
        label = "Healthy"
    return label


def calculate_confidence(prediction):
    pre = np.argmax(prediction)
    confidence = prediction[0][pre]
    confidence = int(confidence)
    return confidence


def predict(model, image):
    prediction = model.predict(np.array([image]))
    max_prob_val = np.argmax(prediction)
    label = turn_predictions_to_labels(max_prob_val)
    remarks = label_remarks(prediction)
    confidence = calculate_confidence(prediction)

    if confidence > 100:
        confidence = 100
    if confidence >= 20:
        confidence_remarks = "Confidence: {} %".format(confidence)
    elif confidence < 20:
        confidence_remarks = "Confidence: {}%, Not confident about the image".format(confidence)
        label = " "
        remarks = " "

    return label, remarks, confidence_remarks


#@login_required(login_url='login')
def predictImage(request):
    image_width = 512
    image_height = 512

    f = request.FILES['filePath']
    fs = FileSystemStorage()
    filePathName = fs.save(f.name, f)
    filePathName = fs.url(filePathName)
    testimage = '.'+filePathName

    original = load_img(testimage, target_size=(image_width, image_height))
    numpy_image = img_to_array(original)

    label, remarks, confidence = predict(model, numpy_image)

    context = {'filePathName': filePathName,
               'label': label, 'remarks': remarks, 'confidence': confidence}
    return render(request, "main/index.html", context)


#@login_required(login_url='login')
def index(request):
    heading = "X-ray TB diagonosis"
    context = {'route': heading}
    return render(request, 'main/index.html', context)
