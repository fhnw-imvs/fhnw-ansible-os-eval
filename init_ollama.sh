#!/bin/bash

# Funktion, um zu prüfen, ob der Docker-Container existiert
container_exists() {
    docker ps -a --format '{{.Names}}' | grep -Eq "^ollama\$"
}

# Funktion, um zu prüfen, ob der Docker-Container läuft
container_running() {
    docker ps --format '{{.Names}}' | grep -Eq "^ollama\$"
}

# Wenn der Container nicht existiert, initialisiere ihn
if ! container_exists; then
    echo "Docker-Container 'ollama' wird zum ersten Mal erstellt und gestartet..."
    docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
    sleep 5  # Warte, bis der Container vollständig hochgefahren ist
    docker exec ollama ollama pull llama3.1
    pip install ollama
elif ! container_running; then
    # Wenn der Container existiert, aber nicht läuft, starte ihn
    echo "Docker-Container 'ollama' wird gestartet..."
    docker start ollama
else
    echo "Docker-Container 'ollama' läuft bereits."
fi