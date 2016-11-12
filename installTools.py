#!/usr/bin/env python

import platform , os, ntpath, sys,signal, subprocess, errno,shutil, urllib2
import logging, time, datetime

from logging.handlers import TimedRotatingFileHandler

platform = platform.system()
app_path = ''
config_path = ''


# the application main entry point

def createLogger():
    global logger
    logFile = "installTools_{0}.log".format(datetime.datetime.now().strftime('%Y_%m_%d %H_%M_%S'))
    # logFile = "installTools.log"
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    # add a rotating handler
    handler = TimedRotatingFileHandler(logFile,when='d', interval=1, backupCount=10)
    logger.addHandler(handler)
    logger.info("******************************")
    logger.info("Logging Initiated")
    logger.info("{0}".format(datetime.datetime.now().strftime('%Y_%m_%d %H_%M_%S')))
    logger.info("******************************")


def main():
    global logger    
    createLogger()
    # Windows Setup:
    # - check and notify user to install
    # - copy configuration to '%APPDATA%\Sublime Text 3'
    if platform == 'Windows':
        if(logger == None):
            print("Logger object is null or undefined. Logging will not be done.");
        logger.info("Windows OS detected")
        print "Start work"
        app_path = r"C:/Program Files/Sublime Text 3/subl.exe"
        config_path = os.getenv('APPDATA') + '/Sublime Text 3'
        if not Helpers.is_installed(app_path):
            logger.info('Sublime not installed...')
            # install_windows(app_path)
        # config(config_path)
        installOtherTools()
        print "End Work. For more information please see the log file"
        sys.exit(0)
    else:
        print("Operating system is not supported. Please make sure that you are running this script on a WindowsOS")
        raise Exception('Operating system not supported')
        sys.exit(1)

# Windows installation instructions
def install_windows(app_path):
    print('Installing Sublime')
    try:
        if not Helpers.is_installed(['chocolatey']):
            logger.info('Chocolatey is not installed. Will attempt to install chocolatey')
            os.system("support\\windows\\chocoinstall.cmd")
            logger.info("chocolatey installed")
            print("Please relaunch this script as an admin")
        # p = subprocess.Popen(['choco', 'install', '-y', 'sublimetext3'],
        # stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system("choco install -y --force sublimetext3")
        print('Installation complete...')
    except OSError as e:
        print(e)
        sys.exit(1)


def installOtherTools():
    import xml.etree.ElementTree as ET
    try:
        appsRoot = ET.parse("installTools.config").getroot()
        apps = appsRoot.findall(".//app")
        toolsConfig = appsRoot.find(".//toolsConfig")
        for app in apps:
            logger.info("refreshing the environment")
            os.system("refreshenv")
            appName = app.attrib["name"]
            appConfig = app.find(".//config")
            
            logger.info("Now checking if I need to install : {0}".format(appName))
            if(app.attrib["install"] == 'true'):
                if "force" in app.attrib and app.attrib["force"]== 'true':
                    logger.info("App : {0} will be forcefully installed".format(appName));
                    # os.system("choco install -y --force {0}".format(appName))
                    executeConfigurationInformation(appConfig, toolsConfig)
                else:
                    logger.info("{0} will be installed".format(appName))
                    # os.system("choco install -y {0}".format(appName))
                    executeConfigurationInformation(appConfig, toolsConfig)
            else:
                logger.info("{0} will NOT be installed".format(appName))
        pass
    except Exception as e:
        raise e
    pass

def executeConfigurationInformation(appConfig, toolsConfig):
    if(appConfig == None):
        logger.info("appConfig entry not present.")
        return
    for entry in appConfig:
        cls = eval(entry.tag)
        cls.handle(entry, toolsConfig);
    pass

# configuration instructions
def config(config_path):
    packages = config_path + '/Installed Packages'
    settings = config_path + '/Packages/User'
    # create the settings directories
    Helpers.make_dir(config_path)
    Helpers.make_dir(packages)
    Helpers.make_dir(settings)
    # install 'Package Control'
    Helpers.install_package_control(config_path)
    # copy the themes
    Helpers.copytree('./themes', packages)
    # copy the user preferences
    Helpers.copytree('./user-settings', settings)
    print('Configuration complete...')

# Download File class
class downloadfile():
    @staticmethod
    def handle(entry, config):
        Helpers.logStatement("Download File Module")
        downloadParams = config.find(".//downloadParams").attrib['params']
        source = entry.attrib['source']
        target = entry.attrib['target']
        active = entry.attrib['active']
        if(active):
            sourcePathFileName = ntpath.basename(source)
            logger.info("Will download the file : {0}".format(sourcePathFileName))
            logger.info("Download Location : {0}".format(source))
            logger.info("Target Location : {0}".format(target))
            targetFileName = target+'\\'+sourcePathFileName
            downloadFileCompleteCommand = downloadParams.format(target = targetFileName,source = source)
            logging.info(downloadFileCompleteCommand)
            try:
                os.system(downloadFileCompleteCommand)
                logger.info("File download completed successfully")
                pass
            except Exception as e:
                logger.error("There was an error while downloading the file. Please see the error below..")
                print(str(e))
                logger.error(e)
                pass

# FileDelete class
class filedelete():
    @staticmethod
    def handle(entry,config):
        Helpers.logStatement("File Delete Module")
        try:
            # logger.info("File delete process started")
            fileToDelete = entry.text
            active = entry.attrib['active']
            logger.info("File to delete :{0}".format(fileToDelete))
            if(active and os.path.exists(fileToDelete) and os.path.isfile(fileToDelete)):
                os.remove(fileToDelete)
                logger.info("File : {0} was removed".format(fileToDelete))
            else:
                logger.info("Please make sure that active flag is set to true. If it is set to true then either the file does not exist, or the file is not of type file. The path that was supplied : {0}".format(fileToDelete))
            pass
        except Exception as e:
            logger.error(str(e))
            print(str(e))
            pass

# MakeDir class
class makedirectory():
    @staticmethod
    def handle(entry,config):
        Helpers.logStatement("Make Directory Module")
        try:
            directoryToMake = entry.text
            active = entry.attrib['active']
            if(active): 
                logger.info("Directory to make : {0}".format(directoryToMake))
                if(os.path.exists(directoryToMake) and os.path.isdir(directoryToMake)):
                logger.info("Directory : {0} already exists".format(directoryToMake));
                return
                else:
                    Helpers.make_dir(directoryToMake)
                    logger.info("Directory : {0} created successfully".format(directoryToMake))
            else:
                logger.info("active flag is set to false, make directory will not executed")
            pass
        except Exception as e:
            logger.error(str(e))
            print(str(e))
            pass

# Delete Directory class
class deletedirectory():
    @staticmethod
    def handle(entry,config):
        Helpers.logStatement("Delete Directory Module")
        try:
            active = entry.attrib['active']
            if(active):
                directoryToDelete = entry.text
                logger.info("Directory to delete : {0}".format(directoryToDelete))
                if(os.path.exists(directoryToDelete) and os.path.isdir(directoryToDelete)):
                    shutil.rmtree(directoryToDelete)
                    logger.info("Directory was removed")
                else:
                    logger.info("Directory does not exist, or the given path is not a directory")
            else:
                logger.info("Delete directory module is not set active. It will not be executed")
            pass
        except Exception as e:
            logger.error(str(e))
            print(str(e))
            pass

# Copy File class
class copyfile():
    @staticmethod
    def handle(entry,config):
        Helpers.logStatement("Copy File Module")
        try:
            sourceFile = entry.attrib['sourceFile'] 
            active = entry.attrib['active']
            if(active and os.path.exists(sourceFile) and os.path.isfile(sourceFile)):
                targetDirectory = entry.attrib['targetDirectory']
                newFileName = entry.attrib['newFileName']
                if(newFileName is None):
                    newFileName = ntpath.basename(sourceFile)

                newFileNameAndLocation = targetDirectory+"\\"+newFileName

                # check copyfile options in the toolsconfig section
                shouldRenameExistingFile = config.find(".//copyfile").attrib['renameExistingFile']
                if(shouldRenameExistingFile == 'true'):
                    # ok - we have to rename the existing file
                    Helpers.renameExistingFile(newFileNameAndLocation)
                
                
                if(os.path.exists(newFileNameAndLocation) and os.path.isfile(newFileNameAndLocation)):
                    print("File already exists - will not copy the file. You should use the tools config options for the copyfile command ")
                    logger.info("Will not copy the file because the file already exists in the target location")
                    return

                logger.info("New File Name location :  {0}".format(newFileNameAndLocation))
                shutil.copy2(sourceFile,newFileNameAndLocation)
                logger.info("File was copied successfully to the source location")
            else:
                logger.info("Either the source file does not exist or it is not a file")
            pass
        except Exception as e:
            logger.error(str(e))
            print(str(e))
            pass

class copydirectory():
    @staticmethod
    def handle(entry,config):
        Helpers.logStatement("Copy Directory Module");
        try:
            sourceDirectory = entry.attrib['sourcedirectory']
            targetDirectory = entry.attrib['targetdirectory']
            active = entry.attrib['active']
            if(active):
                logger.info("source directory : {0}".format(sourceDirectory))
                logger.info("target directory : {0}".format(targetDirectory))
                Helpers.copytree(sourceDirectory, targetDirectory)
                logger.info("Directory copied successfully")
            else:
                logger.info("Copy directory is not active, hence the step will not be executed.")
            pass
        except Exception as e:
            print(str(e))
            logger.error(str(e))
            pass

# A class containting static helper methods used to perform the install +
# config
class Helpers():
    
    @staticmethod
    # Log a statement to the logger and print it to the console
    def logStatement(statement):
        logger.info("---------------------")
        logger.info(statement) 
        logger.info("---------------------")
        print(statement)
     
    # Check to see if an application is installed
    @staticmethod
    def is_installed(app_path):
        try:
            p = subprocess.Popen(
                app_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.kill(p.pid, signal.SIGTERM)
            return True
        except OSError as e:
            return False
    
    # rename an existing file
    @staticmethod
    def renameExistingFile(existingFile):
        if(os.path.exists(existingFile) and os.path.isfile(existingFile)):
            currentFileNameWithExtension = ntpath.basename(existingFile)
            currentFileName = os.path.splitext(currentFileNameWithExtension)[0]
            currentExtension = os.path.splitext(currentFileNameWithExtension)[1]
            newFileName =  "{0}_{1}{2}".format(currentFileName,datetime.datetime.now().strftime('%Y_%m_%d %H_%M_%S'), currentExtension)
            logging.info("Generated New File Name : {0}".format(newFileName))
            newFileNameLocation = os.path.dirname(existingFile)+"\\"+newFileName
            shutil.copy2(existingFile,newFileNameLocation)     
            logging.info("Copied the new file from : {0} to : {1}".format(existingFile, newFileNameLocation))
            logging.info("since the file has already been copied , delete the original file")
            os.remove(existingFile)  
        
    # create a directory if it doesn't already exist
    @staticmethod
    def make_dir(dir):
        try:
            os.makedirs(dir)
        # capture any non-file-creation errors
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    # recursively copies all the files in a directory
    # required because shutil.copytree can't overwrite directories
    @staticmethod
    def copytree(src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                try:
                    shutil.copytree(s, d, symlinks, ignore)
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        raise
            else:
                shutil.copy2(s, d)

    
if __name__ == '__main__':
    main()
