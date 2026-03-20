"""
Debt Clicker — Multiplayer Server
Usage: python server.py [port]
Default port: 5555
Max players per lobby: 3

Also runs an HTTP server on port+1 (default 5556) for the global leaderboard:
  GET  /leaderboard        → JSON array of top-50 entries
  POST /leaderboard        → submit {"name": ..., "days": ..., "country": ...}
"""

import socket
import threading
import json
import sys
import random
import string
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


MAX_PLAYERS  = 3
DEFAULT_PORT = 5555

# lobby_id -> {"players": [{"name": ..., "conn": ..., "addr": ...}]}
lobbies      = {}
lobbies_lock = threading.Lock()

# ──────────────────────────────────────────────────────────────────────────────
# Global leaderboard (in-memory + persisted to leaderboard_global.json)
# ──────────────────────────────────────────────────────────────────────────────

GLOBAL_LB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "leaderboard_global.json")
global_lb      = []
global_lb_lock = threading.Lock()


def _load_global_lb():
    global global_lb
    try:
        with open(GLOBAL_LB_FILE) as f:
            global_lb = json.load(f)
    except Exception:
        global_lb = []


def _save_global_lb():
    try:
        with open(GLOBAL_LB_FILE, "w") as f:
            json.dump(global_lb, f, indent=2)
    except Exception:
        pass


def add_global_score(name: str, days: int, country: str):
    with global_lb_lock:
        global_lb.append({"name": name, "days": days, "country": country})
        global_lb.sort(key=lambda x: x["days"], reverse=True)
        del global_lb[50:]          # keep top 50
        _save_global_lb()


def get_global_lb():
    with global_lb_lock:
        return list(global_lb)


class _LBHandler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass   # silence HTTP access log

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/leaderboard":
            data = json.dumps(get_global_lb()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/leaderboard":
            length = int(self.headers.get("Content-Length", 0))
            body   = self.rfile.read(length)
            try:
                entry = json.loads(body)
                name    = str(entry.get("name", "")).strip()[:32]
                days    = int(entry.get("days", 0))
                country = str(entry.get("country", "")).strip()[:64]
                if name and days > 0:
                    add_global_score(name, days, country)
            except Exception:
                pass
            self.send_response(200)
            self._cors()
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()


def _run_http(http_port: int):
    _load_global_lb()
    server = HTTPServer(("0.0.0.0", http_port), _LBHandler)
    print(f"Global leaderboard HTTP on port {http_port}  (GET/POST /leaderboard)")
    server.serve_forever()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def send_msg(conn, msg_dict):
    """Send a newline-delimited JSON message."""
    try:
        data = json.dumps(msg_dict) + "\n"
        conn.sendall(data.encode("utf-8"))
    except Exception:
        pass


def broadcast(lobby_id, msg_dict, exclude_conn=None):
    """Send a message to every player in a lobby."""
    with lobbies_lock:
        lobby = lobbies.get(lobby_id)
        if not lobby:
            return
        targets = [p["conn"] for p in lobby["players"] if p["conn"] is not exclude_conn]
    for conn in targets:
        send_msg(conn, msg_dict)


def player_names(lobby_id):
    with lobbies_lock:
        lobby = lobbies.get(lobby_id)
        if not lobby:
            return []
        return [p["name"] for p in lobby["players"]]


# ──────────────────────────────────────────────────────────────────────────────
# Client handler
# ──────────────────────────────────────────────────────────────────────────────

def handle_client(conn, addr):
    print(f"[connect] {addr}")
    buf = ""
    current_lobby_id = None
    current_name = None

    try:
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buf += chunk.decode("utf-8", errors="replace")

            # Process all complete newline-terminated messages in buffer
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[{addr}] bad JSON: {line!r}")
                    continue

                mtype = msg.get("type")

                # ── join ──────────────────────────────────────────────────
                if mtype == "join":
                    lobby_id = str(msg.get("lobby_id", "")).upper().strip()
                    name     = str(msg.get("name", "")).strip()
                    country  = str(msg.get("country", "")).strip()

                    if not lobby_id or not name:
                        send_msg(conn, {"type": "error", "msg": "Missing lobby_id or name."})
                        continue

                    with lobbies_lock:
                        if lobby_id not in lobbies:
                            lobbies[lobby_id] = {"players": []}

                        lobby = lobbies[lobby_id]

                        # Check for duplicate name
                        existing_names = [p["name"] for p in lobby["players"]]
                        if name in existing_names:
                            send_msg(conn, {"type": "error",
                                            "msg": f"Name '{name}' is already taken in this lobby."})
                            continue

                        if len(lobby["players"]) >= MAX_PLAYERS:
                            send_msg(conn, {"type": "error", "msg": "Lobby is full."})
                            continue

                        lobby["players"].append({
                            "name":    name,
                            "conn":    conn,
                            "addr":    addr,
                            "country": country,
                        })
                        current_lobby_id = lobby_id
                        current_name     = name
                        player_count     = len(lobby["players"])
                        names_snapshot   = [p["name"] for p in lobby["players"]]

                    print(f"[lobby {lobby_id}] {name} joined ({player_count}/{MAX_PLAYERS})")

                    # Confirm to joiner
                    send_msg(conn, {
                        "type":         "lobby_joined",
                        "player_count": player_count,
                        "max":          MAX_PLAYERS,
                        "players":      names_snapshot,
                        "lobby_id":     lobby_id,
                    })

                    # Notify others
                    broadcast(lobby_id, {
                        "type":         "player_joined",
                        "name":         name,
                        "player_count": player_count,
                        "players":      names_snapshot,
                    }, exclude_conn=conn)

                    # Start game if lobby is now full
                    if player_count == MAX_PLAYERS:
                        print(f"[lobby {lobby_id}] FULL — broadcasting game_start")
                        with lobbies_lock:
                            lobby = lobbies.get(lobby_id)
                            if lobby:
                                game_players = [{"name": p["name"], "country": p["country"]}
                                                for p in lobby["players"]]
                        broadcast(lobby_id, {
                            "type":    "game_start",
                            "players": game_players,
                        })

                # ── state update ──────────────────────────────────────────
                elif mtype == "state":
                    if current_lobby_id and current_name:
                        state = msg.get("state", {})
                        broadcast(current_lobby_id, {
                            "type":  "player_update",
                            "name":  current_name,
                            "state": state,
                        }, exclude_conn=conn)

                # ── chat ──────────────────────────────────────────────────
                elif mtype == "chat":
                    if current_lobby_id and current_name:
                        broadcast(current_lobby_id, {
                            "type": "chat",
                            "name": current_name,
                            "text": str(msg.get("text", ""))[:200],
                        })
                        # Also echo back to sender
                        send_msg(conn, {
                            "type": "chat",
                            "name": current_name,
                            "text": str(msg.get("text", ""))[:200],
                        })

                # ── war declaration ───────────────────────────────────────
                elif mtype == "war":
                    if current_lobby_id and current_name:
                        broadcast(current_lobby_id, {
                            "type":           "war",
                            "attacker":       current_name,
                            "target_country": msg.get("target_country", ""),
                            "victim":         msg.get("victim", ""),
                        })
                        print(f"[lobby {current_lobby_id}] WAR: {current_name} "
                              f"attacked {msg.get('target_country','')} "
                              f"(player: {msg.get('victim','')})")

                # ── war action (militia attack) ───────────────────────────
                elif mtype == "war_action":
                    if current_lobby_id and current_name:
                        broadcast(current_lobby_id, {
                            "type":      "war_action",
                            "attacker":  current_name,
                            "action_id": msg.get("action_id", ""),
                            "target":    msg.get("target", ""),
                            "meta":      msg.get("meta", {}),
                        })
                        print(f"[lobby {current_lobby_id}] WAR_ACTION: {current_name} "
                              f"→ {msg.get('target','')} ({msg.get('action_id','')})")

                # ── leave ─────────────────────────────────────────────────
                elif mtype == "leave":
                    break

                else:
                    print(f"[{addr}] unknown message type: {mtype!r}")

    except Exception as e:
        print(f"[{addr}] error: {e}")

    finally:
        # Clean up: remove player from lobby
        if current_lobby_id and current_name:
            with lobbies_lock:
                lobby = lobbies.get(current_lobby_id)
                if lobby:
                    lobby["players"] = [
                        p for p in lobby["players"] if p["name"] != current_name
                    ]
                    remaining = len(lobby["players"])
                    print(f"[lobby {current_lobby_id}] {current_name} left "
                          f"({remaining} remaining)")
                    if remaining == 0:
                        del lobbies[current_lobby_id]
                        print(f"[lobby {current_lobby_id}] closed (empty)")

            broadcast(current_lobby_id, {
                "type": "player_left",
                "name": current_name,
            })

        send_msg(conn, {"type": "disconnected"})
        try:
            conn.close()
        except Exception:
            pass
        print(f"[disconnect] {addr}")


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main():
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port '{sys.argv[1]}', using {DEFAULT_PORT}")

    # Start HTTP leaderboard server on port+1
    http_port = port + 1
    threading.Thread(target=_run_http, args=(http_port,), daemon=True).start()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("0.0.0.0", port))
    server_sock.listen(16)
    print(f"Debt Clicker server listening on port {port} (max {MAX_PLAYERS} per lobby)")

    try:
        while True:
            conn, addr = server_sock.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server_sock.close()


if __name__ == "__main__":
    main()
