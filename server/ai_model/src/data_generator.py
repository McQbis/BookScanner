#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File name: data_generator.py
Author: Maciej Kubiś
Date: 2025-03-19
Description: This module contains a data generator class that generates images with wavy distortions and 3D rotations.
"""

from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import Style, TextProperties
from odf.table import Table, TableRow, TableCell
from odf.text import P
import random
from numpy.random import choice
import subprocess
import os
from pdf2image import convert_from_path
import cv2
import numpy as np
import math

class DocumentImageGenerator():
    def __init__(self, file_path: str):
        """
        Initializes the data generator with a list of words from a text file.

        Params:
            file_path (str): Path to a text file containing a list of words.
        """

        self._images = []
        self._grids = []
        
        with open(file_path, "r", encoding="utf-8") as file:
            self._text = file.read().split()

    def __str__(self):
        return "DocumentImageGenerator"
    
    def __len__(self):
        return len(self._images)
    
    def __getitem__(self, index):
        return self._images[index], self._grids[index]
    
    def _generate_random_font_style(self):
        """Generate a random font style for table cells."""
        style = Style(name=f"Style_{random.randint(1, 1_000_000)}", family="table-cell")
        
        font_size = choice(["12pt", "14pt", "17pt", "21pt", "26pt"],
                        p=[0.8, 0.05, 0.05, 0.05, 0.05])
        bold = choice(["bold", "normal"], p=[0.05, 0.95])
        italic = choice(["italic", "normal"], p=[0.05, 0.95])
        
        style.addElement(TextProperties(fontstyle=italic, fontweight=bold, fontsize=font_size))
        return style

    def _generate_random_file_content(self):
        """Generate an OpenDocument spreadsheet with random text formatting."""
        # Prepare data
        random.shuffle(self._text)
        words = self._text[random.randint(0, 101):random.randint(102, len(self._text))]
        num_of_words = len(words)

        
        # Create a new spreadsheet document
        doc = OpenDocumentSpreadsheet()
        table = Table(name="Table")
        file_content = []
        
        # Generate table content
        i = 0
        while i < num_of_words:
            line_length = random.randint(1, 10)
            tab_adding = choice([True, False], p=[0.05, 0.95])
            dash_adding = choice([True, False], p=[0.05, 0.95])
            star_adding = choice([True, False], p=[0.05, 0.95])
            
            row_data = []
            if tab_adding:
                row_data.append("")
                tab_adding = False
            
            for _ in range(line_length):
                if i >= num_of_words:
                    break
                
                if dash_adding:
                    row_data.append("-")
                    dash_adding = False
                elif star_adding:
                    row_data.append("*")
                    star_adding = False
                else:
                    row_data.append(words[i])
                    i += 1
            
            file_content.append(row_data)
        
        # Add rows and cells to the table
        for row_data in file_content:
            row = TableRow()
            for cell_data in row_data:
                font_style = self._generate_random_font_style()
                doc.automaticstyles.addElement(font_style)
                cell = TableCell(stylename=font_style)
                cell.addElement(P(text=cell_data))
                row.addElement(cell)
            table.addElement(row)
        
        # Add table to document
        doc.spreadsheet.addElement(table)
        
        # Save the document
        doc.save("server/ai_model/src/assets/document.ods")

    def _convert_ods_to_pdf(self):
        """Convert an ODS file to PDF using LibreOffice CLI."""
        
        try:
            subprocess.run([
                "libreoffice", "--headless", 
                "--convert-to", "pdf", "server/ai_model/src/assets/document.ods", 
                "--outdir", "server/ai_model/src/assets"
            ], check=True)
            os.remove("server/ai_model/src/assets/document.ods")
        except subprocess.CalledProcessError as e:
            print(f"Error during conversion: {e}")

    def _convert_pdf_to_jpeg(self):
        """Convert all pages of a PDF file to JPEG using pdf2image."""
        
        try:
            images = convert_from_path("server/ai_model/src/assets/document.pdf")
            for i, image in enumerate(images):
                image.save(f"server/ai_model/src/assets/document_page_{i + 1}.jpg", "JPEG")
                self._images.append(cv2.imread(f"server/ai_model/src/assets/document_page_{i + 1}.jpg"))
                os.remove(f"server/ai_model/src/assets/document_page_{i + 1}.jpg")
            os.remove("server/ai_model/src/assets/document.pdf")
        except Exception as e:
            print(f"Error during conversion: {e}")

    def _add_padding(self, image, padding):
        """Adds padding to an image to prevent cropping after warping."""
        h, w, c = image.shape
        new_h, new_w = h + 2 * padding, w + 2 * padding
        padded_image = np.zeros((new_h, new_w, c), dtype=np.uint8)
        padded_image[padding:padding+h, padding:padding+w] = image
        return padded_image
    
    def _get_rotation_matrix(self, angle_x, angle_y, angle_z):
        """Compute 3D rotation matrix from given angles in degrees."""
        ax, ay, az = map(math.radians, [angle_x, angle_y, angle_z])
        
        rot_x = np.array([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]], dtype=np.float32)
        rot_y = np.array([[math.cos(ay), 0, math.sin(ay)], [0, 1, 0], [-math.sin(ay), 0, math.cos(ay)]], dtype=np.float32)
        rot_z = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]], dtype=np.float32)
        
        rot_matrix = np.eye(4, dtype=np.float32)
        rot_matrix[:3, :3] = rot_z @ rot_y @ rot_x  # Combine rotations
        return rot_matrix
    
    def _generate_mesh_grid(self, width, height):
        """Generate a mesh grid for remapping transformation."""
        x_map, y_map = np.meshgrid(np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32))
        mesh_3d = np.stack([x_map, y_map, np.zeros_like(x_map), np.ones_like(x_map)], axis=-1)  # (H, W, 4)
        return mesh_3d
    
    def _apply_transformations(self, mesh, rotation_matrix, amplitude, frequency):
        """Apply both wavy distortion and 3D rotation to the transformation mesh."""
        h, w, _ = mesh.shape
        flat_mesh = mesh.reshape(-1, 4).T  # Shape: (4, H*W)

        low_val = random.uniform(-1.0, 1.0)
        high_low = random.uniform(low_val, 1.0)

        # Generate a vector with values ranging from -1 to 1
        vector = np.linspace(low_val, high_low, flat_mesh.shape[1])
        
        # Apply wavy transformation
        flat_mesh[1] += amplitude * np.sin(frequency * flat_mesh[0] + random.randint(0, 1000)) * vector
        
        # Apply 3D rotation
        transformed_mesh = rotation_matrix @ flat_mesh
        x_new, y_new = transformed_mesh[0], transformed_mesh[1]  # Ignore Z-axis
        
        return x_new.reshape(h, w).astype(np.float32), y_new.reshape(h, w).astype(np.float32)

    def get_images(self):
        """Returns images generated by the data generator."""
        return self._images
    
    def get_grids(self):
        """Returns deformation grids generated by the data generator."""
        return self._grids
    
    def delete_images(self):
        """Deletes all images generated by the data generator."""
        self._images = []

    def delete_grids(self):
        """Deletes all deformation grids generated by the data generator."""
        self._grids = []

    def set_seed(self, seed: int):
        """
        Sets the seed for the random number generators.

        Params:
            seed (int): Seed for the random number generators.
        """
        random.seed(seed)
        np.random.seed(seed)

    def set_text_from_file_path(self, file_path: str):
        """
        Sets the text data for the data generator.

        Params:
            file_path (str): Path to a text file containing a list of words.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            self._text = file.read().split()
    
    def generate_new_images(self):
        """Generates new images using the data generator."""
        self._generate_random_file_content()
        self._convert_ods_to_pdf()
        self._convert_pdf_to_jpeg()

        for i in range(len(self._images)):

            # Add padding to prevent cropping
            padding = random.randint(400, 550)
            scaled_image = self._add_padding(self._images[i], padding)

            # Get new dimensions
            height, width = scaled_image.shape[:2]

            # Generate mesh grid
            mesh_3d = self._generate_mesh_grid(width, height)

            # Define transformations
            amplitude = random.randint(0, 100)  # Pixel displacement
            frequency = random.uniform(0.5, 3.0) * np.pi / width # Frequency relative to width
            rotation_matrix = self._get_rotation_matrix(random.randint(-10, 10),
                                                random.randint(-10, 10),
                                                random.randint(-5, 5))
            
            # Apply combined transformations
            x_map_final, y_map_final = self._apply_transformations(mesh_3d, rotation_matrix, amplitude, frequency)
            
            # Ensure correct data type for remap
            x_map_final = x_map_final.astype(np.float32)
            y_map_final = y_map_final.astype(np.float32)

            # Remap image using the transformed mesh
            self._images[i] = cv2.remap(scaled_image, x_map_final, y_map_final, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            self._grids.append((x_map_final, y_map_final))

    def regenerate_data(self):
        """Regenerates images and deformation grids using the data generator."""
        self.delete_images()
        self.delete_grids()
        self.generate_new_images()