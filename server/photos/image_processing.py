import cv2
import numpy as np
import torch
import torch.nn.functional as F

import sys
sys.path.append("../ai_model/src")
from unet_flexible import UNetFlexible

class ImageProcessing:
    def __init__(self):
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model = UNetFlexible()
        self._model.load_state_dict(torch.load("server/ai_model/src/unet_deform.pth", map_location=self._device))
        self._model.to(self._device)
        self._model.eval()

    def __call__(self, uploaded_file):
        """
        Process the uploaded grayscale image using a neural network and inverse warping.

        Args:
            uploaded_file: The uploaded file object.
        
        Returns:
            bytes: The processed image in bytes format.
        """
        image_cv = self._convert_to_cv(uploaded_file)
        input_tensor = self._prepare_tensor(image_cv).to(self._device)  # [1, 1, H, W]

        with torch.no_grad():
            offsets = self._model(input_tensor)[0]  # [2, H, W]
            processed_tensor = self._apply_inverse_warp(input_tensor[0], offsets)  # [1, H, W]

        processed_image = self._to_cv_image(processed_tensor)
        return self._convert_to_bytes(processed_image)

    def _convert_to_cv(self, uploaded_file):
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        return cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

    def _prepare_tensor(self, img):
        img_tensor = torch.from_numpy(img).unsqueeze(0).float() / 255.0  # [1, H, W]
        return img_tensor.unsqueeze(0)  # [1, 1, H, W]

    def _apply_inverse_warp(self, image_tensor, offsets):
        """
        Applies inverse warping using predicted absolute coordinates.

        Args:
            image_tensor: torch.Tensor [1, H, W]
            offsets: torch.Tensor [2, H, W] - absolute target coordinates

        Returns:
            torch.Tensor [1, H, W] - corrected image
        """
        _, H, W = image_tensor.shape
        device = image_tensor.device

        yy, xx = torch.meshgrid(torch.arange(H, device=device), torch.arange(W, device=device), indexing='ij')
        source_grid = torch.stack([xx, yy], dim=0).float()  # [2, H, W]

        displacement = offsets - source_grid
        inverse_coords = source_grid - displacement  # [2, H, W]

        norm_grid = inverse_coords.clone()
        norm_grid[0] = 2.0 * norm_grid[0] / (W - 1) - 1.0
        norm_grid[1] = 2.0 * norm_grid[1] / (H - 1) - 1.0
        norm_grid = norm_grid.permute(1, 2, 0).unsqueeze(0)  # [1, H, W, 2]

        warped = F.grid_sample(image_tensor.unsqueeze(0), norm_grid, mode='bilinear',
                               padding_mode='border', align_corners=True)
        return warped.squeeze(0)  # [1, H, W]

    def _to_cv_image(self, tensor):
        tensor = (tensor.clamp(0, 1) * 255).byte().cpu().squeeze(0)  # [H, W]
        img_np = tensor.numpy()
        return cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)

    def _convert_to_bytes(self, image):
        return cv2.imencode('.jpg', image)[1].tobytes()
