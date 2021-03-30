import os
from django.core.files.storage import FileSystemStorage
from pathlib import Path

from classify.models import Person, Record, User
from keras.models import load_model
import numpy as np
from django.conf import settings


#DRF components:
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

#importing all regular views helper functions
from classify.views import label_remarks, turn_predictions_to_labels, calculate_confidence, predict

BASE_DIR = Path(__file__).resolve().parent.parent
model_path = os.path.join(BASE_DIR, 'models/tb_diagnosis_model.h5')

model = load_model(model_path)


def upload_image(request):

    f = request.FILES['image']
    fs = FileSystemStorage()
    filePathName = fs.save(f.name, f)
    filePathName = fs.url(filePathName)
    testimage = '.'+filePathName

    return testimage, filePathName


def predictImage(testimage, filePathName): 
    from keras.preprocessing.image import img_to_array, load_img
    image_width = 512
    image_height = 512

    original = load_img(testimage, target_size=(image_width, image_height))
    numpy_image = img_to_array(original)

    label, remarks, confidence = predict(model, numpy_image)

    return label, remarks, confidence


class Image(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        testimage, filePathName = upload_image(request=request)
        label, remarks, confidence = predictImage(testimage, filePathName)
        response_data = {"label" : label,
                         "remarks" : remarks,
                         "confidence" : confidence,
                        }
        return Response(response_data,
                        status=status.HTTP_202_ACCEPTED)


# All about authentication and authorization: 

from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, \
                         changePasswordSerializer, UpdateUserSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from rest_framework import generics


class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class changePasswordView(generics.UpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = changePasswordSerializer


class UpdateProfileView(generics.UpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer
