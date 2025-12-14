# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('credentials.example.json', '.'), ('config.py', '.')],
    hiddenimports=['customtkinter', 'google_auth_oauthlib', 'google_auth', 'googleapiclient', 'googleapiclient.discovery', 'requests', 'keyring', 'keyring.backends', 'dotenv'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary testing and development modules
        'pytest', 'unittest', 'test', 'tests',
        # Exclude unused scientific computing libraries
        'numpy', 'pandas', 'scipy', 'matplotlib',
        # Exclude other unused modules
        'IPython', 'jupyter', 'notebook',
        'PIL', 'cv2', 'opencv',
        'sqlalchemy', 'sqlite3',
        'xml.etree.ElementTree',
        'logging.handlers',
        'multiprocessing',
        # Exclude unused email modules
        'email.mime.audio', 'email.mime.image',
    ],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AI Email Summarizer',
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
