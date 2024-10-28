import json
import pathlib
import string
from colorama import init
from lxml import etree
from download_and_unzip import DownloadAndUnzip
import shutil
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
import shlex
import re
import sys
import errno
import os
import stat


def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


def run_shell_command(command_line: list) -> bool:
    command_line = " ".join(command_line)
    command_line_args = shlex.split(command_line)
    print(f'Start - {command_line}')
    try:
        command_line_process = Popen(
            command_line_args,
            stdout=PIPE,
            stderr=STDOUT,
        )
        for line in command_line_process.stdout:
            log_txt = line.decode('utf-8', errors='ignore')
            if 'Transcode' not in log_txt and 'Copy' not in log_txt and 'Revert' not in log_txt and 'Convert' not in log_txt:
                print(log_txt)
    except (OSError, CalledProcessError) as exception:
        print(exception)
        return False
    print(f'Done - {command_line}')
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


def CreateGSM(folders: dict):
    gsm_folder = folders['GSM']
    xml_folder = folders['XML_TEMP']
    devKit = folders['DEVKIT']
    param = [f'"{devKit}"', 'x2l -l CYR',
             f'"{xml_folder}"', f'"{gsm_folder}"']
    return run_shell_command(param)


def CreateLCF(folders: dict):
    gsm_folder = folders['GSM']
    lcf_name = folders['LCF']
    devKit = folders['DEVKIT']
    param = [f'"{devKit}"', 'createcontainer',
             f'"{lcf_name}"', '-compress 9',  f'"{gsm_folder}"']
    return run_shell_command(param)


def DownloadLP_XMLConverters(configData: dict):
    """
    Проверяет наличие LP_XMLConverter для версий, заданных в configData

    Args:
        configData (dict): Словарь с настройками
    """
    version = configData['MaxVersion']
    toolfolder = pathlib.Path(__file__).parent.absolute()
    devKitFolder = toolfolder / 'LP_XMLConverter'
    if not devKitFolder.exists():
        devKitFolder.mkdir(parents=True)
    devKitFolderVersion = toolfolder / \
        'LP_XMLConverter' / f'LP_XMLConverter{version}'
    configData['LP_XMLConverter']['path'] = {}
    if not devKitFolderVersion.exists():
        print(f"Download LP_XMLConverter {version}")
        DownloadAndUnzip(
            configData['LP_XMLConverter'][version], devKitFolder)
        if not devKitFolderVersion.exists():
            print(f"ERROR, folder for LP_XMLConverter {version} not exists")
            return False
        else:
            configData['LP_XMLConverter']['path'][version] = devKitFolderVersion.absolute()
    else:
        print(f"LP_XMLConverter {version} exist")
        configData['LP_XMLConverter']['path'][version] = devKitFolderVersion
    for version in configData["VersionList"]:
        if version in configData['LP_XMLConverter']:
            toolfolder = pathlib.Path(__file__).parent.absolute()
            devKitFolder = toolfolder / 'LP_XMLConverter'
            if not devKitFolder.exists():
                devKitFolder.mkdir(parents=True)
            devKitFolderVersion = toolfolder / \
                'LP_XMLConverter' / f'LP_XMLConverter{version}'
            if not devKitFolderVersion.exists():
                print(f"Download LP_XMLConverter {version}")
                DownloadAndUnzip(
                    configData['LP_XMLConverter'][version], devKitFolder)
                if not devKitFolderVersion.exists():
                    print(
                        f"ERROR, folder for LP_XMLConverter {version} not exists")
                    return False
                else:
                    configData['LP_XMLConverter']['path'][version] = devKitFolderVersion.absolute(
                    )
            else:
                print(f"LP_XMLConverter {version} exist")
                configData['LP_XMLConverter']['path'][version] = devKitFolderVersion.absolute(
                )
    return True


def prepfolder(folder):
    if folder.exists():
        shutil.rmtree(folder, ignore_errors=False,
                      onerror=handleRemoveReadonly)
    folder.mkdir(parents=True)
    return folder


def PrepareDirectories(configData: dict, gdl_root: pathlib.WindowsPath):
    """
    Создание папок для пакетов библиотек

    Args:
        configData (dict): Словарь с настройками
        gdl_root (pathlib.WindowsPath): Путь к корневой папке gdl
    """
    workspaceRootFolder = gdl_root.parent  # Путь к корневой папке
    # Создание временных папок для hsf различных версий
    configData['HSF_GIT'] = {}
    configData['XML_ROOT'] = {}
    configData['LCF'] = {}
    configData['GSM'] = gdl_root
    configData['TOOL'] = pathlib.Path(
        __file__).parent.absolute() / 'LP_XMLConverter'
    for version in configData["VersionList"]:
        configData['XML_ROOT'][version] = prepfolder(
            workspaceRootFolder / f"xml_temp_{version}")
    for lcfName in configData["Package"]:
        lcf_root = workspaceRootFolder / lcfName  # Путь к папке пакета
        configData['LCF'][lcfName] = {}
        # Путь к hsf версии для Git (декодированного)
        configData['HSF_GIT'][lcfName] = prepfolder(lcf_root / f'hsf')
        for version in configData["VersionList"]:
            is_skip = False
            if "SkipVersion" in configData['Package'][lcfName]:
                if version in configData['Package'][lcfName]["SkipVersion"]:
                    is_skip = True
            if not is_skip:
                # Путь к версии пакета
                buildFolder = lcf_root / version
                if not buildFolder.exists():
                    buildFolder.mkdir(parents=True)
                # Путь к hsf версии пакета
                xml_folder = prepfolder(buildFolder / f'xml')
                # Путь к макросам
                macro_folder = prepfolder(xml_folder / '_macro_')
                # Путь к gsm
                gsm_folder = prepfolder(buildFolder / 'gsm')
                lcf_name = lcfName+version+'.lcf'
                # Словарь с папками
                configData['LCF'][lcfName][version] = {}
                configData['LCF'][lcfName][version]['XML_TEMP'] = xml_folder
                configData['LCF'][lcfName][version]['MACRO'] = macro_folder
                configData['LCF'][lcfName][version]['GSM'] = gsm_folder
                configData['LCF'][lcfName][version]['LCF'] = buildFolder / lcf_name
                configData['LCF'][lcfName][version]['XML_ROOT'] = configData['XML_ROOT'][version]
                configData['LCF'][lcfName][version]['DEVKIT'] = configData['TOOL'] / \
                    f'LP_XMLConverter{version}'/'WIN'/'LP_XMLConverter.EXE'


def GetGUID(filename: pathlib.WindowsPath) -> str:
    """
    Получение GUID объекта

    Args:
        filename (pathlib.WindowsPath): Путь к папке с hsf объекта
    Returns:
        str: GUID объекта
    """
    GUIDelem = None
    try:
        parser = etree.XMLParser(strip_cdata=False)
        root = etree.parse(str(filename), parser)
        croot = root.getroot()
        GUIDelem = croot.attrib['MainGUID']
    except Exception as e:
        print(f'В файле {filename} возникла ошибка при получении GUID')
        print(e)
    return GUIDelem


def GetCalledMacro(filename: pathlib.WindowsPath) -> dict:
    """
    Получение словаря с вызываемыми макросами

    Args:
        filename (pathlib.WindowsPath): Путь к папке с hsf объекта, в котором нужно найти ссылки на макросы
    Returns:
        dict: Словарь с вызываемыми макросами в формате [Имя] = GUID
    """
    macro_dict = {}
    try:
        parser = etree.XMLParser(strip_cdata=False)
        root = etree.parse(str(filename), parser)
        croot = root.getroot()
        macros = croot.find('CalledMacros')
        if macros is not None:
            for macro in macros:
                namemacro = macro.find('MName')
                if namemacro is not None:
                    guidemacro = macro.find('MainGUID')
                    if guidemacro is not None:
                        guidemacro = guidemacro.text
                        namemacro = namemacro.text.strip('"')
                        if namemacro not in macro_dict:
                            macro_dict[namemacro] = guidemacro
        subtypes = croot.find('Ancestry')
        if subtypes is not None:
            for subtype in subtypes:
                guidesubtype = subtype.text
                if guidesubtype not in macro_dict:
                    macro_dict[guidesubtype] = guidesubtype
    except Exception as e:
        print(f'В файле {filename} возникла ошибка при поиске макросов')
    return macro_dict


def GetIncludeFileDict(xml_folder: pathlib.WindowsPath) -> dict:
    include_dict = {}
    paths = sorted(pathlib.Path(xml_folder).glob('**/include.json'))
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


def GetGUIDDict(xml_folder: pathlib.WindowsPath) -> dict:
    xml_dict = {}
    xml_dict['Name'] = {}
    xml_dict['GUID'] = {}
    paths = sorted(pathlib.Path(xml_folder).glob('**/*.xml'))
    for file in paths:
        filename = file.absolute()
        name = file.stem
        GUIDelem = GetGUID(file)
        if GUIDelem is not None:
            xml_dict['Name'][name] = {
                'filename': filename, 'GUID': GUIDelem, 'name': name}
            xml_dict['GUID'][GUIDelem] = {
                'filename': filename, 'GUID': GUIDelem, 'name': name}

    return xml_dict


def GetMacroDict(xml_folder: pathlib.WindowsPath) -> dict:
    macro_dict = {}
    paths = sorted(pathlib.Path(xml_folder).glob('**/*.xml'))
    for file in paths:
        filename = file.absolute()
        macro_dict = {**macro_dict, **GetCalledMacro(filename)}
    return macro_dict


def CopyXML(config: dict, folders: dict, xml_dict: dict) -> list:
    copied_file = []
    for hsf in config["Include"]:
        if hsf in xml_dict['Name']:
            fname = xml_dict['Name'][hsf]['filename'].name
            shutil.copy(xml_dict['Name'][hsf]['filename'],
                        folders['XML_TEMP'] / fname)
            copied_file.append(hsf)
        else:
            print(f'Не найден объект {hsf}')
    return copied_file


def find(xml_dict: dict, k, v):
    if k in xml_dict['Name']:
        return xml_dict['Name'][k]['name'], xml_dict['Name'][k]['GUID'], True
    if k in xml_dict['GUID']:
        return xml_dict['GUID'][k]['name'], xml_dict['GUID'][k]['GUID'], True
    if v in xml_dict['Name']:
        return xml_dict['Name'][v]['name'], xml_dict['Name'][v]['GUID'], True
    if v in xml_dict['GUID']:
        return xml_dict['GUID'][v]['name'], xml_dict['GUID'][v]['GUID'], True
    print(f'Не найден макрос {k}, GUID {v}')
    return "", "", False


def CopyMacro(config: dict, folders: dict, xml_dict: dict, copied_file: list):
    all_macro_dict = GetMacroDict(folders['XML_TEMP'])
    include_macro = {}
    for k, v in all_macro_dict.items():
        name, GUID, findflag = find(xml_dict, k, v)
        if findflag and name not in config["Ignore"] and name not in copied_file:
            include_macro[name] = GUID
    if len(include_macro) == 0:
        print('Макросы скопированы')
        return copied_file, True
    for name_macro in include_macro.keys():
        fname = xml_dict['Name'][name_macro]['filename'].name
        shutil.copy(xml_dict['Name'][name_macro]['filename'],
                    folders['MACRO'] / fname)
        print(f'Скопирован макрос {name_macro}')
        copied_file.append(name_macro)
    return copied_file, False


def CopyIncludeFolder(folders: dict, include_dict: dict, copied_file: list, lcfName: str) -> list:
    if lcfName in include_dict['Package']:
        for folder in include_dict['Package'][lcfName]:
            shutil.copytree(folder,
                            folders['MACRO'] / folder.parts[-1], dirs_exist_ok=True)
            for p in sorted(pathlib.Path(folder).glob('**/*.*')):
                if p.is_file():
                    copied_file.append(p.stem)
    for file in copied_file:
        if file in include_dict['File']:
            for folder in include_dict['File'][file]:
                shutil.copytree(folder,
                                folders['MACRO'] / folder.parts[-1], dirs_exist_ok=True)
                for p in sorted(pathlib.Path(folder).glob('**/*.*')):
                    if p.is_file():
                        copied_file.append(p.stem)
    return copied_file


def CopyUsedFile(folders: dict, copied_file: list) -> list:
    filedepends_list = []
    XML_ROOT = folders['XML_ROOT']
    paths = sorted(pathlib.Path(folders['XML_TEMP']).glob('**/*.gdl'))
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
            paths = sorted(pathlib.Path(XML_ROOT).glob(f'**/{file}'))
            if len(paths) > 0:
                shutil.copy(paths[0], folders['MACRO'])
                copied_file.append(file)
    return copied_file


def ConvertGDL2AllXML(configData: dict):
    for version in configData["VersionList"]:
        if version in configData['LP_XMLConverter']:
            ConvertGDL2XML(configData, version)


def ConvertGDL2HSF(configData: dict, lcfName: string, version: string):
    gdl_root = configData['LCF'][lcfName][version]['GSM']
    hsf = configData['HSF_GIT'][lcfName]
    devKit = configData['LCF'][lcfName][version]['DEVKIT']
    param = [f'"{devKit}"', f'l2hsf -l CYR -compatibility {version}',
             f'"{gdl_root}"', f'"{hsf}"']
    return run_shell_command(param)


def ConvertAllLCF(configData: dict):
    paths = sorted(pathlib.Path(configData['GSM']).glob('**/*.lcf'))
    for file in paths:
        ConvertLCF(configData, file)


def ConvertLCF(configData: dict, fname):
    gdl_root = configData['GSM']
    lcf_folder = prepfolder(gdl_root / 'LCF2GSM' / fname.stem)
    maxversion = configData['MaxVersion']
    devKit = configData['TOOL'] / \
        f'LP_XMLConverter{maxversion}'/'WIN'/'LP_XMLConverter.EXE'
    param = [f'"{devKit}"', 'extractcontainer',
             f'"{fname}"', f'"{lcf_folder}"']
    return run_shell_command(param)


def ConvertGDL2XML(configData: dict, version: string):
    gdl_root = configData['GSM']
    XML_ROOT = configData['XML_ROOT'][version]
    maxversion = configData['MaxVersion']
    devKit = configData['TOOL'] / \
        f'LP_XMLConverter{maxversion}'/'WIN'/'LP_XMLConverter.EXE'
    param = [f'"{devKit}"', f'l2x -l CYR -compatibility {version}',
             f'"{gdl_root}"', f'"{XML_ROOT}"']
    return run_shell_command(param)


def run(configPath: pathlib.WindowsPath, gdl_root: pathlib.WindowsPath):
    configFile = open(configPath, encoding="utf-8")
    configData = json.load(configFile)
    configFile.close()
    if 'MaxVersion' not in configData:
        configData['MaxVersion'] = '27'
    if not DownloadLP_XMLConverters(configData):
        return 0
    if 'AddSourse' in configData:
        addsourse = prepfolder(gdl_root / 'AddSourse_temp')
        i = 0
        for source in configData['AddSourse']:
            folder = pathlib.Path(source)
            if folder.is_dir():
                i += 1
                dst = addsourse / f'{folder.name}_{i}'
                shutil.copytree(folder,
                                dst, dirs_exist_ok=True)
    PrepareDirectories(configData, gdl_root)
    ConvertAllLCF(configData)
    ConvertGDL2AllXML(configData)

    for version in configData["VersionList"]:
        if version in configData['LP_XMLConverter']:
            XML_ROOT = configData['XML_ROOT'][version]
            xml_dict = GetGUIDDict(XML_ROOT)
            include_dict = GetIncludeFileDict(XML_ROOT)
            if len(include_dict) < 1:
                print(f'Не найден список файлов для {XML_ROOT}')
            for lcfName in configData["Package"]:
                is_skip = False
                if "SkipVersion" in configData['Package'][lcfName]:
                    if version in configData['Package'][lcfName]["SkipVersion"]:
                        is_skip = True
                if not is_skip:
                    folders = configData['LCF'][lcfName][version]
                    config = configData["Package"][lcfName]
                    if "Ignore" not in config:
                        config["Ignore"] = []
                    copied_file = CopyXML(config, folders, xml_dict)
                    if len(include_dict) > 0:
                        copied_file = CopyIncludeFolder(
                            folders, include_dict, copied_file, lcfName)
                    copied_file = CopyUsedFile(folders, copied_file)
                    for i in range(50):  # Пока не надоест)
                        copied_file, is_all = CopyMacro(
                            config, folders, xml_dict, copied_file)
                        if is_all:
                            break
                    if CreateGSM(folders):
                        CreateLCF(folders)
                        if not any(configData['HSF_GIT'][lcfName].iterdir()):
                            ConvertGDL2HSF(configData, lcfName, version)
                            DecodeGDL(configData['HSF_GIT']
                                      [lcfName], "utf-8-sig", "utf-8")
                    shutil.rmtree(folders['XML_TEMP'], ignore_errors=False,
                                  onerror=handleRemoveReadonly)
                    shutil.rmtree(folders['GSM'], ignore_errors=False,
                                  onerror=handleRemoveReadonly)

    for v, f in configData['XML_ROOT'].items():
        if f.exists():
            shutil.rmtree(f, ignore_errors=False,
                          onerror=handleRemoveReadonly)
    lcf_folder = gdl_root / 'LCF2GSM'
    if lcf_folder.exists():
        shutil.rmtree(lcf_folder, ignore_errors=False,
                      onerror=handleRemoveReadonly)
    add_folder = gdl_root / 'AddSourse_temp'
    if add_folder.exists():
        shutil.rmtree(add_folder, ignore_errors=False,
                      onerror=handleRemoveReadonly)
    print('Готово!')


def main(configPath=None, gdl_root=None):
    if configPath is None:
        configPath = pathlib.Path(__file__).parent.absolute() / 'config.json'
    if gdl_root is None:
        gdl_root = pathlib.Path(
            __file__).parent.parent.absolute() / 'gdl'
    run(configPath, gdl_root)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
