import os
import sys
import html
from pathlib import Path
from htag import Tag, ChromeApp, State

class Sidebar(Tag.div):
    """Navigation sidebar for quick access."""
    styles = """
        .sidebar {
            width: 200px;
            padding: 16px;
            background: rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            gap: 8px;
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        .sidebar-title {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
            padding-left: 8px;
        }
        .nav-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.9rem;
            color: var(--text);
        }
        .nav-item:hover {
            background: var(--hover);
            color: var(--primary);
        }
    """
    def init(self, go_to_callback):
        self._class = "sidebar"
        self <= Tag.div("Favorites", _class="sidebar-title")
        
        # Shortcuts
        self <= Tag.div("🏠 Home", _class="nav-item", _onclick=lambda e: go_to_callback(Path.home()))
        self <= Tag.div("📂 Root", _class="nav-item", _onclick=lambda e: go_to_callback(Path("/")))
        self <= Tag.div("💻 Current", _class="nav-item", _onclick=lambda e: go_to_callback(Path.cwd()))

class Explorer(Tag.div):
    """Component responsible for listing files and folders."""
    styles = """
        .explorer {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 16px;
            align-content: start;
        }
        .item {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px 12px;
            background: var(--surface);
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid rgba(255,255,255,0.05);
            text-align: center;
        }
        .item:hover {
            background: var(--hover);
            border-color: var(--primary);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .item.selected {
            background: rgba(129, 193, 223, 0.15);
            border-color: var(--primary);
            box-shadow: 0 0 15px rgba(129, 193, 223, 0.2);
        }
        .icon {
            font-size: 2.5rem;
            margin-bottom: 12px;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
        }
        .item.folder .icon { color: var(--accent); }
        .item.file .icon { color: var(--primary); }
        .item .info { width: 100%; }
        .item .name { 
            display: block; 
            font-weight: 500; 
            font-size: 0.85rem; 
            white-space: nowrap; 
            overflow: hidden; 
            text-overflow: ellipsis; 
            color: var(--text);
        }
        .item .details { display: block; font-size: 0.7rem; color: var(--text-dim); margin-top: 4px; }
    """

    def init(self, path, selected_file, select_callback):
        self._class="explorer"
        self.path = path
        self.selected_file = selected_file
        self.select_callback = select_callback
        self.render()

    def render(self):
        self.clear()
        try:
            entries = list(self.path.iterdir())
            entries.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
            
            for item in entries:
                is_dir = item.is_dir()
                cls = "folder" if is_dir else "file"
                is_selected = self.selected_file == item
                
                div = Tag.div(_class=f"item {cls} {'selected' if is_selected else ''}", 
                            _onclick=lambda e, p=item: self.select_callback(p))
                
                div <= Tag.div("📁" if is_dir else "📄", _class="icon")
                
                info = Tag.div(_class="info")
                info <= Tag.span(item.name, _class="name")
                
                if not is_dir:
                    try:
                        size = item.stat().st_size
                        info <= Tag.span(self.format_size(size), _class="details")
                    except Exception: pass
                else:
                    info <= Tag.span("Folder", _class="details")
                
                div <= info
                self <= div
        except Exception as e:
            self <= Tag.div(f"Error: {e}", _style="color: #ff6b6b; padding: 20px; grid-column: 1/-1")

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024: return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

class Viewer(Tag.div):
    """Component responsible for previewing file content."""
    styles = """
        .preview-panel {
            width: 500px;
            background: var(--surface);
            display: flex;
            flex-direction: column;
            border-left: 1px solid rgba(129,193,223,0.3);
            animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            height: 100%;
            box-shadow: -10px 0 30px rgba(0,0,0,0.3);
            z-index: 50;
        }
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        .preview-header {
            padding: 20px 24px;
            background: var(--surface-light);
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .preview-title {
            font-weight: 600;
            font-size: 1rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: var(--primary);
        }
        .preview-content {
            flex: 1;
            overflow: auto;
            padding: 24px;
            font-family: 'Fira Code', monospace;
            font-size: 0.8rem;
            line-height: 1.6;
            white-space: pre;
            background: #0f171e;
            color: #a0aec0;
            border-radius: 0 0 0 12px;
        }
        .close-btn {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            color: var(--text-dim);
            font-size: 1rem;
            cursor: pointer;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        .close-btn:hover {
            background: var(--error);
            border-color: var(--error);
            color: white;
        }
    """

    def init(self, file_path, close_callback):
        self._class="preview-panel"
        self.file_path = file_path
        self.close_callback = close_callback
        self.render()

    def render(self):
        self.clear()
        if not self.file_path or not self.file_path.is_file():
            return
            
        header = Tag.div(_class="preview-header")
        header <= Tag.span(self.file_path.name, _class="preview-title")
        header <= Tag.button("✕", _class="close-btn", _onclick=lambda e: self.close_callback())
        self <= header
        
        content = Tag.div(_class="preview-content")
        if self.is_text_file(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
                    all_text = f.read(50000)
                    lines = all_text.splitlines()[:1000]
                    text = "\n".join(lines)
                    if len(all_text) > 50000 or len(all_text.splitlines()) > 1000:
                        text += "\n... (truncated)"
                    content += html.escape(text)
            except Exception as e:
                content += f"Error reading file: {e}"
        else:
            content += "Preview not available for this file type."
        
        self <= content

    def is_text_file(self, path):
        text_extensions = {
            '.py', '.md', '.txt', '.json', '.yml', '.yaml', 
            '.css', '.html', '.js', '.toml', '.xml', '.sh', 
            '.bat', '.log', '.ini', '.cfg', '.sql', '.svg', ".conf", ".properties", ".env"
        }
        return path.suffix.lower() in text_extensions


class FileNavigator(Tag.App):
    statics = [
        Tag.style("""
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap');
            :root {
                --bg: #0f172a;
                --surface: #1e293b;
                --surface-light: #334155;
                --primary: #38bdf8;
                --accent: #f59e0b;
                --text: #f1f5f9;
                --text-dim: #94a3b8;
                --hover: rgba(56, 189, 248, 0.1);
                --error: #ef4444;
            }
            body {
                background: var(--bg);
                color: var(--text);
                font-family: 'Outfit', sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                height: 100vh;
                overflow: hidden;
            }
            .main-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                height: 100vh;
                overflow: hidden;
            }
            .navbar {
                padding: 12px 24px;
                background: var(--surface);
                display: flex;
                align-items: center;
                gap: 24px;
                z-index: 100;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            .navbar h1 {
                margin: 0;
                font-weight: 600;
                font-size: 1.1rem;
                color: var(--primary);
                letter-spacing: -0.5px;
                white-space: nowrap;
            }
            .split-view {
                flex: 1;
                display: flex;
                overflow: hidden;
                position: relative;
            }
            .explorer-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .breadcrumb {
                padding: 10px 24px;
                background: rgba(0,0,0,0.2);
                font-size: 0.8rem;
                color: var(--text-dim);
                border-bottom: 1px solid rgba(255,255,255,0.05);
                white-space: nowrap;
                overflow-x: auto;
                scrollbar-width: none;
            }
            .btn {
                background: var(--surface-light);
                color: var(--text);
                border: 1px solid rgba(255,255,255,0.1);
                padding: 6px 14px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                font-size: 0.85rem;
                transition: all 0.2s;
            }
            .btn:hover:not(:disabled) {
                background: var(--primary);
                color: var(--bg);
                border-color: var(--primary);
            }
            .btn:disabled {
                opacity: 0.3;
                cursor: not-allowed;
            }
            ::-webkit-scrollbar { width: 8px; height: 8px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }
        """)
    ]

    def init(self):
        # 1. State Initialization
        self.path = State(Path(os.getcwd()).resolve())
        self.selected = State(None)

        # 2. Declarative Layout
        with Tag.div(_class="main-container"):
            # Header
            with Tag.div(_class="navbar"):
                Tag.h1("htag2 Explorer")
                Tag.button("↑ Back", 
                    _class="btn", 
                    _disabled=lambda: self.path.value.parent == self.path.value,
                    _onclick=self.go_up
                )

            # Split View
            with Tag.div(_class="split-view") as split_view:
                # Sidebar (NEW)
                Sidebar(self.go_to)

                # Explorer Main Area
                with Tag.div(_class="explorer-container") as explorer_container:
                    Tag.div(lambda: str(self.path.value), _class="breadcrumb")
                    
                    # Explorer Grid
                    explorer_container.add(lambda: Explorer(self.path.value, self.selected.value, self.on_item_click))
                
                # Viewer (Right side)
                split_view.add(lambda: Viewer(self.selected.value, self.on_close_viewer) if self.selected.value else "")

    def on_item_click(self, item):
        if item.is_dir():
            self.go_to(item)
        else:
            self.selected.value = item

    def go_to(self, target_path):
        self.path.value = Path(target_path).resolve()
        self.selected.value = None

    def go_up(self, e):
        if self.path.value.parent != self.path.value:
            self.go_to(self.path.value.parent)

    def on_close_viewer(self):
        self.selected.value = None

if __name__ == "__main__":
    ChromeApp(FileNavigator, width=1280, height=900).run()
