import os

import torch
from torch.utils.data import DataLoader

from nn.dataset import AmongUsDataset
from nn.model import LSTMModel, Model
from util.loader import read_all_recordings

import numpy as np

def main():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = LSTMModel().to(device)

    # should be cross binary entropy loss for binary/bool outputs TODO: BCEWITHLOGITSLOSS
    #criterion = torch.nn.CrossEntropyLoss()
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0005)

    games = read_all_recordings()
    # split into train and val
    train_data, val_data = games[:int(len(games) * 0.9)], games[int(len(games) * 0.9):]

    train_dataset = AmongUsDataset(train_data, device)
    val_dataset = AmongUsDataset(val_data, device)

    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=128, shuffle=True)
    
    try:
        for epoch in range(200):
            # train
            model.train()
            training_loss = 0
            for x, y in train_loader:
                optimizer.zero_grad()
                y_pred = model(x)
                loss = criterion(y_pred, y)
                loss.backward()
                
                optimizer.step()
                
                training_loss += loss.item()
            print(f"Epoch {epoch} training loss  : {training_loss / len(train_loader)}")

            # validate
            total_loss = 0
            model.eval()
            for x, y in val_loader:
                y_pred = model(x)
                loss = criterion(y_pred, y)
                total_loss += loss.item()
            print(f"Epoch {epoch} validation loss: {total_loss / len(val_loader)}")
            
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        torch.save(model.state_dict(), os.path.dirname(__file__) + "/model.pt")

if __name__ == "__main__":
    main()
