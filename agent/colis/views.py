from agent import settings
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from .models import *
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import date, timedelta
import secrets
import string
from django.db.models import Sum
import random
from .producer import publish_message
# Create your views here.
def home(request):
    return render(request,'index.html')
def tarif(request):
    tarif = 5
    return render(request,'tarif.html',{'tarif':tarif})
def service(request):
    return render(request,'service.html')
def contact(request):
    if request.method == 'POST':
        noms = request.POST['noms'].lower()
        mail = request.POST['mail'].lower()
        sujet = request.POST['sujet'].lower()
        message = request.POST['message'].lower()
        new_contact= Contact.objects.create(noms=noms, mail=mail,sujet=sujet, message=message)
        new_contact.save()
    return render(request,'contact.html')


def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        # if user is not None and user.is_admin:
        #     login(request, user)
        #     return redirect('agent')
        if user is not None and user.is_agent:
            login(request, user)
            return redirect('enreg_colis')
        else:
            messages.error(request, 'Identifiants incorrects')
            return render(request, 'login.html')
    return render(request, 'login.html')

@login_required
def enreg_colis(request):
    prix=5
    total=0 
    if request.user.is_authenticated:
        page = 'colis'
        pays = Pays.objects.all()
        villes = Ville.objects.all()
        typecolis = TypeColi.objects.all()
        administrateurs = User.objects.filter(is_admin=True).order_by('username')
        if request.method == 'POST':
            alimentsid = int(request.POST.get('alimentsid'))
            typeColiId = TypeColi.objects.get(id=alimentsid)
            paysvilleenmvoieid = int(request.POST.get('paysvilleenmvoieid'))
            villeEnvois = Ville.objects.get(id=paysvilleenmvoieid)
            villeDestine = request.POST['villeDestine'].lower()
            expedi = request.POST['expediteur'].lower()
            desti = request.POST['destinateur'].lower()
            kilo=int(request.POST['kilo'])
            total=kilo*prix
            telephone = request.POST['telephone']
            email = request.POST['email']
            description = request.POST['description'].lower()
            digits = string.digits
            alphabet = digits
            pwd_length = 8
            codeColi=''
            for i in range(pwd_length):
                codeColi += ''.join(secrets.choice(alphabet)) 
            image= request.FILES['image']
            is_administrateur=True 
            #print(typeColiId, villeEnvois, villeDestine, expedi, desti, kilo, total, telephone, email, description, codeColi)
            new_coli= Coli.objects.create(typeColiId=typeColiId, villeEnvois=villeEnvois, villeDestine=villeDestine, expedi=expedi, desti=desti, kilo=kilo, total=total, telephone=telephone, email=email,description=description,codeColi=codeColi, image=image)
            new_coli.save()
            get_typeColiId = typeColiId.typeColi
            get_villeEnvois = villeEnvois.nomPaysId
            message =f"alimentsid: {get_typeColiId}, paysvilleenmvoieid: {get_villeEnvois}, villeDestine: {villeDestine}, expedi: {expedi}, desti: {desti}, kilo: {kilo}, total: {total}, telephone: {telephone}, email: {email}, description: {description}, codeColi: {codeColi}, image: {image}"
            print(message)
            publish_message('colis', message)  
            if new_coli is not None:
                messages.success(request, "Colis envoyer avec succès !")
                sujet = "Votre code du colis est : " + codeColi 
                message = "Nom expéditeur: " + new_coli.expedi + ", Nom du destinataire: " + new_coli.desti + ", Kilo: " + str(new_coli.kilo) + ", Montant payé: " + str(new_coli.total) +".00.USD"+ ", Description: " + new_coli.description
                expediteur = settings.EMAIL_HOST_USER
                destinateur = [email]
                send_mail(sujet, message, expediteur,destinateur, fail_silently=True)
            else:
                messages.error(request, "échoué d'envoie !")
    return render(request,'enreg_colis.html',{'prix':prix,'typecolis':typecolis,'villes':villes})


@login_required
def detailColi(request, id):
    if request.user.is_authenticated:
        coli = get_object_or_404(Coli, id=id)  
    return render(request, 'detailColi.html',{'coli':coli})

@login_required
def list_colis(request):
    coli= Coli.objects.all()
    if request.method == "GET":
        codeColi = request.GET.get('recherche')
        if codeColi is not None:
            coli= Coli.objects.filter(codeColi=codeColi)
    context = {
        'colis':coli,

    }
    return render(request,'listeColi.html',context)

@login_required
def printFacturePdf(request, id):
    facturations = get_object_or_404(Coli, id=id)
    template_path = 'printFact.html'
    numero_facture = random.randint(1000, 9999)
    context = {
        'facturations': facturations,
        'numero_facture': numero_facture
    }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="facture_client.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Nous avons rencontré des erreurs lors de la création du PDF.')
    return response


def update_coli(request, id):
    if request.user.is_authenticated:
        colis = get_object_or_404(Coli, id=id)
        page = 'list_colis'
        if request.method == 'POST':
            typeColi = request.POST['typeColi'].lower()
            lieuDepart = request.POST['lieuDepart'].lower()
            lieuArriver = request.POST['lieuArriver'].lower()
            villeArriver= request.POST['villeArriver'].lower()
            expediteur = request.POST['expediteur'].lower()
            destinateur = request.POST['destinateur'].lower()
            kilo=int(request.POST['kilo'])
            telephone = request.POST['telephone']
            email = request.POST['email']
            created_coli=request.POST['created_coli']
            description= request.POST['description'].lower()
            codeColi = request.POST['codeColi'].lower()
            image= request.FILES['image']
            objet = Coli.objects.get(id=id)
            objet.typeColi = typeColi
            objet.lieuDepart = lieuDepart
            objet.lieuArriver = lieuArriver
            objet.villeArriver = villeArriver
            objet.expediteur = expediteur
            objet.destinateur = destinateur
            objet.telephone = telephone
            objet.email = email
            objet.created_coli = created_coli
            objet.description = description
            objet.codeColi = codeColi
            objet.image = image
            objet.save()
            return redirect('list_colis')
        return render(request, 'update_coli.html',{'colis':colis,'page':page})
    else:
        return redirect('connexion')
@login_required
def delete_coli(request, id):
    if request.user.is_authenticated:
        coli = get_object_or_404(Coli, id=id)
        coli.delete()
        return redirect('list_colis')
    else:
        return redirect('connexion')


@login_required
def list_message(request):
    contact= Contact.objects.all()
    context = {
        'contacts':contact,
    }
    return render(request,'listeMessage.html',context)
@login_required
def deconnexion(request):
    logout(request)
    return redirect('connexion')