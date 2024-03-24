from tqdm import tqdm
import os
from pathlib import Path
import time

import numpy as np
import pandas as pd

import requests

def get_altitude(longitude: float, latitude: float) -> float:

    addr = 'https://api.opentopodata.org/v1/mapzen'
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


def add_altitude_to_df_from_api(dataframe_input_file: Path, dataframe_output_file: Path, data_environmental_dir:Path) -> None:

    # Get the 'hotspot_id' from the csv file
    df_input = pd.read_csv(dataframe_input_file)
    df_output = df_input.copy()

    hotspot_ids = df_input['hotspot_id'].values
    
    progress_bar = tqdm(hotspot_ids)

    for hotspot_id in progress_bar:
        # Change the tqdm bar description
        progress_bar.set_description(f"Processing {hotspot_id}")

        # # Get the latitude and longitude of the hotspot_id
        lon = df_input[df_input['hotspot_id'] == hotspot_id]['lon'].values[0]
        lat = df_input[df_input['hotspot_id'] == hotspot_id]['lat'].values[0]

        # Compute the altitude
        altitude = get_altitude(lon, lat)

        if altitude == -1000:
            print(f"Could not get altitude for {hotspot_id}")
            continue

        # Add altitude to dataframe
        df_output.loc[df_output['hotspot_id'] == hotspot_id, 'altitude'] = altitude

        # Pause for 1 second
        # This is to avoid sending too many requests to the API
        time.sleep(1.0)

    df_output.to_csv(dataframe_output_file, index=False)


def add_altitude_to_df_from_npy(dataframe_input_file: Path, data_environmental_dir:Path) -> None:

    # Get the 'hotspot_id' from the csv file
    df_input = pd.read_csv(dataframe_input_file)
    df_output = df_input.copy()

    hotspot_ids = df_input['hotspot_id'].values
    
    progress_bar = tqdm(hotspot_ids)

    for hotspot_id in progress_bar:
        # Change the tqdm bar description
        progress_bar.set_description(f"Processing {hotspot_id}")

        # # Get the latitude and longitude of the hotspot_id

        # Load the npy file from data_environmental_dir
        npy_file = data_environmental_dir / f"{hotspot_id}.npy"
        hotspot_data = np.load(npy_file)

        altitude = hotspot_data[-1, 0, 0]


        if altitude == -1000:
            print(f"Could not get altitude for {hotspot_id}")
            continue

        # Add altitude to dataframe
        df_output.loc[df_output['hotspot_id'] == hotspot_id, 'altitude'] = altitude


    df_output.to_csv(dataframe_output_file, index=False)



if __name__ == "__main__":

    dataframe_input_file = Path("/home/fidaa/Documents/Github/SatBird/data/California/valid_split.csv")
    dataframe_output_file = Path("/home/fidaa/Documents/Github/SatBird/data/California/valid_alt_split.csv")
    environmental_data_dir = Path("/home/fidaa/Documents/Github/SatBird/data/California/environmental_altitude")

    add_altitude_to_df_from_api(dataframe_input_file, dataframe_output_file)

    add_altitude_to_df_from_npy(environmental_data_dir, environmental_data_dir)
