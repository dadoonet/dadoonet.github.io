#!/usr/bin/env python3
"""
Script pour générer les talks à partir de l'API Notist de speaker.pilato.fr
"""

import json
import os
import re
import urllib.request
import urllib.error
import ssl
import html
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Configuration
BASE_URL = "https://speaker.pilato.fr"
TALKS_DIR = Path(__file__).parent / "content" / "talks"
EXISTING_TALKS = set()

# Créer un contexte SSL qui ne vérifie pas les certificats
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def slugify(text):
    """Convertit un texte en slug URL-friendly."""
    text = text.lower()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ýÿ]', 'y', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r"[''`]", '-', text)
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def fetch_json(url):
    """Récupère le JSON depuis une URL."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"  ⚠️  Erreur lors de la récupération de {url}: {e}")
        return None


def download_file(url, dest_path):
    """Télécharge un fichier."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ssl_context, timeout=60) as response:
            with open(dest_path, 'wb') as f:
                f.write(response.read())
        return True
    except Exception as e:
        print(f"  ⚠️  Erreur téléchargement {url}: {e}")
        return False


def html_to_text(html_content):
    """Convertit le HTML en texte simple."""
    if not html_content:
        return ""
    # Supprimer les balises HTML
    text = re.sub(r'<[^>]+>', '', html_content)
    # Décoder les entités HTML
    text = html.unescape(text)
    return text.strip()


def extract_city_from_address(address):
    """Extrait la ville de l'adresse."""
    if not address:
        return ""
    # Format typique: "21000 Dijon, France" ou "Paris, France"
    parts = address.split(',')
    if len(parts) >= 1:
        city_part = parts[0].strip()
        # Enlever le code postal s'il y en a
        match = re.search(r'(?:\d{5}\s+)?(.+)', city_part)
        if match:
            return match.group(1).strip()
    return address


def get_country_name(country_code):
    """Retourne le nom du pays à partir du code."""
    countries = {
        'FR': 'France',
        'BE': 'Belgium',
        'CH': 'Switzerland',
        'CA': 'Canada',
        'GB': 'United Kingdom',
        'UK': 'United Kingdom',
        'US': 'United States',
        'DE': 'Germany',
        'ES': 'Spain',
        'IT': 'Italy',
        'NL': 'Netherlands',
        'PL': 'Poland',
        'PT': 'Portugal',
        'LU': 'Luxembourg',
        'SG': 'Singapore',
        'MU': 'Mauritius',
        'BG': 'Bulgaria',
        'RS': 'Serbia',
        'MA': 'Morocco',
    }
    return countries.get(country_code.upper(), country_code)


def process_presentation(pres_data):
    """Traite une présentation et génère le talk."""
    pres_id = pres_data['id'].replace('pr_', '')
    title = pres_data['attributes']['title']
    presented_on = pres_data['attributes']['presented_on']
    
    # Extraire la date
    date = datetime.strptime(presented_on.split(' ')[0], '%Y-%m-%d')
    date_str = date.strftime('%Y-%m-%d')
    
    # Récupérer les détails complets de la présentation
    detail_url = f"{BASE_URL}/{pres_id}.json"
    details = fetch_json(detail_url)
    
    if not details or 'data' not in details or not details['data']:
        print(f"  ⚠️  Impossible de récupérer les détails pour {pres_id}")
        return None
    
    detail = details['data'][0]
    attrs = detail['attributes']
    
    # Extraire les infos de l'événement
    event_info = {}
    if 'relationships' in detail and 'data' in detail['relationships']:
        events = detail['relationships']['data']
        if events:
            event = events[0]['attributes']
            event_info = {
                'name': event.get('title', ''),
                'url': event.get('url', ''),
                'city': extract_city_from_address(event.get('address', '')),
                'country': get_country_name(event.get('country_code', 'FR')),
                'country_code': event.get('country_code', 'fr').lower(),
            }
    
    # Créer le slug pour le répertoire
    event_slug = slugify(event_info.get('name', 'unknown'))
    dir_name = f"{date_str}-{event_slug}"
    talk_dir = TALKS_DIR / dir_name
    
    # Vérifier si le talk existe déjà
    if talk_dir.exists():
        print(f"  ⏭️  Talk déjà existant: {dir_name}")
        return dir_name
    
    # Créer le répertoire
    talk_dir.mkdir(parents=True, exist_ok=True)
    
    # Récupérer l'URL de la première slide pour la couverture
    cover_url = None
    if 'slidedeck' in attrs and 'data' in attrs['slidedeck'] and attrs['slidedeck']['data']:
        slides_data = attrs['slidedeck']['data'][0]
        if 'slides' in slides_data and slides_data['slides']:
            cover_url = slides_data['slides'][0].get('image')
    
    # Récupérer l'URL du PDF
    pdf_url = attrs.get('download')
    
    # Télécharger la couverture
    if cover_url:
        cover_ext = 'png' if cover_url.endswith('.png') else 'jpg'
        cover_path = talk_dir / f"cover.{cover_ext}"
        if download_file(cover_url, cover_path):
            print(f"  📸 Image téléchargée: {cover_path.name}")
    
    # Télécharger le PDF
    pdf_path = None
    if pdf_url:
        pdf_name = f"{dir_name}.pdf"
        pdf_path = talk_dir / pdf_name
        if download_file(pdf_url, pdf_path):
            print(f"  📄 PDF téléchargé: {pdf_name}")
    
    # Extraire la description
    description = ""
    if 'blurb' in attrs and attrs['blurb']:
        description = html_to_text(attrs['blurb'].get('html', ''))
    
    # Générer le fichier index.md
    cover_file = None
    for ext in ['png', 'jpg', 'jpeg', 'JPG', 'PNG']:
        if (talk_dir / f"cover.{ext}").exists():
            cover_file = f"cover.{ext}"
            break
    
    # Corriger l'URL si elle est None
    event_url = event_info.get('url', '') or ''
    if event_url == 'None':
        event_url = ''
    
    frontmatter = f'''---
title: "{title}"
description: ""
conference: 
  name: "{event_info.get('name', '')}"
  url: "{event_url}"
  city: "{event_info.get('city', '')}"
  country: "{event_info.get('country', '')}"
  country_code: "{event_info.get('country_code', 'fr')}"
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - elasticsearch
  - conference
  - java
  - cloud
categories:
  - speaker
series:
  - conferences
date: {date_str}
nolastmod: true
draft: false
'''
    
    if cover_file:
        frontmatter += f'cover: {cover_file}\n'
    
    frontmatter += f'''
# Speaker specific fields
#youtube: ""
notist: "dadoonet/{pres_id}"
---

{description}
'''
    
    index_path = talk_dir / "index.md"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
    
    print(f"✅ Talk créé: {dir_name}")
    return dir_name


def main():
    print("🚀 Génération des talks depuis speaker.pilato.fr\n")
    
    # Récupérer la liste des présentations
    print("📥 Récupération de la liste des présentations...")
    presentations_url = f"{BASE_URL}/presentations.json"
    data = fetch_json(presentations_url)
    
    if not data or 'data' not in data:
        print("❌ Impossible de récupérer les présentations")
        return
    
    presentations = data['data']
    print(f"📊 {len(presentations)} présentations trouvées\n")
    
    # Lister les talks existants
    if TALKS_DIR.exists():
        for item in TALKS_DIR.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                EXISTING_TALKS.add(item.name)
    print(f"📁 {len(EXISTING_TALKS)} talks existants\n")
    
    # Traiter chaque présentation
    created = 0
    skipped = 0
    errors = 0
    
    for i, pres in enumerate(presentations, 1):
        title = pres['attributes']['title']
        print(f"\n[{i}/{len(presentations)}] {title}")
        
        try:
            result = process_presentation(pres)
            if result:
                if result in EXISTING_TALKS:
                    skipped += 1
                else:
                    created += 1
                    EXISTING_TALKS.add(result)
            else:
                errors += 1
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            errors += 1
    
    print(f"\n{'='*50}")
    print(f"📊 Résumé:")
    print(f"   - Créés: {created}")
    print(f"   - Existants (ignorés): {skipped}")
    print(f"   - Erreurs: {errors}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()

