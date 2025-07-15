from flask import Flask, jsonify
from scrape import get_bounties

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    response = get_bounties()
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True) 