# -*- mode: python -*-
a = Analysis(['install.py'],
             pathex=['C:\\Users\\ilovetux\\workspaces\\mast\\mast.installer\\mast\\installer'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)

def extra_datas(mydir):
    def rec_glob(p, files):
        import os
        import glob
        for d in glob.glob(p):
            if os.path.isfile(d):
                files.append(d)
            rec_glob("%s/*" % d, files)
    files = []
    rec_glob("%s/*" % mydir, files)
    extra_datas = []
    for f in files:
        extra_datas.append((f, f, 'DATA'))

    return extra_datas

# append the 'data' dir
a.datas += extra_datas('files')
a.datas += extra_datas('packages')
a.datas += extra_datas('scripts')
             
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='install.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
