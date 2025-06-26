import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

api_key = os.getenv("JINA_API_KEY")
headers = {
    "Authorization": api_key, # has bearer prefix
    "X-Md-Link-Style": "discarded"
}

def jina(url:str):
    endpoint = f"https://r.jina.ai/{url}"
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        content = response.text
        return content
    else:
        return f"Error: {response.status_code}"

if __name__ == "__main__":
    #url = "https://www.climate.gov/news-features/understanding-climate/climate-change-atmospheric-carbon-dioxide"
    #url = "https://store.steampowered.com/app/413150"
    #url = "http://arxiv.org/abs/2504.15392v1"
    #url = "http://arxiv.org/pdf/2001.09608v1.pdf"
    url = "https://www.goodreads.com/book/show/35487222-barkus?from_search=true&from_srp=true&qid=eN3qNuTEkh&rank=1"
    #url = "https://www.imdb.com/title/tt15398776"
    res = jina(url)
    print(res)
    #print(type(res))
    token_info = model.count_tokens(res)
    print("🔢 Token count:", token_info.total_tokens)
