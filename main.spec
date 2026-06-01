# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\main.py'],
    pathex=['.'],
    binaries=[('C:\\Users\\GABRIEL\\miniconda3\\Lib\\site-packages\\pyzbar\\libiconv.dll', 'pyzbar'), ('C:\\Users\\GABRIEL\\miniconda3\\Lib\\site-packages\\pyzbar\\libzbar-64.dll', 'pyzbar')],
    datas=[('app\\templates', 'templates'), ('app\\static', 'static')],
    hiddenimports=['bcrypt', 'passlib.handlers.bcrypt'],
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
    name='main',
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
