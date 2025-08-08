import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def resolve_short_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        response.raise_for_status()
        return response.url
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
        print(f"Error saat menghubungi API downloader: {e}")
        return None

@app.route('/download', methods=['POST'])
def handle_download_request():
    req_data = request.get_json()
    if not req_data or 'url' not in req_data:
        return jsonify({"error": "URL TikTok tidak ditemukan dalam permintaan"}), 400
    
    initial_url = req_data['url']
    final_url = initial_url  # Asumsikan URL sudah lengkap

    # --- LOGIKA BARU DITAMBAHKAN DI SINI ---
    # Hanya resolve jika ini adalah URL singkat
    if "vt.tiktok.com" in initial_url or "vm.tiktok.com" in initial_url:
        print(f"URL singkat terdeteksi ({initial_url}), me-resolve...")
        resolved_url = resolve_short_url(initial_url)
        if not resolved_url:
            return jsonify({"error": "Gagal mendapatkan URL lengkap dari link singkat (kemungkinan diblokir TikTok)."}), 400
        final_url = resolved_url
        print(f"URL lengkap ditemukan: {final_url}")
    # --- AKHIR LOGIKA BARU ---

    my_api_key = os.environ.get('TIKTOK_API_KEY')
    if not my_api_key:
        return jsonify({"error": "Kunci API server tidak diatur"}), 500

    video_data = get_video_from_tiktok_api(final_url, my_api_key)

    if video_data:
        return jsonify(video_data)
    else:
        return jsonify({"error": "Gagal mengambil data dari layanan API downloader."}), 502
