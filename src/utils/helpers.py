import re
from datetime import datetime

def sanitize_filename(name):
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    return name[:80]

def make_output_filename(source_name, source_type="file"):
    date_str = datetime.now().strftime("%Y%m%d")
    clean_name = sanitize_filename(source_name)
    prefix = "YT" if source_type == "youtube" else "File"
    return f"{prefix}_{clean_name}_{date_str}.md"

def extract_video_id(url):
    for pattern in [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'(?:shorts/)([a-zA-Z0-9_-]{11})',
    ]:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def parse_proxy_input(raw):
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith(("http://", "https://", "socks")):
        return raw
    parts = raw.split(":")
    if len(parts) == 4:
        host, port, user, password = parts
        return f"http://{user}:{password}@{host}:{port}"
    if "@" in raw:
        try:
            creds, server = raw.rsplit("@", 1)
            return f"http://{creds}@{server}"
        except ValueError:
            pass
    return f"http://{raw}"
