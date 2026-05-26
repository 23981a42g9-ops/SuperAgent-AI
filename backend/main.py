import os, json, urllib.parse, ollama
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# GLOBAL SECTOR MATRIX (Multi-site Fallbacks)
SECTOR_MAP = {
    "food": ["https://www.zomato.com/search?query={q}", "https://www.swiggy.com/search?q={q}", "https://www.ubereats.com/search?q={q}"],
    "grocery": ["https://www.zeptonow.com/search?q={q}", "https://www.bigbasket.com/ps/?q={q}", "https://www.instamart.com/search?q={q}", "https://www.amazon.in/pantry/s?k={q}"],
    "shopping": ["https://www.meesho.com/search?q={q}&sort=price_asc", "https://www.amazon.com/s?k={q}", "https://www.flipkart.com/search?q={q}", "https://www.ebay.com/sch/i.html?_nkw={q}"],
    "travel": ["https://www.redbus.in/search?fromCityName={q}", "https://www.makemytrip.com/search?q={q}", "https://www.skyscanner.net/transport/flights?query={q}", "https://www.booking.com/searchresults.html?ss={q}&order=price"],
    "movies": ["https://in.bookmyshow.com/explore/search?q={q}", "https://www.fandango.com/search?q={q}", "https://www.google.com/search?q=movie+theaters+near+me+playing+{q}"],
    "emergency": ["https://www.google.com/maps/search/emergency+{q}+near+me", "tel:102", "https://www.google.com/search?q=emergency+hospitals+near+me"],
    "district": ["https://www.google.com/search?q={q}+local+district+sales", "https://www.facebook.com/marketplace/search/?query={q}", "https://www.indiamart.com/search.mp?ss={q}"],
    "temples": ["https://www.google.com/maps/search/{q}+best+temples+nearby/@17.6,83.2,12z/data=!3m1!4b1!4m2!2m1!6e1"]
}

@app.post("/ai")
async def process_ai(request: Request):
    body = await request.json()
    user_input = body.get('text', '').lower()
    
    prompt = f"""
    Analyze user intent: "{user_input}"
    Classify into: food, grocery, shopping, travel, movies, emergency, district, temples.
    Return ONLY JSON:
    {{
      "sector": "sector_name",
      "query": "search_keyword",
      "reply": "Short supersonic voice confirmation",
      "is_sale": true/false
    }}
    """
    try:
        res = ollama.generate(model=os.getenv("OLLAMA_MODEL", "llama3"), prompt=prompt, format='json')
        data = json.loads(res['response'])
        
        sector = data.get('sector', 'shopping')
        query = data.get('query', user_input)
        
        # Select best URLs based on sector
        raw_urls = SECTOR_MAP.get(sector, ["https://www.google.com/search?q={q}"])
        final_urls = [u.format(q=urllib.parse.quote(query)) for u in raw_urls]

        return {
            "reply": data['reply'],
            "urls": final_urls,
            "is_sale": data.get('is_sale', False),
            "sector": sector
        }
    except Exception as e:
        return {"reply": "Ollama error. Check local server.", "urls": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
