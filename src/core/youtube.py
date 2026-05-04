import json
import subprocess
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.proxies import GenericProxyConfig, WebshareProxyConfig
except ImportError:
    YouTubeTranscriptApi = None
    GenericProxyConfig = None
    WebshareProxyConfig = None

from src.utils.helpers import extract_video_id, parse_proxy_input

def get_youtube_metadata(url):
    import requests as req
    title = ""
    description = ""
    try:
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        resp = req.get(oembed_url, timeout=10)
        if resp.status_code == 200:
            title = resp.json().get("title", "")
    except Exception:
        pass
    if not title:
        try:
            r = subprocess.run(
                ["python", "-m", "yt_dlp", "--dump-json", "--no-download", "--skip-download", url],
                capture_output=True, text=True, timeout=30, encoding='utf-8'
            )
            if r.returncode == 0 and r.stdout.strip():
                meta = json.loads(r.stdout)
                title = meta.get("title", "")
                description = meta.get("description", "")
        except Exception:
            pass
    return title, description

def create_ytt_api(p_mode, p_user, p_pass, p_custom):
    class SafeWebshareProxyConfig(GenericProxyConfig):
        @property
        def prevent_keeping_connections_alive(self) -> bool:
            return True
        @property
        def retries_when_blocked(self) -> int:
            return 10

    if p_mode == "Webshare" and p_user and p_pass and GenericProxyConfig:
        user = p_user.strip()
        pwd = p_pass.strip()
        url = f"http://{user}:{pwd}@p.webshare.io:80"
        return YouTubeTranscriptApi(proxy_config=SafeWebshareProxyConfig(
            http_url=url, https_url=url,
        ))
    elif p_mode == "Custom URL" and p_custom and GenericProxyConfig:
        url = parse_proxy_input(p_custom)
        return YouTubeTranscriptApi(proxy_config=GenericProxyConfig(
            http_url=url, https_url=url,
        ))
    return YouTubeTranscriptApi()

def get_youtube_transcript(url, p_mode, p_user, p_pass, p_custom):
    video_id = extract_video_id(url)
    if not video_id:
        return None, None, "Không thể trích xuất Video ID."
    title, description = get_youtube_metadata(url)
    if not YouTubeTranscriptApi:
        return None, title, "youtube_transcript_api chưa được cài."
    last_err = ""
    text = ""
    for attempt in range(5):
        try:
            api = create_ytt_api(p_mode, p_user, p_pass, p_custom)
            transcript_list = api.list(video_id)
            try:
                transcript = transcript_list.find_transcript(['vi', 'en'])
            except:
                transcript = next(iter(transcript_list))
            data = transcript.fetch()
            text = ' '.join([item.text for item in data])
            break  # Thành công thì thoát loop
        except Exception as e:
            err_type = type(e).__name__
            # Nếu video thật sự không có phụ đề thì không cần thử lại
            if err_type in ["TranscriptsDisabled", "NoTranscriptFound", "VideoUnavailable"]:
                return None, title, f"Video này không có phụ đề (Lỗi: {err_type})."
            
            last_err = str(e)
            # Nếu đã thử 5 lần (attempt 0 đến 4) mà vẫn lỗi
            if attempt == 4:
                return None, title, (
                    f"🚫 Đã thử 5 IP Proxy khác nhau nhưng đều bị YouTube chặn.\n\n"
                    f"Có thể do YouTube đang càn quét dải IP của Webshare. Hãy thử lại sau nhé!\n"
                    f"(Chi tiết lỗi cuối: {last_err})"
                )
            continue # Thử lại với IP mới

    parts = [f"# {title}" if title else "# YouTube Video", "", f"**URL:** {url}", ""]
    if description:
        parts += ["## Description", description, ""]
    parts += ["## Transcript", "", text]
    return '\n'.join(parts), title, None
