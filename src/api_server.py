from fastapi import Depends, FastAPI, Header, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_401_UNAUTHORIZED
from pydantic import BaseModel
from src.main import SearchBot
from dotenv import load_dotenv
import os

load_dotenv()

# Your API key from .env
API_KEY = os.getenv("FASTAPI_KEY")
API_KEY_NAME = "X-API-Key"

app = FastAPI(title="SearchBot API")

bot = SearchBot()

class QueryRequest(BaseModel):
    query: str

api_key_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: str = Security(api_key_scheme)) -> str:
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/search")
def search(request: QueryRequest,
           api_key: APIKey = Depends(get_api_key)
           ):
    result = bot.main(request.query)
    return result

# RUN: uvicorn src.api_server:app --host 0.0.0.0 --port 8000
# swagger UI at http://localhost:8000/docs