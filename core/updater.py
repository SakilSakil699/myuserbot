"""
Self-Updating System
- Pulls latest from GitHub
- Preserves vars, database, session
- Zero-downtime restart
"""
import subprocess
import os
import sys
import shutil
from pathlib import Path

PRESERVE = [".env", "data_*.json", "*.session", "vault.db"]

class Updater:
    def __init__(self, repo_url, branch="main"):
        self.repo_url = repo_url
        self.branch = branch

    def backup(self):
        backup_dir = Path("backup_tmp")
        backup_dir.mkdir(exist_ok=True)
        for pattern in PRESERVE:
            for f in Path(".").glob(pattern):
                shutil.copy(f, backup_dir / f.name)
        return backup_dir

    def restore(self, backup_dir):
        for f in backup_dir.glob("*"):
            shutil.copy(f, Path(".") / f.name)
        shutil.rmtree(backup_dir)

    def update(self):
        backup_dir = self.backup()
        try:
            # Fetch latest
            subprocess.check_call(["git", "fetch", "origin", self.branch])
            subprocess.check_call(["git", "reset", "--hard", f"origin/{self.branch}"])
            
            # Install new requirements
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            
            self.restore(backup_dir)
            return True, "Update successful"
        except Exception as e:
            self.restore(backup_dir)
            return False, str(e)