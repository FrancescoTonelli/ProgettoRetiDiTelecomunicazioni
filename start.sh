#!/bin/bash

# Nome dell'ambiente virtuale
VENV_DIR="venv"

# Creazione dell'ambiente virtuale
echo "Creazione dell'ambiente virtuale..."
python -m venv $VENV_DIR

# Controllo se l'ambiente è stato creato
if [ -d "$VENV_DIR" ]; then
    echo "Ambiente virtuale creato con successo."
else
    echo "Errore nella creazione dell'ambiente virtuale."
    exit 1
fi

# Attivazione dell'ambiente virtuale
echo "Attivazione dell'ambiente virtuale..."
source $VENV_DIR/bin/activate

# Installazione dei pacchetti se requirements.txt è presente
if [ -f "requirements.txt" ]; then
    echo "Installazione dei pacchetti da requirements.txt..."
    pip install -r requirements.txt
    clear
else
    echo "File requirements.txt non trovato, nessun pacchetto installato."
fi

echo "L'ambiente virtuale è attivato. Per uscire, eseguire 'deactivate'."

python main.py