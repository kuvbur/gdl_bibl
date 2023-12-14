import json
import pathlib
from lxml import etree
from download_and_unzip import DownloadAndUnzip
import shutil
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
import shlex
configPath = "config.json"
versionList = ["23", "24", "25"]

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


def CreateGSM(version: str, gsm_folder: pathlib.WindowsPath, hsf_folder: pathlib.WindowsPath):
    """_summary_

    Args:
        version (str): _description_
        gsm_folder (pathlib.WindowsPath): _description_
        hsf_folder (pathlib.WindowsPath): _description_

    Returns:
        bool: _description_
    """
    devKit = workspaceRootFolder / 'LP_XMLConverter' / \
        f'LP_XMLConverter{version}'/'LP_XMLConverter.EXE'
    param = [f'"{devKit}"', 'hsf2l', f'"{hsf_folder}"', f'"{gsm_folder}"']
    return run_shell_command(param)


def CreateLCF(version: str, gsm_folder: pathlib.WindowsPath, lcf_name: str):
    """_summary_

    Args:
        version (str): _description_
        gsm_folder (pathlib.WindowsPath): _description_
        lcf_name (str): _description_

    Returns:
        bool: _description_
    """
    devKit = workspaceRootFolder / 'LP_XMLConverter' / \
        f'LP_XMLConverter{version}'/'LP_XMLConverter.EXE'
    param = [f'"{devKit}"', 'createcontainer',
             f'"{lcf_name}.lcf"', '-compress 9',  f'"{gsm_folder}"']
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
        DownloadAndUnzip(
            configData['LP_XMLConverter'][version], devKitFolder)


def DownloadLP_XMLConverters(configData: dict, versionList: str):
    """
    Скачивает LP_XMLConverter для всех заданных в настройках

    Args:
        configData (dict): Словарь с настройками
        versionList (list): Номеры версий
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
    for lcfName in configData["Package"]:
        buildFolder = workspaceRootFolder / lcfName
        if not buildFolder.exists():
            buildFolder.mkdir(parents=True)
        hsf_folder = buildFolder / f'hsf'
        if not hsf_folder.exists():
            hsf_folder.mkdir(parents=True)
        for version in versionList:
            gsm_folder = buildFolder / version / 'gsm'
            if not gsm_folder.exists():
                gsm_folder.mkdir(parents=True)
            lcf_folder = buildFolder / version / 'lcf'
            if not lcf_folder.exists():
                lcf_folder.mkdir(parents=True)


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
            if namemacro not in name_dict and namemacro is not None:
                guidemacro = macro.find('MainGUID')
                if guidemacro is not None:
                    guidemacro = guidemacro.text
                    namemacro = namemacro.text.strip('"')
                    macro_dict[namemacro] = guidemacro
    except Exception as e:
        print(f'Папка {filename} не содержит HSF объект')
    return macro_dict


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


def CopyMacro(exsist_file: list, macro_dict: dict, hsf_dict: dict) -> list:
    copied_file = []
    if len(macro_dict) == 0:
        return copied_file
    macro_folder = hsf_folder / '_macro_'
    if not macro_folder.exists():
        macro_folder.mkdir(parents=True)
    for name_macro in macro_dict.keys():
        if name_macro not in exsist_file:
            if name_macro in hsf_dict:
                shutil.copytree(hsf_dict[name_macro]['filename'], macro_folder /
                                name_macro, dirs_exist_ok=True)
                copied_file.append(name_macro)
            else:
                print(f'Не найден макрос {name_macro}')
    return copied_file


def CopyHSF(configData: dict, lcfName: str, hsf_dict: dict):
    """Копирует HSF объекты для пакета

    Args:
        configData (dict): Словарь с настройками
        lcfName (str): Имя пакета
        hsf_dict (dict): Словарь со всеми существующими объектами
    """
    hsf_folder = workspaceRootFolder / lcfName / 'hsf'
    copied_file = []
    for hsf in configData["Package"][lcfName]:
        if hsf in hsf_dict:
            shutil.copytree(hsf_dict[hsf]['filename'],
                            hsf_folder/hsf, dirs_exist_ok=True)
            copied_file.append(hsf)
        else:
            print(f'Не найден объект {hsf}')
    for i in range(10):
        macro_dict = GetMacroDict(hsf_folder)
        copied_macro = CopyMacro(copied_file, macro_dict, hsf_dict)
        copied_file.extend(copied_macro)


hsf_root = workspaceRootFolder / 'hsf'

configFile = open(configPath, encoding="utf-8")
configData = json.load(configFile)

DownloadLP_XMLConverters(configData, versionList)
PrepareDirectories(configData, versionList)
name_dict = GetGUIDDict(hsf_root)
for lcfName in configData["Package"]:
    buildFolder = workspaceRootFolder / lcfName
    hsf_folder = buildFolder / 'hsf'
    CopyHSF(configData, lcfName, name_dict)
    for version in versionList:
        gsm_folder = buildFolder / version / 'gsm'
        if CreateGSM(version, gsm_folder, hsf_folder):
            lcf_name = buildFolder / version / 'lcf' / lcfName
            CreateLCF(version, gsm_folder, lcf_name)
