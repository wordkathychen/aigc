# -*- mode: python ; coding: utf-8 -*-

# 导入必要的模块
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集额外的数据文件和子模块
extra_datas = []
extra_imports = []

# 收集可能有问题的模块
for module in ['tkinter', 'PIL', 'cryptography']:
    try:
        extra_datas.extend(collect_data_files(module))
        extra_imports.extend(collect_submodules(module))
    except Exception:
        pass

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/web/templates', 'src/web/templates'), ('src/web/static', 'src/web/static'), ('src/config', 'src/config')] + extra_datas,
    hiddenimports=['src.web.routes.main', 'src.web.routes.auth', 'src.web.routes.paper_module'] + extra_imports,
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
    name='ai_text_generator',
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
    icon=['resources\\icon.ico'],
)
