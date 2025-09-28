import os
import torch
import asyncio
from src.configs.env import HF_TOKEN
from huggingface_hub import hf_hub_download
from transformers import AutoModel
import torch
from .network import SegGenerator, ALIASGenerator

# Import model classes from VITON-HD
from src.apps.tryonml.services.network import SegGenerator, GMM, ALIASGenerator

REPO_ID = "emekadefirst/virtualfit-models"

def get_opt():
    """Define options matching test.py from VITON-HD."""
    class Opt:
        semantic_nc = 13  # Number of human-parsing map classes
        init_type = 'xavier'
        init_variance = 0.02
        grid_size = 5  # For GMM
        norm_G = 'spectralaliasinstance'  # For ALIASGenerator
        ngf = 64  # Number of generator filters
        num_upsampling_layers = 'most'  # For ALIASGenerator
        load_height = 1024  # Added from test.py
        load_width = 768   # Added from test.py
    return Opt()

async def load_model_async(filename: str, model_class, model_args):
    """Download & load one model asynchronously."""
    def _load():
        model_path = hf_hub_download(REPO_ID, filename, token=HF_TOKEN)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model_class(**model_args).to(device)  # Instantiate the model
        state_dict = torch.load(model_path, map_location=device)
        model.load_state_dict(state_dict)  # Load the weights
        model.eval()  # Set to evaluation mode
        return model
    
    return await asyncio.to_thread(_load)



# src/apps/tryonml/services/loader.py
from transformers import AutoModel
import torch
from .network import SegGenerator, ALIASGenerator, GMM

async def load_viton_models():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    class Options:
        def __init__(self):
            self.ngf = 64
            self.norm = 'alias_instance'
            self.norm_G = 'spectralaliasmask'
            self.semantic_nc = 8
            self.input_nc = 9
            self.num_features = 64
            self.load_height = 1024
            self.load_width = 768
            self.grid_size = 5
            self.num_upsampling_layers = 'normal'
            self.init_type = 'normal'
            self.init_variance = 0.02

    opt = Options()
    seg_model = SegGenerator(opt, input_nc=21, output_nc=13).to(device)
    gmm_model = GMM(opt, inputA_nc=7, inputB_nc=3).to(device)
    alias_model = ALIASGenerator(opt, input_nc=9).to(device)
    
    seg_model.eval()
    gmm_model.eval()
    alias_model.eval()
    
    return seg_model, gmm_model, alias_model

