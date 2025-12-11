#!/usr/bin/env python3
"""
Script to fetch YouTube video IDs and Twitter/X posts from Notist pages.
"""

import os
import re
import requests
from pathlib import Path
import time

def get_notist_data(notist_id):
    """Fetch YouTube ID and tweets from a Notist page."""
    url = f"https://noti.st/{notist_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text
        
        # Find YouTube video ID
        youtube_id = None
        # Pattern 1: youtube.com/watch?v=ID
        match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})', html)
        if match:
            youtube_id = match.group(1)
        # Pattern 2: youtube.com/embed/ID
        if not youtube_id:
            match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', html)
            if match:
                youtube_id = match.group(1)
        # Pattern 3: youtu.be/ID
        if not youtube_id:
            match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', html)
            if match:
                youtube_id = match.group(1)
        
        # Find Twitter/X posts
        tweets = []
        # Pattern: twitter.com/USER/status/ID or x.com/USER/status/ID
        tweet_matches = re.findall(r'(?:twitter|x)\.com/([^/]+)/status/(\d+)', html)
        for user, tweet_id in tweet_matches:
            if user not in ['i', 'intent', 'share']:  # Skip non-user paths
                tweets.append({'user': user, 'id': tweet_id})
        
        return {
            'youtube_id': youtube_id,
            'tweets': tweets
        }
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {'youtube_id': None, 'tweets': []}

def get_talks_with_commented_youtube():
    """Find all talks with #youtube: commented out."""
    talks_dir = Path("content/talks")
    talks = []
    
    for index_file in talks_dir.rglob("index.md"):
        content = index_file.read_text()
        if "#youtube:" in content:
            # Extract notist ID
            notist_match = re.search(r'^notist:\s*"?([^"\n]+)"?', content, re.MULTILINE)
            if notist_match:
                notist_id = notist_match.group(1).strip('"')
                talks.append({
                    'file': str(index_file),
                    'notist_id': notist_id
                })
    
    return talks

def main():
    talks = get_talks_with_commented_youtube()
    print(f"Found {len(talks)} talks with commented youtube")
    
    results = []
    for i, talk in enumerate(talks):
        print(f"\n[{i+1}/{len(talks)}] Processing {talk['file']}")
        print(f"  Notist: {talk['notist_id']}")
        
        data = get_notist_data(talk['notist_id'])
        
        if data['youtube_id']:
            print(f"  YouTube: {data['youtube_id']}")
        if data['tweets']:
            print(f"  Tweets: {len(data['tweets'])}")
            for t in data['tweets'][:3]:
                print(f"    - @{t['user']}: {t['id']}")
        
        results.append({
            'file': talk['file'],
            'notist_id': talk['notist_id'],
            **data
        })
        
        # Rate limiting
        time.sleep(0.5)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    with_youtube = [r for r in results if r['youtube_id']]
    with_tweets = [r for r in results if r['tweets']]
    
    print(f"Talks with YouTube videos: {len(with_youtube)}")
    print(f"Talks with Tweets: {len(with_tweets)}")
    
    print("\n--- Talks with YouTube ---")
    for r in with_youtube:
        print(f"{r['file']}|{r['youtube_id']}")
    
    print("\n--- Talks with Tweets ---")
    for r in with_tweets:
        print(f"{r['file']}|{len(r['tweets'])} tweets")
        for t in r['tweets']:
            print(f"  - user: \"{t['user']}\"")
            print(f"    id: \"{t['id']}\"")

if __name__ == "__main__":
    main()

