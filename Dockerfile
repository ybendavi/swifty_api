# Étape 1 : utiliser une image Python officielle
FROM python:3.12-slim

# Étape 2 : définir le répertoire de travail
WORKDIR /app

# Étape 3 : copier les fichiers (.env à ajouter avec les variables:
# CLIENT_SECRET, CLIENT_ID, AUTHORIZATION_ENDPOINT, REDIRECT_URI, SERVER_SECRET)
COPY ./* .

# Étape 4 : installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : exposer le port Flask
EXPOSE 5000

# Étape 6 : lancer l'application
CMD ["python", "app.py"]
