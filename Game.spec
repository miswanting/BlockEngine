# -*- mode: python -*-

block_cipher = None


a = Analysis(['Game.py'],
             pathex=['D:\\Users\\OneDrive\\CODE\\SquareWorld\\dist'],
             binaries=None,
             datas=[('config.conf', '.'),
                    ('msyh.ttc', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Game',
          debug=False,
          strip=False,
          upx=True,
          console=True )
