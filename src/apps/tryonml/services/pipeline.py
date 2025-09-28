import torch
import asyncio
from typing import Tuple
from fastapi import HTTPException
from PIL import Image
import numpy as np
import cv2
import os
from src.apps.file.service import FileService
from src.utilities.reader import read_img_url
from src.apps.tryonml.services.loader import load_viton_models
from src.apps.tryonml.schemas import DataSchema



class VHDMService:
    seg_model = None
    gmm_model = None
    alias_model = None

    @classmethod
    async def init(cls):
        """
        Load models once at startup.
        """
        cls.seg_model, cls.gmm_model, cls.alias_model = await load_viton_models()

    @classmethod
    async def run(cls, dto: DataSchema) -> str:
        if not (cls.seg_model and cls.gmm_model and cls.alias_model):
            raise HTTPException(status_code=500, detail="Models not loaded. Call VHDMService.init() first.")
        user_img = await read_img_url(dto.user_full_image.image_url)
        cloth_img = await read_img_url(dto.product_image.image_url)
        person = cls._load_image(user_img)
        cloth = cls._load_image(cloth_img)

        # 2. Segmentation
        seg_output = cls.seg_model(person)

        # 3. Warp cloth
        warped_cloth = cls.gmm_model(cloth, seg_output)

        # 4. Final try-on
        final_output = cls.alias_model(person, warped_cloth, seg_output)

        # 5. Convert tensor → numpy → image
        final_image = cls._tensor_to_image(final_output)
        stored_img = await FileService.upload(final_image)
        return stored_img

    @staticmethod
    def _load_image(path: str) -> torch.Tensor:
        img = Image.open(path).convert("RGB")
        img = img.resize((512, 512))  # match VITON-HD input size
        arr = np.array(img).astype(np.float32) / 255.0
        arr = arr.transpose(2, 0, 1)  # HWC → CHW
        tensor = torch.tensor(arr).unsqueeze(0)  # add batch dimension
        return tensor

    @staticmethod
    def _tensor_to_image(tensor: torch.Tensor) -> Image.Image:
        """
        Convert model tensor output to PIL Image.
        """
        arr = tensor.detach().cpu().numpy()[0]
        arr = np.transpose(arr, (1, 2, 0))  # CHW → HWC
        arr = (arr * 255).clip(0, 255).astype(np.uint8)
        return Image.fromarray(arr)
