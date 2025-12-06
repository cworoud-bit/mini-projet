# Surveillance automatique - Projet

## Prérequis
- Python 3.8+
- Installer dépendances : pip install -r requirements.txt
- (sudoers) permettre restart systemctl sans mot de passe si auto-restart voulu

## Lancement
- En local : streamlit run dashboard_with_logs.py
- Visualisation auto-refresh + dashboard en temps réel

## Fonctionnalités
- Surveillance CPU / RAM / Disk
- Auto-clean pour disque plein
- Historique des incidents
- Graphiques et pie chart des incidents
- Metrics colorées selon seuils
