from engines.google import get_google_urls
from engines.reddit import search_reddit
from engines.wikipedia import search_wikipedia
from engines.goodreads import search_goodreads
from engines.arxiv import search_arxiv
from engines.steam import search_steam_store
from engines.imdb import search_imdb
from engines.deviantart import search_deviantart
from engines.github import search_github_repos
from engines.hackernews import search_hackernews
from engines.huggingface import search_huggingface
from engines.openstreetmap import search_osm
from engines.astrophysics_data_system import search_ads
from engines.jina_search import jina_search

# Map engine names to their search functions
SEARCH_ENGINES = {
    "jina_search": jina_search,
    "google": get_google_urls,
    "reddit": search_reddit,
    "wikipedia": search_wikipedia,
    "goodreads": search_goodreads,
    "arxiv": search_arxiv,
    "steam": search_steam_store,
    "imdb": search_imdb,
    "deviantart": search_deviantart,
    "github": search_github_repos,
    "hackernews": search_hackernews,
    "huggingface": search_huggingface,
    "openstreetmap": search_osm,
    "astrophysics_data_system": search_ads
}