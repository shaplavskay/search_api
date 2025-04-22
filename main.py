from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

def parse_zhnivo(surname):
    url = f"https://db.zhnivo.com/by/belarus-genealogical-databases/?s={surname}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception:
        return []
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []
    table = soup.find('table', class_='table')
    if table:
        for tr in table.find_all('tr')[1:]:
            tds = tr.find_all('td')
            if len(tds) >= 6:
                results.append({
                    'surname': tds[0].get_text(strip=True),
                    'name': tds[1].get_text(strip=True),
                    'year': tds[2].get_text(strip=True),
                    'region': tds[3].get_text(strip=True),
                    'site': 'Жніво',
                    'link': tds[5].find('a')['href'] if tds[5].find('a') else url
                })
    return results

@app.route('/search')
def search():
    surname = request.args.get('surname', '').strip()
    if not surname:
        return jsonify({'error': 'surname required'}), 400
    results = parse_zhnivo(surname)
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
