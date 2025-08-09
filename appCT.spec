# cofre_qt.spec
# run: pyinstaller cofre_qt.spec

from PyInstaller.utils.hooks import collect_all
datas, binaries, hiddenimports = collect_all('PySide6')

a = Analysis(
    ['app_pyside6.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas + [('icone.png','.')],
    hiddenimports=hiddenimports,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts,
    name='CofreSenhas',
    icon='icone.ico',
    console=False,
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=False, name='CofreSenhas-Qt')
