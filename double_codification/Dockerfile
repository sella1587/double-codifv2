# Utiliser Python Alpine 3.19
FROM python:3.12-alpine3.19

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires pour LDAP
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openldap-dev \
    python3-dev \
    py3-pip \
    build-base \
    && rm -rf /var/cache/apk/*

# Copier le fichier requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'application Django
COPY . .

# Exposer le port 8000
EXPOSE 8000

# Démarrer le serveur Django
CMD ["gunicorn", "-b", "0.0.0.0:8000", "double_codification.wsgi:application"]