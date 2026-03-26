def __minify_js(js_code: str) -> str:
    import re
    # Remove single line comments (but not URL schemes like http://)
    js = re.sub(r'(?<!:)//.*', '', js_code)
    # Remove newlines and tabs
    js = re.sub(r'\s+', ' ', js).strip()
    return js

CLIENT_JS = __minify_js("""
// The client-side bridge that connects the browser to the Python server.
window.ws = null;
window.use_fallback = false;
window.use_pure_http = false;
window.sse = null;
window.HTAG_TIMEOUT = 3000; // Timeout for transport establishment (ms)
var _base_path = window.location.pathname.endsWith("/") ? window.location.pathname : window.location.pathname + "/";
window._htag_callbacks = {}; // Store promise resolvers
function _sync_interacting() {
    if(Object.keys(window._htag_callbacks).length > 0) {
        document.body.classList.add("interacting");
    } else {
        document.body.classList.remove("interacting");
    }
}
function _dec_interacting(callback_id) {
    if(callback_id) delete window._htag_callbacks[callback_id];
    _sync_interacting();
}

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
    window.ws = new WebSocket(ws_protocol + window.location.host + _base_path + "ws");
    
    var ws_timeout = setTimeout(() => {
        if (window.ws && window.ws.readyState === WebSocket.CONNECTING) {
            console.warn("htag: websocket connection timeout, falling back");
            fallback();
        }
    }, window.HTAG_TIMEOUT);

    window.ws.onopen = function() {
        clearTimeout(ws_timeout);
        console.log("htag: websocket connected");
        if(window._htag_queue && window._htag_queue.length > 0) {
            window._htag_queue.forEach(function(payload) {
                window.ws.send(_enc(payload));
            });
            window._htag_queue = [];
        }
    };

    window.ws.onmessage = function(event) {
        var data = _dec(event.data);
        handle_payload(data, "WS");
    };

    window.ws.onerror = function(err) {
        clearTimeout(ws_timeout);
        console.warn("htag: websocket error, switching to HTTP fallback (SSE)", err);
        fallback();
    };

    window.ws.onclose = function(event) {
        clearTimeout(ws_timeout);
        // If it closes abnormally or very quickly, trigger fallback
        if (event.code !== 1000 && event.code !== 1001) {
             console.warn("htag: websocket closed unexpectedly, switching to HTTP fallback (SSE)", event);
             fallback();
        }
    };
}

function handle_payload(data, source) {
    if(data.action == "update") {
        console.log("htag (" + (source || "??") + "): processing payload updates:", Object.keys(data.updates || {}));
        // Apply partial DOM updates received from the server
        for(var id in data.updates) {
            var el = document.getElementById(id) || document.querySelector('[data-htag-id="' + id + '"]');
            if(el) {
                if(el.tagName === 'BODY') {
                    var doc = new DOMParser().parseFromString(data.updates[id], 'text/html');
                    
                    // Sync attributes properly
                    var newAttrNames = new Set();
                    for(var i = 0; i < doc.body.attributes.length; i++) {
                        var attr = doc.body.attributes[i];
                        el.setAttribute(attr.name, attr.value);
                        newAttrNames.add(attr.name);
                    }
                    // Remove old attributes that are not in the new body
                    for(var i = el.attributes.length - 1; i >= 0; i--) {
                        var attrName = el.attributes[i].name;
                        if(!newAttrNames.has(attrName)) {
                            el.removeAttribute(attrName);
                        }
                    }
                    
                    el.innerHTML = doc.body.innerHTML;
                } else {
                    el.outerHTML = data.updates[id];
                }
            }
        }
        
        // Ensure overlays are still in the DOM (in case the body was replaced)
        if(_error_overlay && _error_overlay.parentNode !== document.body) {
            document.body.appendChild(_error_overlay);
        }
        // 1. Inject new css/js statics if they haven't been loaded yet (BEFORE JS calls)
        if(data.statics) {
            data.statics.forEach(s => {
                try {
                    var div = document.createElement('div');
                    div.innerHTML = s.trim();
                    var node = div.firstChild;
                    if (!node) return;
                    
                    if (node.tagName === "STYLE" || node.tagName === "LINK") {
                        document.head.appendChild(node);
                    } else if (node.tagName === "SCRIPT") {
                        var script = document.createElement('script');
                        script.async = false; // Force sequential execution for multiple dynamic scripts
                        for (var i = 0; i < node.attributes.length; i++) {
                            var attr = node.attributes[i];
                            script.setAttribute(attr.name, attr.value);
                        }
                        if (node.textContent) script.textContent = node.textContent;
                        document.head.appendChild(script);
                    }
                } catch(e) {
                    console.error("htag: static injection error", s, e);
                }
            });
        }

        // 2. Execute any JavaScript calls emitted by the Python tags
        if(data.js) {
            for(var i=0; i<data.js.length; i++) {
                try {
                    eval(data.js[i]);
                } catch(e) {
                    console.error("htag: eval error for", data.js[i], e);
                    if(_error_overlay && typeof _error_overlay.show === 'function') {
                        _error_overlay.show("JS Eval Error", e.message + "\\nSource: " + data.js[i]);
                    }
                }
            }
        }
    } else if (data.action == "error") {
        if(_error_overlay && typeof _error_overlay.show === 'function') {
            _error_overlay.show("Server Error", data.traceback);
        } else {
            console.error("Server Error:", data.traceback);
        }
    }
    // Resolve promise if a result is returned for a callback (even for errors)
    if(data.callback_id && window._htag_callbacks[data.callback_id]) {
        var resolve = window._htag_callbacks[data.callback_id];
        _dec_interacting(data.callback_id);
        resolve(data.result);
    }
}

function fallback() {
    // Preserve callbacks for items in the queue
    var queued_callbacks = {};
    if (window._htag_queue) {
        window._htag_queue.forEach(function(p) {
            if (p && p.data && p.data.callback_id && window._htag_callbacks[p.data.callback_id]) {
                queued_callbacks[p.data.callback_id] = window._htag_callbacks[p.data.callback_id];
            }
        });
    }
    window._htag_callbacks = queued_callbacks;
    _sync_interacting();

    if (window.use_fallback) return; 
    window.use_fallback = true;
    console.warn("htag: fallback() called, killing transport...");
    if(window.ws) {
        console.error("htag: DEBUG - killing websocket now");
        window.ws.onclose = null; 
        var _ws = window.ws;
        window.ws = null;
        setTimeout(function() { _ws.close(); }, 0);
    }
    
    // Flush the queue via HTTP fallback
    if (window._htag_queue && window._htag_queue.length > 0) {
        console.log("htag: flushing queue via fallback");
        var queue = window._htag_queue;
        window._htag_queue = [];
        queue.forEach(function(payload) {
            window.htag_transport(payload);
        });
    }

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

    window.sse = new window.EventSource(_base_path + "stream");
    var sse_timeout = setTimeout(() => {
        if (window.sse && window.sse.readyState === 0) { // 0 is CONNECTING
            console.warn("htag: SSE connection timeout, falling back to pure HTTP");
            fallback_pure_http();
        }
    }, window.HTAG_TIMEOUT);

    window.sse.onopen = () => {
        clearTimeout(sse_timeout);
        console.log("htag: SSE connected");
    };
    window.sse.onmessage = function(event) {
        handle_payload(_dec(event.data), "SSE");
    };
    window.sse.onerror = function(err) {
        clearTimeout(sse_timeout);
        console.error("htag: SSE error", err);
        fallback_pure_http();
    };
}

function fallback_pure_http() {
    if (window.use_pure_http) return;
    window.use_pure_http = true;
    window.use_fallback = true;
    console.error("htag: DEBUG - fallback_pure_http() called");
    console.warn("htag: switching to pure HTTP mode (SSE failed)");
    if(window.sse) {
        console.log("htag: killing SSE");
        window.sse.onerror = null;
        window.sse.close();
        window.sse = null;
    }
    if(window.ws) {
        console.log("htag: killing websocket (re-check)");
        window.ws.onclose = null;
        window.ws.close();
        window.ws = null;
    }
    
    // hide error overlay if it was shown by SSE error
    if(_error_overlay && _error_overlay.hasAttribute('show')) {
        _error_overlay.removeAttribute('show');
    }
    
    if (window._htag_queue && window._htag_queue.length > 0) {
        var queue = window._htag_queue;
        window._htag_queue = [];
        queue.forEach(function(payload) {
            window.htag_transport(payload);
        });
    }
}

// Start with WebSockets
// Use HTAG_EXT_INIT flag to prevent auto-start in custom environments (e.g., PyScript)
if (!window.HTAG_EXT_INIT) {
    init_ws();
}

window._htag_queue = window._htag_queue || [];

// Default transport layer (WebSocket + HTTP Fallback)
window.htag_transport = window.htag_transport || function(payload) {
    if(!window.use_fallback && window.ws) {
        if(window.ws.readyState === WebSocket.OPEN) {
            window.ws.send(_enc(payload));
        } else if(window.ws.readyState === WebSocket.CONNECTING) {
            window._htag_queue.push(payload);
        } else {
            // Use HTTP POST Fallback
            if (!window.use_fallback) fallback();
            _send_http(payload);
        }
    } else {
        // Use HTTP POST Fallback
        if (!window.use_fallback) fallback();
        _send_http(payload);
    }
};

function _send_http(payload) {
    if (window.use_pure_http) {
        payload.fallback = true;
    }
    fetch(_base_path + "event", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-HTAG-TOKEN": window.HTAG_CSRF
        },
        body: _enc(payload)
    }).then(response => {
        if (!response.ok) {
            _dec_interacting(payload.data.callback_id);
            if(_error_overlay && typeof _error_overlay.show === 'function') {
                _error_overlay.show("HTTP Error", `Server returned status: ${response.status}`);
            }
            throw new Error("HTTP " + response.status);
        }
        return response.text();
    }).then(text => {
        if (!text) return;
        var res = JSON.parse(text);
        if (res && res.payloads) {
            res.payloads.forEach(p_str => {
                var p = (typeof p_str === "string") ? _dec(p_str) : p_str;
                handle_payload(p, "HTTP");
            });
        }
    }).catch(err => {
        if (payload && payload.data && payload.data.callback_id) {
            _dec_interacting(payload.data.callback_id);
        }
        console.error("htag event POST error:", err);
        if(!window.use_pure_http && _error_overlay && typeof _error_overlay.show === 'function') {
            _error_overlay.show("Network Error", "Could not reach server to trigger event.");
        }
    });
}

// Function called by HTML 'on{event}' attributes to send interactions back to Python
// Returns a Promise that resolves with the server's return value.
function htag_event(id, event_name, event) {
    var callback_id = Math.random().toString(36).substring(2);
    var data = {callback_id: callback_id};

    if (event instanceof Event) {
        // Standard DOM Event
        var target = event.target;
        if (target && target.tagName) {  // Ensure target is a DOM element
            // Check if the event source is a form or inside a form
            //var form = (target.tagName === 'FORM') ? target : target.closest('form');
            var form = (target.tagName === 'FORM') ? target : null;
            if (form && event_name === 'submit') {
                // Collect all form data into value attribute (standard htag v2 pattern)
                var formData = new FormData(form);
                data.value = {};
                formData.forEach((v, k) => { data.value[k] = v; });
            } else if (target.type === 'checkbox') {
                data.value = target.checked;
            } else {
                data.value = target.value;
            }
        }
        data.key = event.key;
        data.pageX = event.pageX;
        data.pageY = event.pageY;
        data.button = event.button;
        data.which = event.which;
        
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

    return new Promise(resolve => {
        window._htag_callbacks[callback_id] = resolve;
        _sync_interacting();
        window.htag_transport(payload);
    });
}
""")

