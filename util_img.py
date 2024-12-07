from PIL import Image
import os
from customtkinter import CTkImage

img_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")

def re_img(img_name, size):
    pil_image = Image.open(os.path.join(img_path, img_name)).resize(size, Image.LANCZOS)
    ct_image = CTkImage(pil_image, size=size)
    
    return ct_image

def open_img(img_name):
    return os.path.join (img_path, img_name)