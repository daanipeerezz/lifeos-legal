#!/usr/bin/env python3
"""Genera index.html y condiciones.html a partir de LegalView.swift de la app,
para que la web y lo que se lee dentro de LifeOS digan siempre lo mismo.

    python3 generar.py
"""
import html, os, re

APP = os.path.expanduser('~/Desktop/Proyectos/LifeOS_App/LifeOS/Views/Shared/LegalView.swift')
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(APP, encoding='utf-8').read()

def const(name):
    return re.search(r'static let %s = "([^"]*)"' % name, src).group(1)

values = {'supportEmail': const('supportEmail'), 'lastUpdated': const('lastUpdated')}

def sections(name):
    block = re.search(r'static let %s: \[LegalSection\] = \[(.*?)\n    \]' % name, src, re.S).group(1)
    out = []
    for heading, body in re.findall(r'\.init\(heading: "([^"]*)",\s*body: """\n(.*?)\n\s*"""\)', block, re.S):
        lines = [l.strip() for l in body.split('\n')]
        text = '\n'.join(lines).strip()
        text = re.sub(r'\\\((\w+)\)', lambda m: values[m.group(1)], text)
        out.append((heading, text))
    return out

def linkify(text):
    t = html.escape(text, quote=False)
    mail = html.escape(values['supportEmail'])
    return t.replace(mail, '<a href="mailto:%s">%s</a>' % (mail, mail))

head = open(os.path.join(HERE, 'index.html'), encoding='utf-8').read()
style = re.search(r'<style>.*?</style>', head, re.S).group(0)

def page(title, desc, current, secs):
    nav = ''.join('    <a href="%s"%s>%s</a>\n' % (href, ' aria-current="page"' if href == current else '', label)
                  for href, label in [('./', 'Política de privacidad'), ('./condiciones.html', 'Condiciones de uso')])
    body = ''.join('  <h2>%s</h2>\n  <p>%s</p>\n' % (html.escape(h), linkify(t)) for h, t in secs)
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{style}
<title>{title} · LifeOS</title>
<meta name="description" content="{desc}">
</head>
<body>
<div class="wrap">
<header>
  <p class="brand">LifeOS</p>
  <h1>{title}</h1>
  <p class="meta">Última revisión: {values['lastUpdated']}</p>
  <nav>
{nav}  </nav>
</header>
{body}<footer>
  LifeOS · Daniel Pérez López · <a href="mailto:{values['supportEmail']}">{values['supportEmail']}</a><br>
  Este texto es el mismo que se puede leer dentro de la app, en Configuración.
</footer>
</div>
</body>
</html>
'''

open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(
    page('Política de privacidad', 'Qué datos recoge LifeOS, dónde se guardan y con quién se comparten.', './', sections('privacySections')))
open(os.path.join(HERE, 'condiciones.html'), 'w', encoding='utf-8').write(
    page('Condiciones de uso', 'Condiciones de uso de LifeOS: tolerancia cero con el contenido ofensivo, denuncias y moderación.', './condiciones.html', sections('termsSections')))
print('ok')
