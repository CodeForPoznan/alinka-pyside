# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [
        'run.py',
        'alinka/widget/actions.py',
        'alinka/widget/main_window.py',
    ],
    pathex=[],
    binaries=[],
    datas=[
        ("statics", "statics"),
        # these data files are necessary to run Alembic migrations
        # I was not able to put them as hidden imports as it looks like
        # Alembic doesn't use standard Python import mechanism
        ("alembic.ini", "."),
        ('migrations/env.py', 'migrations'),
        ('migrations/versions', 'migrations/versions'),
    ],
    hiddenimports=[
        # required by Alembic's env.py
        'logging.config',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='alinka',
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
    icon="statics/alinka.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='alinka',
)
