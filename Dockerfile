FROM python:3.11.5

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers
COPY ./ ./

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exposer le port de Django (par défaut : 8000)
EXPOSE 8000

# Lancer le serveur Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

