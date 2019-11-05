# python3 transfer.py build_ext --inplace

# !/usr/bin/env python
'''
Created on 2019
@author: Ken 20 years old
'''
'''
API1: convert whole project to .so and move to a new folder
API2: convert single files to .so and move to the .so folder
API3: convert single files to .so, rename the old file to _temp.py, and move .so file to the original folder
'''
import sys
# sys.path.append('/home/pi/misfit/ShineProduction/newATE/')

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import shutil
import os
import time
import sys
import datetime

#######################################################################################################################
# SINGLE_FILE = 0
#######################################################################################################################
SINGLE_FILE = True
MAC_OS = False
API3 = True

CHECK_VERSION_GIT    = False
CHECK_VERSION_MANUAL = True

if CHECK_VERSION_GIT == True:
    CHECK_VERSION_MANUAL = True

if not SINGLE_FILE:
    API3 = False
fileNames = ['pinViewController.py']

if MAC_OS:
    PATH_TRANSFER = '/Users/130760/Documents/Work/2019/2_Feb/newATE_secure_bdAPI/ShineProduction/transferToSo/'
    PATH_SRC = '/Users/130760/Documents/Work/2019/2_Feb/newATE_secure_bdAPI/ShineProduction/newATE/'
else:
    PATH_TRANSFER = '/home/pi/' # Dir to the trasfer file
    PATH_SRC = '/home/pi/ATE_release/newATE/' # Dir to source
SO = '_so'
TEMP = '_temp.py'
PATH_SRC_SO = ''

# github
now = datetime.datetime.now()
time_now = (now.year, now.month, now.day)

if CHECK_VERSION_GIT:
    from debug.gitCommands import GitCommands
    gitCmd    = GitCommands()
    cm_number = (gitCmd.gitGetCommitHash()).decode("utf-8")
    b_name    = (gitCmd.gitGetCurrentBranchName()).split('\n')[0]
else:
    cm_number = 'd806464'
    b_name    = 'diana/RATE/dev'

commit_number = "'commit_number':"
branch_name   = "'branch_name':"
fileName_saved= "'cython_file_name':"
date_saved    = "'cython_date':" 

d_saved  = date_saved    + "'" + str(time_now) + "'"
cm_saved = commit_number + "'" + cm_number     + "'"
b_saved  = branch_name   + "'" + b_name        + "'"

def createDescription(fileDirectory, fileName):
    # print(fileName)
    # print(time_now)
    # print(b_name)
    # print(cm_number)

    information = 'File name: '+str(fileName)+'.. Date created: '+str(time_now)\
                    +'.. Branch: '+str(b_name) + '.. Commit: '+str(cm_number)

    description = 'description_' + str(fileName.split('.')[0]) + ' = ' + "'" + str(information) + "'\n"

    saveToFile(fileDirectory, description)

def saveToFile(fileDirectory, info):
    # print(fileDirectory)
    src=open(fileDirectory,"r")
    oline=src.readlines()
    oline.insert(0,info)
    src.close()     
     
    src=open(fileDirectory,"w")
    src.writelines(oline)
    src.close()

###########################################################################################
def createSoFolder(folders_list):
    _len = len(folders_list[0]) - 1

    so_folders_list = []

    for folder in folders_list:
        so_folder = folder[:_len] + SO + folder[_len:]

        if os.path.exists(so_folder) is False:
            print("\033[1;32mFolder is not existed: " + so_folder + "\033[0m\n")
            print("\033[1;32mCreating folder: " + so_folder + "\033[0m\n\n")
            print("\033[1;32m.......................................\033[0m\n\n")
            os.mkdir(so_folder)

        so_folders_list.append(folder[:_len] + SO + folder[_len:])

    return so_folders_list


def listAllFolderName(folders_list, path):
    folders_list.append(path)

    files = os.listdir(path)
    for file in files:
        sub_path = os.path.join(path, file)

        if os.path.isdir(sub_path):
            listAllFolderName(folders_list, sub_path)


def execute(path):
    print("\033[1;32m===============================================================================================\n")
    print("Start to convert to .so file entire folder: " + path + "\n")
    print("===============================================================================================\033[0m\n")
    folders_list = []
    listAllFolderName(folders_list, path)

    so_folders_list = createSoFolder(folders_list)

    for folderPath in folders_list:
        _index = folders_list.index(folderPath)
        files = os.listdir(folderPath)
        for file in files:
            filePath = os.path.join(folderPath, file)
            if filePath[-2:] == '.c':
                print("\033[1;32mRemoving file: " + filePath + "\033[0m\n")
                os.remove(filePath)

            elif os.path.isfile(filePath):
                if (file != '__pycache__') and ('.pyc' not in file) and ('__init__.' not in file) \
                        and (file != 'shine_production_tests.py') and (file != 'gui_run_tests.py') \
                        and (file != 'updaterController.py') and (file != 'updater.py') and (file != 'ble_commands.py'):
                    convertSingleFile(file, folderPath, so_folders_list[_index])
                else:
                    shutil.copy(filePath, so_folders_list[_index])


def convertEntireFolder(path):
    execute(path)
    print("\033[1;33mFinish!\033[0m\n\n")


def convertMultipleFiles(fileNames, path):
    print("\033[1;32m===============================================================================================\n")
    print("Start to convert to .so file...\n")
    print("===============================================================================================\033[0m\n")
    folders_list = []
    listAllFolderName(folders_list, path)

    so_folders_list = createSoFolder(folders_list)

    results = []

    for file in fileNames:
        result = {'file': file, 'result': None}
        results.append(result)

    for folderPath in folders_list:
        _index = folders_list.index(folderPath)
        for x in os.listdir(folderPath):
            x = os.path.join(folderPath, x)
            if os.path.isfile(x):
                for result in results:
                    if os.path.join(folderPath, result['file']) == x:
                        print(folderPath)
                        print(result['file'])
                        _ret = convertSingleFile(result['file'], folderPath, so_folders_list[_index])
                        result['result'] = _ret

    for re in results:
        print(re)
        if re['result'] is True:
            print("\033[1;32m" + re['file'] + " is successful!\033[0m")
        elif re['result'] is False:
            print("\033[1;31m" + re['file'] + " is fell!\033[0m")
        elif re['result'] is None:
            print("\033[1;31m" + re['file'] + " is not existed!\033[0m")


def convertSingleFile(fileName, path, pathSo):
    try:
        _pythonVersion = sys.version_info[0]

        if _pythonVersion == 3 and not MAC_OS:
            soFileSrc = os.path.join(PATH_TRANSFER, fileName[:-3] + '.cpython-34m.so')
        else:
            soFileSrc = os.path.join(PATH_TRANSFER, fileName[:-3] + '.so')

        soFile = os.path.join(pathSo, fileName[:-3] + '.so')
        cFile = os.path.join(path, fileName[:-3] + '.c')
        srcFile = os.path.join(path, fileName)

        if CHECK_VERSION_MANUAL:
            createDescription(srcFile, fileName)

        if os.path.exists(soFile):
            print("\033[1;32mRemoving file: " + soFile + "\033[0m\n")
            os.remove(soFile)

        print("\033[1;33mConverting file: " + fileName + "\033[0m")
        ext_modules = [
            Extension(fileName[:-3], [srcFile]),
        ]
        #extensions = cythonize(extensions, language_level = "3")
        #extensions = cythonize(extensions, compiler_directives={'language_level' : "3"}) # or "2" or "3str" 
        # os.environ['CC'] = 'arm-linux-gnueabihf-gcc -I/home/parallels/Desktop/ParallelsSharedFolders/Work/Documents/0.0.Scripts/Cython/tools/arm-bcm2708'# -Wno-div-by-zero'
        #os.environ['LDSHARED'] = 'arm-linux-gnueabihf-gcc -shared'
        #os.environ['LD'] = 'arm-linux-gnueabihf-ld'
        #sysroot_args=['--sysroot', '/home/parallels/Desktop/Parallels\ Shared\ Folders/Work/Documents/0.0.Scripts/Cython/tools-master/arm-bcm2708/arm-rpi-4.9.3-linux-gnueabihf']
        setup(
            name='Convert all python file to .so',
            cmdclass={'build_ext': build_ext},
            ext_modules=cythonize(ext_modules))

        if '.cpython-34m' in soFileSrc:
            print("===============================================================================================\n")
            os.rename(soFileSrc, soFileSrc.replace('.cpython-34m', '', 1))
            soFileSrc = soFileSrc.replace('.cpython-34m', '', 1)

        if API3:
            shutil.move(soFileSrc, path)
            fileSrc = os.path.join(path, fileName)
            os.rename(fileSrc, fileSrc.replace('.py', TEMP, 1))
            fileSrc = fileSrc.replace('.py', TEMP, 1)
        else:
            shutil.move(soFileSrc, pathSo)
        os.remove(cFile)
        print("\033[1;33mFinished converting file: " + fileName + "!\033[0m\n\n")
        return True
    except:
        print("\033[1;31mCrashed during converting process! \033[0m\n\n")
        print("\033[1;31mMoving " + fileName + "....... \033[0m\n\n")
        shutil.copy(srcFile,pathSo)
        return False

sys.argv.append('build_ext')
sys.argv.append('--inplace')
t = time.time()
if SINGLE_FILE:
    convertMultipleFiles(fileNames, PATH_SRC)
else:
    convertEntireFolder(PATH_SRC)


duration = time.time() - t
print("\033[1;33mDuration: %s\033[0m" % duration)

# createVariable('/Users/130760/Documents/test1.py', 'test1.py')
