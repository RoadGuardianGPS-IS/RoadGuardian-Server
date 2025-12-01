# 🛣️ RoadGuardian – Linee guida per contribuire (GitHub Desktop)

Benvenuto nel progetto **RoadGuardian**.  
Questo documento descrive come contribuire usando **GitHub Desktop**, semplificando il flusso per frontend, backend e database.

---

# 👥 Struttura del Team

- **Frontend (Flutter)** → 4 membri di cui un Team Leader  
- **Backend (Python)** → 4 membri di cui un Team Leader  
- **Database (MongoDB)** → 3 membri di cui Team Leader  

I **Team Leader** approvano le PR tecniche.  
I **PM** supervisionano processi, milestone e organizzazione.

---

# 🌿 Branching Model (GitHub Desktop)

Utilizziamo tre livelli:

### **1. `main`**
- Codice stabile e pronto alla consegna.
- Non si può modificare direttamente.
- Solo PR approvate dai Team Leader.

### **2. `develop`**
- Contiene tutte le funzionalità integrate.
- È la base da cui creare nuovi branch.

### **3. Branch “feature”**
Usati dai membri dei team per ogni nuova funzione.

Formato: feature/nome-funzionalita

Esempi:
- `feature/login`
- `feature/registrazione-utente`
- `feature/visualizza-mappa`
- `feature/api-segnalazioni`

---

# 🔁 Workflow completo con GitHub Desktop

## ✔ 1. Aggiornare `develop`
1. Aprire **GitHub Desktop**
2. In alto a sinistra → selezionare la branch `develop`
3. Premere **Fetch origin**
4. Premere **Pull origin**

---

## ✔ 2. Creare un nuovo branch (feature)
1. In alto → **Current Branch**
2. Seleziona **New Branch**
3. Nome branch:  
   `feature/nome-funzionalita`
4. Premere **Create Branch**  
5. In automatico siete ora sul nuovo branch.

---

## ✔ 3. Sviluppare la funzionalità
- Lavorare nel proprio IDE (VS Code / PyCharm).
- GitHub Desktop mostrerà i file modificati.

---

## ✔ 4. Fare i commit
1. Tornare su GitHub Desktop
2. Scrivere un **Titolo del commit** chiaro
3. Aggiungere **descrizione**
4. Premere **Commit to feature/nome-funzionalita**
5. Premere **Push origin**

---

## ✔ 5. Aprire una Pull Request
1. Dopo il push, in GitHub Desktop comparirà un banner **"Create Pull Request"**
2. Premere il pulsante
3. Si aprirà GitHub nel browser
4. Controllare:
   - **Base branch:** develop  
   - **Compare:** feature/nome-funzionalita  
5. Inserire:
   - Titolo PR chiaro
   - Descrizione completa:
     - cosa fa la feature
     - come testarla
6. Assegnare come **Reviewer** il *Team Leader* del proprio gruppo
7. Premere **Create Pull Request**

---

## ✔ 6. Code Review

Il Team Leader:
- controlla la correttezza del codice
- verifica UI/endpoint/modelli DB
- richiede eventuali modifiche tramite commenti

Lo sviluppatore:
- aggiorna la PR facendo nuovi commit
- GitHub Desktop gestisce tutto automaticamente

Quando tutto è OK → **il Team Leader approva**.

---

## ✔ 7. Merge su `develop`
Avviene solo quando:
- la feature è pronta
- la review è stata approvata
- non ci sono conflitti

Il merge lo fa:
- il Team Leader  
**oppure**
- viene autorizzato il merge automatico da GitHub

---

# 🚨 Merge su `main` (Solo a fine milestone)

Quando i PM decidono che il progetto ha raggiunto una milestone:

1. Aprire una PR da `develop` → `main`
2. Richiedere **tutti e 3 i Team Leader** come reviewer
3. I PM verificano la documentazione e approvano la milestone

Questo merge genera una versione stabile (tag).

---

# ✍️ Regole per i Commit (GitHub Desktop)
Per garantire uno storico chiaro, leggibile e professionale, ogni commit deve rispettare le seguenti regole.

✅ Formato del Messaggio di Commit
1. Struttura generale. Un commit deve essere composto da due parti:

<tipo>: <soggetto>
<body>

🧩 Regole per il soggetto
Deve essere separato dal corpo da una riga bianca.
Deve essere lungo massimo 50 caratteri.
Inizia con la lettera maiuscola.
Non deve terminare con un punto.
Deve essere scritto all’impersonale (es: “Aggiunta…”, “Modificato…”, non “Ho aggiunto…”).

✔️ Esempio corretto
feat: Aggiunta pagina profilo
📝 Regole per il corpo (opzionale ma consigliato)
Deve essere racchiuso in righe da massimo 72 caratteri.
Deve rispondere a tre domande:
What? Cosa è stato fatto?
Why? Perché è stato fatto?
How? Come è stato implementato?

✔️ Esempio completo
fix: Risolta validazione email

Corretto il controllo lato client che impediva l'invio del form
anche quando il formato dell'email era valido.
Aggiornata funzione validateEmail con nuova regex più permissiva.


| Tipo     | Quando si usa                                      | Esempio                                |
|----------|-----------------------------------------------------|-----------------------------------------|
| feat     | Aggiunta di una nuova funzionalità                 | feat: Aggiunta pagina profilo          |
| fix      | Correzione di un bug                               | fix: Risolta validazione email         |
| chore    | Manutenzione senza impatto sulla logica            | chore: Aggiornato .gitignore           |
| refactor | Ristrutturazione senza cambiare il comportamento    | refactor: Semplificate funzioni login  |
| docs     | Aggiornamento documentazione                       | docs: Aggiunta sezione API             |
| style    | Modifiche di formattazione senza logica            | style: Formattato codice con prettier  |
| test     | Aggiunta / modifica test                           | test: Aggiunti unit test               |
| perf     | Migliorie prestazionali                            | perf: Migliorata query al DB           |
| build    | Modifiche a build tools o dipendenze               | build: Aggiornato webpack              |

---

# 🧪 Testing richiesto prima della PR

### Frontend
- l’app si avvia senza errori
- la pagina implementata è navigabile

### Backend
- l’endpoint risponde correttamente via Postman o curl
- nessun errore nel server

### Database
- schema coerente
- script validi

---

# 🔐 Protezione dei branch

Sono attive le seguenti regole:

- ❌ Vietato pushare su `main`
- ✔ Necessaria almeno **1 review** (Team Leader)
- ✔ Tutti i check di GitHub devono risultare verdi
- ✔ Branch deve essere aggiornato con `develop`

---

# 🤝 Norme di collaborazione

- Rispetta il lavoro dei reviewer  
- Rispondi ai commenti con educazione  
- Non approvare il tuo codice  
- Mantieni la struttura definita (Frontend/Backend/DB)  
- Avvisa il tuo Team Leader o PM in caso di problemi o ritardi  

---

# 🏁 Conclusione

Usare GitHub Desktop non cambia il processo:  
lo semplifica.

Seguendo questo documento garantiamo:

- qualità
- ordine
- trasparenza
- consegna impeccabile

Grazie per contribuire a RoadGuardian! 🚀