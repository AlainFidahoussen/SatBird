from pathlib import Path
from typing import Any, Callable, Dict, Optional, Sequence

from src.dataset.geo import VisionDataset  #RasterDataset, 
#from dataset.sampler import RandomGeoSampler
from src.dataset.utils import load_file, is_image_file 
from torch.utils.data import DataLoader
from torch.nn import Module
from torch import Tensor
import numpy as np
from PIL import Image
import torch
#from rasterio.crs import CRS
import os
import pandas as pd
import time 

def get_path(df, index, band):
    
    return Path(df.iloc[index][band])

    #return (df.loc[df["hotspot_id"] == hotspot][band])

class Identity(Module):  # type: ignore[misc,name-defined]
    """Identity function used for testing purposes."""

    def forward(self, sample: Dict[str, Tensor]) -> Dict[str, Tensor]:
        """Do nothing.
        Args:
            sample: the input
        Returns:
            the unchanged input
        """
        return sample


class EbirdVisionDataset(VisionDataset):
    def __init__(self,  
                 df_paths,
                 bands,
                 split, 
                 transforms: Optional[Callable[[Dict[str, Any]], Dict [str, Any]]] = None,
                 mode : Optional[str] = "train")-> None:
        """
        df_paths: dataframe with paths to data for each hotspot
        bands: list of bands to include, anysubset of  ["r", "g", "b", "nir"] or  "rgb" (for image dataset) 
        mode : train|val|test
        """
        super().__init__()
        #self.datadir = datadir
        #all_images = os.listdir(self.datadir)
        self.df = df_paths
        self.total_images = len(df_paths)
        #maybe have to write get_transforms funciton ??
        self.transform = transforms
        self.bands = bands
        self.mode = mode
        self.split = split

        

    def __len__(self) -> int:
        # import pdb;pdb.set_trace()

        return self.total_images

    def __getitem__(self, index: int) -> Dict[str, Any]:

        meta = load_file(get_path(self.df, index, "meta"))
        
        # band_img = get_path(self.df, index, "rgb_paths")
        # band_npy = get_path(self.df, index, "r_paths")
        band_npy = [(b,get_path(self.df, index, b)) for b in self.bands if get_path(self.df, index, b).suffix == ".npy"]
        #band_img = [(b,get_path(self.df, index, b)) for b in self.bands if is_image_file(get_path(self.df, index, b).suffix)]
        
        item_ = {}

        if len(band_npy) > 0:
            #start = time.time()

            bands = [load_file(band) for (_,band) in band_npy]
            npy_data = np.stack(bands, axis = 1).astype(np.int32)
            item_["sat"] = torch.from_numpy(npy_data)
            #elapsed = (time.time() - start)
            #print("finished loading satellite band in " + str(elapsed))
            #print("****************************************************")
        #TODO later if we are using img data
        #for (b, data) in band_img :                                                                           
          #  tensor_image = self.transform(image)
         #   item_[b] = tensor_image

        item_ = self.transform(item_)
        
       
        #add target
        item_["target"] = None
        item_["num_complete_checklists"] = None
        if self.mode != "test":
            species = load_file(get_path(self.df, index, "species"))
            item_["target"] = torch.Tensor(species["probs"])
            item_["num_complete_checklists"] = species["num_complete_checklists"]
        #add metadata information (hotspot info)
        meta.pop('earliest_date', None)
        item_.update(meta)
        
        
        return item_
    