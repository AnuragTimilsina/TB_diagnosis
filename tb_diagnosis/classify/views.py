from django.contrib import messages
from django.shortcuts import render,redirect
import os
from django.core.files.storage import FileSystemStorage
from pathlib import Path

from .models import Person, Record
from django.contrib.auth.models import User
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
        confidence_remarks = "Confidence: {}%, Not confident about the image".format(
            confidence)
        label = " "
        remarks = " "

    return label, remarks, confidence_remarks


@login_required(login_url='login')
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

    img_path = filePathName.split('/')[2]
    print(img_path)

    user=User.objects.get(username=request.user.username)
    person=Person.objects.get(user=user)
    records = Record(lungs_status=label, remarks=remarks,
                     x_ray=img_path, person=person)
    records.save()

    return render(request, "main/index.html", context)

def home(request):
    return render(request,'main/home.html')
        
@login_required(login_url='signin')
def index(request):
    heading = "X-ray TB diagonosis"
    context = {'route': heading}
    return render(request, 'main/index.html', context)

def validateEmail(email):
    from django.core import validators
    from django.core.exceptions import ValidationError
    try:
        validators.validate_email(email)
        return True
    except ValidationError:
        return False

def Sign_In(request):
    from django.contrib.auth import authenticate, login
    if request.method=="GET":
        return render(request,'main/login.html')
    if request.method=="POST":
        email=request.POST['email']
        password = request.POST.get('password', None)
        user=User.objects.filter(email=email)
        if user.exists():
            person=authenticate(username=user[0].username,password=password)
            login(request,person)
        else:
            messages.error(request, message="Person not found, please retry")
            return redirect('signin')
        return redirect('index')


def Sign_Up(request):

    from django.contrib.auth import authenticate, login

    if request.method == "GET":
        return render(request, 'main/signup.html')

    if request.method == "POST":
        from django.contrib import messages

        firstname=request.POST['firstname']
        lastname=request.POST['lastname']
        email=request.POST['email']
        preuser=User.objects.filter(email=email)
        if preuser.exists():
            messages.error(request,message="Email Already Taken")
            return redirect('signup')
        if not validateEmail(email):
            messages.error(request, message="Enter a valid email")
            return redirect('signup')
        password = request.POST['password']
        age = request.POST['age']
        address = request.POST['address']
        bloodgroup = request.POST['bloodgroup']
        is_doctor = request.POST['customRadio']
        doctor = False
        if int(is_doctor) == 1:
            doctor = True
        phoneno = request.POST['phoneno']
        if not phoneno.isdigit():
            messages.error(request, message="Please Use Only Numbers.")
            return redirect('signup')

        username=firstname+phoneno
        user=User.objects.create_user(username=username.lower(),first_name=firstname,last_name=lastname,email=email,password=password)
        user.save(False)
        person=Person.objects.create(user=user,blood_group=bloodgroup,phoneno=phoneno,address=address,age=age,is_doctor=doctor)
        person.save(True)
        return redirect('index')

@login_required(login_url='signin')
def logout(request):
    from django.contrib.auth import logout
    if request.user.is_authenticated:
        messages.info(request,"Logged Out Successfully")
        logout(request)
    return redirect('signin')


