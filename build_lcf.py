import json
import pathlib
from colorama import init
from lxml import etree
from download_and_unzip import DownloadAndUnzip
import shutil
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
import shlex
import re
import os
configPath = "config.json"
versionList = ["25"]

workspaceRootFolder = pathlib.Path(
    __file__).parent.absolute()


def run_shell_command(command_line: list) -> bool:
    command_line = " ".join(command_line)
    command_line_args = shlex.split(command_line)
    try:
        command_line_process = Popen(
            command_line_args,
            stdout=PIPE,
            stderr=STDOUT,
        )
        for line in command_line_process.stdout:
            log_txt = line.decode('utf-8', errors='ignore')
            print(log_txt)
    except (OSError, CalledProcessError) as exception:
        return False
    return True


def decodefile(srcfile, from_codec, to_codec):
    oldname = srcfile.name
    tempname = oldname+"_"
    trgfile = srcfile.parent / tempname
    with open(srcfile, 'r', encoding=from_codec) as f, open(trgfile, 'w', encoding=to_codec) as e:
        text = f.read()
        if text.startswith('\ufeff') and to_codec == 'utf-8-sig':
            return
        e.write(text)
    srcfile.unlink()  # remove old encoding file
    trgfile.rename(srcfile)  # rename new encoding


def DecodeGDL(hsf_folder, from_codec, to_codec):
    paths = sorted(pathlib.Path(hsf_folder).glob('**/*.gdl'))
    for file in paths:
        filename = file.absolute()
        decodefile(filename, from_codec, to_codec)


def CreateGSM(version: str, folders):
    gsm_folder = folders['gsm'][version]
    hsf_folder = folders['hsf']
    devKit = workspaceRootFolder / 'LP_XMLConverter' / \
        f'LP_XMLConverter{version}'/'WIN'/'LP_XMLConverter.EXE'
    param = [f'"{devKit}"', 'hsf2l', '-l CYR',
             f'"{hsf_folder}"', f'"{gsm_folder}"']
    return run_shell_command(param)


def CreateLCF(version: str, folders):
    gsm_folder = folders['gsm'][version]
    lcf_name = folders['lcf'][version]
    devKit = workspaceRootFolder / 'LP_XMLConverter' / \
        f'LP_XMLConverter{version}'/'WIN'/'LP_XMLConverter.EXE'
    param = [f'"{devKit}"', 'createcontainer',
             f'"{lcf_name}"', '-compress 9',  f'"{gsm_folder}"']
    return run_shell_command(param)


def DownloadLP_XMLConverterOne(configData: dict, version: str):
    """
    Скачивает LP_XMLConverter для указанной версии

    Args:
        configData (dict): Словарь с настройками
        version (str): Номер версии
    """
    if version in configData['LP_XMLConverter']:
        devKitFolder = workspaceRootFolder / 'LP_XMLConverter'
        if not devKitFolder.exists():
            devKitFolder.mkdir(parents=True)
        devKitFolderVersion = workspaceRootFolder / \
            'LP_XMLConverter' / f'LP_XMLConverter{version}'
        if not devKitFolderVersion.exists():
            DownloadAndUnzip(
                configData['LP_XMLConverter'][version], devKitFolder)


def DownloadLP_XMLConverters(configData: dict, versionList: str):
    """
    Скачивает LP_XMLConverter для всех заданных в настройках

    Args:
        configData (dict): Словарь с настройками
        versionList (list): Номера версий
    """
    for version in versionList:
        DownloadLP_XMLConverterOne(configData, version)


def PrepareDirectories(configData: dict, versionList: str):
    """
    Создание папок для пакетов библиотек

    Args:
        configData (dict): Словарь с настройками
        versionList (list): Номеры версий
    """
    folderpath = {}
    for lcfName in configData["Package"]:
        buildFolder = workspaceRootFolder / lcfName
        if not buildFolder.exists():
            buildFolder.mkdir(parents=True)
        hsf_folder = buildFolder / f'hsf'
        if not hsf_folder.exists():
            hsf_folder.mkdir(parents=True)
        macro_folder = hsf_folder / '_macro_'
        if not macro_folder.exists():
            macro_folder.mkdir(parents=True)
        folderpath[lcfName] = {}
        folderpath[lcfName]['hsf'] = hsf_folder
        folderpath[lcfName]['macro'] = macro_folder
        folderpath[lcfName]['gsm'] = {}
        folderpath[lcfName]['lcf'] = {}
        for version in versionList:
            gsm_folder = buildFolder / version / 'gsm'
            folderpath[lcfName]['gsm'][version] = gsm_folder
            if not gsm_folder.exists():
                gsm_folder.mkdir(parents=True)
            lcf_filename = lcfName+version+'.lcf'
            folderpath[lcfName]['lcf'][version] = buildFolder / \
                version / lcf_filename
    return folderpath


def GetGUID(filename: pathlib.WindowsPath) -> str:
    """
    Получение GUID gdl объекта, сохранённого в HSF формате

    Args:
        filename (pathlib.WindowsPath): Путь к папке с HSF

    Returns:
        str: GUID элемента
    """
    GUIDelem = None
    try:
        parser = etree.XMLParser(strip_cdata=False)
        root = etree.parse(str(filename / 'libpartdata.xml'), parser)
        croot = root.getroot()
        GUIDelem = croot.find('Identification/MainGUID').text
    except Exception as e:
        print(f'Папка {filename} не содержит HSF объект')
    return GUIDelem


def GetCalledMacro(filename: pathlib.WindowsPath) -> dict:
    """
    Получение словаря с использованными в объекте макросами

    Args:
        filename (pathlib.WindowsPath): Путь к папке с HSF

    Returns:
        dict(str:str): Словарь в формате Имя макроса : GUID
    """
    macro_dict = {}
    try:
        parser = etree.XMLParser(strip_cdata=False)
        root = etree.parse(str(filename / 'calledmacros.xml'), parser)
        for macro in root.getroot():
            namemacro = macro.find('MName')
            if namemacro is not None:
                guidemacro = macro.find('MainGUID')
                if guidemacro is not None:
                    guidemacro = guidemacro.text
                    namemacro = namemacro.text.strip('"')
                    macro_dict[namemacro] = guidemacro
    except Exception as e:
        print(f'Папка {filename} не содержит HSF объект')
    return macro_dict


def GetIncludeFileDict(hsf_folder: pathlib.WindowsPath) -> dict:
    """
    Составляет словарь папок, содержащих файл include.json
    В файле должен быть словарь с ключами "File" или "Package"

    Args:
        hsf_folder (pathlib.WindowsPath): Путь к папке

    Returns:
        dict(str:{str: [pathlib.WindowsPath]}): Словарь в формате "File"/"Package" : {Имя файла : [Список включаемых папок]}
    """
    include_dict = {}
    paths = sorted(pathlib.Path(hsf_folder).glob('**/include.json'))
    for file in paths:
        if file.is_file():
            includeFile = open(file, 'r', encoding="utf-8")
            includeData = json.load(includeFile)
            includeFile.close()
            filename = file.parent.absolute()
            for k, v in includeData.items():
                if k not in include_dict:
                    include_dict[k] = {}
                for el in v:
                    if el not in include_dict[k]:
                        include_dict[k][el] = []
                    include_dict[k][el].append(filename)
    return include_dict


def GetGUIDDict(hsf_folder: pathlib.WindowsPath) -> dict:
    """
    Составляет словарь элементов, лежащих в папке

    Args:
        hsf_folder (pathlib.WindowsPath): Путь к папке

    Returns:
        dict(str:{str: pathlib.WindowsPath, str: str}): Словарь в формате Имя элемента : {'filename': Путь к файлу, 'GUID': GUID элемента}
    """
    hsf_dict = {}
    paths = sorted(pathlib.Path(hsf_folder).glob('**/libpartdata.xml'))
    for file in paths:
        filename = file.parent.absolute()
        name = file.parts[-2]
        GUIDelem = GetGUID(filename)
        if GUIDelem is not None:
            hsf_dict[name] = {'filename': filename, 'GUID': GUIDelem}
    return hsf_dict


def GetMacroDict(hsf_folder: pathlib.WindowsPath) -> dict:
    """
    Составляет словарь макросов для элементов, лежащих в папке

    Args:
        hsf_folder (pathlib.WindowsPath): Путь к папке

    Returns:
        dict(str:str): Словарь в формате GUID : Имя макроса
    """
    macro_dict = {}
    paths = sorted(pathlib.Path(hsf_folder).glob('**/libpartdata.xml'))
    for file in paths:
        filename = file.parent.absolute()
        macro_dict = {**macro_dict, **GetCalledMacro(filename)}
    return macro_dict


def CopyHSF(config, folders, hsf_dict):
    """Копирует HSF объекты для пакета

    Args:
        configData (dict): Словарь с настройками
        lcfName (str): Имя пакета
        hsf_dict (dict): Словарь со всеми существующими объектами
    """
    copied_file = []
    for hsf in config["Include"]:
        if hsf in hsf_dict:
            shutil.copytree(hsf_dict[hsf]['filename'],
                            folders['hsf'] / hsf, dirs_exist_ok=True)
            copied_file.append(hsf)
        else:
            print(f'Не найден объект {hsf}')
    return copied_file


def CopyMacro(config, folders, hsf_dict, copied_file):
    all_macro_dict = GetMacroDict(folders['hsf'])
    include_macro = {}
    for k, v in all_macro_dict.items():
        if k not in config["Ignore"] and k not in copied_file:
            if k in hsf_dict:
                include_macro[k] = v
            else:
                print(f'Не найден макрос {name_macro}')
    if len(include_macro) == 0:
        return copied_file, True
    for name_macro in include_macro.keys():
        shutil.copytree(hsf_dict[name_macro]['filename'],
                        folders['macro'] / name_macro, dirs_exist_ok=True)
        copied_file.append(name_macro)
    return copied_file, False


def CopyIncludeFolder(folders, include_dict, copied_file, lcfName):
    if lcfName in include_dict['Package']:
        for folder in include_dict['Package'][lcfName]:
            shutil.copytree(folder,
                            folders['macro'] / folder.parts[-1], dirs_exist_ok=True)
            for p in sorted(pathlib.Path(folder).glob('**/*.*')):
                if p.is_file():
                    copied_file.append(p.stem)
    for file in copied_file:
        if file in include_dict['File']:
            for folder in include_dict['File'][file]:
                shutil.copytree(folder,
                                folders['macro'] / folder.parts[-1], dirs_exist_ok=True)
                for p in sorted(pathlib.Path(folder).glob('**/*.*')):
                    if p.is_file():
                        copied_file.append(p.stem)
    return copied_file


def CopyUsedFile(hsf_root, folders, copied_file) -> dict:
    filedepends_list = []
    paths = sorted(pathlib.Path(folders['hsf']).glob('**/*.gdl'))
    for file in paths:
        f = open(file, 'r', encoding='utf-8')
        for line in f:
            nlistl = re.findall(r'[^"]+\.txt', line, re.IGNORECASE)
            if len(nlistl) > 0:
                filedepends_list.extend(nlistl)
            nlistl = re.findall(r'[^"]+\.png', line, re.IGNORECASE)
            if len(nlistl) > 0:
                filedepends_list.extend(nlistl)
        f.close()
    for file in list(set(filedepends_list)):
        if '.' in file:
            filename = file.split('.')[0]
        else:
            filename = file
        if filename not in copied_file:
            paths = sorted(pathlib.Path(hsf_root).glob(f'**/{file}'))
            if len(paths) > 0:
                shutil.copy(paths[0], folders['macro'])
                copied_file.append(file)
    return copied_file


hsf_root = workspaceRootFolder / 'hsf'

configFile = open(configPath, encoding="utf-8")
configData = json.load(configFile)
configFile.close()

DownloadLP_XMLConverters(configData, versionList)
folderpath = PrepareDirectories(configData, versionList)
hsf_dict = GetGUIDDict(hsf_root)
include_dict = GetIncludeFileDict(hsf_root)

for lcfName in configData["Package"]:
    folders = folderpath[lcfName]
    config = configData["Package"][lcfName]
    copied_file = CopyHSF(config, folders, hsf_dict)
    copied_file = CopyIncludeFolder(
        folders, include_dict, copied_file, lcfName)
    copied_file = CopyUsedFile(hsf_root, folders, copied_file)
    for i in range(40):
        copied_file, is_all = CopyMacro(config, folders, hsf_dict, copied_file)
        if is_all:
            break
    DecodeGDL(folders['hsf'], "utf-8", "utf-8-sig")
    for version in versionList:
        if CreateGSM(version, folders):
            CreateLCF(version, folders)
    DecodeGDL(folders['hsf'], "utf-8-sig", "utf-8")
