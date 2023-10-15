from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Fetch OpenAI API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_API_ENDPOINT = "https://api.openai.com/v1/engines/davinci/completions"

# Set a limit for the number of characters to pass to the model
MAX_CHARS_FOR_SUMMARY = 4096

@app.route('/fetch_text', methods=['GET'])
def fetch_body_text_api():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is missing'}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = [p.get_text().strip() for p in soup.find_all('p')]
        body_text = " ".join(paragraphs)
        word_count = len(body_text.split())
        char_count = len(body_text)
        return jsonify({
            'text': body_text.strip(),
            'word_count': word_count,
            'char_count': char_count
        })

    except requests.RequestException as e:
        return jsonify({'text': f'Error fetching content: {e}', 'word_count': 0, 'char_count': 0})
    except Exception as e:
        return jsonify({'text': f'Unexpected error: {e}', 'word_count': 0, 'char_count': 0})

@app.route('/generate_summary', methods=['GET'])
def generate_summary_api():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is missing'}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = [p.get_text().strip() for p in soup.find_all('p')]
        body_text = " ".join(paragraphs)
        
        # Limit the text to a certain number of characters for summarization
        limited_text = body_text[:MAX_CHARS_FOR_SUMMARY]

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": f"Summarize the following content in a concise manner: {limited_text}",
            "max_tokens": 600
        }
        openai_response = requests.post(OPENAI_API_ENDPOINT, headers=headers, json=data)
        openai_response.raise_for_status()
        summary = openai_response.json()["choices"][0]["text"].strip()

        return jsonify({'summary': summary})

    except requests.RequestException as e:
        return jsonify({'summary': f'Error fetching content or calling API: {e}'})
    except Exception as e:
        return jsonify({'summary': f'Unexpected error: {e}'})

@app.route('/generate_howto_guide', methods=['GET'])
def generate_howto_guide_api():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is missing'}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = [p.get_text().strip() for p in soup.find_all('p')]
        body_text = " ".join(paragraphs)
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": f"Given this text: {body_text}, Generate a Friendly How-To Guide with clear, understandable steps based on the text. Make sure to number the steps.",
            "max_tokens": 500
        }
        openai_response = requests.post(OPENAI_API_ENDPOINT, headers=headers, json=data)
        openai_response.raise_for_status()
        guide = openai_response.json()["choices"][0]["text"].strip()

        return jsonify({'guide': guide})

    except requests.RequestException as e:
        return jsonify({'guide': f'Error fetching content or calling API: {e}'})
    except Exception as e:
        return jsonify({'guide': f'Unexpected error: {e}'})

if __name__ == '__main__':
    app.run(debug=False)
