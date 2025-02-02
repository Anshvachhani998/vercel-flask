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


# ✅ URLs for Testing Proxy
TEST_URL_HTTP = "http://httpbin.org/ip"
TEST_URL_HTTPS = "https://httpbin.org/ip"

@app.route('/c', methods=['GET'])
def proxy_check():
    proxy = request.args.get('proxy')  # Proxy format: ip:port
    proxy_type = request.args.get('type', 'http')  # Default HTTP, change to https if needed
    
    if not proxy:
        return jsonify({"error": "❌ Proxy is required! Use ?proxy=IP:PORT&type=http/https"}), 400

    # ✅ Proxy Format
    proxy_url = f"{proxy_type}://{proxy}"
    proxies = {proxy_type: proxy_url}

    try:
        test_url = TEST_URL_HTTP if proxy_type == "http" else TEST_URL_HTTPS
        response = requests.get(test_url, proxies=proxies, timeout=10)

        return jsonify({
            "status": "✅ Proxy is Active!",
            "proxy": proxy_url,
            "proxy_type": proxy_type,
            "response": response.json()
        })
    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "❌ Proxy Test Failed!",
            "proxy": proxy_url,
            "proxy_type": proxy_type,
            "error": str(e)
        })

@app.route('/test')
def test():
    return 'Test'

