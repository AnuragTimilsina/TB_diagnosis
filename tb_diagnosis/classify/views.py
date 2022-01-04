from django.contrib import messages
from django.shortcuts import render,redirect
import os
from django.core.files.storage import FileSystemStorage
from pathlib import Path

from .models import Person, Record, User
from django.contrib.auth.decorators import login_required



from keras.models import load_model
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
model_path = os.path.join(BASE_DIR, 'models/tb_diagnosis_model.h5')

model = load_model(model_path)


def fetchrecentreports(user):
    person=Person.objects.get(user=user)
    person_records=person.record_set.filter()
    if person_records.exists():
        person_records=person_records.order_by('-test_date')
        data = [[index+1, data] for index, data in enumerate(person_records)]
        return data
    else:
        return None
        

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
    prediction = int(prediction)
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
    if confidence >= 50:
        confidence_remarks = "Confidence: {} %".format(confidence)
    elif confidence < 50:
        confidence_remarks = "Confidence: {}%, Not confident about the image".format(
            confidence)
        label = " "
        remarks = " "

    return label, remarks, confidence_remarks


@login_required(login_url='login')
def predictImage(request):
    from keras.preprocessing.image import img_to_array, load_img
    from django.core.cache import cache
    from django.urls import reverse
    image_width = 512
    image_height = 512

    f = request.FILES['filePath']
    person=Person.objects.get(user=request.user)
    filepath='./media/'+person.user.username+'/'
    files=filepath+f.name
    if not person.record_set.filter(x_ray=files).exists():
        fs = FileSystemStorage(location=filepath)
        filePathName = fs.save(f.name, f)
        testimage = './media/'+person.user.username+'/'+filePathName

        original = load_img(testimage, target_size=(image_width, image_height))
        numpy_image = img_to_array(original)

        label, remarks, confidence = predict(model, numpy_image)
        records = Record.objects.create(lungs_status=label, remarks=remarks,
                     x_ray=testimage, person=person,confidence=confidence)
    else:
        import datetime
        record=Record.objects.get(x_ray=files)
        offset=datetime.timezone(datetime.timedelta(hours=5,minutes=45))
        record.test_date=datetime.datetime.now(offset)
        record.save()

    person_data=fetchrecentreports(request.user)
    filePathName=person_data[0][1].x_ray
    label=person_data[0][1].lungs_status
    remarks=person_data[0][1].remarks
    confidence=person_data[0][1].confidence
    context = {'filePathName': filePathName,
               'label': label, 'remarks': remarks, 'confidence': confidence}
    context['person_data']=person_data
    cache.delete(reverse('predictImage'))
    return render(request, "main/index.html", context)

def home(request):
    return render(request,'main/home.html')
        
@login_required(login_url='signin')
def index(request):
    heading = "X-ray TB diagonosis"
    person_data=fetchrecentreports(request.user)
    context = {'route': heading,'person_data':person_data}
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
    if request.user.is_authenticated:
        return redirect('index')
    from django.contrib.auth import authenticate, login
    if request.method=="GET":
        return render(request,'main/login.html')
    if request.method=="POST":
        email=request.POST['email']
        password = request.POST['password']
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
def Get_Report(request,id,*args,**kwargs):
    person=Person.objects.get(user=request.user)
    record=Record.objects.get(id=id)
    record.x_ray=record.x_ray[1:]
    context_data={'person':person,'record':record}
    return render(request, 'main/record.html',context_data)

@login_required(login_url='signin')
def logout(request):
    from django.contrib.auth import logout
    if request.user.is_authenticated:
        messages.info(request, "Logged Out Successfully")
        logout(request)
    return redirect('signin')


