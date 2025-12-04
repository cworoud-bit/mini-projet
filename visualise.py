#!/usr/bin/env python3
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


DB_FILE = 'db.sqlite3'


def load_incidents():
conn = sqlite3.connect(DB_FILE)
df = pd.read_sql_query('SELECT * FROM incidents', conn, parse_dates=['ts'])
conn.close()
return df


if __name__ == '__main__':
df = load_incidents()
if df.empty:
print('Aucun incident enregistré.')
exit()


# incidents per type
counts = df['type'].value_counts()
counts.plot(kind='bar')
plt.title('Nombre d\'incidents par type')
plt.tight_layout()
plt.savefig('report/incidents_by_type.png')


# timeline: CPU/RAM/DISK events
df_thr = df[df['type']=='threshold_exceeded']
if not df_thr.empty:
df_thr['date'] = pd.to_datetime(df_thr['ts']).dt.date
pivot = df_thr.groupby(['date','target']).size().unstack(fill_value=0)
pivot.plot()
plt.title('Incidents seuils par jour')
plt.tight_layout()
plt.savefig('report/thresholds_timeline.png')


print('Graphiques générés dans report/')