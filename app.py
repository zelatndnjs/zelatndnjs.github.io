from flask import Flask, request, render_template
from scrapers import search_all

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', results=None, term='')


@app.route('/search', methods=['GET'])
def search():
    term = (request.args.get('q') or '').strip()
    if not term:
        return render_template('index.html', results=None, term=term)
    results = search_all(term)
    return render_template('index.html', results=results, term=term)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
