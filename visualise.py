#!/usr/bin/env python3
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_FILE = 'db.sqlite3'
REPORT_DIR = 'report'

def load_incidents():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT * FROM incidents', conn, parse_dates=['ts'])
    conn.close()
    return df

def plot_incidents_by_type(df):
    """Graphique : nombre d'incidents par type"""
    counts = df['type'].value_counts()
    counts.plot(kind='bar')
    plt.title("Nombre d'incidents par type")
    plt.ylabel("Nombre")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, 'incidents_by_type.png'))
    plt.close()

def plot_threshold_timeline(df):
    """Graphique : timeline des incidents de seuil"""
    df_thr = df[df['type'] == 'threshold_exceeded'].copy()
    if df_thr.empty:
        return
    df_thr['date'] = df_thr['ts'].dt.date
    pivot = df_thr.groupby(['date', 'target']).size().unstack(fill_value=0)
    pivot.plot()
    plt.title('Incidents seuils par jour')
    plt.ylabel("Nombre")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, 'thresholds_timeline.png'))
    plt.close()

def plot_dynamic_per_type_target(df):
    """Graphique dynamique : chaque type et chaque target"""
    for incident_type in df['type'].unique():
        df_type = df[df['type'] == incident_type].copy()
        if df_type.empty:
            continue

        # Graphique général par date
        df_type['date'] = df_type['ts'].dt.date
        pivot = df_type.groupby(['date', 'target']).size().unstack(fill_value=0)
        pivot.plot()
        plt.title(f"Incidents '{incident_type}' par jour et par cible")
        plt.ylabel("Nombre")
        plt.tight_layout()
        filename = f"{incident_type}_by_date_target.png".replace(" ", "_")
        plt.savefig(os.path.join(REPORT_DIR, filename))
        plt.close()

def main():
    df = load_incidents()
    if df.empty:
        print('Aucun incident enregistré.')
        return

    # Créer le dossier report si nécessaire
    os.makedirs(REPORT_DIR, exist_ok=True)

    # Graphiques
    plot_incidents_by_type(df)
    plot_threshold_timeline(df)
    plot_dynamic_per_type_target(df)

    print(f"Graphiques générés dans {REPORT_DIR}/")

if __name__ == '__main__':
    main()
