from django.db import models
from django.contrib.auth.models import User
import datetime
# Create your models here.


class Record(models.Model):
    # def file_path(self,*args,**kwargs):
    #     return 'user_'+self.person.user.username+'/'

    def time_date():
        return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=45)))

    lungs_status = models.CharField(max_length=30)
    remarks = models.CharField(max_length=200)
    test_date = models.DateTimeField(default=time_date)
    x_ray = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    confidence = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.username + '_record'
