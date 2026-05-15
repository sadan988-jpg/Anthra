"""
============================================================
 Facial Disease Classifier Training Script
 Model: EfficientNet-B0 (Transfer Learning)
 
 DATASET SETUP INSTRUCTIONS:
 ----------------------------
 Create this folder structure inside the project root:
 
   face_dataset/
     train/
       Oncology/          <- ~100+ images of cancer/chemo patients
       Hyperthyroidism/   <- ~100+ images of exophthalmos patients
       Down_Syndrome/     <- ~100+ images of trisomy 21 patients
       Beta_Thalassemia/  <- ~100+ images of thalassemia patients
       Leprosy/           <- ~100+ images of leprosy patients
       Healthy/           <- ~200+ images of healthy faces
     val/
       (same structure)
 
 Free Dataset Sources:
 - DermNet NZ: https://dermnetnz.org/
 - Kaggle Facial Disease: search 'facial disease recognition'
 - NIH Open-I: https://openi.nlm.nih.gov/
 - ISIC Archive (skin): https://www.isic-archive.com/
============================================================
"""

import torch
import torch.nn as nn
import torchvision
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import os

# ── Configuration ────────────────────────────────────────
DATASET_DIR = "face_dataset"
MODEL_SAVE_PATH = "face_disease_model.pth"
NUM_CLASSES = 6     # Oncology, Hyperthyroidism, Down_Syndrome, Beta_Thalassemia, Leprosy, Healthy
EPOCHS = 20
BATCH_SIZE = 16
LR = 1e-4
IMG_SIZE = 224
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASS_NAMES = ["Beta_Thalassemia", "Down_Syndrome", "Healthy", 
               "Hyperthyroidism", "Leprosy", "Oncology"]
# ─────────────────────────────────────────────────────────

def get_transforms():
    train_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    val_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    return train_tf, val_tf

def build_model(num_classes):
    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
    # Freeze base layers
    for param in model.features.parameters():
        param.requires_grad = False
    # Replace the classifier head
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    return model.to(DEVICE)

def train():
    train_tf, val_tf = get_transforms()
    train_dir = os.path.join(DATASET_DIR, "train")
    val_dir = os.path.join(DATASET_DIR, "val")
    
    if not os.path.exists(train_dir):
        print(f"ERROR: Dataset not found at '{train_dir}'")
        print("Please follow the dataset setup instructions at the top of this file.")
        return

    train_ds = datasets.ImageFolder(train_dir, transform=train_tf)
    val_ds = datasets.ImageFolder(val_dir, transform=val_tf)
    
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    
    class_names = train_ds.classes
    print(f"Classes detected: {class_names}")
    print(f"Training on {DEVICE}...")
    
    model = build_model(len(class_names))
    optimizer = torch.optim.Adam(model.classifier[1].parameters(), lr=LR)
    criterion = nn.CrossEntropyLoss()
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
    
    best_acc = 0.0
    for epoch in range(EPOCHS):
        model.train()
        train_loss, train_correct = 0.0, 0
        
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            train_correct += (outputs.argmax(1) == labels).sum().item()
        
        model.eval()
        val_correct, val_total = 0, 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                outputs = model(imgs)
                val_correct += (outputs.argmax(1) == labels).sum().item()
                val_total += labels.size(0)
        
        val_acc = val_correct / val_total
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {train_loss/len(train_loader):.3f} | Val Acc: {val_acc:.2%}")
        
        if val_acc > best_acc:
            best_acc = val_acc
            # Save model weights and class names together
            torch.save({
                "model_state": model.state_dict(),
                "class_names": class_names
            }, MODEL_SAVE_PATH)
            print(f"  ✓ Best model saved ({best_acc:.2%})")
        
        scheduler.step()
    
    print(f"\nTraining complete. Best accuracy: {best_acc:.2%}")
    print(f"Model saved to: {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train()
