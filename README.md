# SatBird Dataset and Benchmarks

This repository is a fork of the SatBird project:

M. Teng, A. Elmustafa, B. Akera, Y. Bengio, H. Abdelwahed, H. Larochelle and D. Rolnick. ["SatBird: a Dataset for Bird Species Distribution Modeling using Remote Sensing and Citizen Science Data"](), *NeurIPS 2023 Datasets and Benchmarks track*

You can also visit the project's website [here](https://satbird.github.io/).

The goal of our project is to :
* Reproduce the results of the paper
* Explore the ConvNext models 
* Encode the geographical information using the Altitude of each hotspot.

Because this project is just for exploration, we used only a subset (california) of the original dataset (USA).


###  Installation

Code runs on Python 3.10. You can create the Python environment using the `requirements/requirements.txt` file.

We recommend following these steps for installing the required packages: 

```python -m venv ./venv``` 

```python -m pip install -r requirements/requirements.txt```

### Models
* To run the SatMAE and the Satlas model, you need to download the [pre-trained weights](https://drive.google.com/drive/folders/1hvp-VOLTBerszNENuTHjBe2hz58qcO4e?usp=drive_link) and put them inside a directory called 
*pretrained_weights* inside the main directory.

* The ResNet-18 and ConvNeXt models will be downloaded (and cached) when running the code.


### Dataset 
The California dataset can be downloaded at this [address](https://drive.google.com/file/d/1x2M6o8gGctb_z1Gp5pX6UFAhEyH2ce_c/view?usp=drive_link).
Your can unzip this folder anywhere you want. You will just have to adjust the path location in the config file.


### Train

To train the model, you first need to choose which benchmark you want to run. Let's say you want to run *California / ConvNeXt / RBG*. Then you will need to :

* Edit the config file (inside the *config* folder) to replace the field *data-->files-->base* by your dataset path.

* From the main directory, run the command `python train.py args.config=configs/SatBird-California-summer/ConvNeXt/convnext_small_RGB.yaml`. 

To log experiments on comet-ml, make sure you have exported your COMET_API_KEY and COMET_WORKSPACE in your environmental variables.
You can do so with `export COMET_API_KEY=your_comet_api_key` in your terminal or create a .env file inside the main directory.





This work is licensed under a
[Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License](https://creativecommons.org/licenses/by-nc/4.0/).
