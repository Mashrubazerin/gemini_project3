from flask import Flask, request, render_template, jsonify
from PIL import Image, UnidentifiedImageError
import os
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

undertone_data = {
    "Cool": {
        "emoji": "💙",
        "summary": "Cool foundation, berry blush. 💄 Ash blonde, burgundy.",
        "colors": ["#5B72E5", "#D9B8F9", "#94D7E3"],
        "recommendations": {
            "Dress Colors": "sapphire, emerald, ruby, icy blue, lavender, soft rose",
            "Makeup": "Blue-based red lipstick, mauve tones, silver eyeshadow",
            "Hair": "Ash blonde, platinum, cool brown, blue-black"
        }
    },
    "Warm": {
        "emoji": "🧡",
        "summary": "Golden glow with peach makeup. 🍑 Honey or chestnut hair.",
        "colors": ["#FFA85C", "#E36C5B", "#B39C5F"],
        "recommendations": {
            "Dress Colors": "olive, rust, mustard, warm brown",
            "Makeup": "Peach blush, coral lipstick, gold eyeshadow",
            "Hair": "Golden blonde, honey, chestnut, auburn"
        }
    },
    "Neutral": {
        "emoji": "⚪",
        "summary": "Soft balance. 🌸 Blush makeup & subtle highlights.",
        "colors": ["#EADFE4", "#BDC8C0", "#D9AFAF"],
        "recommendations": {
            "Dress Colors": "Soft rose, jade, blush, teal, gray",
            "Makeup": "Neutral blush, berry lipstick, taupe eyeshadow",
            "Hair": "Neutral brown, dark blonde, bronde with highlights"
        }
    }
}

def analyze_skin_tone(image_path):
    try:
        image = Image.open(image_path).convert('RGB')
        image = image.resize((300, 300))
        center_crop = image.crop((100, 100, 200, 200))
        pixels = np.array(center_crop).reshape(-1, 3)
        avg_color = np.mean(pixels, axis=0)
        r, g, b = avg_color

        if b > r and b > g:
            undertone = "Cool"
        elif r > b and g >= b:
            undertone = "Warm"
        else:
            undertone = "Neutral"

        return undertone
    except UnidentifiedImageError:
        raise ValueError("Uploaded file is not a valid image.")
    except Exception as e:
        raise RuntimeError(f"Error analyzing image: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files['image']
        if not file:
            return jsonify({'error': 'No image uploaded'}), 400

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        filename = file.filename
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        undertone = analyze_skin_tone(path)
        data = undertone_data.get(undertone)

        return jsonify({
            "undertone": undertone,
            "emoji": data["emoji"],
            "summary": data["summary"],
            "colors": data["colors"],
            "recommendations": data["recommendations"],
            "image_url": path
        })
    except Exception as e:
        return jsonify({'error': f'Failed to analyze image: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
