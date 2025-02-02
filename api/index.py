from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, world'

@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    """Flask-based Proxy Server with Redirect Handling"""
    target_url = request.args.get('url')  # Client se destination URL lena
    if not target_url:
        return jsonify({"error": "URL is required"}), 400

    # Prevent proxy from calling itself (recursion)
    if request.host in target_url or "localhost" in target_url:
        return jsonify({"error": "Proxy recursion detected"}), 400

    try:
        session = requests.Session()
        session.max_redirects = 5  # Set redirect limit to avoid infinite loops

        if request.method == 'GET':
            response = session.get(target_url, headers=request.headers, allow_redirects=True, timeout=10)
        elif request.method == 'POST':
            response = session.post(target_url, json=request.json, headers=request.headers, allow_redirects=True, timeout=10)
        else:
            return jsonify({"error": "Method not supported"}), 405
        
        # Return response with status and headers
        return (response.content, response.status_code, response.headers.items())

    except requests.exceptions.TooManyRedirects:
        return jsonify({"error": "Too many redirects. Limit reached (5)."}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test():
    return 'Test'

