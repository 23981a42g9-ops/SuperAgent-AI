import os, json, urllib.parse, ollama
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# UNIVERSAL PERMIT: This fixes the "Offline" status
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HEALTH CHECK: Needed for the UI to see the backend as "Online"
@app.get("/")
async def root():
    return {"status": "online", "agent": "SuperAgent Supersonic v4"}

# FULL SECTOR MATRIX - ALL CONDITIONS
SECTOR_MAP = {
    "food": ["https://www.zomato.com/search?query={q}", "https://www.swiggy.com/search?q={q}", "https://www.ubereats.com/search?q={q}"],
    "grocery": ["https://www.zeptonow.com/search?q={q}", "https://www.bigbasket.com/ps/?q={q}", "https://www.blinkit.com/s/?q={q}"],
    "shopping": ["https://www.meesho.com/search?q={q}&sort=price_asc", "https://www.amazon.in/s?k={q}", "https://www.flipkart.com/search?q={q}"],
    "travel": ["https://www.redbus.in/search?fromCityName={q}", "https://www.makemytrip.com/search?q={q}", "https://www.skyscanner.net/transport/flights?query={q}"],
    "movies": ["https://in.bookmyshow.com/explore/search?q={q}", "https://www.fandango.com/search?q={q}", "https://www.google.com/search?q=movie+theaters+near+me+{q}"],
    "emergency": ["https://www.google.com/maps/search/emergency+{q}+near+me", "tel:102", "https://www.google.com/search?q=emergency+hospitals+near+me"],
    "district": ["https://www.indiamart.com/search.mp?ss={q}", "https://www.facebook.com/marketplace/search/?query={q}", "https://www.google.com/search?q={q}+local+district+sales"],
    "temples": ["https://www.google.com/maps/search/{q}+best+temples+nearby/@17.6,83.2,12z/data=!3m1!4b1!4m2!2m1!6e1"]
}

@app.post("/ai")
async def process_ai(request: Request):
    body = await request.json()
    user_input = body.get('text', '').lower()
    print(f"📥 Intent Received: {user_input}")
    
    prompt = f"""
    Analyze: "{user_input}"
    JSON ONLY: {{"sector": "food/travel/shopping/grocery/movies", "query": "search term", "reply": "short voice response", "is_sale": false}}
    """
    
    try:
        # Use a direct client call to avoid library timeouts
        from ollama import Client
        client = Client(host='http://127.0.0.1:11434')
        res = client.generate(model="llama3", prompt=prompt, format='json')
        
        data = json.loads(res['response'])
        sector = data.get('sector', 'shopping')
        query = data.get('query', user_input)
        
        raw_urls = SECTOR_MAP.get(sector, ["https://www.google.com/search?q={q}"])
        final_urls = [u.format(q=urllib.parse.quote(query)) for u in raw_urls]

        print(f"🚀 Sector: {sector} | Status: Success")
        return {"reply": data['reply'], "urls": final_urls, "is_sale": data.get('is_sale', False)}

    except Exception as e:
        print(f"❌ Backend Error: {e}")
        # Fallback if Ollama is actually being slow
        return {
            "reply": "I'm processing your request, but the brain is a bit slow. Let me open the search for you directly.",
            "urls": [f"https://www.google.com/search?q={urllib.parse.quote(user_input)}"],
            "is_sale": False
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
