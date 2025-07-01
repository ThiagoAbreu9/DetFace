# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['detface_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[('faces', 'faces'), ('templates', 'templates'), ('config.json', '.'), ('users.json', '.')],
    hiddenimports=['tkinter', 'tkinter.ttk', 'PIL._tkinter_finder', 'sklearn.metrics.pairwise', 'reportlab.pdfgen'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DETFACE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
