#!/usr/bin/env python3
"""Fetch YouTube IDs from Notist pages using only standard library."""

import urllib.request
import re
import ssl
import time

# Disable SSL verification for simplicity
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def fetch_url(url):
    """Fetch URL content."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return ""

def get_youtube_id(notist_id):
    """Get YouTube ID from Notist page."""
    # Fetch main page
    main_html = fetch_url(f"https://noti.st/{notist_id}")
    
    # Find embed ID
    match = re.search(r'notist\.ninja/embed/([a-zA-Z0-9]+)', main_html)
    if not match:
        return None
    
    embed_id = match.group(1)
    
    # Fetch embed page
    embed_html = fetch_url(f"https://notist.ninja/embed/{embed_id}")
    
    # Find YouTube ID
    match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', embed_html)
    if match:
        return match.group(1)
    
    return None

def main():
    # Read remaining talks
    with open('/tmp/notist_to_check.txt', 'r') as f:
        lines = f.readlines()[84:]  # Start from line 85 (0-indexed: 84)
    
    results = []
    total = len(lines)
    
    for i, line in enumerate(lines, 85):
        parts = line.strip().split('|')
        if len(parts) != 2:
            continue
        
        file_path, notist_id = parts
        youtube_id = get_youtube_id(notist_id)
        
        if youtube_id:
            print(f"[{i}/140] {notist_id} -> {youtube_id}")
            results.append(f"{file_path}|{youtube_id}")
        
        time.sleep(0.2)
    
    # Append to results file
    with open('/tmp/youtube_results.txt', 'a') as f:
        for r in results:
            f.write(r + '\n')
    
    print(f"\nFound {len(results)} additional YouTube IDs")

if __name__ == "__main__":
    main()

