---
title: 'Talk name'
conference: 
  name: '{{ replace (substr .File.ContentBaseName 11) "-" " " | title }}'
#  url: ""
  city: ""
  country: "France"
  country_code: "fr" # online, fr, us, etc.
#  latitude: ""
#  longitude: ""
authors:
  - author: David Pilato
    avatar: /about/david_pilato.avif
 #   link: "https://www.linkedin.com/in/username"
date: '{{ substr .File.ContentBaseName 0 10 }}'
talk-lang: fr # fr or en
nolastmod: true
draft: true
pdf: "{{ substr .File.ContentBaseName 0 4 }}/{{ .File.ContentBaseName }}.pdf"
#cover: "cover.avif"

# talk: Talk template name (like black friday, ES|QL, Serverless, etc.)

# Speaker specific fields
#youtube: ""      # ID de la vidéo YouTube (ex: dQw4w9WgXcQ)
#links:
#  - title: ""
#    url: ""
#    description: ""

#social:
#  - "https://x.com/USERNAME/status/TWEET_ID"
#  - "https://bsky.app/profile/HANDLE.bsky.social/post/POST_RKEY"
#  - "https://www.linkedin.com/embed/feed/update/urn:li:activity:ACTIVITY_ID"
---

Write your abstract here.
