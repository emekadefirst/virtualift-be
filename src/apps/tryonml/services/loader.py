import os
import torch
import asyncio
from src.configs.env import HF_TOKEN
from huggingface_hub import hf_hub_download

REPO_ID = "emekadefirst/virtualfit-models"


async def load_model_async(filename: str):
    """Download & load one model asynchronously."""
    def _load():
        model_path = hf_hub_download(REPO_ID, filename, token=HF_TOKEN)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = torch.load(model_path, map_location=device)
        model.eval()
        return model
    
    return await asyncio.to_thread(_load)

async def load_viton_models():
    seg_task = asyncio.create_task(load_model_async("seg_final.pth"))
    gmm_task = asyncio.create_task(load_model_async("gmm_final.pth"))
    alias_task = asyncio.create_task(load_model_async("alias_final.pth"))

    seg_model, gmm_model, alias_model = await asyncio.gather(seg_task, gmm_task, alias_task)
    return seg_model, gmm_model, alias_model
