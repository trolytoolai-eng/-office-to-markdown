import os
import json

CONFIG_FILE = "app_config.json"
PROXY_CONFIG_FILE = "proxy_config.json"

def load_config():
    app_config = {}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                app_config = json.load(f)
        elif os.path.exists(PROXY_CONFIG_FILE):
            with open(PROXY_CONFIG_FILE, "r") as f:
                app_config = json.load(f)
    except Exception:
        pass
    
    # Defaults
    app_config.setdefault("proxy_mode", "Không dùng (Local)")
    app_config.setdefault("ws_user", "")
    app_config.setdefault("ws_pass", "")
    app_config.setdefault("custom_proxy_raw", "")
    app_config.setdefault("ai_provider", "Google Gemini")
    app_config.setdefault("ai_api_key", "")
    app_config.setdefault("ai_model", "gemini-2.5-flash-lite")
    
    return app_config

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        return True, "✅ Cấu hình đã được lưu thành công!"
    except Exception as e:
        return False, f"Không thể lưu cấu hình: {e}"
