#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File name: neuralnet_handler.py
Author: Maciej Kubiś
Date: 2025-03-24
Description: Class for handling the neural network model training and evaluation.
"""

from data_generator import DocumentImageGenerator
from train import train_model
from evaluate import evaluate_model
import torch
from functools import wraps

def require_model_and_generator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._model is None:
            raise ValueError(f"Cannot execute '{func.__name__}': Model is not set.")
        if self._generator is None:
            raise ValueError(f"Cannot execute '{func.__name__}': Generator is not set.")
        return func(self, *args, **kwargs)
    return wrapper


class NeuralNetHandler:
    def __init__(self, model=None, 
                 generator: DocumentImageGenerator=None, 
                 device: str=None, 
                 epochs: int=30, 
                 learning_rate: float=0.001,
                 num_batches: int=300, 
                 name: str="model"):
        """
        Initialize the NeuralNetHandler class.
        
        Params:
            model: PyTorch model or path to saved model
            generator: DocumentImageGenerator instance for creating training data
            device: Device to run training on (CPU or GPU)
            epochs: Number of training epochs
            learning_rate: Learning rate for optimizer
            num_batches: Number of mini batches to train on
            name: Name of the model
        """
        self._device = torch.device(device)
        print(f"Using device: {self._device}")

        self._epochs = epochs
        self._learning_rate = learning_rate
        self._num_batches = num_batches
        self._name = name

        self._generator = None
        self.set_generator(generator)

        self._optimizer = None
        self._model = None
        self.set_model(model, name)

        self._criterion = torch.nn.MSELoss()
        self._train_losses = []
        self._val_losses = []
        self._best_val_loss = float('inf')

    def set_model(self, model, name: str):
        """
        Set the model to use for training and evaluation.
        
        Params:
            model: PyTorch model or path to saved model
        """
        if model is not None: 

            if isinstance(model, torch.nn.Module):
                self._model = model.to(self._device)
            elif type(model) == str:
                self._model = torch.load(model).to(self._device)
            else:
                ValueError("Invalid model type. Please provide a valid PyTorch model or path to a saved model.")
            self._optimizer = torch.optim.Adam(self._model.parameters(), lr=self._learning_rate)
        else:
            print("Model is None. Please provide a valid model using set_model() method.")

        self._name = name

    def set_generator(self, generator):
        """
        Set the DocumentImageGenerator instance to use for creating training data.
        
        Params:
            generator: DocumentImageGenerator instance
        """
        if generator.__class__.__name__ == "DocumentImageGenerator":
            self._generator = generator
        else:
            ValueError("Invalid generator type. Please provide a valid DocumentImageGenerator instance.")

    @require_model_and_generator
    def set_generator_seed(self, seed: int):
        """
        Set the seed for the DocumentImageGenerator instance.
        
        Params:
            seed: (int) Seed value for random number generation
        """
        self._generator.set_seed(seed)

    @require_model_and_generator
    def get_train_losses(self):
        """
        Get the training losses.
        
        Returns:
            List of training losses
        """
        return self._train_losses
    
    @require_model_and_generator
    def get_val_losses(self):     
        """
        Get the validation losses.
        
        Returns:
            List of validation losses
        """
        return self._val_losses

    @require_model_and_generator
    def train(self, resume_from_checkpoint: bool = False):
        """
        Train the model using the specified generator and hyperparameters.
        
        Params:
            resume_from_checkpoint: (bool) Whether to resume training from last saved checkpoint
        """
        results = train_model(self._model, 
                                self._generator, 
                                self._device, 
                                self._epochs, 
                                self._criterion, 
                                self._optimizer, 
                                self._num_batches,
                                self._name,
                                resume_from_checkpoint=resume_from_checkpoint)
        
        self._model = results[0]
        self._best_val_loss = results[1]
        self._train_losses = results[2]
        self._val_losses = results[3]
        
    @require_model_and_generator
    def evaluate(self):
        """
        Evaluate the model using the validation data.
        """
        self._best_val_loss = evaluate_model(self._model, 
                                            self._generator, 
                                            self._device, 
                                            self._criterion, 
                                            self._num_batches)
        
    @require_model_and_generator
    def save_model(self, path: str):
        """
        Save the trained model to a file.
        
        Params:
            path: (str) Path to save the model to
        """
        torch.save(self._model.state_dict(), path)
        print(f"Model saved to {path}")