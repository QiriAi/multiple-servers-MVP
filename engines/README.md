# Engines

LEARNINGS:

- Some engines work better to ask entities (important phrases or words) rather than whole questions as would get received from the chat interface - these are noted down e.g. arxiv performs very poorly with getting relevant articles if I search up "tell me about what llms are" vs just "llms"
- Also add free proxies to not get banned

ENGINES HAVE DIFFERENT METHODS OF RETRIVAL:

- Arxiv = This is the official api to access arXiv programmatically. The response is Atom XML with namespaces. No API key is needed - it's public. The retrieval type is simple keyword search + metadata filtering.

GOAL:

- Trying to make all the engines return relevant links
