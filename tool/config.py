from typing import Optional
import torch
def get_device():
    """
    自动检测设备
    """
    if torch.cuda.is_available():
        device = 'cuda'
        print(f"🚀 检测到 NVIDIA GPU，将使用 CUDA 加速")
    elif torch.backends.mps.is_available():
        device = 'mps'
        print(f"🚀 检测到 Apple Silicon，将使用 MPS 加速")
    else:
        device = 'cpu'
        print(f"💻 将使用 CPU 运行")
    return device


if __name__ == '__main__':
    get_device()