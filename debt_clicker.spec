# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for Debt Clicker
# Build with:  python -m PyInstaller debt_clicker.spec
#
from PyInstaller.utils.hooks import collect_all, collect_data_files

# Collect entire packages that use native extensions or lazy imports
geopandas_datas,   geopandas_binaries,   geopandas_hiddens   = collect_all('geopandas')
shapely_datas,     shapely_binaries,     shapely_hiddens     = collect_all('shapely')
pyproj_datas,      pyproj_binaries,      pyproj_hiddens      = collect_all('pyproj')
matplotlib_datas,  matplotlib_binaries,  matplotlib_hiddens  = collect_all('matplotlib')
yfinance_datas,    yfinance_binaries,    yfinance_hiddens    = collect_all('yfinance')
pandas_datas,      pandas_binaries,      pandas_hiddens      = collect_all('pandas')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=(
        shapely_binaries + pyproj_binaries +
        geopandas_binaries + matplotlib_binaries +
        yfinance_binaries + pandas_binaries
    ),
    datas=(
        # Game data files
        [('world_countries.gpkg', '.')]
        + geopandas_datas + shapely_datas + pyproj_datas
        + matplotlib_datas + yfinance_datas + pandas_datas
    ),
    hiddenimports=(
        geopandas_hiddens + shapely_hiddens + pyproj_hiddens +
        matplotlib_hiddens + yfinance_hiddens + pandas_hiddens + [
            # tkinter backend for matplotlib
            'matplotlib.backends.backend_tkagg',
            'matplotlib.backends._backend_tk',
            # network / multiplayer
            'socket', 'threading', 'json',
            # audio (Windows only)
            'winsound',
            # common stdlib used at runtime
            'random', 'datetime', 'os', 'sys', 'pathlib',
            'collections', 'itertools', 'functools',
        ]
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
    exclude_binaries=True,       # folder mode — faster startup, smaller delta updates
    name='DebtClicker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,               # no terminal window
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
