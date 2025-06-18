# Multi-Engine Search System

A collection of search engine integrations for various platforms and data sources.

## Active Engines

### General Search

- **Bing** - Web search engine using Microsoft's Bing API
- **Wikipedia** - Encyclopedia articles and knowledge base search

### Location

- **OpenStreetMap** - Geographic and location-based search
- **Apple Maps** - Location search using Apple Maps (via DuckDuckGo integration)

### Academic & Research

- **arXiv** - Scientific paper repository search with focus on physics, mathematics, computer science
- **Astrophysics Data System** - NASA/Harvard's database for astronomy and physics research

### Entertainment & Media

- **IMDb** - Movie, TV show, and entertainment industry database search
- **Steam** - Video game store search (works best with specific game titles)
- **DeviantArt** - Art and creative works search engine

### Social & Community

- **Reddit** - Community discussion and content aggregation search
- **Goodreads** - Book recommendation and review platform search

### Tech

- **Hacker News** - Tech news and discussion platform search
- **GitHub** - Code repository and software project search
- **Hugging Face** - Machine learning model, dataset, and space search

## Non-Working Engines (Attempted)

Located in `engine-not-working/`:

- **Baidu** - Chinese search engine
- **Reuters** - News search
- **Yahoo News** - News aggregation
- **BASE (Bielefeld Academic Search Engine)** - Academic search engine

## Planned Future Integrations

### Media & Entertainment

- **YouTube** - Video platform search
- **DailyMotion** - Video sharing platform
- **Rotten Tomatoes** - Movie review aggregator
- **Pinterest** - Visual discovery platform

### Academic & Reviews

- **Google Scholar** - Academic paper search
- **Stack Exchange** - Q&A network search
- **Google Images** - Image search

### News & Photos

- **Google News** - News aggregation
- **Unsplash** - Free high-resolution photo search

## Query Types and Best Engines

Different engines work best for different types of queries:

- **Books & Literature** → Goodreads
- **Academic Research** → arXiv, Astrophysics Data System
- **Community Advice** → Reddit
- **Factual Information** → Wikipedia
- **Location Search** → OpenStreetMap, Apple Maps
- **Code & Software** → GitHub
- **Art & Creative Works** → DeviantArt
- **Games** → Steam
- **Music** → Spotify

## Usage Notes

- Some engines require API keys (Bing, Spotify)
- Steam search works best with specific game titles rather than general categories
- Apple Maps search requires precise location names for best results

## Setup

1. Clone the repository
2. Create a `.env` file with required API keys
3. Install dependencies
4. Import desired engines from the `engines/` directory
