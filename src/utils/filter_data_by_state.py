import shutil
import pandas as pd
from pathlib import Path
from tqdm import tqdm

DATA_PATH = Path('../../data')
COUNTRY_PATH = Path("")

def get_country_database() -> pd.DataFrame:

    global COUNTRY_PATH

    # Ask the use to choose between 'USA Summer', 'USA Winter' and 'Kenya'

    print("Please choose between 'USA Summer' [1], 'USA Winter' [2] and 'Kenya' [3]")

    database = int(input("Enter the database: "))

    if database == 1:
        COUNTRY_PATH = DATA_PATH / 'USA_summer'
        path_csv = Path(COUNTRY_PATH / 'all_summer_hotspots_final.csv')
        if not path_csv.exists():
            raise FileNotFoundError(f"File {path_csv} not found")
        df = pd.read_csv(path_csv)

    elif database == 2:
        COUNTRY_PATH = DATA_PATH / 'USA_winter'
        path_csv = Path(COUNTRY_PATH / 'all_winter_hotspots_final.csv')
        if not path_csv.exists():
            raise FileNotFoundError(f"File {path_csv} not found")
        df = pd.read_csv(path_csv)

    elif database == 3:
        COUNTRY_PATH = DATA_PATH / 'kenya'
        path_csv = Path(COUNTRY_PATH / 'allkenya_hotspots_splits_final.csv')
        if not path_csv.exists():
            raise FileNotFoundError(f"File {path_csv} not found")
        df = pd.read_csv(path_csv)

    else:
        raise ValueError(f"Invalid input: {database}")
    
    return df


def get_state_database(df_country: pd.DataFrame) -> pd.DataFrame:

    # Get all the 'state' columns from the dataframe
    states = df_country['state'].unique()

    # Ask the user to choose a state from the list of states
    print(f"Please choose the states, separated by a comma, from the list of states:")
    print(states)

    states = input("Enter the state: ")

    states = states.split(',')
    states = [s.strip() for s in states]
    print(states)
    # Filter the dataframe by the chosen state
    df_filtered = df_country[df_country['state'].isin(states)]

    return df_filtered


def save_state(df_state: pd.DataFrame) -> None:

    global COUNTRY_PATH

    country = COUNTRY_PATH.name

    state = '_'.join(df_state['state'].unique())
    print(state)
    #state = df_state['state'].unique()[0]   

    # Create a new folder for the chosen state
    state_path = Path(DATA_PATH / state)
    if not state_path.exists():
        state_path.mkdir(parents=True)

    # 1. Save the filtered dataframe to a new csv file
    state_csv = state_path / f'{state}_hotspots.csv'
    df_state.to_csv(state_csv, index=False)

    # 2. Get the 'hotspot_id' column from the filtered dataframe
    hotspot_ids = df_state['hotspot_id'].unique()

    # 3. Filter 'all_summer_hotspots_final.csv' and save in state_path
    all_hotspots_path = Path(COUNTRY_PATH / 'all_summer_hotspots_final.csv')
    if not all_hotspots_path.exists():
        raise FileNotFoundError(f"File {all_hotspots_path} not found")
    all_hotspots_df = pd.read_csv(all_hotspots_path)

    all_hotspots_df = all_hotspots_df[all_hotspots_df['hotspot_id'].isin(hotspot_ids)]

    all_hotspots_path = state_path / f'all_{state}_hotspots_final.csv'
    all_hotspots_df.to_csv(all_hotspots_path, index=False)

    # 4. Copy the file called 'all_species.txt' from COUNTRY_PATH to state_path
    all_species = Path(COUNTRY_PATH / 'species_list.txt')
    if not all_species.exists():
        raise FileNotFoundError(f"File {all_species} not found")
    shutil.copy(all_species, state_path)

    # 5. Filter the images and the images_visual and save in state_path
    copy_images(COUNTRY_PATH, state_path, hotspot_ids)

    # 6. Filter the environmental variables and save in state_path
    copy_environmental(COUNTRY_PATH, state_path, hotspot_ids)

    # 7. Filter the targets variables and save in state_path
    copy_targets(COUNTRY_PATH, state_path, hotspot_ids)

    # 8. Filter the range maps variables and save in state_path
    copy_range_maps(COUNTRY_PATH, state_path, hotspot_ids)

    # 9. Filter the train/valid/test split csv files and save in state_path
    copy_splits(COUNTRY_PATH, state_path, hotspot_ids)

    # 10. Copy the folder called 'stats' from COUNTRY_PATH to state_path
    copy_stats(COUNTRY_PATH, state_path)


def copy_images(source: Path, destination: Path, hotspot_ids: list[str]) -> None:
    
    # 3.1. Create the 'images' directory for the chosen state
    images_path = destination / 'images'
    if not images_path.exists():
        images_path.mkdir()

    # 3.2. Copy the images called {hotspot_id}.tif from COUNTRY_PATH/images to state_path/images
    for hotspot_id in tqdm(hotspot_ids, desc="images"):
        src_image = Path(source / 'images' / f'{hotspot_id}.tif')
        dest_image = images_path / f'{hotspot_id}.tif'
        if src_image.exists():
            shutil.copy(src_image, dest_image)

    # Repeat 3.1 and 3.2 with the directory called 'images_visual'
    images_visual_path = destination / 'images_visual'
    if not images_visual_path.exists():
        images_visual_path.mkdir()

    for hotspot_id in tqdm(hotspot_ids, desc="images_visual"):
        src_image = Path(source / 'images_visual' / f'{hotspot_id}_visual.tif')
        dest_image = images_visual_path / f'{hotspot_id}_visual.tif'
        if src_image.exists():
            shutil.copy(src_image, dest_image)
    


def copy_environmental(source: Path, destination: Path, hotspot_ids: list[str]) -> None:
    # Repeat 3.1 and 3.2 with the directory called 'environmental'
    environmental_path = destination / 'environmental'
    if not environmental_path.exists():
        environmental_path.mkdir()

    for hotspot_id in tqdm(hotspot_ids, desc="environmental"):
        src_image = Path(source / 'environmental' / f'{hotspot_id}.npy')
        dest_image = environmental_path / f'{hotspot_id}.npy'
        if src_image.exists():
            shutil.copy(src_image, dest_image)


def copy_targets(source: Path, destination: Path, hotspot_ids: list[str]) -> None:
    # Repeat 3.1 and 3.2 with the directory called 'targets'
    targets_path = destination / 'targets'
    if not targets_path.exists():
        targets_path.mkdir()

    for hotspot_id in tqdm(hotspot_ids, desc="targets"):
        src_image = Path(source / 'targets' / f'{hotspot_id}.json')
        dest_image = targets_path / f'{hotspot_id}.json'
        if src_image.exists():
            shutil.copy(src_image, dest_image)
    

def copy_range_maps(source: Path, destination: Path, hotspot_ids: list[str]) -> None:
    # Load the file called 'range_maps.pkl' from COUNTRY_PATH
    range_maps_path = Path(source / 'range_maps.pkl')
    if not range_maps_path.exists():
        raise FileNotFoundError(f"File {range_maps_path} not found")
    range_maps_df = pd.read_pickle(range_maps_path)
     
    # filter the 'hotspot_id' column by the chosen state
    range_maps_df = range_maps_df[range_maps_df['hotspot_id'].isin(hotspot_ids)]

    # Save the filtered dataframe to a new file called 'range_maps.pkl' in state_path
    range_maps_path = destination / 'range_maps.pkl'
    range_maps_df.to_pickle(range_maps_path)


def copy_splits(source: Path, destination: Path, hotspot_ids: list[str]) -> None:

    list_files = ['train_split.csv', 'valid_split.csv', 'test_split.csv']
    for file in list_files:
        # Load the file called 'train_split.csv' from COUNTRY_PATH
        df_path = Path(source / file)
        if not df_path.exists():
            raise FileNotFoundError(f"File {df_path} not found")
        df = pd.read_csv(df_path)

        # filter the 'hotspot_id' column by the chosen state
        df = df[df['hotspot_id'].isin(hotspot_ids)]

        # Save the filtered dataframe to a new file called 'train_split.csv' in state_path
        df_path = destination / file
        df.to_csv(df_path, index=False)


def copy_stats(source: Path, destination: Path) -> None:
    # Copy the folder called 'stats' from COUNTRY_PATH to state_path
    stats = Path(source / 'stats')
    if not stats.exists():
        raise FileNotFoundError(f"File {stats} not found")
    shutil.copytree(stats, destination / 'stats')
    




if __name__ == "__main__":

    try:
        df_country = get_country_database()
    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)


    df_state = get_state_database(df_country)

    save_state(df_state)





