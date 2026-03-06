CLIENT_JS = """
// The client-side bridge that connects the browser to the Python server.
var ws;
var use_fallback = false;
var sse;
var _base_path = window.location.pathname.endsWith("/") ? window.location.pathname : window.location.pathname + "/";
window._htag_callbacks = {}; // Store promise resolvers

// --- htag-error Web Component (Shadow DOM for style isolation) ---
class HtagError extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({mode: 'open'});
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 2147483647;
                    align-items: center;
                    justify-content: center;
                    backdrop-filter: blur(2px);
                }
                :host([show]) { display: flex; }
                .dialog {
                    width: 80%;
                    max-width: 600px;
                    background: #fee2e2;
                    border: 1px solid #ef4444;
                    border-left: 5px solid #ef4444;
                    color: #991b1b;
                    padding: 15px;
                    border-radius: 4px;
                    font-family: system-ui, -apple-system, sans-serif;
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
                    max-height: 80vh;
                    overflow-y: auto;
                    text-align: left;
                    position: relative;
                }
                h3 { margin: 0 0 10px 0; font-size: 16px; display: inline-block;}
                pre { background: #fef2f2; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; overflow-x: auto; margin:0; text-align: left; }
                .close { position: absolute; top: 10px; right: 15px; cursor: pointer; font-weight: bold; font-size: 18px; color: #ef4444; }
                .close:hover { color: #b91c1c; }
                .copy { float: right; margin-right: 40px; cursor: pointer; background: #ef4444; color: white; border: none; padding: 2px 8px; border-radius: 3px; font-size: 12px; transition: background 0.2s; }
                .copy:hover { background: #b91c1c; }
                .copy:active { background: #991b1b; }
            </style>
            <div class="dialog">
                <div class="close" title="Close">×</div>
                <button class="copy" id="copy-btn">Copy</button>
                <h3 id="title">Error</h3>
                <pre id="trace"></pre>
            </div>
        `;
        this.shadowRoot.querySelector('.close').onclick = () => this.removeAttribute('show');
        this.shadowRoot.getElementById('copy-btn').onclick = () => {
            const trace = this.shadowRoot.getElementById('trace').textContent;
            navigator.clipboard.writeText(trace).then(() => {
                const btn = this.shadowRoot.getElementById('copy-btn');
                const old = btn.textContent;
                btn.textContent = 'Copied!';
                setTimeout(() => btn.textContent = old, 1500);
            });
        };
    }
    show(title, trace) {
        this.shadowRoot.getElementById('title').textContent = title;
        this.shadowRoot.getElementById('trace').textContent = trace || 'No traceback available.';
        this.setAttribute('show', '');
    }
}
customElements.define('htag-error', HtagError);

// Global references for UI overlays
var _error_overlay = document.createElement('htag-error');

document.addEventListener("DOMContentLoaded", () => {
    document.body.appendChild(_error_overlay);
});

window.onerror = function(message, source, lineno, colno, error) {
    if(_error_overlay && typeof _error_overlay.show === 'function') {
        _error_overlay.show("Client JavaScript Error", `${message}\\n${source}:${lineno}:${colno}\\n${error ? error.stack : ''}`);
    }
};
window.onunhandledrejection = function(event) {
    if(_error_overlay && typeof _error_overlay.show === 'function') {
        _error_overlay.show("Unhandled Promise Rejection", String(event.reason));
    }
};

function _enc(obj) {
    if(window.PARANO) {
        var str = unescape(encodeURIComponent(JSON.stringify(obj)));
        var res = "";
        for(var i=0; i<str.length; i++) res += String.fromCharCode(str.charCodeAt(i) ^ window.PARANO.charCodeAt(i % window.PARANO.length));
        return btoa(res);
    }
    return JSON.stringify(obj);
}

function _dec(b64) {
    if(window.PARANO) {
        var str = atob(b64);
        var res = "";
        for(var i=0; i<str.length; i++) res += String.fromCharCode(str.charCodeAt(i) ^ window.PARANO.charCodeAt(i % window.PARANO.length));
        return JSON.parse(decodeURIComponent(escape(res)));
    }
    return JSON.parse(b64);
}

function init_ws() {
    var ws_protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    ws = new WebSocket(ws_protocol + window.location.host + _base_path + "ws");
    
    ws.onopen = function() {
        console.log("htag: websocket connected");
    };

    ws.onmessage = function(event) {
        var data = _dec(event.data);
        handle_payload(data);
    };

    ws.onerror = function(err) {
        console.warn("htag: websocket error, switching to HTTP fallback (SSE)", err);
        fallback();
    };

    ws.onclose = function(event) {
        // If it closes abnormally or very quickly, trigger fallback
        if (event.code !== 1000 && event.code !== 1001) {
             console.warn("htag: websocket closed unexpectedly, switching to HTTP fallback (SSE)", event);
             fallback();
        }
    };
}

function handle_payload(data) {
    if(data.action == "update") {
        // Apply partial DOM updates received from the server
        for(var id in data.updates) {
            var el = document.getElementById(id) || document.querySelector('[data-htag-id="' + id + '"]');
            if(el) el.outerHTML = data.updates[id];
        }
        
        // Ensure overlays are still in the DOM (in case the body was replaced)
        if(_error_overlay && _error_overlay.parentNode !== document.body) {
            document.body.appendChild(_error_overlay);
        }
        // Execute any JavaScript calls emitted by the Python tags
        if(data.js) {
            for(var i=0; i<data.js.length; i++) eval(data.js[i]);
        }
        // Inject new css/js statics if they haven't been loaded yet
        if(data.statics) {
            data.statics.forEach(s => {
                var div = document.createElement('div');
                div.innerHTML = s.trim();
                var node = div.firstChild;
                if (node && (node.tagName === "STYLE" || node.tagName === "LINK")) {
                    document.head.appendChild(node);
                }
            });
        }
        // Resolve promise if a result is returned for a callback
        if(data.callback_id && window._htag_callbacks[data.callback_id]) {
            window._htag_callbacks[data.callback_id](data.result);
            delete window._htag_callbacks[data.callback_id];
        }
    } else if (data.action == "error") {
        if(_error_overlay && typeof _error_overlay.show === 'function') {
            _error_overlay.show("Server Error", data.traceback);
        } else {
            console.error("Server Error:", data.traceback);
        }
    }
}

function fallback() {
    if (use_fallback) return; 
    use_fallback = true;
    if(ws) ws.close(); // Ensure ws is torn down
    
    // Auto-reload mechanism
    if (window.HTAG_RELOAD) {
        console.log("htag: connection lost, starting auto-reload polling...");
        
        function poll_reload() {
            fetch("/").then(response => {
                if (response.ok) {
                    console.log("htag: server is back! Reloading page...");
                    window.location.reload();
                } else {
                    setTimeout(poll_reload, 500);
                }
            }).catch(err => {
                setTimeout(poll_reload, 500);
            });
        }
        
        setTimeout(poll_reload, 500);
        return; // Don't try SSE, we just want to reload the page when the server comes back
    }

    sse = new window.EventSource(_base_path + "stream");
    sse.onopen = () => console.log("htag: SSE connected");
    sse.onmessage = function(event) {
        handle_payload(_dec(event.data));
    };
    sse.onerror = function(err) {
        console.error("htag: SSE error", err);
        if(_error_overlay && typeof _error_overlay.show === 'function') {
            _error_overlay.show("Connection Lost", "Server Sent Events connection failed.");
        }
    };
}

// Start with WebSockets
// Use HTAG_EXT_INIT flag to prevent auto-start in custom environments (e.g., PyScript)
if (!window.HTAG_EXT_INIT) {
    init_ws();
}

// Default transport layer (WebSocket + HTTP Fallback)
window.htag_transport = window.htag_transport || function(payload) {
    if(!use_fallback && ws && ws.readyState === WebSocket.OPEN) {
        ws.send(_enc(payload));
    } else {
        // Use HTTP POST Fallback
        // (Fastest trigger even if SSE is still initializing)
        if (!use_fallback) fallback();
        fetch(_base_path + "event", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: _enc(payload)
        }).then(response => {
            if (!response.ok) {
                if(_error_overlay && typeof _error_overlay.show === 'function') {
                    _error_overlay.show("HTTP Error", `Server returned status: ${response.status}`);
                }
            }
        }).catch(err => {
            console.error("htag event POST error:", err);
            if(_error_overlay && typeof _error_overlay.show === 'function') {
                _error_overlay.show("Network Error", "Could not reach server to trigger event.");
            }
        });
    }
};

// Function called by HTML 'on{event}' attributes to send interactions back to Python
// Returns a Promise that resolves with the server's return value.
function htag_event(id, event_name, event) {
    var callback_id = Math.random().toString(36).substring(2);
    var data = {callback_id: callback_id};

    if (event instanceof Event) {
        // Standard DOM Event
        if (event.target) {
            if (event.target.type === 'checkbox') {
                data.value = event.target.checked;
            } else {
                data.value = event.target.value;
            }
        }
        data.key = event.key;
        data.pageX = event.pageX;
        data.pageY = event.pageY;
        
        // HashChangeEvent specifics
        if (event.newURL) data.newURL = event.newURL;
        if (event.oldURL) data.oldURL = event.oldURL;
    } else if (event && typeof event === 'object') {
        // Custom object passed as event
        Object.assign(data, event);
    } else if (event !== undefined) {
        // Simple value passed as event
        data.value = event;
    }

    var payload = {id: id, event: event_name, data: data};
    
    window.htag_transport(payload);

    return new Promise(resolve => {
        window._htag_callbacks[callback_id] = resolve;
    });
}
"""
