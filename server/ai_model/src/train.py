#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File name: train.py
Author: Maciej Kubiś
Date: 2025-03-24
Description: Functions for training the neural network model.
"""

import torch
from evaluate import evaluate_model

def train_model(model, 
                generator, 
                device, 
                epochs, 
                criterion, 
                optimizer, 
                num_batches):
    """
    Train the U-Net model using dynamically generated document images.
    
    Params:
        model: The neural network model to train
        generator: DocumentImageGenerator instance for creating training data
        device: The device to run training on (CPU or GPU)
        epochs: Number of training epochs
        criterion: Loss function
        optimizer: Optimizer instance
        num_batches: Number of mini batches to train on
    
    Returns:
        The trained model, best validation loss and lists of training and validation losses.
    """
    train_losses = []
    val_losses = []
    best_val_loss = float('inf')
    early_stop_counter = 0
    patience = 3  # Stop training if no improvement for 'patience' epochs
    
    with open("../logs/train.log", "w") as log_file:
        log_file.write(f"Starting training for {epochs} epochs...\n")
        
        for epoch in range(epochs):
            model.train()
            epoch_loss = 0.0
            
            for batch_idx in range(num_batches):
                generator.regenerate_data()
                images = generator.get_images()
                grids = generator.get_grids()
                
                if not images:
                    continue
                
                batch_loss = 0.0
                
                for img, (x_grid, y_grid) in zip(images, grids):
                    img_tensor = torch.from_numpy(img).permute(2, 0, 1).float().to(device)
                    img_tensor = img_tensor.unsqueeze(0)
                    
                    x_grid_tensor = torch.from_numpy(x_grid).unsqueeze(0).unsqueeze(0).to(device)
                    y_grid_tensor = torch.from_numpy(y_grid).unsqueeze(0).unsqueeze(0).to(device)
                    target_grid = torch.cat([x_grid_tensor, y_grid_tensor], dim=1)
                    
                    optimizer.zero_grad()
                    predicted_offsets = model(img_tensor)
                    loss = criterion(predicted_offsets, target_grid)
                    loss.backward()
                    optimizer.step()
                    
                    batch_loss += loss.item()
                
                avg_batch_loss = batch_loss / len(images)
                epoch_loss += avg_batch_loss
                log_file.write(f"Epoch {epoch+1}/{epochs}, Batch {batch_idx+1}/{num_batches}, Loss: {avg_batch_loss:.6f}\n")
            
            avg_epoch_loss = epoch_loss / num_batches if num_batches > 0 else 0
            train_losses.append(avg_epoch_loss)
            log_file.write(f"Epoch {epoch+1}/{epochs} completed, Avg Loss: {avg_epoch_loss:.6f}\n")
            
            val_loss = evaluate_model(model, generator, device, criterion, val_losses, num_batches)
            val_losses.append(val_loss)
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save(model.state_dict(), "best_model.pth")
                log_file.write(f"New best model saved with validation loss: {val_loss:.6f}\n")
                early_stop_counter = 0
            else:
                early_stop_counter += 1
                if early_stop_counter >= patience:
                    log_file.write("Early stopping triggered.\n")
                    break
    
    return model, best_val_loss, train_losses, val_losses