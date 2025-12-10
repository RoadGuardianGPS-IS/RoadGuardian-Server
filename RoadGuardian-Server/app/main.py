import uvicorn
from fastapi import FastAPI
from api import profilo_utente_api, mappa_api, segnalazione_api

# Creazione dell'app FastAPI
app = FastAPI(title="RoadGuardian Server")

# Registrazione del router
app.include_router(profilo_utente_api.router)
app.include_router(mappa_api.router)
app.include_router(segnalazione_api.router)

@app.get("/")
def root():
    return {"message": "Server RoadGuardian attivo!"}

if __name__ == "__main__":
    # Avvia il server
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
