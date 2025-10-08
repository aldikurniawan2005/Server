from flask import Flask, request, send_from_directory, render_template_string, jsonify
import os, mimetypes
from datetime import datetime

app = Flask(__name__)

UPLOADS_FOLDER = "uploads"
IMAGE_FOLDER = os.path.join(UPLOADS_FOLDER, "images")
VIDEO_FOLDER = os.path.join(UPLOADS_FOLDER, "videos")

os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

STYLE = """
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: 'Segoe UI', Tahoma, sans-serif;
        background-color: #0f0f0f;
        color: #e0e0e0;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 600;
        margin-bottom: 10px;
        text-align: left;
    }
    p { color: #bbb; margin-bottom: 15px; text-align: left; }

    /* Navbar */
    .navbar {
        background: #1a1a1a;
        padding: 12px 40px;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        gap: 25px;
        border-bottom: 1px solid #333;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .navbar a {
        color: #f0f0f0;
        font-size: 15px;
        font-weight: 500;
        text-decoration: none;
    }
    .navbar a:hover {
        color: #1e90ff;
    }

    /* Konten utama di bawah navbar */
    .main {
        padding: 25px 40px;
        text-align: left;
    }

    .upload-box {
        background: #1c1c1c;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 16px 20px;
        margin-top: 20px;
        width: 100%;
        max-width: 500px;
    }

    .upload-box h3 {
        margin-bottom: 10px;
        font-size: 15px;
        color: #fff;
        text-align: left;
    }

    input[type=file] {
        background: #222;
        color: #ccc;
        border: 1px solid #333;
        padding: 8px;
        border-radius: 6px;
        width: 70%;
        font-size: 13px;
    }
    button {
        padding: 8px 14px;
        background: #1e90ff;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        margin-left: 10px;
        font-size: 13px;
    }
    button:hover {
        background: #0d74d1;
    }

    /* Grid layout untuk galeri */
    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 16px;
        margin-top: 20px;
    }
    .card {
        background: #1b1b1b;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 3px 8px rgba(0,0,0,0.4);
        transition: all 0.2s ease;
        text-align: left;
    }
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.5);
    }
    .card img, .card video {
        width: 100%;
        height: 150px;
        object-fit: cover;
        border-bottom: 1px solid #333;
    }
    .card-info {
        padding: 10px 14px;
        text-align: left;
    }
    .card-info strong {
        display: block;
        font-size: 13px;
        color: #fff;
        margin-bottom: 4px;
        word-wrap: break-word;
    }
    .time {
        color: #aaa;
        font-size: 12px;
    }
    .empty {
        font-size: 14px;
        color: #999;
        margin-top: 15px;
        text-align: left;
    }
</style>
"""

NAVBAR = """
<div class="navbar">
    <a href='/'>🏠 Home</a>
    <a href='/gallery/images'>🖼️ Foto</a>
    <a href='/gallery/videos'>🎥 Video</a>
</div>
"""

@app.route("/")
def home():
    return render_template_string(f"""
        {STYLE}
        {NAVBAR}
        <div class="main">
            <h1>📁 Server Media Capture</h1>
            <p>Upload foto atau video di bawah ini, lalu lihat di galeri kiri atas menu.</p>
            <div class="upload-box">
                <h3>🔼 Upload File</h3>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" required>
                    <button type="submit">Upload</button>
                </form>
            </div>
        </div>
    """)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files["file"]
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = file.filename
    mime_type = mimetypes.guess_type(filename)[0] or file.mimetype

    if "image" in mime_type:
        file.save(os.path.join(IMAGE_FOLDER, filename))
        folder = "images"
    elif "video" in mime_type:
        file.save(os.path.join(VIDEO_FOLDER, filename))
        folder = "videos"
    else:
        return jsonify({"error": f"Tipe file {mime_type} tidak didukung"}), 400

    return jsonify({"status": "success", "folder": folder, "filename": filename}), 200

@app.route("/gallery/images")
def gallery_images():
    files = sorted(os.listdir(IMAGE_FOLDER), key=lambda f: os.path.getmtime(os.path.join(IMAGE_FOLDER, f)), reverse=True)
    cards = []
    for f in files:
        t = datetime.fromtimestamp(os.path.getmtime(os.path.join(IMAGE_FOLDER, f))).strftime("%d %B %Y, %H:%M:%S")
        cards.append(f"""
        <div class='card'>
            <a href='/images/{f}' target='_blank'>
                <img src='/images/{f}' alt='{f}'>
            </a>
            <div class='card-info'>
                <strong>{f}</strong>
                <span class='time'>📅 {t}</span>
            </div>
        </div>
        """)
    return render_template_string(f"{STYLE}{NAVBAR}<div class='main'><h2>🖼️ Galeri Foto</h2><div class='grid'>{''.join(cards) if cards else '<p class=empty>Belum ada foto.</p>'}</div></div>")

@app.route("/gallery/videos")
def gallery_videos():
    files = sorted(os.listdir(VIDEO_FOLDER), key=lambda f: os.path.getmtime(os.path.join(VIDEO_FOLDER, f)), reverse=True)
    cards = []
    for f in files:
        t = datetime.fromtimestamp(os.path.getmtime(os.path.join(VIDEO_FOLDER, f))).strftime("%d %B %Y, %H:%M:%S")
        cards.append(f"""
        <div class='card'>
            <video src='/videos/{f}' controls></video>
            <div class='card-info'>
                <strong>{f}</strong>
                <span class='time'>📅 {t}</span>
            </div>
        </div>
        """)
    return render_template_string(f"{STYLE}{NAVBAR}<div class='main'><h2>🎥 Galeri Video</h2><div class='grid'>{''.join(cards) if cards else '<p class=empty>Belum ada video.</p>'}</div></div>")

@app.route("/images/<path:filename>")
def get_image(filename): return send_from_directory(IMAGE_FOLDER, filename)

@app.route("/videos/<path:filename>")
def get_video(filename): return send_from_directory(VIDEO_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
