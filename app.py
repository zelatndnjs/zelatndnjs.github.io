import os
from flask import Flask, request, send_from_directory
from scrapers import search_all

app = Flask(__name__)


@app.after_request
def add_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/')
def index():
    root = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(root, 'index.html')


@app.route('/api/search', methods=['GET'])
def api_search():
    term = (request.args.get('q') or '').strip()
    if not term:
        return {'berlinstartupjobs.com': [], 'weworkremotely.com': [], 'web3.career': []}
    results = search_all(term)
    return results


if __name__ == '__main__':
    app.run(debug=True, port=5000)
