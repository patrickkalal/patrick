from django.urls import path, include
from .views import *

urlpatterns = [
   path('',home, name='home'),
   path('connexion', connexion, name='connexion'),
   path('agent', agent, name='agent'),
   path('update_agent/<int:id>', update_agent, name='update_agent'),
   path('delete_agent/<int:id>', delete_agent, name='delete_agent'),
   path('tarif', tarif, name='tarif'), 
   path('service', service, name='service'),
   path('contact', contact, name='contact'),
   path('pays', pays, name='pays'),
   path('delete_pays/<int:id>', delete_pays, name='delete_pays'),
   path('ville', ville, name='ville'),
   path('delete_ville/<int:id>', delete_ville, name='delete_ville'),
   path('typeColisAdmin', typeColisAdmin, name='typeColisAdmin'),
   path('enreg_colis', enreg_colis, name='enreg_colis'),
   path('list_colis', list_colis, name='list_colis'),
   path('contact', contact, name='contact'),
   path('list_message', list_message, name='list_message'),
   path('detailMessage/<int:id>', detailMessage, name='detailMessage'),
   path('update_coli/id=<int:id>', update_coli, name='update_coli'),
   path('delete_coli/id=<int:id>', delete_coli, name='delete_coli'),
   path('deconnexion',deconnexion, name='deconnexion'),  
]