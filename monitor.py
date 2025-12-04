import os
import subprocess
import time
import sqlite3
import logging
from datetime import datetime
import psutil
import shutil
# Configuration
CHECK_INTERVAL_MIN = 1 # intervalle en minutes
SERVICES = ["nginx", "mysql", "ssh"]
THRESHOLDS = {
'cpu_percent': 85.0,
'ram_percent': 90.0,
'disk_percent': 90.0,
}
LOG_FILE = 'logs/monitor.log'
DB_FILE = 'db.sqlite3'
TMP_CLEAN_PATHS = ['/tmp'] # chemins à nettoyer si nécessaire


# Logger
os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename=LOG_FILE,
level=logging.INFO,
format='%(asctime)s %(levelname)s %(message)s')

# DB helper
def init_db():
 conn = sqlite3.connect(DB_FILE)
 cur = conn.cursor()
 cur.execute('''
CREATE TABLE IF NOT EXISTS incidents (
id INTEGER PRIMARY KEY AUTOINCREMENT,
ts TEXT,
type TEXT,
target TEXT,
metric REAL,
threshold REAL,
action TEXT,
notes TEXT
)
''')
 conn.commit()
 conn.close()


def log_incident(type_, target, metric, threshold, action, notes=''):
 conn = sqlite3.connect(DB_FILE)
 cur = conn.cursor()
 cur.execute('''INSERT INTO incidents (ts, type, target, metric, threshold, action, notes)
VALUES (?, ?, ?, ?, ?, ?, ?)''',
(datetime.utcnow().isoformat(), type_, target, metric, threshold, action, notes))
 conn.commit()
 conn.close()
 logging.info(f"INCIDENT {type_} {target} metric={metric} thr={threshold} action={action} notes={notes}")


# Service check
def is_service_active(service_name):
  
 try:
    res = subprocess.run(['systemctl', 'is-active', service_name], capture_output=True, text=True)
    return res.stdout.strip() == 'active'
 except Exception as e:
  logging.error(f"Erreur vérif service {service_name}: {e}")
  return False


def restart_service(service_name):
 try:
  res = subprocess.run(['sudo', 'systemctl', 'restart', service_name], capture_output=True, text=True)
  ok = res.returncode == 0
  notes = res.stdout + res.stderr
  return ok, notes
 except Exception as e:
  return False, str(e)


# Cleanup action example
def cleanup_tmp():
 removed = 0
 for base in TMP_CLEAN_PATHS:
    
  for root, dirs, files in os.walk(base):
    
   for f in files:
    
      try:
       fp = os.path.join(root, f)
    # safety rule: only remove files older than X days? for demo we remove none
    # os.remove(fp)
       removed += 0

      except Exception as e:
       logging.warning(f"Impossible de supprimer {fp}: {e}")
 return removed


# Metrics
def get_metrics():
 cpu = psutil.cpu_percent(interval=1)
 vm = psutil.virtual_memory()
 disk = psutil.disk_usage('/')
 net = psutil.net_io_counters()
 return {
'cpu_percent': cpu,
'ram_percent': vm.percent,
'disk_percent': disk.percent,
'net_bytes_sent': net.bytes_sent,
'net_bytes_recv': net.bytes_recv
}

SERVICES = ["nginx", "mysql", "ssh"]
import subprocess

def is_service_active(service):
    try:
        res = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True)
        return res.stdout.strip() == "active"
    except:
        return False

def restart_service(service):
    try:
        res = subprocess.run(["systemctl", "restart", service], capture_output=True, text=True)
        ok = res.returncode == 0
        notes = res.stdout + res.stderr
        return ok, notes
    except Exception as e:
        return False, str(e)

def log_incident(type, item, value, threshold, action, notes):
    print(f"[INCIDENT] {type} - {item} - action:{action} notes:{notes}")

# Main loop
def run_once():
 metrics = get_metrics()


# Check services
 for s in SERVICES:
  active = is_service_active(s)
 if not active:
  action = 'attempt_restart'
  ok, notes = restart_service(s)
 if ok:
  log_incident('service_down', s, 0.0, 0.0, 'restarted', notes)
 else:
  log_incident('service_down', s, 0.0, 0.0, 'restart_failed', notes)


# Check thresholds
 for m, thr in THRESHOLDS.items():
  val = metrics.get(m)
 if val is not None and val >= thr:
 # corrective action
  if m == 'disk_percent':
   removed = cleanup_tmp()
   notes = f'cleaned {removed} files'
   action = 'cleanup_tmp'
  else:
   action = 'notify'
   notes = ''
 log_incident('threshold_exceeded', m, float(val), float(thr), action, notes)


# Also log metrics periodically
 logging.info(f"METRICS {metrics}")

 if __name__ == '__main__':
    init_db()
 while True:
  try:
   run_once()
  except Exception as e:
   logging.exception(f"Erreur dans run_once: {e}")
   time.sleep(CHECK_INTERVAL_MIN * 60)