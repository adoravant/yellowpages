from django.db import models
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

# Create your models here.
class Dato(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    phone_type = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    contacted = models.IntegerField(default=0)
    website = models.CharField(max_length=250, null=True, blank=True)
    website_status = models.CharField(max_length=200, null=True, blank=True)
    website_type = models.CharField(max_length=200, null=True, blank=True)
    search_tag = models.CharField(max_length=200, null=True, blank=True)








class Lead(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(unique=True, max_length=200, null=True, blank=True)
    phone_type = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    contacted = models.IntegerField(default=0)
    website = models.CharField(max_length=250, null=True, blank=True)
    website_type = models.CharField(max_length=200, null=True, blank=True)
    website_status = models.CharField(max_length=200, null=True, blank=True)
    search_tag = models.CharField(max_length=200, null=True, blank=True)


    class Meta:
        ordering = ['id']

        def __str__(self):
            return str(self.name)

        def __unicode__(self):
            return self.name
    

    # def save(self, *args, **kwargs):
    #     # self.phone = self.phone.replace("\n", "").replace(" ", "").replace("-", "")
    #     # if self.phone.startswith("1") == False and self.phone.startswith("+1") == False and self.country == "CANADA":
    #     #     self.phone = "+1" + self.phone
    #     # if self.phone.startswith("1") == True:
    #     #     self.phone = "+" + self.phone    

        
    #     super(Lead, self).save(*args, **kwargs)
    #     try:
    #         check_existing = Lead.objects.get(phone=self.phone)

    #     except MultipleObjectsReturned as e:
    #         print("objeto duplicado..", self.phone)        
    #         self.delete() 
    #         return