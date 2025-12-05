\# Surveillance automatique - Projet





\## Prérequis

\- Python 3.8+

\- Installer dépendances : pip install -r requirements.txt

\- (sudoers) permettre restart systemctl sans mot de passe pour l'utilisateur si on veut aut0-restart





\## Lancement

\- En local : python3 monitor.py

\- En service systemd : créer un service unit qui lance monitor.py





\## Visualisation

\- python3 visualise.py

\- Ouvrir report/dashboard.html

