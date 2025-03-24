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
        learning_rate: Learning rate for optimizer
        criterion: Loss function
        optimizer: Optimizer instance
        num_batches: Number of mini batches to train on
    
    Returns:
        The trained model and best validation loss
    """

    train_losses = []
    val_losses = []
    best_val_loss = float('inf')

    log_file = open("../logs/train.log", "w")
    
    log_file.write(f"Starting training for {epochs} epochs...")
    
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        
        for batch_idx in range(num_batches):
            # Generate new batch of data
            generator.regenerate_data()
            
            # Get images and grids
            images = generator.get_images()
            grids = generator.get_grids()
            
            batch_loss = 0.0
            
            # Process each image in the batch
            for img, (x_grid, y_grid) in zip(images, grids):
                # Convert numpy arrays to PyTorch tensors
                img_tensor = torch.from_numpy(img).permute(2, 0, 1).float().to(device)  # Convert from HWC to CHW
                img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension
                
                x_grid_tensor = torch.from_numpy(x_grid).unsqueeze(0).unsqueeze(0).to(device)
                y_grid_tensor = torch.from_numpy(y_grid).unsqueeze(0).unsqueeze(0).to(device)
                
                # Combine into single target tensor with shape [batch_size, 2, height, width]
                target_grid = torch.cat([x_grid_tensor, y_grid_tensor], dim=1)
                
                # Forward pass
                predicted_offsets = model(img_tensor)
                
                # Calculate loss - compare predicted offsets with the grid coordinates
                loss = criterion(predicted_offsets, target_grid)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                batch_loss += loss.item()
            
            # Average loss for the batch
            avg_batch_loss = batch_loss / len(images) if images else 0
            epoch_loss += avg_batch_loss
            
            log_file.write(f"Epoch {epoch+1}/{epochs}, Batch {batch_idx+1}/{num_batches}, Loss: {avg_batch_loss:.6f}")
        
        # Average loss for the epoch
        avg_epoch_loss = epoch_loss / num_batches if num_batches > 0 else 0
        train_losses.append(avg_epoch_loss)
        
        log_file.write(f"Epoch {epoch+1}/{epochs} completed, Avg Loss: {avg_epoch_loss:.6f}")
        
        # Validation phase
        val_loss = evaluate_model(model, generator, device, criterion, val_losses, num_batches)

        val_losses.append(val_loss)
        
        # Stop training if validation loss didn't improve
        if val_loss > best_val_loss:
            best_val_loss = val_loss
            log_file.write(f"Model with validation loss: {val_loss:.6f}")
            break

    log_file.close()
    
    return model, best_val_loss, train_losses, val_losses