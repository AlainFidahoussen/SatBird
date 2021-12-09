import comet_ml
import os
import sys
from pathlib import Path

sys.path.append(str(Path().resolve().parent))
sys.path.append(str(Path().resolve().parent.parent))

from omegaconf import OmegaConf, DictConfig
from src.trainer.trainer import EbirdTask, EbirdDataModule
import pytorch_lightning as pl
from pytorch_lightning import loggers as pl_loggers
from pytorch_lightning import Trainer
from pytorch_lightning.loggers import CometLogger
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint, LearningRateMonitor
from typing import Any, Dict, Tuple, Type, cast
from src.dataset.utils import set_data_paths
import pdb


def set_up_omegaconf()-> DictConfig:
    """Helps with loading config files"""
    
    conf = OmegaConf.load("./configs/defaults.yaml")
    command_line_conf = OmegaConf.from_cli()

    if "config_file" in command_line_conf:
        
        config_fn = command_line_conf.config_file

        if os.path.isfile(config_fn):
            user_conf = OmegaConf.load(config_fn)
            conf = OmegaConf.merge(conf, user_conf)
        else:
            raise FileNotFoundError(f"config_file={config_fn} is not a valid file")

    conf = OmegaConf.merge(
        conf, command_line_conf
    )
    conf = set_data_paths(conf)
    conf = cast(DictConfig, conf)  # convince mypy that everything is alright

    return conf


if __name__ == "__main__":
    
    conf = set_up_omegaconf()
    
    pl.seed_everything(conf.program.seed)
    
    print(conf.log_comet)

    task = EbirdTask(conf)
    datamodule = EbirdDataModule(conf)
    
    trainer_args = cast(Dict[str, Any], OmegaConf.to_object(conf.trainer))
        
    if conf.log_comet:

        comet_logger= CometLogger(
            api_key="JAQ6zQMoTH7snvbIkpjeBswPW",#os.environ.get("COMET_API_KEY"),
            workspace= "melisandeteng", #os.environ.get("COMET_WORKSPACE"),  # Optional
           # save_dir=".",  # Optional
            project_name=conf.comet.project_name,  # Optional
           # rest_api_key=os.environ.get("COMET_REST_API_KEY"),  # Optional
            #experiment_key=os.environ.get("COMET_EXPERIMENT_KEY"),  # Optional
            experiment_name="default",  # Optional
        )
        comet_logger.experiment.add_tags(conf.comet.tags)
        print(conf.comet.tags)
        trainer_args["logger"] = comet_logger
        #trainer_args["logger"].experiment.add_tags(conf.comet.tags)

    #tb_logger = pl_loggers.comet(conf.program.log_dir, name=experiment_name)

    checkpoint_callback = ModelCheckpoint(
        monitor="val_loss",
        dirpath=conf.save_path,
        save_top_k=3,
        save_last=True,
    )
    #early_stopping_callback = EarlyStopping(
   #      monitor="val_loss",
   #     min_delta=0.00,
   #     patience=10,
   # )
    lr_monitor = LearningRateMonitor(logging_interval='epoch')



   
    trainer_args["callbacks"] = [checkpoint_callback, lr_monitor]#early_stopping_callback, lr_monitor]
    
    trainer_args["profiler"]="simple"
    #trainer_args["overfit_batches"] = 10
    #trainer_args["track_grad_norm"]=2
    
    trainer = pl.Trainer(**trainer_args)


    ## Run experiment
    trainer.fit(model=task, datamodule=datamodule)
    trainer.test(model=task, datamodule=datamodule)

    
