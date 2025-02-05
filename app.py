from flask import Flask, request
from PIL import Image, ImageDraw, ImageFont
import requests
import os
import textwrap
from dotenv import load_dotenv

app = Flask(__name__)

# Environment variables (set on your server)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    process_receipt(data)
    return 'OK'

def process_receipt(receipt_data):
    # Extract customer Telegram ID from Loyverse
    customer = receipt_data.get('customer', {})
    telegram_id = customer.get('telegram_id')

    if not telegram_id:
        print("No Telegram ID found for customer.")
        return

    # Generate receipt image
    img_path = generate_receipt_image(receipt_data)
    
    # Send via Telegram
    send_telegram_image(telegram_id, img_path)
    
    # Clean up temporary image
    os.remove(img_path)

def generate_receipt_image(data):
    # Create image
    img = Image.new('RGB', (500, 800), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("fonts/Roboto-Regular.ttf", 20)  # Custom font (optional)

    # Header
    y = 20
    draw.text((50, y), "🏪 YOUR STORE NAME", font=font, fill=(0, 0, 0))
    y += 40

    # Customer Info
    customer = data.get('customer', {})
    draw.text((50, y), f"Customer: {customer.get('name', 'Guest')}", font=font, fill=(0, 0, 0))
    y += 40

    # Items
    for item in data.get('line_items', []):
        text = f"{item['name']} x{item['quantity']} - ${item['price']}"
        draw.text((50, y), text, font=font, fill=(0, 0, 0))
        y += 30

    # Total
    y += 20
    draw.text((50, y), f"TOTAL: ${data.get('total_price', '0.00')}", font=font, fill=(0, 0, 0))

    # Save image
    img_path = f"receipt_{data['id']}.png"
    img.save(img_path)
    return img_path

def send_telegram_image(chat_id, img_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(img_path, 'rb') as photo:
        response = requests.post(
            url,
            files={'photo': photo},
            data={'chat_id': chat_id}
        )
    if response.status_code != 200:
        print(f"Failed to send image: {response.text}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
