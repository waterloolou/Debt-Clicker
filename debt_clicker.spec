# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for Debt Clicker  (Windows, Linux, macOS)
# Build with:  python -m PyInstaller debt_clicker.spec
#
import sys
from PyInstaller.utils.hooks import collect_all

geopandas_d,  geopandas_b,  geopandas_h  = collect_all('geopandas')
shapely_d,    shapely_b,    shapely_h    = collect_all('shapely')
pyproj_d,     pyproj_b,     pyproj_h     = collect_all('pyproj')
matplotlib_d, matplotlib_b, matplotlib_h = collect_all('matplotlib')
yfinance_d,   yfinance_b,   yfinance_h   = collect_all('yfinance')
pandas_d,     pandas_b,     pandas_h     = collect_all('pandas')

platform_hidden = ['winsound'] if sys.platform == 'win32' else []

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=(
        shapely_b + pyproj_b + geopandas_b +
        matplotlib_b + yfinance_b + pandas_b
    ),
    datas=(
        [('world_countries.gpkg', '.')]
        + geopandas_d + shapely_d + pyproj_d
        + matplotlib_d + yfinance_d + pandas_d
    ),
    hiddenimports=(
        geopandas_h + shapely_h + pyproj_h +
        matplotlib_h + yfinance_h + pandas_h + [
            'matplotlib.backends.backend_tkagg',
            'matplotlib.backends._backend_tk',
            'socket', 'threading', 'json',
            'wave', 'struct', 'io', 'subprocess',
            'random', 'datetime', 'os', 'sys', 'pathlib',
            'collections', 'itertools', 'functools',
        ] + platform_hidden
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'IPython', 'notebook', 'jupyter'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DebtClicker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DebtClicker',
)
