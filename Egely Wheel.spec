# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('egely wheel graphic clockwise .png', '.'), ('egely wheel counter clockwise .png', '.'), ('Egely Wheel Graphic both directions.png', '.'), ('Egely wheel no background graphic counter clockwise.png', '.'), ('black_egely_wheel_only.png', '.'), ('green_arrow_clockwise.png', '.'), ('green_arrow_anticlockwise.png', '.'), ('light_blue_arrows_transparent.png', '.'), ('spin clockwise.mp3', '.'), ('spin counter clockwise.mp3', '.'), ('spin clockwise or counter clockwise.mp3', '.'), ('Spin fast in either direction.mp3', '.'), ('Ten seconds to focus intentions.mp3', '.'), ('Begin.mp3', '.'), ('stop.mp3', '.'), ('end_of_game.mp3', '.'), ('spin clockwise 1 to roations then anti clockwise 1 to 2 rotations.mp3', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Egely Wheel',
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
    name='Egely Wheel',
)
app = BUNDLE(
    coll,
    name='Egely Wheel.app',
    icon=None,
    bundle_identifier=None,
)
