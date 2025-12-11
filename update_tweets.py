#!/usr/bin/env python3
"""Add tweets to markdown files."""

import re
import os

def parse_tweets_results():
    """Parse the tweets results file."""
    results = []
    current_file = None
    current_tweets = []
    
    with open('/tmp/tweets_results.txt', 'r') as f:
        for line in f:
            line = line.rstrip()
            if line.startswith('FILE: '):
                if current_file and current_tweets:
                    results.append({
                        'file': current_file,
                        'tweets': current_tweets
                    })
                current_file = line[6:]
                current_tweets = []
            elif line.startswith('  - user: '):
                user = line.split('"')[1]
                current_tweets.append({'user': user})
            elif line.startswith('    id: ') and current_tweets:
                tweet_id = line.split('"')[1]
                current_tweets[-1]['id'] = tweet_id
    
    if current_file and current_tweets:
        results.append({
            'file': current_file,
            'tweets': current_tweets
        })
    
    return results

def add_tweets_to_file(file_path, tweets):
    """Add tweets section to markdown file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if x: already exists
    if '\nx:' in content or '\nx:\n' in content:
        return False
    
    # Build tweets YAML
    tweets_yaml = "\nx:\n"
    for t in tweets:
        tweets_yaml += f'  - user: "{t["user"]}"\n'
        tweets_yaml += f'    id: "{t["id"]}"\n'
    
    # Find the end of frontmatter (after the last field before ---)
    # Insert before the closing ---
    
    # Find the position to insert (just before the closing --- of frontmatter)
    # The frontmatter ends with --- on its own line
    lines = content.split('\n')
    frontmatter_end = -1
    in_frontmatter = False
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                frontmatter_end = i
                break
    
    if frontmatter_end == -1:
        return False
    
    # Insert tweets before the closing ---
    new_lines = lines[:frontmatter_end] + [tweets_yaml.rstrip()] + lines[frontmatter_end:]
    new_content = '\n'.join(new_lines)
    
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    return True

def main():
    results = parse_tweets_results()
    print(f"Found {len(results)} files with tweets")
    
    updated = 0
    for r in results:
        file_path = r['file']
        tweets = r['tweets']
        
        # Skip if too many tweets (likely spam)
        if len(tweets) > 20:
            print(f"⚠ Skipping {file_path} ({len(tweets)} tweets - too many)")
            continue
        
        if add_tweets_to_file(file_path, tweets):
            print(f"✓ Added {len(tweets)} tweets to {file_path}")
            updated += 1
        else:
            print(f"✗ Skipped {file_path} (already has x: section)")
    
    print(f"\nTotal updated: {updated}")

if __name__ == "__main__":
    main()

