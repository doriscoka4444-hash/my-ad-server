from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import urllib.parse
import random
import uuid
import os
import json

app = FastAPI(title="Video Ad Server", version="7.0.0 (Production Ready for Render)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DESKTOP_VIDEOS_DIR = "C:/Users/User/Desktop/videos"
LOCAL_VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "videos")

if os.path.exists(DESKTOP_VIDEOS_DIR):
    VIDEOS_DIR = DESKTOP_VIDEOS_DIR
else:
    VIDEOS_DIR = LOCAL_VIDEOS_DIR

os.makedirs(VIDEOS_DIR, exist_ok=True)

app.mount("/local-videos", StaticFiles(directory=VIDEOS_DIR), name="local-videos")

wa_message = urllib.parse.quote("Dua te di me shume rreth ketij produktit!")
whatsapp_url = f"https://wa.me/355685846937?text={wa_message}"

ADS_DATABASE = {
    "reklama-1": {
        "title": "Zbulo më shumë rreth produktit",
        "video_filename": "video1_fast.mp4",
        "poster_filename": "video1.webp",
        "description": "Ofertë Ekskluzive: Kurseni sot me uljen tonë speciale!",
        "old_price": "3,100 Lekë",
        "price": "2,800 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "clicks": 0
    },
    "reklama-2": {
        "title": "Mbështetëse për Gju - Lehtësim i Dhimbjeve",
        "video_filename": "gjuri_fast.mp4",
        "poster_filename": "gjuri.webp",
        "description": "Zgjidhje ideale për dhimbjet e gjurit dhe rikuperim të shpejtë.",
        "old_price": "3,900 Lekë",
        "price": "3,500 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "clicks": 0
    },
    "reklama-3": {
        "title": "Ofertë e Muajit - Produkt Tepër i Kërkuar",
        "video_filename": "video3_fast.mp4",
        "poster_filename": "video3.webp",
        "description": "Cilësi e lartë, garanci prodhimi dhe dërgesë e shpejtë brenda 24 orëve.",
        "old_price": "2,800 Lekë",
        "price": "2,500 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "clicks": 0
    },
    "reklama-4": {
        "title": "Kokë dushi me disa opsione",
        "video_filename": "dushi_fast.mp4",
        "poster_filename": "dushi.webp",
        "description": "Kokë dushi me shumë opsione. Ofertë: 2 Copë vetëm 2,499 Lekë!",
        "old_price": "1,699 Lekë",
        "price": "1,499 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "clicks": 0
    },
    "reklama-5": {
        "title": "Antene Televizori me magnet",
        "video_filename": "televizori_fast.mp4",
        "poster_filename": "televizori.webp",
        "description": "Per te gjitha stacionet televizive tokesore, eshte me magnet.",
        "old_price": "2,200 Lekë",
        "price": "2,000 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "clicks": 0
    },
    "reklama-6": {
        "title": "Nderese rrobash",
        "video_filename": "rroba_fast.mp4",
        "poster_filename": "rroba.webp",
        "description": "Nuk krijon rremuje dhe shume e lehte per tu perdorur.",
        "old_price": "3,800 Lekë",
        "price": "3,300 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "clicks": 0
    },
    "reklama-7": {
        "title": "Pompe lyerje elektrike",
        "video_filename": "pompa_fast.mp4",
        "poster_filename": "pompa.webp",
        "description": "Mos u lodhni duke lyer muret me dore, pompe elektrike per ju,me super cmim.",
        "old_price": "7,500 Lekë",
        "price": "6,500 Lekë",
        "whatsapp_link": whatsapp_url,
        "views": 0,
        "clicks": 0
    }
}

def get_server_base(request: Request) -> str:
    env_base = os.getenv("SERVER_BASE")
    if env_base:
        return env_base.rstrip("/")
    return str(request.base_url).rstrip("/")

@app.get("/loader.js")
async def get_loader_script(request: Request):
    ads_json = {}
    for ad_id, ad in ADS_DATABASE.items():
        ads_json[ad_id] = {
            "title": ad["title"],
            "description": ad["description"],
            "video_filename": ad["video_filename"],
            "poster_filename": ad.get("poster_filename", "video1.webp"),
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
            const randomIdx = Math.floor(Math.random() * 7) + 1;
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
            poster_url: serverBase + "/local-videos/" + rawAd.poster_filename,
            old_price: rawAd.old_price,
            price: rawAd.price,
            whatsapp_link: rawAd.whatsapp_link,
            tracking_url: serverBase + "/track-click/" + adId,
            view_url: serverBase + "/track-view/" + adId
        }};

        let viewCounted = false;

        const container = document.createElement("div");
        container.style.width = "100%";
        container.style.margin = "14px 0";

        container.innerHTML = `
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

                .adsense-card-native * {{ box-sizing: border-box; }}
                .adsense-card-native {{
                    border: 1px solid #dadce0;
                    border-radius: 8px;
                    background: #ffffff;
                    width: 100%;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
                    position: relative;
                    overflow: hidden;
                    box-shadow: 0 1px 3px rgba(60,64,67,0.08);
                    transition: border-color 0.2s, box-shadow 0.2s;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
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
                    background: rgba(15, 20, 25, 0.85);
                    backdrop-filter: blur(4px);
                    color: #ffffff;
                    font-size: 9px;
                    font-weight: 700;
                    padding: 2px 5px;
                    border-radius: 3px;
                    pointer-events: none;
                }}
                .adsense-card-native .fullscreen-btn {{
                    position: absolute;
                    top: 5px;
                    right: 5px;
                    background: rgba(15, 20, 25, 0.85);
                    backdrop-filter: blur(4px);
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
                    transition: background 0.2s, box-shadow 0.2s;
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
                    <span class="ad-sponsor">Sponsoruar &bull; Ofertë Ekskluzive</span>
                </div>
                <div class="adsense-body">
                    <div class="video-container" id="videoContainer">
                        <video id="adVideo" src="${{ad.video_url}}" poster="${{ad.poster_url}}" autoplay muted playsinline loop preload="metadata" controlsList="nodownload" oncontextmenu="return false;"></video>
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

        if (fsBtn && video) {{
            fsBtn.addEventListener("click", function(e) {{
                e.stopPropagation();
                if (video.requestFullscreen) video.requestFullscreen();
                else if (video.webkitRequestFullscreen) video.webkitRequestFullscreen();
                else if (video.msRequestFullscreen) video.msRequestFullscreen();
            }});
        }}

        if (videoContainer && video) {{
            videoContainer.addEventListener("mouseleave", () => video.pause());
            videoContainer.addEventListener("mouseenter", () => video.play().catch(e => {{}}));
        }}

        container.addEventListener("click", function(e) {{
            if (!e.target.classList.contains("cta-btn") && !e.target.classList.contains("fullscreen-btn") && !e.target.classList.contains("ad-title")) {{
                if (video.muted) {{
                    video.muted = false;
                    video.volume = 1.0;
                    if (soundNotice) soundNotice.style.display = "none";
                }} else {{
                    video.muted = true;
                    if (soundNotice) soundNotice.style.display = "block";
                }}
            }}
        }});

        const observer = new IntersectionObserver(function(entries) {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    video.play().catch(e => {{}});
                    if (!viewCounted) {{
                        viewCounted = true;
                        fetch(ad.view_url).catch(e => {{}});
                    }}
                }} else {{
                    video.pause();
                }}
            }});
        }}, {{ threshold: 0.2 }});

        observer.observe(container);

        document.addEventListener("visibilitychange", function() {{
            if (document.hidden) {{
                video.pause();
            }} else {{
                const rect = container.getBoundingClientRect();
                const isVisible = (rect.top < window.innerHeight && rect.bottom > 0);
                if (isVisible) {{
                    video.play().catch(e => {{}});
                }}
            }}
        }});
    }})();
    """
    return Response(content=js_code, media_type="application/javascript; charset=utf-8")

@app.get("/track-view/{ad_id}")
async def track_view(ad_id: str):
    if ad_id in ADS_DATABASE:
        ADS_DATABASE[ad_id]["views"] += 1
        return {"status": "ok", "views": ADS_DATABASE[ad_id]["views"]}
    return {"status": "not_found"}

@app.get("/track-click/{ad_id}")
async def track_click(ad_id: str):
    if ad_id in ADS_DATABASE:
        ADS_DATABASE[ad_id]["clicks"] += 1
        return RedirectResponse(url=ADS_DATABASE[ad_id]["whatsapp_link"])
    raise HTTPException(status_code=404, detail="Reklama nuk u gjet")

@app.get("/stats", response_class=HTMLResponse)
async def get_stats():
    rows = ""
    for ad_id, ad in ADS_DATABASE.items():
        views = ad['views']
        clicks = ad['clicks']
        ctr = f"{(clicks / views * 100):.1f}%" if views > 0 else "0.0%"

        rows += f"""
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 14px; font-weight: bold; color: #333;">{ad_id}</td>
            <td style="padding: 14px; color: #555;">{ad['title']}</td>
            <td style="padding: 14px; color: #2980b9; font-weight: bold; font-size: 16px;">👁️ {views}</td>
            <td style="padding: 14px; color: #27ae60; font-weight: bold; font-size: 16px;">🖱️ {clicks}</td>
            <td style="padding: 14px; color: #e67e22; font-weight: bold; font-size: 16px;">📊 {ctr}</td>
        </tr>
        """

    html_stats = f"""
    <!DOCTYPE html>
    <html lang="sq">
    <head>
        <meta charset="UTF-8">
        <title>Ad Analytics Dashboard</title>
        <meta http-equiv="refresh" content="3">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f8; margin: 0; padding: 40px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }}
            h1 {{ color: #333; margin-top: 0; }}
            p {{ color: #606770; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
            th {{ background: #1877f2; color: white; text-align: left; padding: 14px; font-size: 14px; }}
            .refresh-note {{ font-size: 12px; color: #888; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Ad Server Analytics & Live Views</h1>
            <p>Statistikat e shfaqjeve (Views) dhe klikimeve (Clicks) në kohë reale.</p>
            <table>
                <thead>
                    <tr>
                        <th>ID e Reklamës</th>
                        <th>Përshkrimi</th>
                        <th>Shfaqjet (Views)</th>
                        <th>Klikimet (Clicks)</th>
                        <th>Konvertimi (CTR)</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            <div class="refresh-note">⏳ Paneli rifreskohet automatikisht çdo 3 sekonda.</div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_stats, media_type="text/html; charset=utf-8")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, timeout_graceful_shutdown=0, timeout_keep_alive=1)
