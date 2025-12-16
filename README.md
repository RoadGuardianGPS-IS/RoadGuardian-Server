# RoadGuardian

## 📱 Descrizione

RoadGuardian è un'applicazione innovativa che fornisce un sistema di segnalazione e condivisione di pericoli sulla strada in tempo reale. Gli utenti possono segnalare incidenti, permettendo alla comunità di restare informata e di viaggiare in sicurezza. L'app integra notifiche push in tempo reale e visualizzazione interattiva dei pericoli su mappa. Attualmente ti trovi nella repository Server premi qui per accedere alla repository Client: https://github.com/RoadGuardianGPS-IS/RoadGuardian-Client

---

## 🛠️ Tecnologie Utilizzate

<div align="center">

![Flutter](https://img.shields.io/badge/Flutter-3.0+-02569B?style=for-the-badge&logo=flutter&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-Cloud%20Services-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)
![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-13AA52?style=for-the-badge&logo=mongodb&logoColor=white)

</div>

---

## 👥 Contributori
- Simone Domenico Avitabile - Team Member
- Giovanna Massa - Team Member
- Ciro Navarra - Team Member
- Mattia D'Auria - Team Member
- Raffaele Cimmino - Team Member
- Angela Setola - Team Member
- Lorenzo Olivola - Team Member
- Sabato Iaquino - Team Member
- Carlo Mancusi - Team Member
- Davide Pio Lazzarini - Team Member
- Eljon Hida - Project Manager
- Luigi Consiglio - Project Manager


---

## 📦 Librerie Necessarie

Le dipendenze variano a seconda del componente:

**Backend (Python):**

- fastapi
- uvicorn
- firebase-admin
- pydantic
- pydantic-extra-types
- pymongo
- pytest
- email-validator


**Frontend (Flutter):**
- Flutter SDK 3.0+
- Dart SDK
- Dipendenze definite in `pubspec.yaml`

---

**⚠️ IMPORTANTE: File delle Credenziali Firebase**

Il file firebase_credentials.json contiene chiavi private e segreti che forniscono accesso completo al tuo progetto Firebase per questo motivo non è stato pubblicato su GitHub. 

**⚠️ IMPORTANTE**

Per motivi di sicurezza, il file google-services.json non è incluso nel repository.

## 🚀 Come Avviare il Progetto

### Backend:

**Prerequisiti:**
- Python 3.14 o superiore
- MongoDB installato e in esecuzione
- Credenziali Firebase (file `firebase_credentials.json`)

**Passaggi:**
1. Clona il repository
2. Naviga nella cartella `RoadGuardian-Server`
3. Crea un ambiente virtuale: `python -m venv venv`
4. Attiva l'ambiente: `source venv/bin/activate`
5. Installa le dipendenze: ````bash pip install fastapi uvicorn pymongo firebase-admin pytest pydantic pydantic-extra-types email-validator````
6. Avvia il server: `python RoadGuardian-Server/app/main.py`


### Frontend:

**Prerequisiti:**
- Flutter SDK 3.0+
- Android Studio o un dispositivo fisico

**Passaggi:**
1. Clona il repository
2. Naviga nella cartella `RoadGuardian-Client`
3. Esegui `flutter pub get` per installare le dipendenze
4. Avvia l'app: `flutter run`

---
 
