from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class County(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    county = models.ForeignKey(County, related_name='districts', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ItemBigTag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ItemSmallTag(models.Model):
    name = models.CharField(max_length=100)
    bigTag = models.ForeignKey(ItemBigTag, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class NetworkGraph(models.Model):
    name = models.CharField(max_length=500)
    json = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    createdTime = models.DateTimeField(auto_now_add=True)
    csv = models.JSONField()

    def __str__(self):
        return self.name
