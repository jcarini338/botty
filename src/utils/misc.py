import time
import random
import ctypes
import numpy as np

from config import Config
from logger import Logger
import cv2
from typing import List, Tuple
import os
from math import cos, sin, dist
import subprocess
from win32con import HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE, HWND_TOP, HWND_BOTTOM, SWP_NOZORDER, SWP_NOOWNERZORDER, HWND_DESKTOP, SWP_NOSENDCHANGING, SWP_SHOWWINDOW, HWND_NOTOPMOST
from win32gui import GetWindowText, SetWindowPos, EnumWindows
import json
import win32api
from collections import OrderedDict


def close_down_d2():
    subprocess.call(["taskkill","/F","/IM","D2R.exe"], stderr=subprocess.DEVNULL)

def set_d2r_always_on_top():
    if os.name == 'nt':
        windows_list = []
        EnumWindows(lambda w, l: l.append((w, GetWindowText(w))), windows_list)
        for w in windows_list:
            if w[1] == "Diablo II: Resurrected":
                SetWindowPos(w[0], HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                print("Set D2R to be always on top")
    else:
        print('OS not supported, unable to set D2R always on top')

def restore_d2r_window_visibility():
    if os.name == 'nt':
        windows_list = []
        EnumWindows(lambda w, l: l.append((w, GetWindowText(w))), windows_list)
        for w in windows_list:
            if w[1] == "Diablo II: Resurrected":
                SetWindowPos(w[0], HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                print("Restored D2R window visibility")
    else:
        print('OS not supported, unable to set D2R always on top')

def wait(min_seconds, max_seconds = None):
    if max_seconds is None:
        max_seconds = min_seconds
    time.sleep(random.uniform(min_seconds, max_seconds))
    return

def kill_thread(thread):
    thread_id = thread.ident
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        Logger.error('Exception raise failure')

def cut_roi(img, roi):
    x, y, width, height = roi
    return img[y:y+height, x:x+width]

def is_in_roi(roi: List[float], pos: Tuple[float, float]):
    x, y, w, h = roi
    is_in_x_range = x < pos[0] < x + w
    is_in_y_range = y < pos[1] < y + h
    return is_in_x_range and is_in_y_range

def color_filter(img, color_range):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    color_mask = cv2.inRange(hsv_img, color_range[0], color_range[1])
    filtered_img = cv2.bitwise_and(img, img, mask=color_mask)
    return color_mask, filtered_img

def hms(seconds: int):
    seconds = int(seconds)
    h = seconds // 3600
    m = seconds % 3600 // 60
    s = seconds % 3600 % 60
    return '{:02d}:{:02d}:{:02d}'.format(h, m, s)

def load_template(path, scale_factor: float = 1.0, alpha: bool = False):
    if os.path.isfile(path):
        try:
            template_img = cv2.imread(path, cv2.IMREAD_UNCHANGED) if alpha else cv2.imread(path)
            template_img = cv2.resize(template_img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_NEAREST)
            return template_img
        except Exception as e:
            print(e)
            raise ValueError(f"Could not load template: {path}")
    return None

def alpha_to_mask(img: np.ndarray):
    # create a mask from template where alpha == 0
    if img.shape[2] == 4:
        if np.min(img[:, :, 3]) == 0:
            _, mask = cv2.threshold(img[:,:,3], 1, 255, cv2.THRESH_BINARY)
            return mask
    return None

def list_files_in_folder(path: str):
    r = []
    for root, _, files in os.walk(path):
        for name in files:
            r.append(os.path.join(root, name))
    return r

def rotate_vec(vec: np.ndarray, deg: float) -> np.ndarray:
    theta = np.deg2rad(deg)
    rot_matrix = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
    return np.dot(rot_matrix, vec)

def unit_vector(vec: np.ndarray) -> np.ndarray:
    return vec / dist(vec, (0, 0))

def run_d2r(path: str):
    Logger.info(f'Execute File : {path}')    
    
    base_path = path.replace( "\D2R.exe", "" );
    video_path = base_path + "\mods\\botty\\botty.mpq\\data\\hd\\global\\video"

    blizzardlogos = video_path + "\\blizzardlogos.webm"
    logoanim = video_path + "\\logoanim.webm"
    modinfo_name = base_path + "\mods\\botty\\botty.mpq\\modinfo.json"

    #Logger.info(f'Base Path : {base_path}')    
    #Logger.info(f'video path : {video_path}')    
    #Logger.info(f'mode path : {blizzardlogos}')    
    path_flag = os.path.isdir(video_path)
    file_flag = os.path.isfile(blizzardlogos)
    file_flag2 = os.path.isfile(logoanim)
    file_flag3 = os.path.isfile(modinfo_name)

    if not path_flag:
        os.makedirs(video_path)
        Logger.info(f'Botty mod not found! will create botty mod')    

    if not file_flag:
        with open(blizzardlogos, 'w'):
            pass

    if not file_flag2:
        with open(logoanim, 'w'):
            pass

    file_data = OrderedDict()
    file_data["name"] = "botty"
    file_data["savepath"] = "../"
    #print( json.dumps(file_data, ensure_ascii=False, indent="\t"))
    if not file_flag3:
        with open(modinfo_name, 'w', encoding="utf-8") as make_file:
            json.dump(file_data, make_file, ensure_ascii=False, indent="\t")
        
    #os.startfile(path + " -mod botty -txt")
    try:
        win32api.WinExec(path + " -mod botty -txt")  # seamless 동작
    except:
       pass
