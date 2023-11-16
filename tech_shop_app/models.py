from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# Create your models here.


class Company(models.Model):
    company_name = models.CharField(max_length=256, null=False, )
    year_of_establishment = models.IntegerField(null=False)
    country = models.CharField(max_length=256, null=False)

    class Meta:
        db_table = 'companies'


class Item(models.Model):
    company = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE, )
    price = models.IntegerField(null=False)
    description = models.TextField(null=False)
    model = models.CharField(max_length=256, null=False)
    category = models.CharField(max_length=256, null=False)
    img_url = models.URLField(max_length=512, null=False)
    quantity = models.IntegerField(null=False)
    color = models.CharField(max_length=256, null=False)
    storage = models.CharField(max_length=256 , null=False)

    class Meta:
        db_table = 'items'

    @property
    def company_name(self):
        return self.company.company_name


class SavedItem(models.Model):
    item = models.ForeignKey(
        'Item',
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_items'
    )

    class Meta:
        db_table = 'saved_items'


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    address = models.CharField(max_length=500, null=False)
    phone_number = models.CharField(max_length=256, null=False)

    class Meta:
        db_table = 'profile'



