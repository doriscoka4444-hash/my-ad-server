from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import urllib.parse
import urllib.request
import urllib.error
import random
import uuid
import os
import json
import threading

app = FastAPI(title="Video Ad Server", version="24.0.0 (Instant Page Load View Tracking)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

root_dir = os.path.dirname(os.path.abspath(__file__))
stats_lock = threading.Lock()

KV_URL = os.getenv("KV_REST_API_URL") or os.getenv("UPSTASH_REDIS_REST_URL") or os.getenv("REDIS_REST_URL")
KV_TOKEN = os.getenv("KV_REST_API_TOKEN") or os.getenv("UPSTASH_REDIS_REST_TOKEN") or os.getenv("REDIS_REST_TOKEN")

LAST_KNOWN_GOOD_STATS = {}

def save_global_stats_kv(data_dict: dict):
    if not KV_URL or not KV_TOKEN:
        return
    try:
        json_str = urllib.parse.quote(json.dumps(data_dict, ensure_ascii=False))
        req_url = f"{KV_URL.rstrip('/')}/set/global_ad_stats_v4/{json_str}"
        req = urllib.request.Request(req_url, headers={"Authorization": f"Bearer {KV_TOKEN}"}, method="POST")
        with urllib.request.urlopen(req, timeout=2) as resp:
            pass
    except Exception:
        pass

def load_global_stats_kv() -> dict:
    if not KV_URL or not KV_TOKEN:
        return {}
    try:
        req_url = f"{KV_URL.rstrip('/')}/get/global_ad_stats_v4"
        req = urllib.request.Request(req_url, headers={"Authorization": f"Bearer {KV_TOKEN}"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            val = data.get("result")
            if val:
                decoded_str = urllib.parse.unquote(val)
                return json.loads(decoded_str)
    except Exception:
        pass
    return {}

def find_file_recursive(filename: str):
    desktop_dir = "C:/Users/User/Desktop/videos"
    if os.path.exists(desktop_dir) and filename in os.listdir(desktop_dir):
        return os.path.join(desktop_dir, filename)

    for current_root, dirs, files in os.walk(root_dir):
        if filename in files:
            return os.path.join(current_root, filename)
    return None

# Fast HTTP 206 Partial Content Range Streaming
@app.get("/local-videos/{filename:path}")
@app.get("/api/local-videos/{filename:path}")
@app.get("/api/index/local-videos/{filename:path}")
async def serve_local_video(filename: str, request: Request, range: str = Header(None)):
    file_path = find_file_recursive(filename)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found in repository")

    file_size = os.path.getsize(file_path)
    media_type = "video/mp4" if filename.endswith(".mp4") else ("image/webp" if filename.endswith(".webp") else "application/octet-stream")

    if not range or not filename.endswith(".mp4"):
        return FileResponse(file_path, media_type=media_type, headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=31536000, immutable"
        })

    try:
        units, range_str = range.strip().split("=")
        start_str, end_str = range_str.split("-")
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else file_size - 1
    except Exception:
        start = 0
        end = file_size - 1

    if start >= file_size or end >= file_size or start > end:
        return Response(status_code=416, headers={"Content-Range": f"bytes */{file_size}", "Accept-Ranges": "bytes"})

    chunk_size = (end - start) + 1

    def iter_file():
        with open(file_path, "rb") as f:
            f.seek(start)
            bytes_left = chunk_size
            while bytes_left > 0:
                read_size = min(64 * 1024, bytes_left)
                data = f.read(read_size)
                if not data:
                    break
                bytes_left -= len(data)
                yield data

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(chunk_size),
        "Content-Type": media_type,
        "Cache-Control": "public, max-age=31536000, immutable"
    }

    return StreamingResponse(iter_file(), status_code=206, headers=headers)

wa_message = urllib.parse.quote("Dua te di me shume rreth ketij produktit!")
whatsapp_url = f"https://wa.me/355685846937?text={wa_message}"

ADS_DATABASE = {
    "reklama-1": {
        "title": "Zbulo më shumë rreth produktit",
        "video_filename": "video1_fast.mp4",
        "description": "Ofertë Ekskluzive: Kurseni sot me uljen tonë speciale!",
        "old_price": "3,100 Lekë",
        "price": "2,800 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "viewable_impressions": 0,
        "clicks": 0,
        "unmutes": 0,
        "fullscreens": 0,
        "video_completes": 0,
        "mobile_views": 0,
        "desktop_views": 0
    },
    "reklama-2": {
        "title": "Mbështetëse për Gju - Lehtësim i Dhimbjeve",
        "video_filename": "gjuri_fast.mp4",
        "description": "Zgjidhje ideale për dhimbjet e gjurit dhe rikuperim të shpejtë.",
        "old_price": "3,900 Lekë",
        "price": "3,500 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "viewable_impressions": 0,
        "clicks": 0,
        "unmutes": 0,
        "fullscreens": 0,
        "video_completes": 0,
        "mobile_views": 0,
        "desktop_views": 0
    },
    "reklama-3": {
        "title": "Ofertë e Muajit - Produkt Tepër i Kërkuar",
        "video_filename": "video3_fast.mp4",
        "description": "Cilësi e lartë, garanci prodhimi dhe dërgesë e shpejtë brenda 24 orëve.",
        "old_price": "2,800 Lekë",
        "price": "2,500 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "viewable_impressions": 0,
        "clicks": 0,
        "unmutes": 0,
        "fullscreens": 0,
        "video_completes": 0,
        "mobile_views": 0,
        "desktop_views": 0
    },
    "reklama-4": {
        "title": "Kokë dushi me disa opsione",
        "video_filename": "dushi_fast.mp4",
        "description": "Kokë dushi me shumë opsione. Ofertë: 2 Copë vetëm 2,499 Lekë!",
        "old_price": "1,699 Lekë",
        "price": "1,499 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "viewable_impressions": 0,
        "clicks": 0,
        "unmutes": 0,
        "fullscreens": 0,
        "video_completes": 0,
        "mobile_views": 0,
        "desktop_views": 0
    },
    "reklama-5": {
        "title": "Antene Televizori me magnet",
        "video_filename": "televizori_fast.mp4",
        "description": "Per te gjitha stacionet televizive tokesore, eshte me magnet.",
        "old_price": "2,200 Lekë",
        "price": "2,000 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "viewable_impressions": 0,
        "clicks": 0,
        "unmutes": 0,
        "fullscreens": 0,
        "video_completes": 0,
        "mobile_views": 0,
        "desktop_views": 0
    },
    "reklama-6": {
        "title": "Nderese rrobash",
        "video_filename": "rroba_fast.mp4",
        "description": "Nuk krijon rremuje dhe shume e lehte per tu perdorur.",
        "old_price": "3,800 Lekë",
        "price": "3,300 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "viewable_impressions": 0,
        "clicks": 0,
        "unmutes": 0,
        "fullscreens": 0,
        "video_completes": 0,
        "mobile_views": 0,
        "desktop_views": 0
    },
    "reklama-7": {
        "title": "Pompe lyerje elektrike",
        "video_filename": "pompa_fast.mp4",
        "description": "Mos u lodhni duke lyer muret me dore, pompe elektrike per ju,me super cmim.",
        "old_price": "7,500 Lekë",
        "price": "6,500 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "viewable_impressions": 0,
        "clicks": 0,
        "unmutes": 0,
        "fullscreens": 0,
        "video_completes": 0,
        "mobile_views": 0,
        "desktop_views": 0
    },
    "reklama-8": {
        "title": "Rubinet me dy koka",
        "video_filename": "rubinet_fast.mp4",
        "description": "Rubinet me dy koka, ideal per pastrimin e tualetit",
        "old_price": "3,500 Lekë",
        "price": "3,000 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "viewable_impressions": 0,
        "clicks": 0,
        "unmutes": 0,
        "fullscreens": 0,
        "video_completes": 0,
        "mobile_views": 0,
        "desktop_views": 0
    },
    "reklama-9": {
        "title": "Makine loder per femije",
        "video_filename": "makiona_fast.mp4",
        "description": "Super dhurate per te vegjlit tuaj, makine me telekomande.",
        "old_price": "6,000 Lekë",
        "price": "5,000 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "viewable_impressions": 0,
        "clicks": 0,
        "unmutes": 0,
        "fullscreens": 0,
        "video_completes": 0,
        "mobile_views": 0,
        "desktop_views": 0
    },
    "reklama-10": {
        "title": "Shtrydhese per limon,portokall dhe shege",
        "video_filename": "shtrydhese_fast.mp4",
        "description": "Kjo shtrydhese eshte shume efikase dhe e shpejte.",
        "old_price": "5,200 Lekë",
        "price": "4,500 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "viewable_impressions": 0,
        "clicks": 0,
        "unmutes": 0,
        "fullscreens": 0,
        "video_completes": 0,
        "mobile_views": 0,
        "desktop_views": 0
    }
}

def get_server_base(request: Request) -> str:
    env_base = os.getenv("SERVER_BASE")
    if env_base:
        return env_base.rstrip("/")
    return str(request.base_url).rstrip("/")

@app.get("/", response_class=HTMLResponse)
@app.get("/api", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse)
async def home(request: Request):
    server_base = get_server_base(request)
    ads_list = ""
    for ad_id, ad in ADS_DATABASE.items():
        ads_list += f"""
        <div style="background: #fff; padding: 20px; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
            <h3 style="margin-top:0; color: #1877f2;">{ad['title']} ({ad_id})</h3>
            <p>{ad['description']}</p>
            <p><strong>Video:</strong> {ad['video_filename']} | <strong>Çmimi:</strong> {ad['price']} <span style="text-decoration: line-through; color: #888;">{ad['old_price']}</span></p>
            <div style="background: #f0f2f5; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 13px; word-break: break-all;">
                &lt;script async src="{server_base}/loader.js" data-ad-slot="{ad_id}"&gt;&lt;/script&gt;
            </div>
        </div>
        """

    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="sq">
    <head>
        <meta charset="UTF-8">
        <title>Video Ad Server Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f8; margin: 0; padding: 40px; color: #333; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            h1 {{ color: #1a1a1a; }}
            .nav-links {{ margin: 20px 0; }}
            .nav-links a {{ background: #27ae60; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-right: 10px; display: inline-block; }}
            .nav-links a.stats {{ background: #e67e22; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Video Ad Server Live Dashboard</h1>
            <p>Serveri është aktiv me numërim automatik të menjëhershëm.</p>
            <div class="nav-links">
                <a href="{server_base}/stats" class="stats">📊 Shiko Statistikat (Analytics)</a>
            </div>
            <h2>Reklamat e Dispozicionit:</h2>
            {ads_list}
        </div>
    </body>
    </html>
    """, media_type="text/html; charset=utf-8")

# Transparent 1x1 GIF for Image Beacon Responses
GIF_1X1 = bytes.fromhex("47494638396101000100800000ffffff00000021f90401000000002c00000000010001000002024401003b")

@app.get("/loader.js")
@app.get("/api/loader.js")
@app.get("/api/index/loader.js")
async def get_loader_script(request: Request):
    ads_json = {}
    for ad_id, ad in ADS_DATABASE.items():
        ads_json[ad_id] = {
            "title": ad["title"],
            "description": ad["description"],
            "video_filename": ad["video_filename"],
            "old_price": ad["old_price"],
            "price": ad["price"],
            "whatsapp_link": ad["whatsapp_link"]
        }

    ads_js_str = json.dumps(ads_json, ensure_ascii=False)

    js_code = f"""
    (function() {{
        let scriptTag = document.currentScript;
        if (!scriptTag) {{
            const allScripts = document.querySelectorAll("script[src*='loader.js']");
            for (let i = 0; i < allScripts.length; i++) {{
                if (!allScripts[i].dataset.processed) {{
                    scriptTag = allScripts[i];
                    break;
                }}
            }}
        }}
        if (!scriptTag) return;
        scriptTag.dataset.processed = "true";

        let slotAttr = scriptTag.getAttribute("data-ad-slot");
        let adId = slotAttr;

        if (!slotAttr || slotAttr === "auto" || slotAttr === "mix") {{
            const randomIdx = Math.floor(Math.random() * 10) + 1;
            adId = "reklama-" + randomIdx;
        }}

        let serverBase = "";
        try {{
            if (scriptTag.src) {{
                const urlObj = new URL(scriptTag.src);
                serverBase = urlObj.origin;
            }}
        }} catch(e) {{}}
        if (!serverBase) {{
            serverBase = window.location.origin;
        }}

        const ADS_DATA = {ads_js_str};
        const rawAd = ADS_DATA[adId] || ADS_DATA["reklama-1"];
        if (!rawAd) return;

        const ad = {{
            title: rawAd.title,
            description: rawAd.description,
            video_url: serverBase + "/local-videos/" + rawAd.video_filename,
            old_price: rawAd.old_price,
            price: rawAd.price,
            whatsapp_link: rawAd.whatsapp_link,
            tracking_url: serverBase + "/track-click/" + adId,
            event_url: serverBase + "/track-event/" + adId
        }};

        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

        // 100% Reliable Cross-Origin Image Beacon Tracker
        function logEvent(eventType) {{
            const beaconUrl = ad.event_url + "/" + eventType + (isMobile ? "?device=mobile&_t=" : "?device=desktop&_t=") + Date.now();
            if (navigator.sendBeacon) {{
                navigator.sendBeacon(beaconUrl);
            }} else {{
                const img = new Image();
                img.src = beaconUrl;
            }}
        }}

        // INSTANT VIEW LOGGING ON SCRIPT EXECUTION (Just like before!)
        logEvent("view");

        let viewableCounted = false;

        const container = document.createElement("div");
        container.style.width = "100%";
        container.style.margin = "14px 0";

        container.innerHTML = `
            <style>
                .adsense-card-native * {{ box-sizing: border-box; }}
                .adsense-card-native {{
                    border: 1px solid #dadce0;
                    border-radius: 8px;
                    background: #ffffff;
                    width: 100%;
                    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    position: relative;
                    overflow: hidden;
                    box-shadow: 0 1px 3px rgba(60,64,67,0.08);
                    transition: border-color 0.15s ease, box-shadow 0.15s ease;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                    contain: content;
                }}
                .adsense-card-native:hover {{
                    border-color: #bdc1c6;
                    box-shadow: 0 2px 8px rgba(60,64,67,0.15);
                }}
                .adsense-card-native .adsense-header {{
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 8px 12px 0 12px;
                }}
                .adsense-card-native .ad-badge {{
                    background: #f1f3f4;
                    color: #202124;
                    border: 1px solid #dadce0;
                    font-size: 10px;
                    font-weight: 700;
                    padding: 1px 5px;
                    border-radius: 3px;
                    letter-spacing: 0.2px;
                }}
                .adsense-card-native .ad-sponsor {{
                    color: #5f6368;
                    font-size: 11px;
                    font-weight: 500;
                }}
                .adsense-card-native .adsense-body {{
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    padding: 8px 14px 12px 14px;
                    gap: 14px;
                    width: 100%;
                }}
                .adsense-card-native .video-container {{
                    flex: 0 0 135px;
                    width: 135px;
                    height: 135px;
                    background: #0f1419;
                    border-radius: 6px;
                    overflow: hidden;
                    position: relative;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .adsense-card-native .video-container video {{
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                    display: block;
                    background: #0f1419;
                }}
                .adsense-card-native .sound-notice {{
                    position: absolute;
                    bottom: 5px;
                    left: 5px;
                    background: rgba(15, 20, 25, 0.88);
                    color: #ffffff;
                    font-size: 9px;
                    font-weight: 700;
                    padding: 2px 6px;
                    border-radius: 3px;
                    pointer-events: none;
                }}
                .adsense-card-native .fullscreen-btn {{
                    position: absolute;
                    top: 5px;
                    right: 5px;
                    background: rgba(15, 20, 25, 0.88);
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    width: 22px;
                    height: 22px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 11px;
                    z-index: 5;
                }}
                .adsense-card-native .info-container {{
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    min-width: 0;
                }}
                .adsense-card-native .rating-box {{
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    margin-bottom: 3px;
                }}
                .adsense-card-native .rating-box .stars {{
                    font-size: 11px;
                }}
                .adsense-card-native .rating-box .rating-num {{
                    color: #5f6368;
                    font-size: 11px;
                    font-weight: 600;
                }}
                .adsense-card-native .ad-title {{
                    font-size: 15.5px;
                    font-weight: 700;
                    color: #1a0dab;
                    margin: 0 0 3px 0;
                    line-height: 1.3;
                    text-decoration: none;
                    letter-spacing: -0.015em;
                }}
                .adsense-card-native .ad-title:hover {{
                    text-decoration: underline;
                }}
                .adsense-card-native .ad-desc {{
                    font-size: 12px;
                    color: #4d5156;
                    margin: 0 0 6px 0;
                    line-height: 1.35;
                    font-weight: 400;
                }}
                .adsense-card-native .price-row {{
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    margin-bottom: 8px;
                }}
                .adsense-card-native .new-price {{
                    font-size: 17.5px;
                    font-weight: 800;
                    color: #202124;
                    letter-spacing: -0.02em;
                }}
                .adsense-card-native .old-price {{
                    font-size: 12px;
                    color: #70757a;
                    text-decoration: line-through;
                    font-weight: 500;
                }}
                .adsense-card-native .cta-btn {{
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    gap: 6px;
                    background: #1a73e8;
                    color: #ffffff;
                    text-align: center;
                    padding: 8px 16px;
                    border-radius: 18px;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 13px;
                    letter-spacing: -0.01em;
                    transition: background 0.15s ease, box-shadow 0.15s ease;
                    width: fit-content;
                }}
                .adsense-card-native .cta-btn:hover {{
                    background: #1557b0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                }}
                @media (max-width: 500px) {{
                    .adsense-card-native .adsense-body {{
                        flex-direction: column;
                        align-items: center;
                        text-align: center;
                        padding: 8px 12px 12px 12px;
                        gap: 10px;
                    }}
                    .adsense-card-native .video-container {{
                        width: 100%;
                        height: 160px;
                        flex: none;
                    }}
                    .adsense-card-native .info-container {{
                        width: 100%;
                        align-items: center;
                    }}
                    .adsense-card-native .price-row {{
                        justify-content: center;
                    }}
                    .adsense-card-native .rating-box {{
                        justify-content: center;
                    }}
                    .adsense-card-native .cta-btn {{
                        width: 100%;
                    }}
                }}
            </style>
            <div class="adsense-card-native" id="adCardNative">
                <div class="adsense-header">
                    <span class="ad-badge">Ad</span>
                    <span class="ad-sponsor">Sponsorizuar &bull; Ofertë Ekskluzive</span>
                </div>
                <div class="adsense-body">
                    <div class="video-container" id="videoContainer">
                        <video id="adVideo" src="${{ad.video_url}}" autoplay muted playsinline loop preload="metadata" controlsList="nodownload" oncontextmenu="return false;"></video>
                        <div id="soundNotice" class="sound-notice">Kliko per ze</div>
                        <button class="fullscreen-btn" id="fsBtn" title="Ekrani i plote">[ ]</button>
                    </div>
                    <div class="info-container">
                        <div class="rating-box">
                            <span class="stars">⭐⭐⭐⭐⭐</span>
                            <span class="rating-num">4.9 (400+ Blerje)</span>
                        </div>
                        <a href="${{ad.tracking_url}}" target="_blank" class="ad-title">${{ad.title}}</a>
                        <div class="ad-desc">${{ad.description}}</div>
                        <div class="price-row">
                            <span class="new-price">${{ad.price}}</span>
                            <span class="old-price">${{ad.old_price}}</span>
                        </div>
                        <a href="${{ad.tracking_url}}" target="_blank" class="cta-btn">
                            <span>Porosit në WhatsApp</span>
                        </a>
                    </div>
                </div>
            </div>
        `;

        scriptTag.parentNode.insertBefore(container, scriptTag);

        const cardEl = container.firstElementChild;
        const video = container.querySelector("#adVideo");
        const videoContainer = container.querySelector("#videoContainer");
        const soundNotice = container.querySelector("#soundNotice");
        const fsBtn = container.querySelector("#fsBtn");

        if (video) {{
            video.muted = true;
            video.defaultMuted = true;
            video.playsInline = true;
            video.setAttribute("muted", "");
            video.setAttribute("playsinline", "");
            video.addEventListener("ended", () => logEvent("video_complete"));
        }}

        if (fsBtn && video) {{
            fsBtn.addEventListener("click", function(e) {{
                e.stopPropagation();
                e.preventDefault();
                logEvent("fullscreen");

                if (typeof video.webkitEnterFullscreen === 'function') {{
                    video.webkitEnterFullscreen();
                }} else if (video.requestFullscreen) {{
                    video.requestFullscreen();
                }} else if (video.webkitRequestFullscreen) {{
                    video.webkitRequestFullscreen();
                }} else if (video.mozRequestFullScreen) {{
                    video.mozRequestFullScreen();
                }} else if (video.msRequestFullscreen) {{
                    video.msRequestFullscreen();
                }}
            }});
        }}

        if (videoContainer && video) {{
            videoContainer.addEventListener("mouseleave", () => video.pause());
            videoContainer.addEventListener("mouseenter", () => {{
                video.muted = true;
                video.play().catch(e => {{}});
            }});
        }}

        container.addEventListener("click", function(e) {{
            if (!e.target.classList.contains("cta-btn") && !e.target.classList.contains("fullscreen-btn") && !e.target.classList.contains("ad-title")) {{
                if (video.muted) {{
                    video.muted = false;
                    video.volume = 1.0;
                    if (soundNotice) soundNotice.style.display = "none";
                    logEvent("unmute");
                }} else {{
                    video.muted = true;
                    if (soundNotice) soundNotice.style.display = "block";
                }}
            }}
        }});

        function tryPlayVideo() {{
            if (!video) return;
            video.muted = true;
            video.playsInline = true;
            const playPromise = video.play();
            if (playPromise !== undefined) {{
                playPromise.catch(error => {{
                    document.addEventListener('touchstart', function() {{
                        video.muted = true;
                        video.play().catch(e => {{}});
                    }}, {{ once: true }});
                }});
            }}
        }}

        let viewableTimer = null;

        const observer = new IntersectionObserver(function(entries) {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    tryPlayVideo();
                    if (!viewableCounted && !viewableTimer) {{
                        viewableTimer = setTimeout(() => {{
                            viewableCounted = true;
                            logEvent("viewable");
                        }}, 1000);
                    }}
                }} else {{
                    video.pause();
                    if (viewableTimer) {{
                        clearTimeout(viewableTimer);
                        viewableTimer = null;
                    }}
                }}
            }});
        }}, {{ threshold: 0.15 }});

        observer.observe(container);

        document.addEventListener("visibilitychange", function() {{
            if (document.hidden) {{
                video.pause();
            }} else {{
                const rect = container.getBoundingClientRect();
                const isVisible = (rect.top < window.innerHeight && rect.bottom > 0);
                if (isVisible) {{
                    tryPlayVideo();
                }}
            }}
        }});
    }})();
    """
    return Response(
        content=js_code,
        media_type="application/javascript; charset=utf-8",
        headers={"Cache-Control": "public, max-age=86400, s-maxage=86400, stale-while-revalidate=604800"}
    )

@app.get("/track-event/{ad_id}/{event_type}")
@app.get("/api/track-event/{ad_id}/{event_type}")
@app.get("/api/index/track-event/{ad_id}/{event_type}")
async def track_event(ad_id: str, event_type: str, device: str = "desktop"):
    with stats_lock:
        if ad_id in ADS_DATABASE:
            ad = ADS_DATABASE[ad_id]
            if event_type == "view":
                ad["views"] += 1
                if device == "mobile":
                    ad["mobile_views"] += 1
                else:
                    ad["desktop_views"] += 1
            elif event_type == "viewable":
                ad["viewable_impressions"] += 1
            elif event_type == "unmute":
                ad["unmutes"] += 1
            elif event_type == "fullscreen":
                ad["fullscreens"] += 1
            elif event_type == "video_complete":
                ad["video_completes"] += 1

            save_global_stats_kv(ADS_DATABASE)
            return Response(content=GIF_1X1, media_type="image/gif")
    return Response(content=GIF_1X1, media_type="image/gif")

@app.get("/track-view/{ad_id}")
@app.get("/api/track-view/{ad_id}")
@app.get("/api/index/track-view/{ad_id}")
async def track_view(ad_id: str):
    with stats_lock:
        if ad_id in ADS_DATABASE:
            ADS_DATABASE[ad_id]["views"] += 1
            save_global_stats_kv(ADS_DATABASE)
            return Response(content=GIF_1X1, media_type="image/gif")
    return Response(content=GIF_1X1, media_type="image/gif")

@app.get("/track-click/{ad_id}")
@app.get("/api/track-click/{ad_id}")
@app.get("/api/index/track-click/{ad_id}")
async def track_click(ad_id: str):
    with stats_lock:
        if ad_id in ADS_DATABASE:
            ADS_DATABASE[ad_id]["clicks"] += 1
            save_global_stats_kv(ADS_DATABASE)
            return RedirectResponse(url=ADS_DATABASE[ad_id]["whatsapp_link"])
    raise HTTPException(status_code=404, detail="Reklama nuk u gjet")

@app.get("/stats", response_class=HTMLResponse)
@app.get("/api/stats", response_class=HTMLResponse)
@app.get("/api/index/stats", response_class=HTMLResponse)
async def get_stats():
    global LAST_KNOWN_GOOD_STATS
    rows = ""
    with stats_lock:
        kv_data = load_global_stats_kv()
        if kv_data:
            for ad_id, ad_obj in kv_data.items():
                if ad_id in ADS_DATABASE:
                    for k, val in ad_obj.items():
                        if isinstance(val, (int, float)):
                            ADS_DATABASE[ad_id][k] = max(ADS_DATABASE[ad_id].get(k, 0), val)
            LAST_KNOWN_GOOD_STATS = json.loads(json.dumps(ADS_DATABASE, ensure_ascii=False))
        elif not LAST_KNOWN_GOOD_STATS:
            LAST_KNOWN_GOOD_STATS = json.loads(json.dumps(ADS_DATABASE, ensure_ascii=False))

        target_db = LAST_KNOWN_GOOD_STATS if LAST_KNOWN_GOOD_STATS else ADS_DATABASE

        for ad_id, ad in target_db.items():
            views = ad.get('views', 0)
            viewable = ad.get('viewable_impressions', 0)
            clicks = ad.get('clicks', 0)
            unmutes = ad.get('unmutes', 0)
            fullscreens = ad.get('fullscreens', 0)
            completes = ad.get('video_completes', 0)
            mob = ad.get('mobile_views', 0)
            desk = ad.get('desktop_views', 0)

            ctr = f"{(clicks / views * 100):.1f}%" if views > 0 else "0.0%"
            viewability_rate = f"{(viewable / views * 100):.1f}%" if views > 0 else "0.0%"
            completion_rate = f"{(completes / views * 100):.1f}%" if views > 0 else "0.0%"

            rows += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 12px; font-weight: bold; color: #1a0dab;">{ad_id}</td>
                <td style="padding: 12px; color: #333; font-weight: 600;">{ad.get('title', '')}</td>
                <td style="padding: 12px; color: #2980b9; font-weight: bold;">👁️ {views}</td>
                <td style="padding: 12px; color: #8e44ad; font-weight: bold;">🎯 {viewability_rate} <span style="font-size:11px; color:#666;">({viewable})</span></td>
                <td style="padding: 12px; color: #27ae60; font-weight: bold;">🖱️ {clicks} <span style="font-size:11px; color:#27ae60;">({ctr})</span></td>
                <td style="padding: 12px; color: #e67e22; font-weight: bold;">🔊 {unmutes}</td>
                <td style="padding: 12px; color: #d35400; font-weight: bold;">⛶ {fullscreens}</td>
                <td style="padding: 12px; color: #16a085; font-weight: bold;">🎬 {completion_rate} <span style="font-size:11px; color:#666;">({completes})</span></td>
                <td style="padding: 12px; color: #555; font-size: 12px;">📱 {mob} | 💻 {desk}</td>
            </tr>
            """

    html_stats = f"""
    <!DOCTYPE html>
    <html lang="sq">
    <head>
        <meta charset="UTF-8">
        <title>Ad Analytics Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f8; margin: 0; padding: 40px; }}
            .container {{ max-width: 1100px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }}
            .header-bar {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }}
            h1 {{ color: #1a0dab; margin: 0; font-size: 24px; }}
            .refresh-btn {{ background: #1a73e8; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 13px; border: none; cursor: pointer; }}
            .refresh-btn:hover {{ background: #1557b0; }}
            p {{ color: #5f6368; font-size: 14px; margin-top: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }}
            th {{ background: #1a73e8; color: white; text-align: left; padding: 12px; font-weight: 700; }}
            .refresh-note {{ font-size: 12px; color: #888; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-bar">
                <div>
                    <h1>📊 Ad Server Advanced Analytics Suite</h1>
                    <p>Statistikat e shfaqjeve, shikueshmërisë, klikimeve dhe zërit me ruajtje permanente.</p>
                </div>
                <button onclick="window.location.reload();" class="refresh-btn">🔄 Rifresko Statistikat</button>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Titulli</th>
                        <th>Shfaqjet (Views)</th>
                        <th>Shikueshmëria (Viewability)</th>
                        <th>Klikimet (CTR)</th>
                        <th>Zëri (Unmutes)</th>
                        <th>Fullscreen</th>
                        <th>Kompletime (100%)</th>
                        <th>Pajisjet (Mob/Desk)</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            <div class="refresh-note">💡 Rifreskoni faqen kur dëshironi të shihni numërimet e reja.</div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_stats, media_type="text/html; charset=utf-8")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, timeout_graceful_shutdown=0, timeout_keep_alive=1)
