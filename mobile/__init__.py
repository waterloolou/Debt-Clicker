"""Debt Clicker Mobile — a Kivy port of the desktop Tkinter game.

This package is entirely independent of the desktop app's Tkinter mixins
(none of them are imported here, directly or transitively) so it can run
on Android/iOS where Tkinter does not exist. It reuses only the four
desktop modules that were already Tkinter-free: constants.py, market.py,
network_client.py, and groq_integration.py.
"""
