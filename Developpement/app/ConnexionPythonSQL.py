from dataclasses import dataclass
from email.headerregistry import DateHeader
from logging import exception
from shutil import register_unpack_format
from sqlite3 import DatabaseError
from statistics import quantiles
from wsgiref.validate import PartialIteratorWrapper
import sqlalchemy
from sqlalchemy import func
from sqlalchemy import create_engine, cast
from sqlalchemy import Column , Integer, Text , Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
from datetime import date
import random
import string

from .Exposant import Exposant
from .Intervenir import Intervenir
from .Consommateur import Consommateur
from .Staff import Staff
from .Intervenant import Intervenant
from .Auteur import Auteur
from .Presse import Presse
from .Invite import Invite
from .Participant import Participant
from .Loger import Loger
from .Hotel import Hotel
from .Deplacer import Deplacer
from .Manger import Manger
from .Repas import Repas
from .Creneau import Creneau
from .Restaurant import Restaurant
from .Avoir import Avoir
from .Regime import Regime
from .Assister import Assister
from .Secretaire import Secretaire
from .Navette import Navette
from .Transporter import Transporter
from .Travailler import Travailler
from .Voyage import Voyage
from .Mobiliser import Mobiliser
from .Transport import Transport
from .Utilisateur import Utilisateur

from .app import login_manager
# pour avoir sqlalchemy :
# sudo apt-get update 
# sudo apt-get install python3-sqlalchemy
# pip3 install mysql-connector-python
ROLE = ["Auteur", "Exposant", "Staff", "Presse", "Invite", "Secretaire", "Participant"]

def ouvrir_connexion(user,passwd,host,database):
    """
    ouverture d'une connexion MySQL
    paramètres:
       user     (str) le login MySQL de l'utilsateur
       passwd   (str) le mot de passe MySQL de l'utilisateur
       host     (str) le nom ou l'adresse IP de la machine hébergeant le serveur MySQL
       database (str) le nom de la base de données à utiliser
    résultat: l'objet qui gère le connection MySQL si tout s'est bien passé
    """
    try:
        #creation de l'objet gérant les interactions avec le serveur de BD
        engine=sqlalchemy.create_engine('mysql+mysqlconnector://'+user+':'+passwd+'@'+host+'/'+database)
        #creation de la connexion
        cnx = engine.connect()
    except Exception as err:
        print(err)
        raise err
    print("connexion réussie")
    return cnx,engine

#connexion ,engine = ouvrir_connexion("nardi","nardi",'servinfo-mariadb', "DBnardi")
#connexion ,engine = ouvrir_connexion("doudeau","doudeau",'servinfo-mariadb', "DBdoudeau")
connexion ,engine = ouvrir_connexion("doudeau","doudeau","localhost", "BDBOUM")

# if __name__ == "__main__":
#     login=input("login MySQL ")
#     passwd=getpass.getpass("mot de passe MySQL ")
#     serveur=input("serveur MySQL ")
#     bd=input("nom de la base de données ")
#     cnx=ouvrir_connexion(login,passwd,serveur,bd)
#     # ici l'appel des procédures et fonctions
#     cnx.close()

Session = sessionmaker(bind=engine)
session = Session()

def format_creneau(debut, fin):
    heuredebut = str(debut)[11:]
    heurefin = str(fin)[11:]
    return heuredebut + " - " + heurefin

def datetime_to_dateFrancais(date):
    date = str(date)[:10]
    debut_new_date = date[8:]
    fin_new_date = date[:4]
    date = date[5:]
    date = date[:2]
    return debut_new_date + "-" + date + "-" + fin_new_date 

def datetime_to_heure(date):
    new_date = str(date)
    return new_date[11:]

def get_hotel(session, idH):
    return (session.query(Hotel).filter(Hotel.idHotel == idH).first()).nomHotel

def get_periode_hotel(session, idP):
    debut = (session.query(Loger).filter(Loger.idP == idP).first()).dateDebut
    fin = (session.query(Loger).filter(Loger.idP == idP).first()).dateFin
    return format_creneau(debut, fin)

def get_date_dormeur(session, idP):
    dateDeb = (session.query(Loger).filter(Loger.idP == idP).first()).dateDebut
    dateFin = (session.query(Loger).filter(Loger.idP == idP).first()).dateFin
    return (datetime_to_dateFrancais(dateDeb), datetime_to_dateFrancais(dateFin))

def get_consommateur(session, idP):
    return session.query(Consommateur).filter(Consommateur.idP == idP).first()

def get_restaurant(session, idRepas):
    idRestaurant = (session.query(Repas).filter(Repas.idRepas == idRepas).first()).idRest
    return (session.query(Restaurant).filter(Restaurant.idRest == idRestaurant).first()).nomRest

def get_creneau(session, idRepas):
    idCreneau = (session.query(Repas).filter(Repas.idRepas == idRepas).first()).idCreneau
    debut = (session.query(Creneau).filter(Creneau.idCreneau == idCreneau).first()).dateDebut
    fin = (session.query(Creneau).filter(Creneau.idCreneau == idCreneau).first()).dateFin
    return format_creneau(debut, fin)

def get_intervenant(session, idP):
    return session.query(Intervenant).filter(Intervenant.idP == idP).first()

def get_date(session, idRepas):
    idCreneau = (session.query(Repas).filter(Repas.idRepas == idRepas).first()).idCreneau
    debut = (session.query(Creneau).filter(Creneau.idCreneau == idCreneau).first()).dateDebut
    return datetime_to_dateFrancais(debut)


def get_deb_voyage(session, idVoyage):
    row = session.query(Voyage.heureDebVoy).filter(Voyage.idVoy == idVoyage).first()
    return row[0]

def get_lieu_depart_voyage(session, idVoyage):
    if (session.query(Voyage).filter(Voyage.idVoy == idVoyage).first()).directionGare:
        return "Festival → Gare Blois"
    else:
        return "Gare Blois → Festival"
    

# def get_max_id_utilisateur(session):
#     max_id = session.query(func.max(Utilisateur.idP)).first()
    
#     if (max_id[0]) is None:
#         return 0
#     else:
#         return max_id[0]
    

def get_max_id_secretaire(session):
    max_id = session.query(func.max(Secretaire.idP)).first()
    if (max_id[0]) is None:
        return 0
    else:
        return max_id[0]
    
def get_max_id_exposant(session):
    max_id = session.query(func.max(Exposant.idP)).first()
    if (max_id[0]) is None:
        return 0
    else:
        return max_id[0]

def get_max_id_auteur(session):
    max_id = session.query(func.max(Auteur.idP)).first()
    
    if (max_id[0]) is None:
        return 0
    else:
        return max_id[0]

def get_max_id_invite(session):
    max_id = session.query(func.max(Invite.idP)).first()
    
    if (max_id[0]) is None:
        return 0
    else:
        return max_id[0]

def get_max_id_presse(session):
    max_id = session.query(func.max(Presse.idP)).first()
    
    if (max_id[0]) is None:
        return 0
    else:
        return max_id[0]

def get_max_id_staff(session):
    max_id = session.query(func.max(Staff.idP)).first()
    
    if (max_id[0]) is None:
        return 0
    else:
        return max_id[0]

def get_max_num_stand(session):
    max_num = session.query(func.max(Exposant.numStand)).first()
    if (max_num[0]) is None:
        return 0
    else:
        return max_num._data[0]

        
def get_max_id_repas(session):        
    max_num = session.query(func.max(Repas.idRepas)).first()
    if (max_num[0]) is None:
        return 0
    else:
        return max_num._data[0]
    

def get_max_id_creneau(session):        
    max_num = session.query(func.max(Creneau.idCreneau)).first()
    if (max_num[0]) is None:
        return 0
    else:
        return max_num._data[0]

def get_max_id_restaurant(session):
    max_num = session.query(func.max(Restaurant.idRest)).first()
    if (max_num[0]) is None:
        return 0
    else:
        return max_num._data[0]
    
def get_info_all_participants(session, prenomP, nomP, emailP, ddnP, role):
    participants = session.query(Participant)
    if(prenomP != ""):
        participants = participants.filter(Participant.prenomP == prenomP)
    if(nomP != ""):
        participants = participants.filter(Participant.nomP == nomP)
    if(emailP != ""):
        participants = participants.filter(Participant.emailP == emailP)
    if(ddnP!= ""):
        jour = ddnP.split("/")[0]
        mois = ddnP.split("/")[1]
        annee = ddnP.split("/")[2]
        date = datetime.date(int(annee),int(mois),int(jour))
        participants = participants.filter(Participant.ddnP == date)
    if(role!= ""):
        participants = filtrer_par_role(role, participants)
    return participants.all()

def filtrer_par_role(role, participants):
    if role == "Secretaire":
        return participants.join(Secretaire, Participant.idP == Secretaire.idP)
    if role == "Exposant":
        return participants.join(Exposant, Participant.idP == Exposant.idP)
    if role == "Staff":
        return participants.join(Staff, Participant.idP == Staff.idP)
    if role == "Auteur":
        return participants.join(Auteur, Participant.idP == Auteur.idP)
    if role == "Presse":
        return participants.join(Presse, Participant.idP == Presse.idP)
    if role == "Invite":
        return participants.join(Invite, Participant.idP == Invite.idP)
        

def ajoute_secretaire(session, idP, prenomP, nomP, emailP, mdpP): 
    secretaire = Secretaire(idP, prenomP, nomP, emailP, mdpP)
    session.add(secretaire)
    try:
        session.commit()
        print("La secretaire "+ str(secretaire.prenomP) +" a bien été inséré dans la base de donnée")
    except:
        print("Erreur")


def ajoute_exposant(session, idP,prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP):
    exposant = Exposant(idP,prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP)
    session.add(exposant)
    try:
        session.commit()
    except Exception as inst:
        print(inst)
        session.rollback()

def ajoute_staff(session,idP, prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP):
    staff = Staff(idP, prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP)
    personne = session.query(Participant).filter(Participant.idP == staff.idP).first()
    session.add(staff)
    try:
        session.commit()
        print("La personne " + str(personne) + " est devenu un(e) staff")
    except:
        print("Erreur")
        session.rollback()

        
def ajoute_intervenant(session, idP):
    intervenant = Intervenant(idP)
    personne = session.query(Participant).filter(Participant.idP == intervenant.idP).first()
    session.add(intervenant)
    try:
        session.commit()
        print("La personne " + str(personne) + " est devenu un(e) intervenant(e)")
    except:
        print("Erreur")
        session.rollback()

    
def ajoute_auteur(session, idP, prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP): # NE MARCHE PAS TODO
    auteur = Auteur(idP, prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP)
    print("test")
    print(idP, prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP)
    print(auteur)
    session.add(auteur)
    try:
        session.commit()
    except Exception as inst:
        print(inst)
        session.rollback()

def ajoute_presse(session, idP, prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP):
    presse = Presse(idP,prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP)
    session.add(presse)
    try:
        session.commit()
    except:
        print("Erreur")
        session.rollback()

def ajoute_invite(session, idP,prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP):
    invite = Invite(idP,prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP)
    session.add(invite)
    try:
        session.commit()
    except:
        print("Erreur")
        session.rollback()
        

def ajoute_participant_role(session, prenomP, nomP, emailP, adresseP, telP, ddnP, role):
    if role in ROLE:
        mdpP = generate_password()
        if role == "Secretaire" : 
            idP = get_max_id_secretaire(session)+1
            ajoute_secretaire(session, idP, prenomP, nomP, emailP, mdpP )
        elif role == "Exposant":
            idP = get_max_id_exposant(session)+1
            ajoute_exposant(session, idP, prenomP, nomP, emailP, adresseP, telP, ddnP, role)
        elif role == "Staff":
            idP = get_max_id_staff(session)+1
            ajoute_staff(session, idP, prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP)
        elif role == "Auteur":
            idP = get_max_id_auteur(session)+1
            ajoute_auteur(session, idP, prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP)
        elif role == "Presse":
            idP = get_max_id_presse(session)+1
            ajoute_presse(session, idP,prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP)
        elif role == "Invite" :
            idP = get_max_id_invite(session)+1
            ajoute_invite(session, idP,prenomP, nomP, emailP, mdpP, ddnP, telP, adresseP)
    else:
        print("Le rôle n'est pas reconnu")


def ajoute_intervention(session, idP, idCreneau, idLieu, nomIntervention, descIntervention):
    intervenir = Intervenir(idP, idCreneau, idLieu, nomIntervention, descIntervention)
    intervention = session.query(Intervenir).filter(Intervenir.idP == intervenir.idP).filter(Intervenir.idCreneau == intervenir.idCreneau).first()
    if intervention is None:
        session.add(intervenir)
        try:
            session.commit()
            print("L'intervention " + str(intervenir) + " est maintenant créée !")
        except:
            print("Erreur")
            session.rollback()
    else:
        print("Une intervention a déjà lieu à ce créneau pour cette personne")

def ajouter_navette(session, idNavette, nomNavette, capaciteNavette):
    navette = Navette(idNavette, nomNavette, capaciteNavette)
    navette_existe = session.query(Navette).filter(Navette.idNavette == idNavette).first()
    if navette_existe is None:
        session.add(navette)
        try:
            session.commit()
            print("Une nouvelle navette " + nomNavette + " a été créée")
        except:
            print("Erreur")
            session.rollback()
    else:
        print("Une navette à déjà cet id")


#FONCTION A TESTER AVEC DES INSERTIONS
def supprimer_personne_transporter(session, idP, idVoyage):
    liste_personne = session.query(Transporter.idP).filter(Transporter.idVoy == idVoyage).all()
    if len(liste_personne) == 1:
        session.query(Transporter).filter(Transporter.idP == idP).filter(Transporter.idVoy == idVoyage).delete()
        session.query(Voyage).filter(Voyage.idVoy == idVoyage).delete()
        session.query(Mobiliser).filter(Mobiliser.idVoy == idVoyage).delete()
        session.commit()
        print("Le transport a été supprimé car cette personne était seul dans ce voyage")
    else:
        session.query(Transporter).filter(Transporter.idP == idP).filter(Transporter.idVoy == idVoyage).delete()
        session.commit()
        print("Cette personne a bien été supprimé du voyage")


# ajoute_intervention(session, 300, 1, 1, "Dédicace", "Séance de dédicace avec les spectateurs")
        
def supprimer_utilisateur(session, id_utilisateur):
    session.query(Utilisateur).filter(Utilisateur.idP == id_utilisateur).delete()
    session.commit()
    print("L'utilisateur' a été supprimé")

def supprimer_secretaire(session, id_secretaire):
    session.query(Secretaire).filter(Secretaire.idP == id_secretaire).delete()
    session.commit()
    print("La secretaire a été supprimé")

def supprimer_participant(session, id_participant):
    session.query(Participant).filter(Participant.idP == id_participant).delete()
    session.commit()
    print("Le participant a été supprimé")

def supprimer_consommateur(session, id_consommateur):
    session.query(Manger).filter(Manger.idP == id_consommateur).delete()
    session.query(Avoir).filter(Avoir.idP == id_consommateur).delete()
    session.commit()

    session.query(Consommateur).filter(Consommateur.idP == id_consommateur).delete()
    session.commit()
    print("Le consommateur a été supprimé")

def supprimer_intervenant(session, id_intervenant):
    session.query(Transporter).filter(Transporter.idP == id_intervenant).delete()
    session.query(Deplacer).filter(Deplacer.idP == id_intervenant).delete()
    session.query(Assister).filter(Assister.idP == id_intervenant).delete()
    session.query(Loger).filter(Loger.idP == id_intervenant).delete()
    session.commit()

    session.query(Intervenant).filter(Intervenant.idP == id_intervenant).delete()
    session.commit()
    print("L'intervenant a été supprimé")

def supprimer_exposant(session, id_exposant):
    session.query(Exposant).filter(Exposant.idP == id_exposant).delete()
    session.commit()
    print("L'exposant a été supprimé")
  
def supprimer_staff(session, id_staff):
    session.query(Travailler).filter(Travailler.idP == id_staff).delete()
    session.commit()

    session.query(Staff).filter(Staff.idP == id_staff).delete()
    session.commit()
    print("Le staff a été supprimé")

def supprimer_auteur(session, id_auteur):
    session.query(Intervenir).filter(Intervenir.idP == id_auteur).delete()
    session.commit()
    session.query(Auteur).filter(Auteur.idP == id_auteur).delete()
    session.commit()
    print("L'auteur a été supprimé")

def supprimer_presse(session, id_presse):
    session.query(Presse).filter(Presse.idP == id_presse).delete()
    session.commit()
    print("Le membre de la presse a été supprimé")

def supprimer_invite(session, id_invite):
    session.query(Invite).filter(Invite.idP == id_invite).delete()
    session.commit()        
    print("L'invité a été supprimé")


def get_role(session, id_utilisateur):
    utilisateur_existe = get_utilisateur(session, id_utilisateur)
    if utilisateur_existe is None:
        return None
    secretaire = get_secretaire(session, id_utilisateur)
    if secretaire is not None:
        return "Secretaire"
    exposant = get_exposant(session, id_utilisateur)
    if exposant is not None:
        return "Exposant"
    staff = get_staff(session, id_utilisateur)
    if staff is not None:
        return "Staff"
    auteur = get_auteur(session, id_utilisateur)
    if auteur is not None:
        return "Auteur"
    presse = get_presse(session, id_utilisateur)
    if presse is not None:
        return "Presse"
    invite = get_invite(session, id_utilisateur)
    if invite is not None:
        return "Invite"
    return "Pas de rôle"



def supprimer_utilisateur_role(session, id_utilisateur):
    role_utilisateur = get_role(session, id_utilisateur)
    if role_utilisateur is not None:
        if role_utilisateur == "Secretaire":
            supprimer_secretaire(session, id_utilisateur)
        else:
            if role_utilisateur == "Exposant":
                supprimer_exposant(session, id_utilisateur)
            else:
                if role_utilisateur == "Staff":
                    supprimer_staff(session, id_utilisateur)
                else:
                    if role_utilisateur == "Auteur":
                        supprimer_auteur(session, id_utilisateur)
                    elif role_utilisateur == "Presse":
                        supprimer_presse(session, id_utilisateur)
                    elif role_utilisateur == "Invite":
                        supprimer_invite(session, id_utilisateur)
                    supprimer_intervenant(session, id_utilisateur)
                supprimer_consommateur(session, id_utilisateur)
            supprimer_participant(session, id_utilisateur)
        supprimer_utilisateur(session, id_utilisateur)
    else:
        print("La personne que vous voulez supprimer n'existe pas")

     
def modifier_participant(session, idP, adresseP, ddnP, telP):
    session.query(Participant).filter(Participant.idP == idP).update(
        {Participant.adresseP : adresseP, Participant.ddnP : ddnP, Participant.telP : telP})
    session.commit()
    print("Le participant a bien été modifié")
    
    
def modifier_utilisateur(session, idP, prenomP, nomP, emailP):
    session.query(Utilisateur).filter(Utilisateur.idP == idP).update(
        {Utilisateur.prenomP : prenomP, Utilisateur.nomP : nomP, Utilisateur.emailP : emailP})
    session.commit()
    print("L'utilisateur a bien été modifié")

def modifier_participant_tout(session, idP, prenomP, nomP, ddnP, telP, emailP, adresseP, mdpP, invite, emailEnvoye, remarques):
    session.query(Participant).filter(Participant.idP == idP).update(
        {Participant.prenomP : prenomP, Participant.nomP : nomP, Participant.ddnP : ddnP, 
         Participant.telP : telP, Participant.emailP : emailP, Participant.adresseP : adresseP, Participant.mdpP : mdpP,
         Participant.invite : invite, Participant.emailEnvoye : emailEnvoye, Participant.remarques : remarques})
    session.commit()
    print("Le participant a bien été modifié")
   

# def modifier_participant_role(session, idP, prenomP, nomP, ddnP, telP, emailP, adresseP, mdpP, invite, emailEnvoye, remarques, metier):
#     participant = Participant(idP, prenomP, nomP, ddnP, telP, emailP, adresseP, mdpP, invite, emailEnvoye, remarques)
#     ancien_participant = Participant(participant.idP, participant.prenomP, participant.nomP, participant.ddnP, participant.telP, participant.emailP, participant.mdpP, participant.remarques, participant.invite, participant.emailEnvoye)
#     supprimer_utilisateur_role(session, participant.idP)
#     ajoute_participant_role_id(session, ancien_participant, metier)
#     print("Le role du participant a bien été modifié")

def modif_loger(session, ancien_loger, nouveau_loger):
    session.query(Loger).filter(Loger.idP == ancien_loger.idP).filter(Loger.idHotel == ancien_loger.idHotel).filter(Loger.dateDebut == ancien_loger.dateDebut).update({
        Loger.dateDebut : nouveau_loger.dateDebut, Loger.dateFin : nouveau_loger.dateFin, Loger.idHotel : nouveau_loger.idHotel})
    session.commit()
    print("Le logement de cette personne a bien été modifié")  
          

def modif_repas(session, ancien_repas, nouveau_repas):
    session.query(Manger).filter(Manger.idP == ancien_repas.idP).filter(Manger.idRepas == ancien_repas.idRepas).update(
        {Manger.idRepas : nouveau_repas.idRepas}
    )
    session.commit()
    print("Le repas du participant a bien été modifié")     

def get_info_personne(session, email, mdp):
    personne = session.query(Participant).filter(Participant.emailP == email).filter(Participant.mdpP == mdp).first()
    if personne is None:
        return None
    else:
        return personne

def get_participant(session, id_participant):
    return session.query(Participant).filter(Participant.idP == id_participant).first()

def get_exposant(session, id_exposant):
    return session.query(Exposant).filter(Exposant.idP == id_exposant).first()

def get_invite(session, id_invite):
    return session.query(Invite).filter(Invite.idP == id_invite).first()

def get_staff(session, id_staff):
    return session.query(Staff).filter(Staff.idP == id_staff).first()

def get_auteur(session, id_auteur):
    return session.query(Auteur).filter(Auteur.idP == id_auteur).first()

def get_presse(session, id_presse):
    return session.query(Presse).filter(Presse.idP == id_presse).first()


def get_secretaire(session, id_secretaire):
    return session.query(Secretaire).filter(Secretaire.idP == id_secretaire).first()

def get_prenom(session, id_participant):
    return (session.query(Utilisateur).filter(Utilisateur.idP == id_participant).first()).prenomP

def get_nom(session, id_participant):
    return (session.query(Utilisateur).filter(Utilisateur.idP == id_participant).first()).nomP

def get_id_hotel(session, nom_hotel):
    return (session.query(Hotel).filter(Hotel.nomHotel == nom_hotel).first()).idHotel
   

def get_utilisateur(session, id_utilisateur):
    return session.query(Utilisateur).filter(Utilisateur.idP == id_utilisateur).first()

def affiche_participants(session):
    liste_participants = []
    participants = session.query(Participant)
    for part in participants:
        liste_participants.append(part)
    return liste_participants
   

def affiche_participant_trier(session, trie):
     
        if trie == "Auteur" :
            return session.query(Participant).join(Auteur, Participant.idP==Auteur.idP).all()

        elif trie == "Consommateur":
            return session.query(Participant).join(Consommateur, Participant.idP==Consommateur.idP).all() 

        elif trie == "Exposant": 
            return session.query(Participant).join(Exposant, Participant.idP==Exposant.idP).all() 
        
        elif trie == "Intervenant":
            return session.query(Participant).join(Intervenant, Participant.idP==Intervenant.idP).all() 
        
        elif trie == "Invite":
            return session.query(Participant).join(Invite, Participant.idP==Invite.idP).all() 
        
        elif trie == "Presse":
            return session.query(Participant).join(Presse, Participant.idP==Presse.idP).all() 
        
        elif trie == "Staff": 
            return session.query(Participant).join(Staff, Participant.idP==Staff.idP).all()
        
        else: 
            return session.query(Participant).order_by(Participant.idP.asc()).all()

def affiche_participant_trier_consommateur(session):
    participant = session.query(Participant).all()
    return participant


def get_nom_restaurant():
    liste_nom_resteau = []
    for nom in session.query(Restaurant):
        liste_nom_resteau.append((nom.nomRest, nom.idRest))
    return liste_nom_resteau

def get_nom_hotel():
    liste_nom_hotel = []
    for nom in session.query(Hotel):
        liste_nom_hotel.append((nom.nomHotel, nom.idHotel))
    return liste_nom_hotel

    
        
def afficher_consommateur(session, date_jour, restaurant, midi):
    if restaurant != "Restaurant":
        restaurant = int(restaurant)
        print(restaurant)
    if midi == "true":
        midi = True
    elif midi == "false":
        midi = False
    liste_consommateurs = []
    liste_creneau = []
    liste_repas = []
    liste_mangeur = []
    if restaurant != "Restaurant" and midi != "Journee":
        repas = session.query(Creneau, Creneau.dateDebut, Creneau.idCreneau, Repas.idRepas).join(Repas, Repas.idCreneau == Creneau.idCreneau).filter(Repas.idRest == restaurant).filter(Repas.estMidi == midi).all()
    elif restaurant == "Restaurant" and midi == "Journee":
        repas = session.query(Creneau, Creneau.dateDebut, Creneau.idCreneau, Repas.idRepas).join(Repas, Repas.idCreneau == Creneau.idCreneau)
    elif restaurant != "Restaurant":
        repas = session.query(Creneau, Creneau.dateDebut, Creneau.idCreneau, Repas.idRepas).join(Repas, Repas.idCreneau == Creneau.idCreneau).filter(Repas.idRest == restaurant).all()
    elif midi != "Journee":
        repas = session.query(Creneau, Creneau.dateDebut, Creneau.idCreneau, Repas.idRepas).join(Repas, Repas.idCreneau == Creneau.idCreneau).filter(Repas.estMidi == midi).all()
    
    if date_jour[0] != "Date":
        date_jour = date(int(date_jour[0]), int(date_jour[1]), int(date_jour[2]))
        for cren in repas:
            if cren[1].date() == date_jour:
                liste_creneau.append(cren[2])
        repas = session.query(Repas, Repas.idCreneau, Repas.idRepas).all()
        for rep in repas:
            if rep[1] in liste_creneau:
                liste_repas.append(rep[2])
    else:
        for rep in repas:
            liste_repas.append(rep[3])

    manger = session.query(Manger, Manger.idP, Manger.idRepas).all()
    for mangeur in manger:
        if mangeur[2] in liste_repas:
            liste_mangeur.append(mangeur[1])

    consommateurs = session.query(Consommateur, Consommateur.idP).all()

    for consomm in consommateurs:
        if consomm[1] in liste_mangeur:
            liste_consommateurs.append(consomm[1])
    print(liste_consommateurs)
    liste_participants = get_liste_participant_idp_regime(session, liste_consommateurs)
    return liste_participants

def get_liste_participant_idp_regime(session, liste_id):
    liste_participants = []
    participants = session.query(Participant).join(Consommateur, Participant.idP == Consommateur.idP).all()
    for une_personne in participants:
        if une_personne.idP in liste_id:
            liste_participants.append((une_personne, get_regime(session, une_personne.idP)))
    return liste_participants

def affiche_navette(session, date, navette, directionGare):
    if navette != "Navette" :
        navette = int(navette)
    if directionGare == "true" : 
        directionGare = True
    elif directionGare == "false" : 
        directionGare = False
    liste_consommateurs = []
    liste_creneau = []
    liste_transport = []
    liste_mangeur = []
    if navette != "Navette" and directionGare != "Direction":
        transport = session.query(Voyage.idVoy, Participant.prenomP, Participant.nomP, Voyage.directionGare, Navette.nomNavette, Voyage.heureDebVoy).join(Mobiliser, Mobiliser.idVoy == Voyage.idVoy).join(Navette, Navette.idNavette == Mobiliser.idNavette).join(Transporter, Voyage.idVoy == Transporter.idVoy).join(Intervenant, Intervenant.idP == Transporter.idP).join(Participant, Participant.idP == Intervenant.idP).filter(Navette.idNavette == navette).filter(Voyage.directionGare == directionGare).distinct().all()
    elif navette == "Navette" and directionGare == "Direction":
        transport = session.query(Voyage.idVoy, Participant.idP, Participant.prenomP, Participant.nomP, Voyage.directionGare, Voyage.heureDebVoy).join(Mobiliser, Mobiliser.idVoy == Voyage.idVoy).join(Navette, Navette.idNavette == Mobiliser.idNavette).join(Transporter, Voyage.idVoy == Transporter.idVoy).join(Intervenant, Intervenant.idP == Transporter.idP).join(Participant, Participant.idP == Intervenant.idP).distinct().all()
    elif navette != "Restaurant":
        transport = session.query(Voyage.idVoy, Participant.prenomP, Participant.nomP, Voyage.directionGare, Navette.nomNavette, Voyage.heureDebVoy).join(Mobiliser, Mobiliser.idVoy == Voyage.idVoy).join(Navette, Navette.idNavette == Mobiliser.idNavette).join(Transporter, Voyage.idVoy == Transporter.idVoy).join(Intervenant, Intervenant.idP == Transporter.idP).join(Participant, Participant.idP == Intervenant.idP).filter(Navette.idNavette == navette).distinct().all()
    elif directionGare != "Direction":
        transport = session.query(Voyage.idVoy, Participant.prenomP, Participant.nomP, Voyage.directionGare, Navette.nomNavette, Voyage.heureDebVoy).join(Mobiliser, Mobiliser.idVoy == Voyage.idVoy).join(Navette, Navette.idNavette == Mobiliser.idNavette).join(Transporter, Voyage.idVoy == Transporter.idVoy).join(Intervenant, Intervenant.idP == Transporter.idP).join(Participant, Participant.idP == Intervenant.idP).filter(Voyage.directionGare == directionGare).distinct().all()
    
    print(transport)
    
    if date[0] != "Date":
        date = date(int(date[0]), int(date[1]), int(date[2])) # modifier ça et modifier le HTML
        for cren in transport:
            if cren[1].date() == date:
                liste_creneau.append(cren[2])
        transport = session.query(Repas, Repas.idCreneau, Repas.idRepas).all()
        for rep in transport:
            if rep[1] in liste_creneau:
                liste_transport.append(rep[2])
    else:
        for tran in transport:
            liste_transport.append(tran[3])

    return liste_transport

# affiche_navette(session, "Date", "Navette", "Direction")
         

def get_liste_participant_id_consommateur(session, liste_id):
    liste_participants = []
    participants = session.query(Participant).join(Consommateur, Participant.idP == Consommateur.idP).all()
    for une_personne in participants:
        if une_personne.idP in liste_id:
            liste_participants.append(une_personne)
    return liste_participants

def get_regime(session, id_p):
    str_regime = ""
    liste_regime = session.query(Regime.nomRegime).join(Avoir, Avoir.idRegime == Regime.idRegime).filter(Avoir.idP == id_p).all()
    if len(liste_regime) == 0:
        str_regime = "Pas de regime"
    else:
        for un_regime in liste_regime:
            str_regime += str(un_regime[0]) + ", "
        str_regime = str_regime[:-2]
    return str_regime

def get_dormeur(session, date_jour, hotel):
    if date_jour[0] != "Date":
        date_jour = date(int(date_jour[0]), int(date_jour[1]), int(date_jour[2]))
    else:
        date_jour = date_jour[0]
        print(date_jour)
    liste_dormeur_date_hotel = []
    if hotel == "Hôtel":
        hotel = None
    else:
        hotel = int(hotel)
    dormeurs = session.query(Loger.idP, Loger.dateDebut, Loger.dateFin, Loger.idHotel).all()
    for un_dormeur in dormeurs:
        date_deb = un_dormeur[1].date()
        date_fin = un_dormeur[2].date()
        if date_jour == "Date" :
            if hotel is None or un_dormeur.idHotel == hotel:
                liste_dormeur_date_hotel.append(un_dormeur[0])

        elif date_deb <= date_jour and date_fin >= date_jour and hotel is None or un_dormeur.idHotel == hotel : 
            liste_dormeur_date_hotel.append(un_dormeur[0])
                
    liste_participants = get_liste_participant_id_consommateur(session, liste_dormeur_date_hotel)

    return liste_participants
#print(get_dormeur(session, "2022-11-19", 2))

def ajoute_deplacer(session, idP, idTransport, lieuDepart, lieuArrive) : 
    deplacement = Deplacer(idP, idTransport, lieuDepart, lieuArrive)
    deplacer = session.query(Deplacer).filter(Deplacer.idP == idP).filter(Deplacer.idTransport == idTransport).filter(Deplacer.lieuDepart == lieuDepart).filter(Deplacer.lieuArrive == lieuArrive).first()
    if deplacer is None:
        session.add(deplacement)
        try: 
            session.commit()
            print("Le deplacement à bien été inséré")
        except:
            print("Erreur !")
            session.rollback()
 
    else:
        print("Un même déplacement existe déjà pour cette personne")
  
#ajoute_deplacer(session, 300, 1, "Paris", "Blois")

def ajoute_mangeur(session, idP, idRepas):
    mangeur = Manger(idP, idRepas)
    manger = session.query(Manger).filter(Manger.idP == idP).filter(Manger.idRepas == idRepas).first()
    if manger is None:
        session.add(mangeur)
        try: 
            session.commit()
            print("Le consommateur à bien été associé à un repas")  

        except: 
            print("Erreur !")
            session.rollback()
    else: 
        print("Un consommateur mange déjà ce repas")


def ajoute_loger(session, idP, dateDebut, dateFin, idHotel):
    logeur = Loger(idP, dateDebut, dateFin, idHotel)
    loger = session.query(Loger.dateDebut, Loger.dateFin).filter(Loger.idP == idP).all()
    
    for log in loger: 
        date_deb = log[0].date()
        date_fin = log[1].date()
        dateDeb = dateDebut.date()
        dateFin = dateFin.date()
        print(dateFin)
        if (dateDeb <= date_deb <= dateFin) or (date_deb <= dateDeb <= date_fin):
            print("Cette intervenant est déjà logé dans un hôtel à ces dates")
            return
    session.add(logeur)
    try:
        session.commit()
        print("Le loger à bien été associé à un hôtel")  

    except: 
        print("Erreur !")
        session.rollback()
        
def get_max_id_regime(session): 
    regime= session.query(func.max(Regime.idRegime)).first()
    if (regime[0]) is None:
        return 0
    else:
        return regime._data[0]
        
def ajoute_regime(session, regime) : 
    id_regime = get_max_id_regime(session)+1
    regime = Regime(id_regime, regime)
    session.add(regime)
    try :
        session.commit()
        return id_regime
    except : 
        print("erreur")
        session.rollback() 
        
def ajoute_avoir_regime(session, id_consommateur, id_regime) :
    avoir_regime = Avoir(id_consommateur, id_regime)
    session.add(avoir_regime)
    try :
        session.commit()
        print("L'association regime-consommateur à bien été ajoutée !")
    except : 
        print("erreur")
        session.rollback() 
    
def est_intervenant(session, idP):
    intervenant = session.query(Intervenant).filter(Intervenant.idP == idP).first()
    return intervenant is not None
            
def est_secretaire(session, idP):
    secretaire = session.query(Secretaire).filter(Secretaire.idP == idP).first()
    return secretaire is not None

        
# ajoute_loger(session, 400, datetime.datetime(2022, 11, 19), datetime.datetime(2022, 11, 19), 1)
        
        
def requete_transport_annee(session, idP, annee) : 
    liste_transport = session.query(Deplacer, Assister.dateDepart).join(Assister, Deplacer.idP == Assister.idP).filter(Deplacer.idP == idP).all()
    liste_deplacement = list()
    annee = annee.year
    for transport in liste_transport: 
        annee_req = transport[1].year
        if annee_req == annee: 
            liste_deplacement.append(transport)
    return liste_deplacement       


def ajoute_assister(session, idP, dateArrive, dateDepart):
    assisteur = Assister(idP, dateArrive, dateDepart)
    assister = session.query(Assister).filter(Assister.dateArrive == dateArrive).filter(Assister.dateDepart == dateDepart).first()
    if assister is None :
        session.add(assisteur)
        try : 
            session.commit()
            print("L'intervenant à bien été ajouté à ces dates") 
        except : 
            print("Erreur !")
            session.rollback()
            
    else :
        print("Cet intervenant assiste déjà au festival à ces dates")
        
def cherche_transport(session, nom_transport) : 
    liste_transport = session.query(Transport.idTransport, Transport.nomTransport).all()
    res = list()
    for transport in liste_transport : 
        if nom_transport in transport : 
            res.append(transport)
    return res


def modif_participant_remarque(session, idP, remarques) : 
    nouvelles_remarques = remarques + " / "+str((session.query(Participant).filter(Participant.idP == idP).first()).remarques)
    print(nouvelles_remarques)
    session.query(Participant).filter(Participant.idP == idP).update({Participant.remarques : nouvelles_remarques})
    session.commit()  


def get_utilisateur_email_mdp(session, mail, mdp):
    utilisateur = session.query(Utilisateur).filter(Utilisateur.emailP == mail).filter(Utilisateur.mdpP == mdp).first()
    if utilisateur is not None :
        return utilisateur
    

@staticmethod
def transforme_datetime(date):
    date = date.split("-")
    return date

def ajoute_creneau(session, dateDebut,dateFin):
    liste_date_deb = transforme_datetime(dateDebut)
    liste_date_fin = transforme_datetime(dateFin)
    dateDebut = datetime.datetime(int(liste_date_deb[0]), int(liste_date_deb[1]), int(liste_date_deb[2]), int(liste_date_deb[3]), int(liste_date_deb[4]),int(liste_date_deb[5]))
    dateFin = datetime.datetime(int(liste_date_fin[0]), int(liste_date_fin[1]), int(liste_date_fin[2]), int(liste_date_fin[3]), int(liste_date_fin[4]), int(liste_date_fin[5]))
    creneau_test = session.query(Creneau).filter(Creneau.dateDebut == dateDebut).filter(Creneau.dateFin == dateFin).first()
    if creneau_test is None :
        idCreneau = get_max_id_creneau(session)+1
        creneau = Creneau(idCreneau, dateDebut, dateFin)
        session.add(creneau)
        try :
            session.commit()
        except : 
            print("erreur creneau")
            session.rollback()
        return creneau.idCreneau
    return creneau_test.idCreneau

def ajoute_repas(session, estMidi,idRest,idCreneau) : 
    repas_verif = session.query(Repas).filter(Repas.estMidi == estMidi).filter(Repas.idRest == idRest).filter(Repas.idCreneau == idCreneau).first()
    if repas_verif is None :
        idRepas = get_max_id_repas(session)+1
        repas = Repas(idRepas, estMidi, idRest, idCreneau)
        session.add(repas)
        try : 
            session.commit()
        except : 
            print("erreur repas")
            session.rollback()
        return repas.idRepas
    return repas_verif.idRepas

def ajoute_restaurant(session, nomRest) : 
    restaurant_test = session.query(Restaurant).filter(Restaurant.nomRest == nomRest).first()
    if restaurant_test is None :
        idRestaurant = get_max_id_restaurant(session)+1
        restaurant = Restaurant(idRestaurant, nomRest)
        session.add(restaurant)
        try : 
            session.commit()
        except : 
            print("erreur restaurant")
            session.rollback()
    return restaurant_test.idRest

def meilleur_restaurant(session): 
    pass # TODO SELON LE ROLE METTRE UN CERTAIN RESTAU 
    
 
def ajoute_repas_mangeur(session, idP, liste_repas, liste_horaire_restau, dico_horaire_restau):
    for i in range(0, len(liste_repas)):
        if liste_repas[i] == 'true':
            horaire = dico_horaire_restau[liste_horaire_restau[i]]
            idCreneau = ajoute_creneau(session, horaire.split("/")[0], horaire.split("/")[1])
            idRest = meilleur_restaurant(session) # ajouter ROLE TODO 
            idRepas = ajoute_repas(session, False if liste_horaire_restau[i][4:] == "soir" else True, 1 if liste_horaire_restau[i][4:] == "soir" else 1 , idCreneau) #TODO
            ajoute_mangeur(session, idP, idRepas)


@login_manager.user_loader
def load_user(participant_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    if est_secretaire(session, participant_id):
        return get_secretaire(session, participant_id)
    else:
        return get_participant(session, participant_id)



@staticmethod
def generate_password(length=8):
  # Get a list of all the ASCII lowercase letters, uppercase letters, and digits
  characters = string.ascii_letters + string.digits + string.punctuation
  # Use the random.sample function to get a list of `length` random elements from the list of characters
  password = ''.join(random.sample(characters, length))
  return password



