from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, world'

@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    """ Flask-based Proxy Server """
    target_url = request.args.get('url')  # Client se destination URL lena
    if not target_url:
        return jsonify({"error": "URL is required"}), 400

    try:
        if request.method == 'GET':
            response = requests.get(target_url, headers=request.headers)
        elif request.method == 'POST':
            response = requests.post(target_url, json=request.json, headers=request.headers)
        else:
            return jsonify({"error": "Method not supported"}), 405
        
        # Response forward karo
        return (response.content, response.status_code, response.headers.items())

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test():
    return 'Test'
