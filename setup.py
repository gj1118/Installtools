from distutils.core import setup
import py2exe
setup(
    options = {"py2exe":{"packages":"encodings",
                         "includes":[],
                         "dll_excludes":['w9xpopen.exe'],
                         "bundle_files":1,
                         "optimize":2},},
    console=["installTools.py"],
    zipfile = None,
    data_files=[("",
                 ["installTools.config","chocoinstall.cmd"]),
                ],
    name='InstallTools',
    version='1.0.0',
    url='',
    license='MIT',
    author='Gagan Janjua',
    author_email='gj1118@gmail.com',
    description='',
)
