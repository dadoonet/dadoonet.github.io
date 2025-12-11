#!/usr/bin/env python3
"""Fetch Twitter/X posts from Notist pages."""

import urllib.request
import re
import ssl
import time
import os

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

def get_tweets(notist_id):
    """Get tweets from Notist page."""
    html = fetch_url(f"https://noti.st/{notist_id}")
    
    # Find Twitter/X posts
    # Pattern: twitter.com/USER/status/ID or x.com/USER/status/ID
    tweets = []
    seen = set()
    
    for match in re.finditer(r'(?:twitter|x)\.com/([^/"\s]+)/status/(\d+)', html):
        user = match.group(1)
        tweet_id = match.group(2)
        
        # Skip non-user paths
        if user in ['i', 'intent', 'share', 'search']:
            continue
        
        key = f"{user}:{tweet_id}"
        if key not in seen:
            seen.add(key)
            tweets.append({'user': user, 'id': tweet_id})
    
    return tweets

def main():
    # Read all talks with notist
    talks_dir = "content/talks"
    results = []
    
    for root, dirs, files in os.walk(talks_dir):
        if 'index.md' in files:
            file_path = os.path.join(root, 'index.md')
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if file already has x: section
            if '\nx:' in content or '\nx:\n' in content:
                continue
            
            # Extract notist ID
            match = re.search(r'^notist:\s*"?([^"\n]+)"?', content, re.MULTILINE)
            if match:
                notist_id = match.group(1).strip('"')
                
                # Only check files that have a notist but no x: section
                tweets = get_tweets(notist_id)
                if tweets:
                    results.append({
                        'file': file_path,
                        'notist': notist_id,
                        'tweets': tweets
                    })
                    print(f"Found {len(tweets)} tweets for {file_path}")
                    for t in tweets[:5]:
                        print(f"  - @{t['user']}: {t['id']}")
                    
                time.sleep(0.2)
    
    # Save results
    print(f"\n=== Summary ===")
    print(f"Files with tweets: {len(results)}")
    
    # Write results for manual review
    with open('/tmp/tweets_results.txt', 'w') as f:
        for r in results:
            f.write(f"FILE: {r['file']}\n")
            f.write(f"NOTIST: {r['notist']}\n")
            f.write("TWEETS:\n")
            for t in r['tweets']:
                f.write(f"  - user: \"{t['user']}\"\n")
                f.write(f"    id: \"{t['id']}\"\n")
            f.write("\n")

if __name__ == "__main__":
    main()

