# Mini-Projet: Surveillance Proactive et Auto-Réparation

## Description
Ce projet permet de surveiller en temps réel l'état des services et des ressources système (CPU, RAM, Disk) avec auto-réparation et enregistrement des incidents. Il propose un dashboard graphique pour visualiser l'évolution des ressources et des incidents.

---

## Branches

### main
- Contient la version de base du dashboard.

### dashboard-with-logs
- Version améliorée avec le fichier **`dashboard_with_logs.py`**.
- **Features principales :**
  - Affichage des **metrics CPU, RAM, Disk** avec couleurs (vert/rouge) selon les seuils.
  - Historique des ressources dans un **graphique temps réel**.
  - **Pie chart** montrant la répartition des incidents par service.
  - Tableau des **incidents enregistrés**.
  - **Auto-refresh** toutes les 5 secondes.

---

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/votre-utilisateur/mini-projet.git
