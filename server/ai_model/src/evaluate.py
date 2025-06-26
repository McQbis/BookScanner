import torch

def evaluate_model(model, generator, device, criterion, num_val_batches, image_scale: float = 0.45):
    """
    Evaluate the U-Net model using dynamically generated document images.
    
    Params:
        model: The neural network model to evaluate
        generator: DocumentImageGenerator instance for creating evaluation data
        device: The device to run evaluation on (CPU or GPU)
        criterion: Loss function
        num_val_batches: Number of mini batches to evaluate on
        images_scale: Scale of the images to be generated (default is 0.4)
            
    Returns:
        Average validation loss
    """

    model.eval()
    total_val_loss = 0.0
    generator.set_seed(42)
    image_scale = 0.4

    with open("../logs/evaluate.log", "w") as file_log, torch.no_grad():
        for batch_idx in range(num_val_batches):

            # Generate new batch of validation data
            generator.regenerate_data(image_scale=image_scale)
            
            # Get images and grids
            images = generator.get_images()
            grids = generator.get_grids()
            
            batch_loss = 0.0
            
            # Process each image in the batch
            for img, (x_grid, y_grid) in zip(images, grids):
                # Convert numpy arrays to PyTorch tensors
                img_tensor = torch.from_numpy(img).unsqueeze(0).unsqueeze(0).float().to(device)
                
                x_grid_tensor = torch.from_numpy(x_grid).unsqueeze(0).unsqueeze(0).to(device)
                y_grid_tensor = torch.from_numpy(y_grid).unsqueeze(0).unsqueeze(0).to(device)
                
                # Combine into single target tensor
                target_grid = torch.cat([x_grid_tensor, y_grid_tensor], dim=1)
                
                # Forward pass
                predicted_offsets = model(img_tensor)
                
                # Calculate loss
                loss = criterion(predicted_offsets, target_grid)
                batch_loss += loss.item()
            
            # Average loss for the batch
            avg_batch_loss = batch_loss / len(images) if images else 0
            total_val_loss += avg_batch_loss
            
            file_log.write(f"Validation Batch {batch_idx+1}/{num_val_batches}, Loss: {avg_batch_loss:.6f}\n")
    
        # Average validation loss
        avg_val_loss = total_val_loss / num_val_batches if num_val_batches > 0 else 0
        
        file_log.write(f"Validation completed, Avg Loss: {avg_val_loss:.6f}\n")
    
    return avg_val_loss