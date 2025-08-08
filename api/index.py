import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# Inisialisasi aplikasi Flask
app = Flask(__name__)
CORS(app)

# Fungsi untuk memanggil API pihak ketiga
def get_tiktok_data_from_api(tiktok_url, api_key):
    api_url = "https://tiktok-video-downloader.p.rapidapi.com/v1/download"
    api_host = "tiktok-video-downloader.p.rapidapi.com"
    headers = { "x-rapidapi-key": api_key, "x-rapidapi-host": api_host }
    querystring = { "url": tiktok_url }
    
    try:
        response = requests.get(api_url, headers=headers, params=querystring)
        response.raise_for_status() # Cek jika ada error HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API call error: {e}")
        return None

# Membuat "pintu" atau rute untuk aplikasi kita
@app.route('/download', methods=['POST'])
def handle_download():
    # 1. Ambil data yang dikirim dari front-end
    req_data = request.get_json()
    if not req_data or 'url' not in req_data:
        return jsonify({"error": "URL TikTok tidak ditemukan"}), 400
    
    tiktok_url = req_data['url']

    # 2. Ambil kunci API dari environment variable (lebih aman)
    my_api_key = os.environ.get('TIKTOK_API_KEY')
    if not my_api_key:
        return jsonify({"error": "Kunci API tidak diatur di server"}), 500

    # 3. Panggil fungsi logika utama
    result_data = get_tiktok_data_from_api(tiktok_url, my_api_key)

    if result_data:
        # 4. Kirim kembali hasilnya sebagai JSON
        return jsonify(result_data)
    else:
        return jsonify({"error": "Gagal mengambil data dari API TikTok downloader"}), 502
