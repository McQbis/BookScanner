import torch
from evaluate import evaluate_model
import torch.optim as optim
import os

def train_model(model, 
                generator, 
                device, 
                epochs, 
                criterion, 
                optimizer, 
                num_batches,
                name,
                resume_from_checkpoint=False):
    """
    Train the U-Net model using dynamically generated document images.
    If resume_from_checkpoint=True, resume training from last saved checkpoint.

    Params:
        model: The neural network model to train
        generator: DocumentImageGenerator instance for creating training data
        device: The device to run training on (CPU or GPU)
        epochs: Number of training epochs
        criterion: Loss function
        optimizer: Optimizer instance
        num_batches: Number of mini batches to train on
        name: Name of the model
        resume_from_checkpoint: Whether to resume from a saved checkpoint
    
    Returns:
        The trained model, best validation loss and lists of training and validation losses.
    """
    checkpoint_path = f"../models/{name}_checkpoint.pth"
    start_epoch = 0
    train_losses, val_losses = [], []
    best_val_loss = float('inf')
    best_train_loss = float('inf')
    early_stop_counter_train = 0
    early_stop_counter_val = 0
    images_scales = [0.05, 0.1, 0.2, 0.4, 0.45]
    images_scale = images_scales.pop(0)

    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                    optimizer,
                    mode='min',
                    factor=0.5,
                    patience=5,
                )

    # === Resume training if requested ===
    if resume_from_checkpoint and os.path.exists(checkpoint_path):
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

        start_epoch = checkpoint['epoch'] + 1
        train_losses = checkpoint['train_losses']
        val_losses = checkpoint['val_losses']
        best_val_loss = checkpoint['best_val_loss']
        best_train_loss = checkpoint['best_train_loss']
        early_stop_counter_train = checkpoint['early_stop_counter_train']
        early_stop_counter_val = checkpoint['early_stop_counter_val']
        images_scale = checkpoint['images_scale']
        images_scales = checkpoint['images_scales']

        print(f"Resuming training from epoch {start_epoch}")

    with open("../logs/train.log", "a" if resume_from_checkpoint else "w") as log_file:
        log_file.write(f"Starting training for {epochs} epochs...\n")

        try:
            for epoch in range(start_epoch, epochs):
                model.train()
                epoch_loss = 0.0
                
                for batch_idx in range(num_batches):
                    generator.regenerate_data(image_scale=images_scale)
                    images = generator.get_images()
                    grids = generator.get_grids()
                    
                    if not images:
                        continue
                    
                    batch_loss = 0.0
                    
                    for img, (x_grid, y_grid) in zip(images, grids):
                        img_tensor = torch.from_numpy(img).unsqueeze(0).unsqueeze(0).float().to(device)
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
                scheduler.step(avg_epoch_loss)
                train_losses.append(avg_epoch_loss)
                log_file.write(f"Epoch {epoch+1}/{epochs} completed, Avg Loss: {avg_epoch_loss:.6f}\n")

                if avg_epoch_loss < best_train_loss:
                    best_train_loss = avg_epoch_loss
                    torch.save(model.state_dict(), f"../models/{name}_best_train.pth")
                    log_file.write(f"New best model saved with training loss: {avg_epoch_loss:.6f}\n")
                    early_stop_counter_train = 0
                else:
                    early_stop_counter_train += 1
                    if early_stop_counter_train >= 21:
                        if len(images_scales) > 0:
                            images_scale = images_scales.pop(0)
                            log_file.write(f"No improvement for 21 epochs, switching image scale to {images_scale:.2f}\n")
                            early_stop_counter_train = 0
                            best_train_loss = float('inf')
                            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                                            optimizer,
                                            mode='min',
                                            factor=0.5,
                                            patience=4,
                                        )
                        else:
                            log_file.write("Early stopping triggered.\n")
                            break
                
                if (epoch + 1) % 60 == 0 or epoch == epochs - 1:
                    val_loss = evaluate_model(model, generator, device, criterion, num_batches*2)
                    val_losses.append(val_loss)

                    if val_loss < best_val_loss:
                        best_val_loss = val_loss
                        torch.save(model.state_dict(), f"../models/{name}_best_val.pth")
                        log_file.write(f"New best model saved with validation loss: {val_loss:.6f}\n")
                        early_stop_counter_val = 0
                    else:
                        early_stop_counter_val += 1
                        if early_stop_counter_val >= 3:
                            if len(images_scales) > 0:
                                images_scale = images_scales.pop(0)
                                log_file.write(f"No improvement in evaluation, switching image scale to {images_scale:.2f}\n")
                                early_stop_counter_val = 0
                            else:
                                log_file.write("Early stopping triggered.\n")
                                break
                            
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'scheduler_state_dict': scheduler.state_dict(),
                    'train_losses': train_losses,
                    'val_losses': val_losses,
                    'best_val_loss': best_val_loss,
                    'best_train_loss': best_train_loss,
                    'early_stop_counter_train': early_stop_counter_train,
                    'early_stop_counter_val': early_stop_counter_val,
                    'images_scale': images_scale,
                    'images_scales': images_scales
                }, checkpoint_path)
                log_file.write("Checkpoint saved.\n")    

        except KeyboardInterrupt:
            log_file.write("Training interrupted.\n")
    
    return model, best_val_loss, train_losses, val_losses