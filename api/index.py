import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# Inisialisasi aplikasi Flask
app = Flask(__name__)
CORS(app)

def resolve_short_url(url):
    """
    Mengikuti redirect dari URL singkat untuk mendapatkan URL lengkap.
    """
    try:
        # Menggunakan HEAD request agar lebih cepat, karena kita hanya butuh URL final
        response = requests.head(url, allow_redirects=True, timeout=5)
        response.raise_for_status()
        return response.url  # Mengembalikan URL final setelah semua redirect
    except requests.exceptions.RequestException as e:
        print(f"Gagal me-resolve URL singkat: {e}")
        return None

def get_video_from_tiktok_api(tiktok_url, api_key):
    api_url = "https://tiktok-max-quality.p.rapidapi.com/download/"
    api_host = "tiktok-max-quality.p.rapidapi.com"
    headers = { "x-rapidapi-key": api_key, "x-rapidapi-host": api_host }
    params = { "url": tiktok_url }

    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error saat menghubungi API: {e}")
        return None

# Rute utama yang akan dipanggil oleh front-end
@app.route('/download', methods=['POST'])
def handle_download_request():
    req_data = request.get_json()
    if not req_data or 'url' not in req_data:
        return jsonify({"error": "URL TikTok tidak ditemukan dalam permintaan"}), 400
    
    short_url = req_data['url']

    # --- LANGKAH BARU DITAMBAHKAN DI SINI ---
    print(f"Menerima URL: {short_url}")
    print("Me-resolve URL lengkap...")
    full_url = resolve_short_url(short_url)
    
    if not full_url:
        return jsonify({"error": "Gagal mendapatkan URL lengkap dari link yang diberikan"}), 400
    
    print(f"URL lengkap ditemukan: {full_url}")
    # --- AKHIR LANGKAH BARU ---

    my_api_key = os.environ.get('TIKTOK_API_KEY')
    if not my_api_key:
        return jsonify({"error": "Kunci API server tidak diatur"}), 500

    # Memanggil API downloader dengan URL yang sudah lengkap
    video_data = get_video_from_tiktok_api(full_url, my_api_key)

    if video_data:
        return jsonify(video_data)
    else:
        return jsonify({"error": "Gagal mengambil data dari layanan API downloader"}), 502
