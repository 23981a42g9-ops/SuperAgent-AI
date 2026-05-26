from flask import Flask, request, jsonify
from flask_cors import CORSMiddleware
import ollama, urllib.parse, json

app = Flask(__name__)
CORSMiddleware(app)

# Global Sector Matrix with 2026 Fallback Arrays
SECTOR_MAP = {
    "food": ["https://www.zomato.com/search?query={q}", "https://www.swiggy.com/search?q={q}", "https://www.ubereats.com/search?q={q}"],
    "grocery": ["https://www.zeptonow.com/search?q={q}", "https://www.bigbasket.com/ps/?q={q}", "https://www.instamart.com/search?q={q}", "https://www.amazon.in/pantry/s?k={q}"],
    "shopping": ["https://www.meesho.com/search?q={q}&sort=price_asc", "https://www.amazon.in/s?k={q}", "https://www.flipkart.com/search?q={q}", "https://www.ebay.com/sch/i.html?_nkw={q}"],
    "travel": ["https://www.redbus.in/search?fromCityName={q}", "https://www.makemytrip.com/search?q={q}", "https://www.skyscanner.net/transport/flights?query={q}"],
    "movies": ["https://in.bookmyshow.com/explore/search?q={q}", "https://www.google.com/search?q=movie+theaters+near+me+playing+{q}", "https://www.justtickets.in/search?q={q}"],
    "emergency": ["https://www.google.com/maps/search/emergency+{q}+near+me", "tel:102", "https://www.google.com/search?q=emergency+hospitals+near+me"],
    "district": ["https://www.google.com/search?q={q}+local+district+sales+and+deals", "https://www.facebook.com/marketplace/search/?query={q}"]
}

@app.route('/ai', methods=['POST'])
def process_ai():
    user_input = request.json.get('text', '').lower()
    
    # Prompt Ollama to extract the Sector and the "Sale" intent
    prompt = f"""
    Analyze: "{user_input}"
    Identify Sector: food, grocery, shopping, travel, movies, emergency, district.
    Identify Query: specific name or item.
    Check Sale: is user looking for cheap/low-cost?
    Return JSON ONLY:
    {{
      "sector": "sector_name",
      "query": "search_keyword",
      "reply": "Supersonic voice response",
      "is_sale": true/false
    }}
    """
    try:
        response = ollama.generate(model='llama3', prompt=prompt, format='json')
        data = json.loads(response['response'])
        sector = data.get('sector', 'shopping')
        query = data.get('query', user_input)
        
        # Get fallback URLs for the identified sector
        raw_urls = SECTOR_MAP.get(sector, ["https://www.google.com/search?q={q}"])
        final_urls = [u.format(q=urllib.parse.quote(query)) for u in raw_urls]

        return jsonify({
            "reply": data['reply'],
            "urls": final_urls,
            "is_sale": data.get('is_sale', False),
            "sector": sector
        })
    except:
        return jsonify({"reply": "System Error. Is Ollama running?", "urls": []})

if __name__ == '__main__':
    app.run(port=8000, debug=True)
