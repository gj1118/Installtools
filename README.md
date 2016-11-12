![InstallTools][img-logo]
## Introduction
InstallTools is a small wrapper around chocolatey to install tools on your brand new machine. Given a configuration file (which is an xml file ) you can easily add/install/upgrade/uninstall any tool. Using install tools  you can also copy directories, delete directories,copy files , delete files, download files from internet to further configure your tool.

Its primary aims are:

* To ease your pain while setting up your brand new system/VM image
* To be a part of your build process where you can easily set your windows machine by installing all your dependencies prior to your actual build process.

If you have any problems, please search for a similar issue first, before creating [a new one][new-issue]. 

> Also, please check the list of known before doing so.

## Generating an exe 
InstallTools uses [py2xe](http://www.py2exe.org/ "Py2exe") to generate an exe that can be run independently of a python installation. This exe is self contained and has no dependencies. All you need to do in that case, is to just copy it and execute it. 

Run the following from your command line (after installing py2exe) to generate an exe in the dist folder.(The dist folder will be created if it does not exist. If its exists, all its contents will be over written).
```
python setup.py py2exe
```

> When running the generated exe, please make sure that the installTools.config file is in the same location as the script. If you have run the above py2exe command, then the installTools.config file will be copied to the dist folder along with the generated exe.

## Changelog
See [CHANGELOG.md][changelog].

<!-- Resources -->

[img-logo]: https://raw.githubusercontent.com/gj1118/Installtools/master/logo.png
[changelog]: https://github.com/gj1118/Installtools/blob/master/CHANGELOG.md