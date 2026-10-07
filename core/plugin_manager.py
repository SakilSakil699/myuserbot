"""
Self-Healing Plugin Manager
- Auto-scans plugin code for missing dependencies
- Installs via pip automatically
- Handles PEP 668 (externally-managed-environment)
- Reloads without restart when possible
"""
import ast
import subprocess
import sys
import importlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Map import names to pip package names
IMPORT_TO_PIP = {
    "PIL": "pillow",
    "bs4": "beautifulsoup4",
    "cv2": "opencv-python",
    "yaml": "pyyaml",
    "sklearn": "scikit-learn",
    "dotenv": "python-dotenv",
}

class PluginManager:
    def __init__(self, app, modules_dir="modules"):
        self.app = app
        self.modules_dir = Path(modules_dir)
        self.loaded = {}
        self.failed = {}

    def scan_imports(self, file_path):
        """Parse Python file and extract all imports."""
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
        return imports

    def get_missing(self, imports):
        """Check which imports are missing."""
        missing = []
        for imp in imports:
            try:
                importlib.import_module(imp)
            except ImportError:
                pip_name = IMPORT_TO_PIP.get(imp, imp)
                missing.append(pip_name)
        return missing

    def install_package(self, package):
        """Install package with PEP 668 handling."""
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except subprocess.CalledProcessError:
            # PEP 668 fallback
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--break-system-packages", package],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except Exception as e:
                logger.error(f"Failed to install {package}: {e}")
                return False

    def load_plugin(self, file_path):
        """Load a single plugin with auto-healing."""
        module_name = f"modules.{file_path.stem}"
        
        # Check if already loaded
        if module_name in self.loaded:
            return self.loaded[module_name]

        try:
            # Step 1: Scan for imports
            imports = self.scan_imports(file_path)
            
            # Step 2: Install missing deps
            missing = self.get_missing(imports)
            if missing:
                logger.info(f"Installing missing deps for {file_path.stem}: {missing}")
                for pkg in missing:
                    self.install_package(pkg)

            # Step 3: Import module
            module = importlib.import_module(module_name)
            
            # Step 4: Register handlers
            if hasattr(module, "register"):
                module.register(self.app)
            
            self.loaded[module_name] = module
            logger.info(f"✅ Loaded: {file_path.stem}")
            return module

        except Exception as e:
            self.failed[module_name] = str(e)
            logger.error(f"❌ Failed {file_path.stem}: {e}")
            return None

    def load_all(self):
        """Load all plugins in modules/ directory."""
        for file in self.modules_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
            self.load_plugin(file)

    def reload_plugin(self, name):
        """Hot-reload a plugin without restart."""
        module_name = f"modules.{name}"
        if module_name in sys.modules:
            del sys.modules[module_name]
        file_path = self.modules_dir / f"{name}.py"
        if file_path.exists():
            return self.load_plugin(file_path)
        return None