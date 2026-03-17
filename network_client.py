"""
Debt Clicker — Network Client
Thin TCP wrapper that sends/receives newline-delimited JSON messages.
All registered callbacks are invoked from a background thread;
callers are responsible for marshalling back to the main thread
(e.g. root.after(0, ...)).
"""

import socket
import threading
import json


class NetworkClient:
    def __init__(self):
        self.connected = False
        self._callbacks = []   # list of fn(msg_dict)
        self._buf = ""
        self.sock = None
        self._recv_thread = None

    # ──────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────

    def add_callback(self, fn):
        """Register a callback that receives every incoming message dict."""
        if fn not in self._callbacks:
            self._callbacks.append(fn)

    def connect(self, host, port=5555):
        """
        Open a TCP connection to host:port.
        Raises socket.error / OSError on failure.
        Starts background receive loop on success.
        """
        if self.connected:
            self.disconnect()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        self.sock.connect((host, port))          # raises on failure
        self.sock.settimeout(None)               # switch to blocking for recv loop
        self.connected = True
        self._buf = ""

        self._recv_thread = threading.Thread(
            target=self._recv_loop, daemon=True, name="NetClientRecv"
        )
        self._recv_thread.start()

    def send(self, msg_dict):
        """
        Serialise msg_dict as JSON and send over the socket.
        Silently ignores errors (e.g. if already disconnected).
        """
        if not self.connected or self.sock is None:
            return
        try:
            data = json.dumps(msg_dict) + "\n"
            self.sock.sendall(data.encode("utf-8"))
        except Exception:
            pass

    def disconnect(self):
        """Close the connection and clean up."""
        self.connected = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    # ──────────────────────────────────────────────────────────────
    # Background receive loop
    # ──────────────────────────────────────────────────────────────

    def _recv_loop(self):
        """
        Background thread: reads data from the socket and dispatches
        complete newline-delimited JSON messages to all registered callbacks.
        """
        while self.connected:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    # Server closed the connection gracefully
                    break
                self._buf += chunk.decode("utf-8", errors="replace")

                # Dispatch every complete line
                while "\n" in self._buf:
                    line, self._buf = self._buf.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    self._dispatch(msg)

            except OSError:
                # Socket was closed from our side (disconnect() called)
                break
            except Exception:
                break

        # Connection lost — notify callbacks with a synthetic disconnected msg
        if self.connected:
            self.connected = False
            self._dispatch({"type": "disconnected"})

    def _dispatch(self, msg):
        for fn in list(self._callbacks):
            try:
                fn(msg)
            except Exception:
                pass
