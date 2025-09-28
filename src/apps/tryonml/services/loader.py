import os
import torch
import asyncio
from src.configs.env import HF_TOKEN
from huggingface_hub import hf_hub_download

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

async def load_viton_models():
    opt = get_opt()  # Get options for model initialization
    # Model-specific arguments based on test.py
    seg_args = {'opt': opt, 'input_nc': opt.semantic_nc + 8, 'output_nc': opt.semantic_nc}  # 21 input, 13 output
    gmm_args = {'opt': opt, 'inputA_nc': 7, 'inputB_nc': 3}
    # Create a separate opt for ALIASGenerator with semantic_nc=7
    alias_opt = get_opt()
    alias_opt.semantic_nc = 7  # Match test.py
    alias_args = {'opt': alias_opt, 'input_nc': 9}
    
    seg_task = asyncio.create_task(load_model_async("seg_final.pth", SegGenerator, seg_args))
    gmm_task = asyncio.create_task(load_model_async("gmm_final.pth", GMM, gmm_args))
    alias_task = asyncio.create_task(load_model_async("alias_final.pth", ALIASGenerator, alias_args))
    
    seg_model, gmm_model, alias_model = await asyncio.gather(seg_task, gmm_task, alias_task)
    return seg_model, gmm_model, alias_model