# python3 convertToSO.py build_ext --inplace

# !/usr/bin/env python
'''
Created on 2018-09-13
@author: Thien Doan
'''
'''
API1: convert whole project to .so and move to a new folder
API2: convert single files to .so and move to the .so folder
API3: convert single files to .so, rename the old file to _temp.py, and move .so file to the original folder
'''
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import shutil
import os
import time
import sys
from distutils.dir_util import copy_tree

#######################################################################################################################
# SINGLE_FILE = 0
#######################################################################################################################
SINGLE_FILE = False
MAC_OS = False
API3 = True

if not SINGLE_FILE:
    API3 = False

fileNames = ['ateConfig.py']

if MAC_OS:
    PATH_TRANSFER = '/Users/130760/Documents/Work/2019/2_Feb/newATE_secure_bdAPI/ShineProduction/transferToSo/'
    PATH_SRC = '/Users/130760/Documents/Work/2019/2_Feb/newATE_secure_bdAPI/ShineProduction/newATE/'
else:
    PATH_TRANSFER = '/home/pi/misfit/ShineProduction/newATE/'
    PATH_SRC = '/home/pi/ctz/ate_sw/newATE/'
    PATH_PARENTS = PATH_SRC.replace('newATE/','')

SO = '_so'
TEMP = '_temp.py'
PATH_SRC_SO = ''

EXCLUSION_LIST = [
'GpioMonitorApp.py',
'register_activation.py',
'shine_production_tests.py',
'uploadLogExecution.py',
'gpioMonitorSetup.py',
'dmmSetup.py',
'dmmSettings.py',
'ate_settings.py'
]

if os.path.isdir(PATH_PARENTS + 'newATE_so'):
    print("\033[1;32mFolder already exists: " + PATH_PARENTS + 'newATE_so/' + ". Removing it..." + "\033[0m\n")
    shutil.rmtree(PATH_PARENTS + 'newATE_so/')

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
                try:
                    print("\033[1;32mRemoving file: " + filePath + "\033[0m\n")
                    os.remove(filePath)
                except:
                    pass

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
                        _ret = convertSingleFile(result['file'], folderPath, so_folders_list[_index])
                        result['result'] = _ret

    for re in results:
        if re['result'] is True:
            print("\033[1;32m" + re['file'] + " is successful!\033[0m")
        elif re['result'] is False:
            print("\033[1;31m" + re['file'] + " is fell!\033[0m")
        elif re['result'] is None:
            print("\033[1;31m" + re['file'] + " is not existed!\033[0m")


def convertSingleFile(fileName, path, pathSo):
    if fileName not in EXCLUSION_LIST and PATH_SRC + 'setup/' not in path and path is not PATH_SRC:
        try:
            _pythonVersion = sys.version_info[0]

            if _pythonVersion == 3 and not MAC_OS:
                soFileSrc = os.path.join(PATH_TRANSFER, fileName[:-3] + '.cpython-34m.so')
            else:
                soFileSrc = os.path.join(PATH_TRANSFER, fileName[:-3] + '.so')

            soFile = os.path.join(pathSo, fileName[:-3] + '.so')
            cFile = os.path.join(path, fileName[:-3] + '.c')
            srcFile = os.path.join(path, fileName)

            if os.path.exists(soFile):
                print("\033[1;32mFile already exists: " + soFile + "\033[0m\n")
                # print("\033[1;32mRemoving file: " + soFile + "\033[0m\n")
                # os.remove(soFile)

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
    else:
        if PATH_SRC + 'setup/' in path:
            print("\033[1;31mIgnore files in folder setup \033[0m\n\n")
        elif path is PATH_SRC:
            print("\033[1;31mIgnore py files in folder newATE \033[0m\n\n")
        srcFile = os.path.join(path, fileName)  
        print("\033[1;31m%s in EXCLUSION_LIST. Ignore it!! \033[0m\n\n" % (path + fileName))
        print("\033[1;31mMoving " + fileName + "....... \033[0m\n\n")
        shutil.copy(srcFile,pathSo)


t = time.time()
sys.argv.append('build_ext')
sys.argv.append('--inplace')

if SINGLE_FILE:
    convertMultipleFiles(fileNames, PATH_SRC)
else:
    convertEntireFolder(PATH_SRC)

shutil.rmtree(PATH_PARENTS + 'newATE_so/setup/')
copy_tree(PATH_PARENTS + 'newATE/setup/', PATH_PARENTS + 'newATE/setup/')

duration = time.time() - t
print("\033[1;33mDuration: %s\033[0m" % duration)
