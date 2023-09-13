from headquaters import settings
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from .models import *
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
        if user is not None and user.is_admin:
            login(request, user)
            return redirect('agent')
        # elif user is not None and user.is_agent:
        #     login(request, user)
        #     return redirect('home')
        else:
            messages.error(request, 'Identifiants incorrects')
            return render(request, 'login.html')
    return render(request, 'login.html')


@login_required
def pays(request):
    if request.user.is_authenticated:
        page = 'pays'
        pays = Pays.objects.all()
        agents = User.objects.filter(is_admin=True).order_by('username')
        if request.method == 'POST':
            nom = request.POST['nom'].lower()
            if Pays.objects.filter(nom=nom):
                messages.error(request, "Le pays existe!")
            else:
                pay = Pays.objects.create(nom=nom)
                pay.save()
                message =f"nom: {nom}"
                print(message)
                publish_message('pays', message)
        return render(request, 'pays.html', {'page': page, 'agents': agents,'pays':pays})
    else:
        return redirect('connexion')

@login_required
def delete_pays(request, id):
    if request.user.is_authenticated:
        pay = get_object_or_404(Pays, id=id)
        pay.delete()
        return redirect('pays')
    else:
        return redirect('connexion')

@login_required
def ville(request):
    if request.user.is_authenticated:
        page = 'ville'
        pays = Pays.objects.all()
        villes = Ville.objects.all()
        agents = User.objects.filter(is_agent=True).order_by('username')
        if request.method == 'POST':
            paysid = int(request.POST.get('paysid'))
            nomPaysId = Pays.objects.get(id=paysid)
            nomCity = request.POST['nomCity'].lower()
            if Ville.objects.filter(nomCity=nomCity):
                messages.error(request, "La ville existe!")
            else:
                print(nomPaysId, nomCity) 
                ville = Ville.objects.create(nomCity=nomCity, nomPaysId=nomPaysId)
                ville.save()
                name_pays = nomPaysId.nom
                message =f"nomCity: {nomCity}, paysid: {name_pays}"
                print(message)
                publish_message('ville', message)
                
        return render(request, 'ville.html', {'page': page, 'pays':pays,'villes':villes})
    else:
        return redirect('connexion')

@login_required
def delete_ville(request, id):
    if request.user.is_authenticated:
        ville = get_object_or_404(Ville, id=id)
        ville.delete()
        return redirect('ville')
    else:
        return redirect('connexion')

@login_required
def typeColisAdmin(request):
    if request.user.is_authenticated:
        page = 'typeColis'
        typecolis = TypeColi.objects.all()
        agents = User.objects.filter(is_agent=True).order_by('username')
        if request.method == 'POST':
            typeColi = request.POST['typeColi'].lower()
            if TypeColi.objects.filter(typeColi=typeColi):
                messages.error(request, "Ce type existe déjà!")
            else:
                typeC = TypeColi.objects.create(typeColi=typeColi)
                typeC.save()
                message =f"typeColi: {typeColi}"
                print(message)
                publish_message('typeColi', message)
        return render(request, 'typecolisadmin.html', {'page': page, 'typecolis':typecolis})
    else:
        return redirect('connexion')

@login_required
def agent(request):
    if request.user.is_authenticated:
        page = 'agent'
        agents = User.objects.filter(is_agent=True).order_by('username')
        if request.method == 'POST':
            username = request.POST['username'].lower()
            first_name = request.POST['first_name'].lower()
            last_name = request.POST['last_name'].lower()
            email = request.POST['email']
            letters = string.ascii_letters
            digits = string.digits
            alphabet = letters + digits
            pwd_length = 4
            password=''
            for i in range(pwd_length):
                password += ''.join(secrets.choice(alphabet)) 
            is_agent = True
            if User.objects.filter(email=email):
                messages.error(request, "L'adresse email existe deja !")
            else:
                user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password, is_agent=is_agent)
                Agent.objects.create(userId=user)
                print("Mot de passe agent: ",password)
                sujet = "Bienvenu dans colis app"
                message = "Votre adresse username : " + username + "\n" + "Votre mot de passe : " + password
                expediteur = settings.EMAIL_HOST_USER
                destinateur = [email]
                send_mail(sujet, message, expediteur, destinateur, fail_silently=True)
                messages.success(request, "Enregistrement réussi")
                message =f"username: {username}, first_name: {first_name}, last_name: {last_name}, password: {password}, email: {email}, is_agent: {is_agent}"
                print(message)
                publish_message('agent', message)
                
        if request.method == "GET":
            username = request.GET.get('recherche')
            if username is not None:
                agents = Agent.objects.filter(userId__username__icontains=username)
                
        return render(request, 'agent.html', {'page': page, 'agents': agents
        })
    else:
        return redirect('connexion')

@login_required
def delete_agent(request, id):
    if request.user.is_authenticated:
        agent = get_object_or_404(User, id=id)
        agent.delete()
        return redirect('agent')
    else:
        return redirect('connexion')

@login_required
def update_agent(request, id):
    if request.user.is_authenticated:
        agent = get_object_or_404(User, id=id)
        page = 'agent'
        if request.method == 'POST':
            username = request.POST['username'].lower()
            first_name = request.POST['first_name'].lower()
            last_name = request.POST['last_name'].lower()
            email = request.POST['email']
            objet = User.objects.get(id=id)
            objet.username = username
            objet.first_name = first_name
            objet.last_name = last_name
            objet.email = email
            objet.save()
            return redirect('agent')
        return render(request, 'update_agent.html', {
            'page':page,
            'agent': agent
        })
    else:
        return redirect('connexion')
    

@login_required
def enreg_colis(request):
    prix=5
    total=0
    if request.user.is_authenticated:
        page = 'colis'
        administrateurs = User.objects.filter(is_administrateur=True).order_by('username')
        
        if request.method == 'POST':
            typeColi = request.POST['typeColi'].lower()
            lieuDepart = request.POST['lieuDepart'].lower()
            lieuArriver = request.POST['lieuArriver'].lower()
            villeArriver= request.POST['villeArriver'].lower()
            expedi = request.POST['expediteur'].lower()
            desti = request.POST['destinateur'].lower()
            telephone = request.POST['telephone']
            email = request.POST['email']
            created_coli=request.POST['created_coli']
            description= request.POST['description'].lower()
            codeColi = request.POST['codeColi'].lower()
            image= request.FILES['image']
            is_administrateur=True 
            kilo=int(request.POST['kilo'])
            total=kilo*prix
            if Coli.objects.filter(codeColi=codeColi):
                messages.error(request, "Le code à été déjà utiliser !")
            else:
                new_coli= Coli.objects.create(typeColi=typeColi, lieuDepart=lieuDepart, lieuArriver=lieuArriver, villeArriver=villeArriver, expedi=expedi,desti=desti,kilo=total, telephone=telephone, email=email, created_coli=created_coli,description=description,codeColi =codeColi, image=image)
                
                if new_coli is not None:
                    messages.success(request, "Colis envoyer avec succès !")
                    sujet = "Colis envoyer est du type : " + new_coli.typeColi + " Pays de depart : " + new_coli.lieuDepart + " Pays d'arriver : "+ new_coli.lieuArriver + " La ville d'arriver :" + new_coli.villeArriver + " Nom expediteur : "+ new_coli.expedi +" Nom du destinateur : " + new_coli.desti + " Adresse email expediteur : " + new_coli.email 
                    message = "Votre mot de passe pour retirer votre colis est : " + codeColi
                    expediteur = settings.EMAIL_HOST_USER
                    destinateur = [email]
                    send_mail(sujet, message, expediteur,destinateur, fail_silently=True)
                else:
                    messages.error(request, "échoué d'envoie !")
    return render(request,'enreg_colis.html')

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
        return render(request, 'update_coli.html',{'colis':colis,'coli':page})
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
def detailMessage(request, id):
    if request.user.is_authenticated:
        contact = get_object_or_404(Contact, id=id)  
    return render(request, 'detailMessage.html',{'contact':contact})

@login_required
def deconnexion(request):
    logout(request)
    return redirect('connexion')