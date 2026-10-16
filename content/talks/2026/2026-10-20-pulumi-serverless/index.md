---
title: "Give your coding agent an (Elastic) memory"
conference: 
  name: "Pulumi workshop"
  city: "Online"
  country: "Online"
  country_code: "online"
  url: "https://www.pulumi.com/events/give-your-coding-agent-an-elastic-memory/"
authors: 
  - author: Engin Diri
    link: "https://www.linkedin.com/in/engin-diri/"
  - author: David Pilato
talk: Serverless
date: 2026-10-20
talk-lang: en
nolastmod: true
draft: false
#pdf: "2026/2026-10-20-pulumi-serverless.pdf"


# Speaker specific fields
#youtube: "Iz_KLhYB9to"

links:
  - title: "Documentation: Elastic Serverless"
    url: "https://www.elastic.co/docs/deploy-manage/deploy/elastic-cloud/serverless"
    description: "This is the official Elastic Serverless documentation."
  - title: "Documentation: Elasticsearch Serverless API"
    url: "https://www.elastic.co/docs/api/doc/elasticsearch-serverless/"
    description: "This is the official Elasticsearch Serverless API documentation."
---

If you work with a coding agent every day, you know the routine. Each new session starts blank: the agent re-reads files it read yesterday, asks about decisions you settled last week, and redoes debugging you already finished. Its only memory is the context window, and that empties every time you close your laptop.

Claude Code ships a built-in fix: markdown notes the agent writes for itself and reads back at the next session start. It helps, but the notes live on one machine, there is no real search, and anything past the first page of the index gets dropped.

In this hands-on workshop, we’ll take that idea further with agent-memory, an open source project that keeps decisions, tasks, and session history in Elasticsearch, so they’re searchable and shared across machines. You’ll stand up the whole memory backend on Elastic Cloud with one Pulumi command, wire it into your coding agent, then kill the agent mid-task and see how much a fresh one remembers when its memory is a search engine instead of a text file.

You’ll leave with a repo you can review and share, so every teammate gets an identical memory backend instead of their own snowflake. No promises about becoming a 1000x AI engineer, but your agent will stop asking you the same question twice.

What you'll learn:

* Why built-in markdown memory breaks down across sessions, machines, and teams.
* How agent-memory stores and searches agent context in Elasticsearch.
* How to deploy the memory backend to Elastic Cloud Serverless with Pulumi as reviewable code.
* How to plug it into your coding agent and recover a killed session.
