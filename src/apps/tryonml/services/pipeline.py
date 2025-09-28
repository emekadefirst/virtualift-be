# src/apps/tryonml/services/pipeline.py
import torch
import asyncio
from typing import Tuple
from fastapi import HTTPException
from PIL import Image
import numpy as np
import os
from src.apps.file.service import FileService
from src.utilities.reader import read_img_url
from src.apps.tryonml.services.loader import load_viton_models
from src.apps.tryonml.schemas import DataSchema
import torch.nn.functional as F
import torchgeometry as tgm
import traceback

class VHDMService:
    seg_model = None
    gmm_model = None
    alias_model = None
    cloth_segmenter = None
    human_parser = None
    pose_estimator = None

    @classmethod
    async def init(cls):
        """
        Load models once at startup.
        """
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            cls.seg_model, cls.gmm_model, cls.alias_model = await load_viton_models()
            cls.seg_model = cls.seg_model.to(device)
            cls.gmm_model = cls.gmm_model.to(device)
            cls.alias_model = cls.alias_model.to(device)
            # Initialize preprocessing models (uncomment when implemented)
            # from cloths_segmentation.model import ClothSegmenter
            # from human_parsing import SCHP
            # from lightweight_pose import LightweightPoseEstimator
            # cls.cloth_segmenter = ClothSegmenter(pretrained=True).to(device)
            # cls.human_parser = SCHP(pretrained=True).to(device)
            # cls.pose_estimator = LightweightPoseEstimator(pretrained=True).to(device)
            print(f"Models loaded successfully. CUDA available: {torch.cuda.is_available()}, Device: {device}")
        except Exception as e:
            print(f"Model loading error: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")

    @classmethod
    async def run(cls, dto: DataSchema) -> str:
        if not (cls.seg_model and cls.gmm_model and cls.alias_model):
            raise HTTPException(status_code=500, detail="Models not loaded. Call VHDMService.init() first.")
        
        try:
            # Set device
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            print(f"Using device: {device}")

            # Load images
            user_img = await read_img_url(dto.user_full_image.image_url)
            cloth_img = await read_img_url(dto.product_image.image_url)
            print(f"Loaded images: user_img size {user_img.size}, cloth_img size {cloth_img.size}")
            person = cls._load_image(user_img).to(device)
            cloth = cls._load_image(cloth_img).to(device)
            print(f"person shape: {person.shape}, cloth shape: {cloth.shape}")

            # Generate required inputs for SegGenerator
            cm = cls._generate_cloth_mask(cloth)  # Cloth mask (1 channel)
            c_masked = cloth * cm  # Masked cloth (3 channels)
            parse_agnostic = cls._generate_parse_agnostic(person)  # Agnostic parsing (13 channels)
            pose = cls._generate_pose(person)  # Pose map (3 channels)
            print(f"cm shape: {cm.shape}, c_masked shape: {c_masked.shape}, parse_agnostic shape: {parse_agnostic.shape}, pose shape: {pose.shape}")

            # Downsample inputs to 256x192 (as in test.py)
            cm_down = F.interpolate(cm, size=(256, 192), mode='bilinear', align_corners=True)
            c_masked_down = F.interpolate(c_masked, size=(256, 192), mode='bilinear', align_corners=True)
            parse_agnostic_down = F.interpolate(parse_agnostic, size=(256, 192), mode='bilinear', align_corners=True)
            pose_down = F.interpolate(pose, size=(256, 192), mode='bilinear', align_corners=True)
            noise = torch.randn_like(cm_down, device=device)  # Noise (1 channel)
            print(f"cm_down shape: {cm_down.shape}, c_masked_down shape: {c_masked_down.shape}, parse_agnostic_down shape: {parse_agnostic_down.shape}, pose_down shape: {pose_down.shape}, noise shape: {noise.shape}")

            # Concatenate inputs for SegGenerator (21 channels)
            seg_input = torch.cat((cm_down, c_masked_down, parse_agnostic_down, pose_down, noise), dim=1)
            print(f"seg_input shape: {seg_input.shape}")

            # 2. Segmentation
            seg_output = cls.seg_model(seg_input)
            print(f"seg_output shape: {seg_output.shape}")

            # Process segmentation output
            up = torch.nn.Upsample(size=(1024, 768), mode='bilinear', align_corners=True)
            gauss = tgm.image.GaussianBlur((15, 15), (3, 3)).to(device)
            parse_pred = gauss(up(seg_output))
            parse_pred = parse_pred.argmax(dim=1)[:, None]
            print(f"parse_pred shape: {parse_pred.shape}")

            parse_old = torch.zeros(parse_pred.size(0), 13, 1024, 768, dtype=torch.float, device=device)
            parse_old.scatter_(1, parse_pred, 1.0)

            labels = {
                0: ['background', [0]],
                1: ['paste', [2, 4, 7, 8, 9, 10, 11]],
                2: ['upper', [3]],
                3: ['hair', [1]],
                4: ['left_arm', [5]],
                5: ['right_arm', [6]],
                6: ['noise', [12]]
            }
            parse = torch.zeros(parse_pred.size(0), 7, 1024, 768, dtype=torch.float, device=device)
            for j in range(len(labels)):
                for label in labels[j][1]:
                    parse[:, j] += parse_old[:, label]
            print(f"parse shape: {parse.shape}")

            # 3. Warp cloth
            agnostic_gmm = F.interpolate(person, size=(256, 192), mode='nearest')
            parse_cloth_gmm = F.interpolate(parse[:, 2:3], size=(256, 192), mode='nearest')
            pose_gmm = F.interpolate(pose, size=(256, 192), mode='nearest')
            c_gmm = F.interpolate(cloth, size=(256, 192), mode='nearest')
            gmm_input = torch.cat((parse_cloth_gmm, pose_gmm, agnostic_gmm), dim=1)
            print(f"gmm_input shape: {gmm_input.shape}, c_gmm shape: {c_gmm.shape}")

            _, warped_grid = cls.gmm_model(gmm_input, c_gmm)
            warped_cloth = F.grid_sample(cloth, warped_grid, padding_mode='border', align_corners=True)
            warped_cm = F.grid_sample(cm, warped_grid, padding_mode='border', align_corners=True)
            print(f"warped_cloth shape: {warped_cloth.shape}, warped_cm shape: {warped_cm.shape}")

            # 4. Final try-on
            misalign_mask = parse[:, 2:3] - warped_cm
            misalign_mask[misalign_mask < 0.0] = 0.0
            parse_div = torch.cat((parse, misalign_mask), dim=1)
            print(f"misalign_mask shape: {misalign_mask.shape}, parse_div shape: {parse_div.shape}")

            alias_input = torch.cat((person, pose, warped_cloth), dim=1)
            print(f"alias_input shape: {alias_input.shape}")
            try:
                final_output = cls.alias_model(alias_input, parse, parse_div, misalign_mask)
                print(f"final_output shape: {final_output.shape}")
            except Exception as e:
                print(f"ALIAS model error: {str(e)}\n{traceback.format_exc()}")
                raise

            # 5. Convert tensor → numpy → image
            try:
                final_image = cls._tensor_to_image(final_output)
                print(f"final_image size: {final_image.size}")
            except Exception as e:
                print(f"Tensor to image error: {str(e)}\n{traceback.format_exc()}")
                raise

            # 6. Upload image
            try:
                stored_img = await FileService.upload(final_image)
            except Exception as e:
                print(f"FileService upload error: {str(e)}\n{traceback.format_exc()}")
                temp_path = "temp_output.jpg"
                final_image.save(temp_path)
                stored_img = await FileService.upload(temp_path)
                os.remove(temp_path)
            return stored_img

        except Exception as e:
            print(f"Pipeline error: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    @staticmethod
    def _load_image(img: Image.Image) -> torch.Tensor:
        """
        Convert a PIL Image to a torch.Tensor.
        """
        img = img.convert("RGB")
        img = img.resize((768, 1024))  # Match test.py input size
        arr = np.array(img).astype(np.float32) / 255.0
        arr = arr.transpose(2, 0, 1)  # HWC → CHW
        tensor = torch.tensor(arr).unsqueeze(0)  # Add batch dimension
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

    @staticmethod
    def _generate_cloth_mask(cloth: torch.Tensor) -> torch.Tensor:
        """
        Generate cloth mask from cloth image.
        TODO: Use a pre-trained segmentation model (e.g., U-Net, DeepLabV3).
        """
        if VHDMService.cloth_segmenter:
            cloth_np = cloth.cpu().numpy()[0].transpose(1, 2, 0)  # CHW → HWC
            mask = VHDMService.cloth_segmenter.predict(cloth_np)  # Binary mask
            return torch.tensor(mask, dtype=torch.float32, device=cloth.device).unsqueeze(0).unsqueeze(0)
        return torch.ones_like(cloth[:, :1, :, :])  # Dummy mask

    @staticmethod
    def _generate_parse_agnostic(person: torch.Tensor) -> torch.Tensor:
        """
        Generate agnostic parsing map.
        TODO: Use a human parsing model (e.g., SCHP).
        """
        if VHDMService.human_parser:
            person_np = person.cpu().numpy()[0].transpose(1, 2, 0)  # CHW → HWC
            parse_map = VHDMService.human_parser.predict(person_np)  # [H, W, 13]
            return torch.tensor(parse_map, dtype=torch.float32, device=person.device).permute(2, 0, 1).unsqueeze(0)
        return torch.zeros((person.size(0), 13, person.size(2), person.size(3)), device=person.device)  # Dummy

    @staticmethod
    def _generate_pose(person: torch.Tensor) -> torch.Tensor:
        """
        Generate pose map.
        TODO: Use a pose estimation model (e.g., OpenPose, DensePose).
        """
        if VHDMService.pose_estimator:
            person_np = person.cpu().numpy()[0].transpose(1, 2, 0)  # CHW → HWC
            pose_map = VHDMService.pose_estimator.predict(person_np)  # [H, W, 3]
            return torch.tensor(pose_map, dtype=torch.float32, device=person.device).permute(2, 0, 1).unsqueeze(0)
        return torch.zeros_like(person)  # Dummy