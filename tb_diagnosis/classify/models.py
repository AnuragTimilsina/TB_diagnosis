from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime


# Create your models here.
class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=4, blank=False)
    age = models.IntegerField(blank=False, default=0, validators=[
                              MinValueValidator(0), MaxValueValidator(120)])
    is_doctor = models.BooleanField(default=False, blank=False)
    phoneno = models.CharField(max_length=15, blank=False)
    address = models.TextField(max_length=100)
    tier = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, default=0.0)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save()


class Record(models.Model):

    def user_directory_path(self, filename):

        # file will be uploaded to MEDIA_ROOT / user_<id>/<filename>
        return 'user_{0}/{1}'.format(self.person.user.username, filename)

    lungs_status = models.CharField(max_length=30)
    remarks = models.CharField(max_length=200)
    test_date = models.DateTimeField(default=datetime.datetime.now)
    x_ray = models.ImageField(
        upload_to=user_directory_path)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self):
        return self.person.user.username + '_record'
