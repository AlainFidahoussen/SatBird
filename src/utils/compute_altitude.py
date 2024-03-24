from tqdm import tqdm
import os
from pathlib import Path
import time

import numpy as np
import pandas as pd

import requests

def get_altitude(longitude: float, latitude: float) -> float:

    addr = 'https://api.opentopodata.org/v1/mapzen'
    # addr = 'http://localhost:5000/v1/test-dataset'
    r = requests.get(f'{addr}?locations={latitude},{longitude}')
    r = r.json()

    if r['status'] == 'OK':
        altitude = r['results'][0]['elevation']
        return altitude

    else:
        return -1000

def get_files_to_process(dir_src: Path, dir_dst: Path) -> list[str]:

    if not dir_src.exists():
        raise FileNotFoundError(f"{dir_src} does not exist")

    # Create the destination directory if it does not exist
    if not dir_dst.exists():
        dir_dst.mkdir(parents=True, exist_ok=True)

    # list all npy files in dir_source
    files = sorted(os.listdir(dir_source))
    print(f'Number of files to process: {len(files)}')

    # list all npy files in dir_destination
    files_done = sorted(os.listdir(dir_destination))
    print(f'Number of files already processed: {len(files_done)}')

    # Get the list of files that have not been processed yet
    files_to_process = list(set(files) - set(files_done))
    print(f'Number of files to process: {len(files_to_process)}')

    return files_to_process


def add_altitude_to_data(dir_src: Path, dir_dst: Path, csv_file: Path) -> None:

    files_to_process = get_files_to_process(dir_src, dir_dst)

    # Get the 'hotspot_id' from the csv file
    df = pd.read_csv(csv_file)
    
    progress_bar = tqdm(files_to_process)
    for file in progress_bar:

        # Change the tqdm bar description
        progress_bar.set_description(f"Processing {file}")

        src_file = dir_source / file

        # Load the numpy array
        data = np.load(src_file)

        # Get the name of the file, which is the hotspot_id
        hotspot_id = file.split("/")[-1].split(".")[0]

        # Get the latitude and longitude of the hotspot_id
        lon = df[df['hotspot_id'] == hotspot_id]['lon'].values[0]
        lat = df[df['hotspot_id'] == hotspot_id]['lat'].values[0]

        altitude = get_altitude(lon, lat)

        if altitude == -1000:
            print(f"Could not get altitude for {hotspot_id}")
            continue

        # Add altitude to data
        # data size is (num_rasters, size, size)
        # Add altitude as a new raster
        data_with_altitude = np.concatenate((data, np.ones((1, data.shape[1], data.shape[2])) * altitude), axis=0)

        # Save the new data with altitude
        np.save(dir_dst / f"{hotspot_id}.npy", data_with_altitude)

        # Pause for 1 second
        # This is to avoid sending too many requests to the API
        time.sleep(1)



if __name__ == "__main__":
    dir_source = Path("/home/fidaa/Documents/Github/SatBird/data/California/environmental")
    dir_destination = Path("/home/fidaa/Documents/Github/SatBird/data/California/environmental_2")
    csv_file = Path("/home/fidaa/Documents/Github/SatBird/data/California/California_hotspots.csv")

    add_altitude_to_data(dir_source, dir_destination, csv_file)
