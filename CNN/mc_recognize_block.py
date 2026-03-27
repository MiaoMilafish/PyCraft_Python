import torch
from torch import nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import ImageGrab
import time
import pyautogui
import tkinter as tk
import json

with open("idx_to_blockid.json", "r") as f:
    class_map = {int(k): int(v) for k, v in json.load(f).items()}

# CNN卷积神经网络模型
class CNN(nn.Module):
    def __init__(self, num_classes):
        super(CNN, self).__init__() 
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.maxpool = nn.MaxPool2d(kernel_size=2)
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(32*16*16, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = F.relu(self.conv1(x)) 
        x = self.maxpool(x)
        x = F.relu(self.conv2(x))
        x = self.maxpool(x) 
        x = self.flatten(x)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = F.log_softmax(x, dim=1)
        return x
    
num_classes = 19
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = CNN(num_classes=num_classes)
model.load_state_dict(torch.load("minecraft_blocks_model.pth", map_location = device))
model.to(device)
model.eval()

def create_red_box():
    root = tk.Tk()
    root.overrideredirect(True)  # 无边框
    root.attributes('-topmost', True)  # 始终在最前面
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - 64
    y = (screen_height // 2) - 64
    
    root.geometry(f"128x128+{x}+{y}")
    root.configure(bg='') 
    
    canvas = tk.Canvas(root, width=128, height=128, bg='white', highlightthickness=0)
    canvas.pack()
    
    canvas.create_rectangle(2, 2, 126, 126, outline='red', width=2, fill='')
    root.wm_attributes('-transparentcolor', 'white')
    return root

red_box = create_red_box()

def recognize_blocks(device, model):
    screen_w, screen_h = pyautogui.size()
    left = (screen_w / 2) -64
    top = (screen_h / 2) - 64
    right = (screen_w / 2) + 64
    bottom = (screen_h / 2) + 64

    red_box.update()

    screenshot = ImageGrab.grab(bbox=(int(left), int(top), int(right), int(bottom)))

    preprocess = transforms.Compose([
    transforms.Resize((64, 64)), 
    transforms.ToTensor(),       
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])
    img_tensor = preprocess(screenshot).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(img_tensor)
        _,predicted_idx = torch.max(output, 1)
    return predicted_idx.item()

# class_map ={0:"1", 1:"2", 2:"3", 3:"4", 4:"5", 5:"7", 6:"12", 7:"13", 8:"17", 9:"18", 10:"24", 11:"35", 12:"41", 13:"42", 14:"43", 15:"44", 16:"45", 17:"46", 18:"47", 19:"48", 20:"49", 21:"54", 22:"56", 23:"57", 24:"58", 25:"60", 26:"61", 27:"73", 28:"78", 29:"79", 30:"82", 31:"89", 32:"98", 33:"103", 34:"246", 35:"247"}
# class_map ={0:"1", 1:"2", 2:"3", 3:"5", 4:"12", 5:"18", 6:"35", 7:"41", 8:"45", 9:"46", 10:"48", 11:"56", 12:"57", 13:"73", 14:"79", 15:"80", 16:"89", 17:"103", 18:"247"}

while True:     
    predict_num = recognize_blocks(device,model)
    block_id = class_map[predict_num]
    print(f"Block Id:{block_id}")
    time.sleep(0.1)

# run:
    # $env:KMP_DUPLICATE_LIB_OK='TRUE'
    # D:\conda\python.exe .\mc_recognize_block.py

