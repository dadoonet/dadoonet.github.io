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
    avatar: /about/david_pilato.png
 #   link: "https://www.linkedin.com/in/username"
date: '{{ substr .File.ContentBaseName 0 10 }}'
talk-lang: fr # fr or en
nolastmod: true
draft: true
pdf: "{{ substr .File.ContentBaseName 0 4 }}/{{ .File.ContentBaseName }}.pdf"
#cover: "cover.png"

# talk: Talk template name (like black friday, ES|QL, Serverless, etc.)

# Speaker specific fields
#youtube: ""      # ID de la vidéo YouTube (ex: dQw4w9WgXcQ)
#links:
#  - title: ""
#    url: ""
#    description: ""

#x:
#  - user: "USERNAME"
#    id: "TWEET_ID"
---

Write your abstract here.
