from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

from django.urls import reverse
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
    # def file_path(self,*args,**kwargs):
    #     return 'user_'+self.person.user.username+'/'
    def time_date():
        return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5,minutes=45)))
    lungs_status = models.CharField(max_length=30)
    remarks = models.CharField(max_length=200)
    test_date = models.DateTimeField(default=time_date)
    x_ray = models.CharField(max_length=100)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    confidence=models.CharField(max_length=20,null=True,blank=True)
    def get_absolute_url(self):
        return reverse('report',kwargs={'id':self.id,})
    def __str__(self):
        return self.person.user.username + '_record'
