import cv2
import numpy as np
import torch
import torch.nn.functional as F

import sys
sys.path.append("./ai_model/src")
from unet_flexible import UNetFlexible

import numpy as np

def extend_line(x1, y1, x2, y2, extension_length=200):
    # 1. Compute direction vector
    dx = x2 - x1
    dy = y2 - y1

    # 2. Normalize vector (unit direction)
    length = np.sqrt(dx**2 + dy**2)
    if length == 0:
        return x1, y1, x2, y2  # Avoid division by zero

    ux = dx / length
    uy = dy / length

    # 3. Extend both ends
    new_x1 = int(x1 - ux * (extension_length / 2))
    new_y1 = int(y1 - uy * (extension_length / 2))
    new_x2 = int(x2 + ux * (extension_length / 2))
    new_y2 = int(y2 + uy * (extension_length / 2))

    return new_x1, new_y1, new_x2, new_y2


class ImageProcessing:
    def __init__(self):
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model = UNetFlexible()
        self._model.load_state_dict(torch.load("./ai_model/models/unet_deform_best_train.pth", map_location=self._device))
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

        image_cv = cv2.GaussianBlur(image_cv, (3, 3), 0.9)

        height, width = image_cv.shape[:2]

        # Define center crop
        crop_size = 200
        center_x, center_y = width // 2, height // 2
        half_crop = crop_size // 2
        start_x = center_x - half_crop
        start_y = center_y - half_crop
        end_x = center_x + half_crop
        end_y = center_y + half_crop

        # Crop image
        cropped_gray = image_cv[start_y:end_y, start_x:end_x]

        # Find brightest pixel (maximum intensity)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(cropped_gray)

        val = ((maxVal - minVal)//2) * 1.6

        image_cv = image_cv.astype(np.int32)  # pozwala na wartości ujemne
        image_cv = image_cv * 3 - (val * 3)
        image_cv[image_cv < 0] = 0
        image_cv[image_cv > 255] = 255
        image_cv = image_cv.astype(np.uint8)

        image_cv = cv2.adaptiveThreshold(
                image_cv,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                15,  # rozmiar sąsiedztwa
                10  # przesunięcie progu
            )
        
        image_cv = cv2.bitwise_not(image_cv)

        # 1. Wykryj krawędzie
        edges = cv2.Canny(image_cv, 50, 150)

        # 2. Domknij przerwy w krawędziach (tolerancja na przerwania)
        kernel = np.ones((20, 20), np.uint8)
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        # 3. Znajdź kontury
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 4. Znajdź największy kontur (według pola)
        largest_contour = max(contours, key=cv2.contourArea)

        # 5. Utwórz maskę i narysuj kontur jako wypełniony
        mask = np.zeros_like(image_cv)
        cv2.drawContours(mask, [largest_contour], -1, 255, thickness=cv2.FILLED)

        # 6. Zastosuj maskę: tylko największy kontur zostaje, reszta czarna
        image_cv = cv2.bitwise_and(image_cv, mask)

        image_cv = cv2.bitwise_not(image_cv)

        lines = cv2.HoughLinesP(image_cv, 1, np.pi / 720, threshold=80, minLineLength=1, maxLineGap=30)

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Check if the line is vertical (within a small tolerance)
                if abs(y1 - y2) > 800 and abs(x1 - x2) < 600:
                    # # Extend line vertically by 20 pixels up and down
                    # y_min = min(y1, y2) - 200
                    # y_max = max(y1, y2) + 200
                    
                    # x1 -= 20  # extend left
                    # x2 += 20  # extend right
                    # x = (x1 + x2) // 2  # use average x

                    # # Clamp to image boundaries
                    # y_min = max(0, y_min)
                    # y_max = min(image_cv.shape[0] - 1, y_max)

                    # Draw the thicker line on image
                    cv2.line(image_cv, (x1, y1), (x2, y2), 255, thickness=20)

        lines = cv2.HoughLinesP(image_cv, 1, np.pi / 180, threshold=80, minLineLength=1, maxLineGap=60)
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Check if the line is vertical (within a small tolerance)
                if abs(y1 - y2) > 1500 and abs(x1 - x2) < 600:
                    # # Extend line vertically by 20 pixels up and down
                    # y_min = min(y1, y2) - 200
                    # y_max = max(y1, y2) + 200
                    
                    # x1 -= 20  # extend left
                    # x2 += 20  # extend right
                    # x = (x1 + x2) // 2  # use average x

                    # # Clamp to image boundaries
                    # y_min = max(0, y_min)
                    # y_max = min(image_cv.shape[0] - 1, y_max)

                    # Draw the thicker line on image
                    x1, y1, x2, y2 = extend_line(x1, y1, x2, y2, extension_length=200)
                    cv2.line(image_cv, (x1, y1), (x2, y2), 255, thickness=20)

        image_cv = cv2.bitwise_not(image_cv)

        # 3. Znajdź kontury
        contours, _ = cv2.findContours(image_cv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 4. Znajdź największy kontur (według pola)
        largest_contour = max(contours, key=cv2.contourArea)

        # 5. Utwórz maskę i narysuj kontur jako wypełniony
        mask = np.zeros_like(image_cv)
        cv2.drawContours(mask, [largest_contour], -1, 255, thickness=cv2.FILLED)

        # 6. Zastosuj maskę: tylko największy kontur zostaje, reszta czarna
        image_cv = cv2.bitwise_and(image_cv, mask)

        # # 1. Wykryj krawędzie
        # edges = cv2.Canny(image_cv, 50, 150)

        # # 2. Domknij przerwy w krawędziach (tolerancja na przerwania)
        # kernel = np.ones((100, 100), np.uint8)
        # closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        # # 3. Znajdź kontury
        # contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # # 4. Znajdź największy kontur (według pola)
        # largest_contour = max(contours, key=cv2.contourArea)

        # # 5. Utwórz maskę i narysuj kontur jako wypełniony
        # mask = np.zeros_like(image_cv)
        # cv2.drawContours(mask, [largest_contour], -1, 255, thickness=cv2.FILLED)

        # # 6. Zastosuj maskę: tylko największy kontur zostaje, reszta czarna
        # image_cv = cv2.bitwise_and(image_cv, mask)

        # input_tensor = self._prepare_tensor(image_cv).to(self._device)  # [1, 1, H, W]

        # with torch.no_grad():
        #     offsets = self._model(input_tensor)[0]  # [2, H, W]
        #     processed_tensor = self._apply_inverse_warp(input_tensor[0], offsets)  # [1, H, W]

        # processed_image = self._to_cv_image(processed_tensor)
        return self._convert_to_bytes(image_cv)

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
