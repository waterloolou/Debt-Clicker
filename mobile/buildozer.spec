[app]
title = Debt Clicker
package.name = debtclicker
package.domain = org.debtclicker

# This spec lives in mobile/, but source.dir points at the repo root so the
# build can see market.py, network_client.py, groq_integration.py, and
# constants.py — the four desktop modules the mobile app reuses directly.
source.dir = ..
source.include_exts = py,json
source.include_patterns = mobile/*.py,market.py,network_client.py,groq_integration.py,constants.py
source.exclude_dirs = tests,bin,.git,__pycache__,mobile/__pycache__
source.exclude_patterns = mobile/_test_launch.py,*.pyc,save_slot_*.json,career.json,legacy.json,leaderboard.json

version = 1.0
requirements = python3,kivy==2.3.1

# Entry point: buildozer expects main.py at source.dir root. We point it at
# the mobile package's entry via an orientation-friendly launcher.
entrypoint = mobile/main.py

orientation = portrait
fullscreen = 1

# No custom icon.filename set — add one and point it here before a real
# release build; buildozer falls back to a default Kivy icon otherwise.

android.permissions = INTERNET
android.api = 33
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
