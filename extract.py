import os
import sys
from pathlib import Path, PosixPath, WindowsPath
from datetime import datetime

import exifread
import pandas as pd
from tqdm import tqdm

import folder_selector

RAW_EXT = 'CR2'

def file_list(maindir):
    files = []
    with os.scandir(maindir) as scan:
        for item in scan:
            name = item.name
            if name.endswith(RAW_EXT) and os.path.exists(item.path.replace(RAW_EXT, 'Info.txt')):
                files.append(name.split('.')[0])
        if len(files) == 0:
            raise ValueError('No .Info.txt files found in the folder!')
    return files


def read_exif(file_path):
    with open(file_path.parent / (file_path.name + '.' + RAW_EXT), 'rb') as f:
        exif_tags = exifread.process_file(f, stop_tag='EXIF DateTimeOriginal', details=False)
    return exif_tags


def parse_exif(exif_tags):
    exif_date_str = str(exif_tags['EXIF DateTimeOriginal'])
    date, time = exif_date_str.split()
    date = date.replace(':', '-')
    photo_datetime = datetime.fromisoformat(date+'T'+time)
    return photo_datetime


def read_dss_info(file_path):
    with open(file_path.parent / (file_path.name + '.Info.txt'), 'r') as f:
        text = f.readlines()
    return text


def parse_dss_info(text):
    keys = ['OverallQuality', 'SkyBackground', 'NrStars']
    vals = []
    for line in text:
        for key in keys:
            if key in line:
                vals.append(line.split('=')[-1].strip())
    return dict(zip(keys, vals))


def merge_dss_exif(file_path):
    """
    Create a dictionary containing all the information from DSS info file
    and EXIF date information for one frame.
    """
    dss_info = parse_dss_info(read_dss_info(file_path))
    exif_date = parse_exif(read_exif(file_path))
    dss_info.update({'datetime':exif_date})
    return dss_info


def iterate_over_files(path):
    files = file_list(path)
    data = []
    for item in tqdm(files):
        data.append({'filename':item, **merge_dss_exif(path / item)})
    return data


def convert_to_dataframe(data):
    df = pd.DataFrame.from_records(data)
    df = df.rename(columns={'OverallQuality':'quality', 'SkyBackground':'background', 'NrStars':'nstars'})
    return df


def extract_and_save(maindir):
    """
    maindir is the folder that contains the folders for lights, darks etc.
    """
    if not type(maindir) in [PosixPath, WindowsPath]:
        maindir = Path(maindir)
    lights_folder = maindir / 'light'
    dataframe = convert_to_dataframe(iterate_over_files(lights_folder))
    os.makedirs(maindir / 'dss_plot', exist_ok=True)
    dataframe.to_csv(maindir / 'dss_plot' / 'dss_quality_data.csv')

if __name__ == '__main__':
    # maindir = Path('/Volumes/Transcend/astrophotography/2021-12-09_cygnus_loop/')
    # maindir = Path('/Volumes/Erol1/astrophotography/2021-12-09_cygnus_loop/')
    # data = convert_to_dataframe(iterate_over_files(maindir))
    if len(sys.argv) == 2:
        selected_folder = sys.argv[1]
    else:
        selected_folder = folder_selector.folder_selector()
    extract_and_save(selected_folder)

