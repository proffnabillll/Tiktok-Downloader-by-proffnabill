import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# Inisialisasi aplikasi Flask
app = Flask(__name__)
CORS(app)

# Fungsi untuk memanggil API TikTok Downloader yang Anda pilih
def get_video_from_tiktok_api(tiktok_url, api_key):
    # Informasi ini diambil dari kode yang Anda berikan
    api_url = "https://tiktok-api23.p.rapidapi.com/api/download/video"
    api_host = "tiktok-api23.p.rapidapi.com"

    # Menyusun headers dengan kunci API
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host
    }

    # Menyusun parameter. Library 'requests' akan otomatis melakukan URL encoding.
    params = {
        "url": tiktok_url
    }

    try:
        # Melakukan permintaan GET ke API
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Ini akan memunculkan error jika status code bukan 200 OK
        return response.json()  # Mengembalikan hasil dalam format JSON
    except requests.exceptions.RequestException as e:
        print(f"Error saat menghubungi API: {e}")
        return None

# Rute utama yang akan dipanggil oleh front-end
@app.route('/download', methods=['POST'])
def handle_download_request():
    # Mengambil URL TikTok dari data yang dikirim front-end
    req_data = request.get_json()
    if not req_data or 'url' not in req_data:
        return jsonify({"error": "URL TikTok tidak ditemukan dalam permintaan"}), 400
    
    tiktok_url_to_download = req_data['url']

    # Mengambil kunci API dari Environment Variable di Vercel (lebih aman)
    my_api_key = os.environ.get('TIKTOK_API_KEY')
    if not my_api_key:
        return jsonify({"error": "Kunci API server tidak diatur"}), 500

    # Memanggil fungsi untuk mendapatkan data video
    video_data = get_video_from_tiktok_api(tiktok_url_to_download, my_api_key)

    if video_data:
        # Jika berhasil, kirim kembali data video ke front-end
        return jsonify(video_data)
    else:
        # Jika gagal, kirim pesan error
        return jsonify({"error": "Gagal mengambil data dari layanan API downloader"}), 502
