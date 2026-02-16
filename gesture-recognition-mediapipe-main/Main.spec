# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

def get_mediapipe_path():
    import mediapipe
    mediapipe_path = mediapipe.__path__[0]
    return mediapipe_path

def get_opencv_path():
    import cv2
    cv_path = cv2.__path__[0]
    return cv_path

def get_snap7_path():
    import snap7
    snap_path = snap7.__path__[0]
    return snap_path

a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
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

mediapipe_tree = Tree(get_mediapipe_path(), prefix='mediapipe', excludes=["*.pyc"])
a.datas += mediapipe_tree
mediapipebinaries = list(filter(lambda x: 'mediapipe' not in x[0], a.binaries))

opencv_tree = Tree(get_opencv_path(), prefix='cv2', excludes=["*.pyc"])
a.datas += opencv_tree
cvbinaries = list(filter(lambda x: 'cv2' not in x[0], a.binaries))

snap_tree = Tree(get_snap7_path(), prefix='snap7', excludes=["*.pyc"])
a.datas += snap_tree
snapbinaries = list(filter(lambda x: 'snap7' not in x[0], a.binaries))

a.binaries = mediapipebinaries + cvbinaries + snapbinaries

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
