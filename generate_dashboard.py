report_dir = 'report'
log_file = 'logs/monitor.log'
html_file = 'dashboard.html'

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>Dashboard surveillance</title></head>
<body>
<h1>Dashboard</h1>
<h2>Graphiques</h2>
""")
    # Ajouter toutes les images du dossier report
    import os
    for img in os.listdir(report_dir):
        if img.endswith('.png'):
            f.write(f'<img src="{report_dir}/{img}" alt="{img}">\n')

    # Ajouter les logs
    f.write("<h2>Logs récents</h2>\n<pre>\n")
    if os.path.exists(log_file):
      with open(log_file, 'r', encoding='utf-8', errors='ignore') as logf:
       f.write(logf.read())

    f.write("</pre>\n</body>\n</html>")
