from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    is_admin = models.BooleanField('admin', default=False)
    is_agent = models.BooleanField('agent', default=False)
    def __str__(self):
        return self.username 

class Agent(models.Model):
    userId = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    def __str__(self):
        return self.userId.username

class Pays(models.Model):
    nom=models.CharField(max_length=50)
    datePays=models.DateField(auto_now_add=True)
    def __str__(self):
        return self.nom 
    
class Ville(models.Model):
    nomPaysId=models.ForeignKey(Pays, on_delete=models.CASCADE, default=False)
    nomCity=models.CharField(max_length=50)
    dateCity=models.DateField(auto_now_add=True)
    def __str__(self):
        return self.nomPaysId.nom

class TypeColi(models.Model):
    typeColi=models.CharField(max_length=50, unique=True)
    dateTypeColi=models.DateField(auto_now_add=True)
    def __str__(self):
        return self.typeColi
    
class Coli(models.Model):
    typeColiId = models.ForeignKey(TypeColi, on_delete=models.CASCADE, default=False)
    villeEnvois = models.ForeignKey(Ville, on_delete=models.CASCADE, default=False)
    villeDestine = models.CharField(max_length=50)
    expedi = models.CharField(max_length=50)
    desti = models.CharField(max_length=50)
    kilo = models.IntegerField(default=0,null=True)
    total=models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    telephone = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    created_coli = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=100,default="Pas de details")
    codeColi = models.CharField(max_length=50)
    image = models.FileField(upload_to='images',blank=True,default='aucune image')
    class Meta:
        verbose_name = 'Coli'
        verbose_name_plural = 'Colis'
    

class Contact(models.Model):
    noms = models.CharField(max_length=50)
    mail = models.CharField(max_length=50)
    sujet = models.CharField(max_length=50,default='pas de sujet')
    message = models.TextField(max_length=100,default="Pas de message")
    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contact'