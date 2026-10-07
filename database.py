import json, os, threading

_lock = threading.Lock()

class DB:
    def __init__(self, name):
        self.path = f"data_{name}.json"
        if not os.path.exists(self.path):
            with open(self.path, "w") as f: json.dump({}, f)

    def _load(self):
        with open(self.path, "r", encoding="utf-8") as f: return json.load(f)

    def _save(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get(self, key, default=None):
        with _lock:
            return self._load().get(str(key), default)

    def set(self, key, value):
        with _lock:
            d = self._load(); d[str(key)] = value; self._save(d)

    def delete(self, key):
        with _lock:
            d = self._load(); d.pop(str(key), None); self._save(d)

    def all(self):
        with _lock:
            return self._load()