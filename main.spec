# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['mnt_src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/icons/system_image.ico', 'resources/icons'),
    ],
    hiddenimports=['psutil', 'GPUtil'],
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
    name='SystemMonitor',
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
    icon='resources/icons/system_image.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SystemMonitor',
)

# macOS specific
app = BUNDLE(
    coll,
    name='SystemMonitor.app',
    icon='resources/icons/icon.ico',
    bundle_identifier='com.sysmonitor.app',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.0.0',
    },
)