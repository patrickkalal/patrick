from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register([User,Agent,Pays,Ville,TypeColi,Coli,Contact])