import os
import pathlib
import platform
import subprocess
import sys
import urllib.parse
import urllib.request
import zipfile
import requests
API_ENDPOINT = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'


def _extract_filename_yadisk_link(direct_link: str):
    for chunk in direct_link.strip().split('&'):
        if chunk.startswith('filename='):
            return chunk.split('=')[1]
    return None


def DownloadFromYadisk(url: str, dest: str) -> str:
    pk_request = requests.get(API_ENDPOINT.format(url))
    direct_link = pk_request.json().get('href')
    if direct_link:
        filename = _extract_filename_yadisk_link(direct_link)
        filePath = os.path.join(dest, filename)
        download = requests.get(direct_link)
        with open(filePath, 'wb') as out_file:
            out_file.write(download.content)
        print('Downloaded "{}" to "{}"'.format(url, filePath))
        return filePath
    else:
        print('Failed to download "{}"'.format(url))
        return None


def DownloadAndUnzip(url: str, dest: str):
    if 'disk.yandex' in url:
        filePath = DownloadFromYadisk(url, dest)
        fileName = filePath.split('/')[-1]
    else:
        fileName = url.split('/')[-1]
        filePath = pathlib.Path(dest, fileName)
        if filePath.exists():
            return
        print(f'Downloading {fileName}')
        urllib.request.urlretrieve(url, filePath)

    print(f'Unzipping {fileName}')
    if platform.system() == 'Windows':
        with zipfile.ZipFile(filePath, 'r') as zip:
            zip.extractall(dest)
    elif platform.system() == 'Darwin':
        subprocess.call([
            'unzip', '-qq', filePath,
            '-d', dest
        ])


if __name__ == "main":
    url = sys.argv[1]
    dest = sys.argv[2]
    DownloadAndUnzip(url, dest)
    sys.exit(0)
