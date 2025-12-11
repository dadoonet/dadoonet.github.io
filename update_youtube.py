#!/usr/bin/env python3
"""Update markdown files with YouTube IDs."""

import re

def update_file(file_path, youtube_id):
    """Update the youtube field in a markdown file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if youtube is commented out
    if '#youtube:' in content:
        # Replace #youtube: "..." or #youtube: "" with youtube: "ID"
        new_content = re.sub(
            r'#youtube:\s*"[^"]*"',
            f'youtube: "{youtube_id}"',
            content
        )
        
        if new_content != content:
            with open(file_path, 'w') as f:
                f.write(new_content)
            return True
    
    return False

def main():
    # Read YouTube results
    with open('/tmp/youtube_results.txt', 'r') as f:
        lines = f.readlines()
    
    # Remove duplicates while preserving order
    seen = set()
    unique_lines = []
    for line in lines:
        if line.strip() and line.strip() not in seen:
            seen.add(line.strip())
            unique_lines.append(line.strip())
    
    updated = 0
    for line in unique_lines:
        parts = line.split('|')
        if len(parts) != 2:
            continue
        
        file_path, youtube_id = parts
        
        if update_file(file_path, youtube_id):
            print(f"✓ Updated {file_path} with {youtube_id}")
            updated += 1
        else:
            print(f"✗ Skipped {file_path} (no #youtube: found)")
    
    print(f"\nTotal updated: {updated}")

if __name__ == "__main__":
    main()

