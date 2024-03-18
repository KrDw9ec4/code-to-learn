#!/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import json
import re

# 从命令行传入视频文件夹和字幕文件夹路径
video_path = sys.argv[1]
subtitle_path = sys.argv[2]

# 用户输入
user_judge_video = True if input('是否需要逐一判断视频文件（y/N）') == 'y' else False
user_judge_subtitle = True if input('是否需要逐一判断字幕文件？（y/N）') == 'y' else False
user_input_video_ext = tuple(input("请输入视频文件的后缀：").split())
user_input_subtitle_ext = tuple(input("请输入字幕文件的后缀：").split())


def user_judge(file_name: str, user_judge_bool: bool) -> bool:
    if user_judge_bool:
        return False if input(f'{file_name}:(y/n)') == 'n' else True
    else:
        return True


def isVideo(file_name: str, video_ext: tuple, user_judge_video: bool = False) -> bool:
    """
    判断文件是否为视频文件

    参数：
    - file_name (str) -- 文件名
    - video_ext (tuple) -- 视频文件扩展名
    - user_judge_video (bool) -- 是否需要逐一判断视频文件

    返回值：
    bool -- 如果文件是视频文件，则返回True；否则返回False
    """
    video_ext_list = ['.mp4', '.mkv', '.avi']
    video_ext_list.extend(video_ext)
    if file_name.endswith(tuple(video_ext_list)) and user_judge(file_name, user_judge_video):
        return True
    else:
        return False


def isSubtitle(file_name: str, subtitle_ext: tuple, user_judge_subtitle: bool = False) -> bool:
    """
    判断文件是否为字幕文件

    参数：
    - file_name (str) -- 文件名
    - subtitle_ext (tuple) -- 字幕文件扩展名
    - user_judge_subtitle (bool) -- 是否需要逐一判断字幕文件

    返回值：
    bool -- 如果文件是字幕文件，则返回True；否则返回False
    """
    subtitle_ext_list = ['.ass', '.srt']
    subtitle_ext_list.extend(subtitle_ext)
    if file_name.endswith(tuple(subtitle_ext_list)) and user_judge(file_name, user_judge_subtitle):
        return True
    else:
        return False


def isFile(file_name: str, file_type: str, file_ext: tuple, user_judge_video: bool = False, user_judge_subtitle: bool = False) -> bool:
    """
    判断文件是否为指定类型的文件

    参数：
    - file_name (str) -- 文件名
    - file_type (str) -- 文件类型（'video'或'subtitle'）
    - file_ext (tuple) -- 文件扩展名
    - user_judge_video (bool) -- 是否需要逐一判断视频文件
    - user_judge_subtitle (bool) -- 是否需要逐一判断字幕文件

    返回值：
    bool -- 如果文件是指定类型的文件，则返回True；否则返回False
    """
    if file_type.lower() == 'video':
        return isVideo(file_name, file_ext, user_judge_video)
    elif file_type.lower() == 'subtitle':
        return isSubtitle(file_name, file_ext, user_judge_subtitle)


def deleteFile(file_list: list, index_to_delete: list):
    new_list = [file_list[x] for x in range(len(file_list)) if x not in index_to_delete]
    return new_list


def get_rclone_files(remote_path: str) -> list:
    temp_files_list = []
    command = ["rclone", "lsjson", remote_path]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if file_list := json.loads(result.stdout):
            for file_info in file_list:
                temp_files_list.append(file_info["Name"])
        return temp_files_list
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        return None


def get_video_files(video_path: str, user_input_video_ext: tuple, user_judge_video: bool) -> list:
    get_files_method = input(f'{video_path} > 请输入获取视频文件的方法（LOCAL/rclone）：')
    if get_files_method.lower() == 'rclone':
        video_temp_files = get_rclone_files(video_path)
    else:
        video_temp_files = os.listdir(video_path)
    # 获取视频文件和字幕文件列表，通过后缀筛选
    video_files = sorted([file for file in video_temp_files if isFile(file, 'video', user_input_video_ext, user_judge_video, False)])
    return video_files


video_files = get_video_files(video_path, user_input_video_ext, user_judge_video)
subtitle_files = sorted([file for file in os.listdir(subtitle_path) if isFile(file, 'subtitle', user_input_subtitle_ext, False, user_judge_subtitle)])

# 开始处理
last_confirm = False
while len(video_files) != len(subtitle_files) and not last_confirm:

    for i in range(min(len(video_files), len(subtitle_files))):
        color_start = '\033[1;37m' if i % 2 != 0 else ''
        color_end = '\033[0m' if i % 2 != 0 else ''
        print(color_start + f'{i}: {video_files[i]}\n{i}: {subtitle_files[i]}' + color_end)

    video_delete_index = [eval(i) for i in input('请输入需要删除的视频文件序号：').split()]
    subtitle_delete_index = [eval(i) for i in input('请输入需要删除的字幕文件序号：').split()]
    video_files = deleteFile(video_files, video_delete_index)
    subtitle_files = deleteFile(subtitle_files, subtitle_delete_index)

    last_confirm = True if input('是否确认？(y/N)') == 'y' else False

# 开始重命名字幕文件
split_pattern = re.compile(r'(^.*?)(\.[a-zA-Z0-9]+?$)')
log_string = ''
for i in range(min(len(video_files), len(subtitle_files))):
    new_subtitle_name = split_pattern.match(video_files[i]).group(1) + split_pattern.match(subtitle_files[i]).group(2)
    os.rename(os.path.join(subtitle_path, subtitle_files[i]), os.path.join(subtitle_path, new_subtitle_name))
    log_string += f'{subtitle_files[i]} -> \n{new_subtitle_name} -> \n{video_files[i]} \n---'

with open('subtitle_rename.log', 'w') as f:
    f.write(log_string)
