from yt_dlp import YoutubeDL
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter import filedialog
import threading
from PIL import Image, ImageTk
import os
import shutil
from ctypes import windll
import subprocess
import speedtest
import json
from win11toast import toast
import win32gui
import win32process
import psutil
import copy
import time
import re


def btn1_push():

    global data_list, data_download, data_downloaded, temp_state, data_list_state

    if temp_state[0] != "pause":
        if os.path.exists("temp\\information\\list.txt"):
            os.remove("temp\\information\\list.txt")
        if not os.path.exists(place["video"]):
            os.makedirs(place["video"])
        if not os.path.exists(place["audio"]):
            os.makedirs(place["audio"])
        if not os.path.exists(place["thumbnail"]):
            os.makedirs(place["thumbnail"])
        if not os.path.exists(place["comment"]):
            os.makedirs(place["comment"])
        data_list_state = False
        data_download = -1
        data_downloaded = 0
        canvas.delete("data")
        checkbox1.place_forget()
        lbl.configure(
            text=""
        )
        entry.config(
            state=tk.DISABLED
        )
        btn1.config(
            state=tk.DISABLED,
            text="動画情報を取得中..."
        )
        btn2.config(
            state=tk.DISABLED,
            text="動画を保存(無効)"
        )
        btn3.config(
            state=tk.DISABLED,
            text="音声を保存(無効)"
        )
        btn4.config(
            state=tk.DISABLED
        )
        btn5.config(
            state=tk.DISABLED
        )
        btn6.config(
            state=tk.DISABLED,
            text="サムネイルを保存(無効)"
        )
        btn7.config(
            state=tk.DISABLED,
            text="コメントを保存(無効)"
        )
    spinbox.config(
        state=tk.DISABLED
    )
    btn8.config(
        state=tk.DISABLED
    )
    temp_state[0] = "run"
    thread_data = threading.Thread(target=data, daemon=True)
    thread_data.start()


def data():

    global thumbnail_number, data_list, data_download, temp_state, finished, data_list_state

    thumbnail_number = 0

    try:
        if data_list_state == False:
            data_list = []
            temp_state[1] = subprocess.Popen(
                'yt-dlp -s --flat-playlist --print-to-file "%(webpage_url)s" "temp\\information\\list.txt" "{}" --socket-timeout 60 -R 10 --file-access-retries 10 --fragment-retries 10 --retry-sleep 5'.format(entry.get()), shell=True)
            temp_state[1].wait()
            with open("temp\\information\\list.txt", "r", encoding="utf-8") as f:
                data_list = [[line] for line in f.read().split("\n")]
                data_list.pop(-1)
    except:
        entry.config(
            state=tk.NORMAL
        )
        spinbox.config(
            state="readonly"
        )
        btn1.config(
            state=tk.NORMAL,
            text="動画情報を取得"
        )
        btn8.config(
            state=tk.NORMAL
        )
        temp_state[0] = "ready"
    else:
        data_list_state = True
        btn1.config(
            state=tk.DISABLED,
            text=f"動画情報取得中...   {data_downloaded} / {len(data_list)}"
        )
        finished = 0
        for _ in range(number):
            if data_download <= len(data_list) - 2:
                data_download += 1
                thread_data = threading.Thread(
                    target=temp_download, args=(data_download,), daemon=True)
                thread_data.start()


def temp_download(a):

    global data_download, data_downloaded, load, download_list, video_state, audio_state, thumbnail_state, comment_state, finished
    for _ in range(10):
        try:
            with YoutubeDL(option) as ydl:
                res = ydl.extract_info(data_list[a][0])
        except:
            pass
        else:
            if "fulltitle" in res:
                data_list[a].append(
                    re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '-', res["fulltitle"]))
            elif "title" in res:
                data_list[a].append(
                    re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '-', res["title"]))
            else:
                data_list[a].append("タイトルなし")

            if "is_live" in res:
                if res["is_live"] == True:
                    data_list.append("LIVE")
                elif "duration_string" in res:
                    data_list[a].append(res["duration_string"])
                else:
                    data_list[a].append(None)
            elif "duration_string" in res:
                data_list[a].append(res["duration_string"])
            else:
                data_list[a].append(None)

            if "id" in res:
                data_list[a].append(
                    re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '-', res["id"]))
            else:
                data_list[a].append(time.time())

            data_list[a].extend([True, "not yet", None])
            break

    subprocess.run('yt-dlp -i --skip-download -o "temp\\information\\{}.%(ext)s" --write-thumbnail --convert-thumbnails png --socket-timeout 60 --embed-thumbnail -R 10 --file-access-retries 10 --retry-sleep 5 --embed-metadata --xattrs -N 10 {}'.format(
        data_list[a][3], data_list[a][0]), shell=True)

    data_downloaded += 1
    if temp_state[0] == "run":
        btn1.config(
            state=tk.DISABLED,
            text=f"動画情報取得中...   {data_downloaded} / {len(data_list)}"
        )

        if data_downloaded == len(data_list):
            temp_state[0] = "ready"
            video_state = "ready"
            audio_state = "ready"
            thumbnail_state = "ready"
            comment_state = "ready"
            thread_notification = threading.Thread(
                target=notification, args=(0,), daemon=True)
            thread_notification.start()
            for i in range(len(data_list) - 1, -1, -1):
                if len(data_list[i]) == 1:
                    data_list.pop(i)
            with Image.open(f"temp\\information\\{data_list[thumbnail_number][3]}.png") as img:
                w = img.width
                h = img.height
                if w / 16 >= h / 9:
                    img = img.resize((int(w * (800 / w)), int(h * (800 / w))))
                else:
                    img = img.resize((int(w * (450 / h)), int(h * (450 / h))))
                load = ImageTk.PhotoImage(img)
            canvas.delete("data")
            canvas.create_image(
                400,
                245,
                image=load,
                anchor=tk.CENTER,
                tag="data"
            )
            canvas.create_text(
                1,
                1,
                text=f" {thumbnail_number + 1} / {len(data_list)}   {data_list[thumbnail_number][1]}   ({data_list[thumbnail_number][2]})",
                anchor=tk.NW,
                font=("游ゴシック", 10),
                tag="data"
            )

            download_list = []
            for i in data_list:
                if i[4] == True:
                    download_list.append(i)
            bln1.set(data_list[thumbnail_number][4])
            checkbox1.place(x=790, y=280, anchor=tk.CENTER)
            lbl.configure(
                text=f"{str(len(download_list))} / {str(len(data_list))} 選択中"
            )
            entry.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            btn1.config(
                state=tk.NORMAL,
                text="動画情報を取得"
            )
            btn2.config(
                state=tk.NORMAL,
                text="動画を保存"
            )
            btn3.config(
                state=tk.NORMAL,
                text="音声を保存"
            )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            btn6.config(
                state=tk.NORMAL,
                text="サムネイルを保存"
            )
            btn7.config(
                state=tk.NORMAL,
                text="コメントを保存"
            )
            btn8.config(
                state=tk.NORMAL
            )

        if data_download <= len(data_list) - 2:
            data_download += 1
            thread_data = threading.Thread(
                target=temp_download, args=(data_download,), daemon=True)
            thread_data.start()

    else:
        finished += 1
        btn1.config(
            state=tk.DISABLED,
            text=f"動画情報取得中...   {data_downloaded} / {len(data_list)}"
        )
        if finished == number or data_downloaded == len(data_list):
            if temp_state[0] == "pause":
                spinbox.config(
                    state="readonly"
                )
                btn1.config(
                    state=tk.NORMAL,
                    text="動画情報を取得(一時停止中)"
                )
                btn8.config(
                    state=tk.NORMAL
                )
            else:
                entry.config(
                    state=tk.NORMAL
                )
                spinbox.config(
                    state="readonly"
                )
                btn1.config(
                    state=tk.NORMAL,
                    text="動画情報を取得"
                )
                btn8.config(
                    state=tk.NORMAL
                )


def temp_menu(e):
    try:
        if temp_state[0] == "run":
            temp_m.post(e.x_root, e.y_root)
    except:
        pass


def temp_pause():

    global temp_state

    try:
        temp_state[0] = "pause"
        subprocess.run(f"taskkill /F /PID {temp_state[1].pid} /T", shell=True)
    except:
        pass


def temp_stop():

    global temp_state

    try:
        temp_state[0] = "ready"
        subprocess.run(f"taskkill /F /PID {temp_state[1].pid} /T", shell=True)
    except:
        pass


def btn2_push():

    global video_list, download_list, subtitle_task, video_state

    queue.append("video")
    if video_state == "ready":
        video_list = copy.deepcopy(download_list)
        subtitle_task = [None for _ in range(len(video_list))]
        if debug == True:
            try:
                shutil.rmtree("video")
                os.mkdir("video")
            except:
                pass
        if os.path.exists("temp\\video"):
            shutil.rmtree("temp\\video")
            os.mkdir("temp\\video")
    if bool(video_list):
        btn9.config(
            state=tk.DISABLED
        )
        if bln3.get() or len(queue) < 2:
            select.config(
                state=tk.DISABLED
            )
            checkbox1.config(
                state=tk.DISABLED
            )
            checkbox2.config(
                state=tk.DISABLED
            )
            checkbox3.config(
                state=tk.DISABLED
            )
            spinbox.config(
                state=tk.DISABLED
            )
            btn1.config(
                state=tk.DISABLED,
                text="動画情報を取得(無効)"
            )
            btn4.config(
                state=tk.DISABLED
            )
            btn5.config(
                state=tk.DISABLED
            )
            btn8.config(
                state=tk.DISABLED
            )
            thread_btn2 = threading.Thread(target=btn2_thread, daemon=True)
            thread_btn2.start()
        else:
            btn2.config(
                state=tk.DISABLED,
                text="動画を保存(待機中)"
            )
            video_state = "waiting"
    else:
        queue.remove("video")
        video_state = "ready"


def btn2_thread():

    global video_list, video_state

    video_state = "run"
    btn2.config(
        state=tk.DISABLED,
        text=f"動画を保存中...   {len([i for i in range(len(video_list)) if video_list[i][5] == 'done'])} / {len(video_list)}"
    )
    for _ in range(number):
        b = [i for i in range(len(video_list))
             if video_list[i][5] == "not yet"]
        if bool(b):
            video_list[b[0]][5] = "in process"
            thread_video = threading.Thread(
                target=video, args=(b[0],), daemon=True)
            thread_video.start()


def video(a):

    global video_list, video_state

    if video_list[a][2] == "LIVE":
        subtitle_task[a] = subprocess.Popen(
            'yt-dlp --live-from-start --skip-download --write-sub -o "temp\\video\\{}_({}).%(ext)s" --socket-timeout 60 -R 10 --file-access-retries 10 --fragment-retries 10 --retry-sleep 5 {}'.format(video_list[a][1], video_list[a][3], video_list[a][0]))
        if v.get() == "利用可能な最高値":
            video_list[a][6] = subprocess.Popen(
                'yt-dlp --live-from-start -i -f bv*+ba[ext=m4a]/b -o "temp\\video\\{}_({}).%(ext)s" --merge-output-format mp4 --socket-timeout 60 --embed-thumbnail -R 10 --file-access-retries 10 --fragment-retries 10 --retry-sleep 5 --embed-metadata --xattrs -N 10 {}'.format(video_list[a][1], video_list[a][3], video_list[a][0]))
        else:
            video_list[a][6] = subprocess.Popen('yt-dlp --live-from-start -i -f bv*[height<=?{}]+ba[ext=m4a]/b -o "temp\\video\\{}_({}).%(ext)s" --merge-output-format mp4 --socket-timeout 60 --embed-thumbnail -R 10 --file-access-retries 10 --fragment-retries 10 --retry-sleep 5 --embed-metadata --xattrs -N 10 {}'.format(
                v.get()[:v.get().find('p')], video_list[a][1], video_list[a][3], video_list[a][0]))
    else:
        if v.get() == "利用可能な最高値":
            video_list[a][6] = subprocess.Popen(
                'yt-dlp --live-from-start -i -f bv*+ba[ext=m4a]/b -o "temp\\video\\{}_({}).%(ext)s" --merge-output-format mp4 --socket-timeout 60 --embed-thumbnail -R 10 --file-access-retries 10 --fragment-retries 10 --retry-sleep 5 --embed-metadata --xattrs -N 10 --embed-subs --sub-lang all {}'.format(video_list[a][1], video_list[a][3], video_list[a][0]))
        else:
            video_list[a][6] = subprocess.Popen('yt-dlp --live-from-start -i -f bv*[height<=?{}]+ba[ext=m4a]/b -o "temp\\video\\{}_({}).%(ext)s" --merge-output-format mp4 --socket-timeout 60 --embed-thumbnail -R 10 --file-access-retries 10 --fragment-retries 10 --retry-sleep 5 --embed-metadata --xattrs -N 10 --embed-subs --sub-lang all {}'.format(
                v.get()[:v.get().find('p')], video_list[a][1], video_list[a][3], video_list[a][0]))

    video_list[a][6].wait()

    if not bln2.get():
        try:
            os.remove("temp\\video\\{}_({}).live_chat.json".format(
                video_list[a][1], video_list[a][3]))
        except:
            pass

    try:
        res = []
        decoder = json.JSONDecoder()
        with open("temp\\video\\{}_({}).live_chat.json".format(video_list[a][1], video_list[a][3]), "r", encoding="utf-8") as f:
            line = f.readline()
            while line:
                res.append(decoder.raw_decode(line))
                line = f.readline()
        with open("temp\\video\\{}_({}).live_chat.json".format(video_list[a][1], video_list[a][3]), "w", encoding="utf-8") as o:
            json.dump(res, o, ensure_ascii=False, indent=4)
    except:
        pass

    try:
        shutil.copy2("temp\\video\\{}_({}).mp4".format(video_list[a][1], video_list[a][3]), rename(
            "{}\\{}_({}).mp4".format(place["video"], video_list[a][1], video_list[a][3])))
        shutil.copy2("temp\\video\\{}_({}).live_chat.json".format(video_list[a][1], video_list[a][3]), rename(
            "{}\\{}_({}).live_chat.json".format(place["video"], video_list[a][1], video_list[a][3])))
    except:
        pass

    if video_list[a][5] != "not yet":
        video_list[a][5] = "done"

        btn2.config(
            state=tk.DISABLED,
            text=f"動画を保存中...   {len([i for i in range(len(video_list)) if video_list[i][5] == 'done'])} / {len(video_list)}"
        )
    if len([i for i in range(len(video_list)) if video_list[i][5] == "done"]) == len(video_list):
        video_state = "ready"
        thread_notification = threading.Thread(
            target=notification, args=(1,), daemon=True)
        thread_notification.start()
        queue.remove("video")
        select.config(
            state="readonly"
        )
        checkbox2.config(
            state=tk.NORMAL
        )
        btn2.config(
            state=tk.NORMAL,
            text="動画を保存"
        )
        btn9.config(
            state=tk.NORMAL
        )
        if bln3.get():
            if not queue:
                checkbox1.config(
                    state=tk.NORMAL
                )
                checkbox3.config(
                    state=tk.NORMAL
                )
                spinbox.config(
                    state="readonly"
                )
                btn1.config(
                    state=tk.NORMAL,
                    text="動画情報を取得"
                )
                btn3.config(
                    state=tk.NORMAL,
                    text="音声を保存"
                )
                btn4.config(
                    state=tk.NORMAL
                )
                btn5.config(
                    state=tk.NORMAL
                )
                btn6.config(
                    state=tk.NORMAL,
                    text="サムネイルを保存"
                )
                btn7.config(
                    state=tk.NORMAL,
                    text="コメントを保存"
                )
                btn8.config(
                    state=tk.NORMAL
                )

        elif bool(queue):
            if queue[0] == "audio":
                btn3_thread()
            if queue[0] == "thumbnail":
                btn6_thread()
            if queue[0] == "comment":
                btn7_thread()

        else:
            checkbox1.config(
                state=tk.NORMAL
            )
            checkbox3.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            btn1.config(
                state=tk.NORMAL,
                text="動画情報を取得"
            )
            btn3.config(
                state=tk.NORMAL,
                text="音声を保存"
            )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            btn6.config(
                state=tk.NORMAL,
                text="サムネイルを保存"
            )
            btn7.config(
                state=tk.NORMAL,
                text="コメントを保存"
            )
            btn8.config(
                state=tk.NORMAL
            )

    if video_list[a][5] != "not yet":
        b = [i for i in range(len(video_list))
             if video_list[i][5] == "not yet"]
        if bool(b):
            video_list[b[0]][5] = "in process"
            thread_video = threading.Thread(
                target=video, args=(b[0],), daemon=True)
            thread_video.start()


def video_menu(e):
    try:
        if video_state == "run" or video_state == "waiting":
            video_m.post(e.x_root, e.y_root)
    except:
        pass


def video_pause():

    global video_list, video_state

    video_state = "pause"
    try:
        queue.remove("video")
        b = [i for i in range(len(video_list))
             if video_list[i][5] == "in process"]
        for i in b:
            video_list[i][5] = "not yet"
            video_list[i][6].kill()
    except:
        pass
    select.config(
        state="readonly"
    )
    checkbox2.config(
        state=tk.NORMAL
    )
    btn2.config(
        state=tk.NORMAL,
        text="動画を保存(一時停止中)"
    )
    btn9.config(
        state=tk.NORMAL
    )
    if bln3.get():
        if not queue:
            checkbox1.config(
                state=tk.NORMAL
            )
            checkbox3.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            if audio_state == "ready":
                btn3.config(
                    state=tk.NORMAL,
                    text="音声を保存"
                )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            if thumbnail_state == "ready":
                btn6.config(
                    state=tk.NORMAL,
                    text="サムネイルを保存"
                )
            if comment_state == "ready":
                btn7.config(
                    state=tk.NORMAL,
                    text="コメントを保存"
                )
            btn8.config(
                state=tk.NORMAL
            )

    elif bool(queue):
        if queue[0] == "audio" and audio_state == "waiting":
            btn3_thread()
        if queue[0] == "thumbnail" and thumbnail_state == "waiting":
            btn6_thread()
        if queue[0] == "comment" and comment_state == "waiting":
            btn7_thread()

    else:
        checkbox1.config(
            state=tk.NORMAL
        )
        checkbox3.config(
            state=tk.NORMAL
        )
        spinbox.config(
            state="readonly"
        )
        if audio_state == "ready":
            btn3.config(
                state=tk.NORMAL,
                text="音声を保存"
            )
        btn4.config(
            state=tk.NORMAL
        )
        btn5.config(
            state=tk.NORMAL
        )
        if thumbnail_state == "ready":
            btn6.config(
                state=tk.NORMAL,
                text="サムネイルを保存"
            )
        if comment_state == "ready":
            btn7.config(
                state=tk.NORMAL,
                text="コメントを保存"
            )
        btn8.config(
            state=tk.NORMAL
        )


def video_stop():

    global video_list, video_state

    video_state = "ready"
    try:
        queue.remove("video")
        b = [i for i in range(len(video_list))
             if video_list[i][5] == "in process"]
        for i in b:
            video_list[i][5] = "not yet"
            video_list[i][6].kill()
    except:
        pass
    select.config(
        state="readonly"
    )
    checkbox2.config(
        state=tk.NORMAL
    )
    btn2.config(
        state=tk.NORMAL,
        text="動画を保存"
    )
    btn9.config(
        state=tk.NORMAL
    )
    if bln3.get():
        if not queue:
            checkbox1.config(
                state=tk.NORMAL
            )
            checkbox3.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            btn1.config(
                state=tk.NORMAL,
                text="動画情報を取得"
            )
            if audio_state == "ready":
                btn3.config(
                    state=tk.NORMAL,
                    text="音声を保存"
                )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            if thumbnail_state == "ready":
                btn6.config(
                    state=tk.NORMAL,
                    text="サムネイルを保存"
                )
            if comment_state == "ready":
                btn7.config(
                    state=tk.NORMAL,
                    text="コメントを保存"
                )
            btn8.config(
                state=tk.NORMAL
            )

    elif bool(queue):
        if queue[0] == "audio" and audio_state == "waiting":
            btn3_thread()
        if queue[0] == "thumbnail" and thumbnail_state == "waiting":
            btn6_thread()
        if queue[0] == "comment" and comment_state == "waiting":
            btn7_thread()

    else:
        checkbox1.config(
            state=tk.NORMAL
        )
        checkbox3.config(
            state=tk.NORMAL
        )
        spinbox.config(
            state="readonly"
        )
        btn1.config(
            state=tk.NORMAL,
            text="動画情報を取得"
        )
        if audio_state == "ready":
            btn3.config(
                state=tk.NORMAL,
                text="音声を保存"
            )
        btn4.config(
            state=tk.NORMAL
        )
        btn5.config(
            state=tk.NORMAL
        )
        if thumbnail_state == "ready":
            btn6.config(
                state=tk.NORMAL,
                text="サムネイルを保存"
            )
        if comment_state == "ready":
            btn7.config(
                state=tk.NORMAL,
                text="コメントを保存"
            )
        btn8.config(
            state=tk.NORMAL
        )


def btn3_push():

    global audio_list, download_list, audio_state

    queue.append("audio")
    if audio_state == "ready":
        audio_list = copy.deepcopy(download_list)
        if debug == True:
            try:
                shutil.rmtree(place["audio"])
                os.mkdir(place["audio"])
            except:
                pass
        if os.path.exists("temp\\audio"):
            shutil.rmtree("temp\\audio")
            os.mkdir("temp\\audio")
    if bool(audio_list):
        btn10.config(
            state=tk.DISABLED
        )
        if bln3.get() or len(queue) < 2:
            checkbox1.config(
                state=tk.DISABLED
            )
            checkbox3.config(
                state=tk.DISABLED
            )
            spinbox.config(
                state=tk.DISABLED
            )
            btn1.config(
                state=tk.DISABLED,
                text="動画情報を取得(無効)"
            )
            btn4.config(
                state=tk.DISABLED
            )
            btn5.config(
                state=tk.DISABLED
            )
            btn8.config(
                state=tk.DISABLED
            )
            thread_btn3 = threading.Thread(target=btn3_thread, daemon=True)
            thread_btn3.start()
        else:
            btn3.config(
                state=tk.DISABLED,
                text="音声を保存(待機中)"
            )
            audio_state = "waiting"
    else:
        queue.remove("audio")
        audio_state = "ready"


def btn3_thread():

    global audio_list, audio_state

    audio_state = "run"
    btn3.config(
        state=tk.DISABLED,
        text=f"音声を保存中...   {len([i for i in range(len(audio_list)) if audio_list[i][5] == 'done'])} / {len(audio_list)}"
    )

    for _ in range(number):
        b = [i for i in range(len(audio_list))
             if audio_list[i][5] == "not yet"]
        if bool(b):
            audio_list[b[0]][5] = "in process"
            thread_audio = threading.Thread(
                target=audio, args=(b[0],), daemon=True)
            thread_audio.start()


def audio(a):

    global audio_list, audio_state

    audio_list[a][6] = subprocess.Popen('yt-dlp --live-from-start -i -f ba* -x --audio-format mp3 --audio-quality 128K -o "temp\\audio\\{}_({}).%(ext)s" --socket-timeout 60 --embed-thumbnail -R 10 --file-access-retries 10 --fragment-retries 10 --retry-sleep 5 --embed-metadata --xattrs -N 10 {}'.format(
        audio_list[a][1], audio_list[a][3], download_list[a][0]))

    audio_list[a][6].wait()

    try:
        shutil.copy2("temp\\audio\\{}_({}).mp3".format(audio_list[a][1], audio_list[a][3]), rename(
            "{}\\{}_({}).mp3".format(place["audio"], audio_list[a][1], audio_list[a][3])))
    except:
        pass

    if audio_list[a][5] != "not yet":
        audio_list[a][5] = "done"

        btn3.config(
            state=tk.DISABLED,
            text=f"音声を保存中...   {len([i for i in range(len(audio_list)) if audio_list[i][5] == 'done'])} / {len(audio_list)}"
        )
    if len([i for i in range(len(audio_list)) if audio_list[i][5] == 'done']) == len(audio_list):
        audio_state = "ready"
        thread_notification = threading.Thread(
            target=notification, args=(2,), daemon=True)
        thread_notification.start()
        queue.remove("audio")
        btn3.config(
            state=tk.NORMAL,
            text="音声を保存"
        )
        btn10.config(
            state=tk.NORMAL
        )

        if bln3.get():
            if not queue:
                checkbox1.config(
                    state=tk.NORMAL
                )
                checkbox3.config(
                    state=tk.NORMAL
                )
                spinbox.config(
                    state="readonly"
                )
                btn1.config(
                    state=tk.NORMAL,
                    text="動画情報を取得"
                )
                btn2.config(
                    state=tk.NORMAL,
                    text="動画を保存"
                )
                btn4.config(
                    state=tk.NORMAL
                )
                btn5.config(
                    state=tk.NORMAL
                )
                btn6.config(
                    state=tk.NORMAL,
                    text="サムネイルを保存"
                )
                btn7.config(
                    state=tk.NORMAL,
                    text="コメントを保存"
                )
                btn8.config(
                    state=tk.NORMAL
                )

        elif bool(queue):
            if queue[0] == "video":
                btn2_thread()
            if queue[0] == "thumbnail":
                btn6_thread()
            if queue[0] == "comment":
                btn7_thread()

        else:
            checkbox1.config(
                state=tk.NORMAL
            )
            checkbox3.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            btn1.config(
                state=tk.NORMAL,
                text="動画情報を取得"
            )
            btn2.config(
                state=tk.NORMAL,
                text="動画を保存"
            )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            btn6.config(
                state=tk.NORMAL,
                text="サムネイルを保存"
            )
            btn7.config(
                state=tk.NORMAL,
                text="コメントを保存"
            )
            btn8.config(
                state=tk.NORMAL
            )

    if audio_list[a][5] != "not yet":
        b = [i for i in range(len(audio_list))
             if audio_list[i][5] == "not yet"]
        if bool(b):
            audio_list[b[0]][5] = "in process"
            thread_audio = threading.Thread(
                target=audio, args=(b[0],), daemon=True)
            thread_audio.start()


def audio_menu(e):
    try:
        if audio_state == "run" or audio_state == "waiting":
            audio_m.post(e.x_root, e.y_root)
    except:
        pass


def audio_pause():

    global audio_list, audio_state

    audio_state = "pause"
    try:
        queue.remove("audio")
        b = [i for i in range(len(audio_list))
             if audio_list[i][5] == "in process"]
        for i in b:
            audio_list[i][5] = "not yet"
            audio_list[i][6].kill()
    except:
        pass
    btn3.config(
        state=tk.NORMAL,
        text="音声を保存(一時停止中)"
    )
    btn10.config(
        state=tk.NORMAL
    )
    if bln3.get():
        if not queue:
            checkbox1.config(
                state=tk.NORMAL
            )
            checkbox3.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            if video_state == "ready":
                btn2.config(
                    state=tk.NORMAL,
                    text="動画を保存"
                )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            if thumbnail_state == "ready":
                btn6.config(
                    state=tk.NORMAL,
                    text="サムネイルを保存"
                )
            if comment_state == "ready":
                btn7.config(
                    state=tk.NORMAL,
                    text="コメントを保存"
                )
            btn8.config(
                state=tk.NORMAL
            )

    elif bool(queue):
        if queue[0] == "video" and video_state == "waiting":
            btn2_thread()
        if queue[0] == "thumbnail" and thumbnail_state == "waiting":
            btn6_thread()
        if queue[0] == "comment" and comment_state == "waiting":
            btn7_thread()

    else:
        checkbox1.config(
            state=tk.NORMAL
        )
        checkbox3.config(
            state=tk.NORMAL
        )
        spinbox.config(
            state="readonly"
        )
        if video_state == "ready":
            btn2.config(
                state=tk.NORMAL,
                text="動画を保存"
            )
        btn4.config(
            state=tk.NORMAL
        )
        btn5.config(
            state=tk.NORMAL
        )
        if thumbnail_state == "ready":
            btn6.config(
                state=tk.NORMAL,
                text="サムネイルを保存"
            )
        if comment_state == "ready":
            btn7.config(
                state=tk.NORMAL,
                text="コメントを保存"
            )
        btn8.config(
            state=tk.NORMAL
        )


def audio_stop():

    global audio_list, audio_state

    audio_state = "ready"
    try:
        queue.remove("audio")
        b = [i for i in range(len(audio_list))
             if audio_list[i][5] == "in process"]
        for i in b:
            audio_list[i][5] = "not yet"
            audio_list[i][6].kill()
    except:
        pass
    btn3.config(
        state=tk.NORMAL,
        text="音声を保存"
    )
    btn10.config(
        state=tk.NORMAL
    )
    if bln3.get():
        if not queue:
            checkbox1.config(
                state=tk.NORMAL
            )
            checkbox3.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            btn1.config(
                state=tk.NORMAL,
                text="動画情報を取得"
            )
            if video_state == "ready":
                btn2.config(
                    state=tk.NORMAL,
                    text="動画を保存"
                )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            if thumbnail_state == "ready":
                btn6.config(
                    state=tk.NORMAL,
                    text="サムネイルを保存"
                )
            if comment_state == "ready":
                btn7.config(
                    state=tk.NORMAL,
                    text="コメントを保存"
                )
            btn8.config(
                state=tk.NORMAL
            )

    elif bool(queue):
        if queue[0] == "video" and video_state == "waiting":
            btn2_thread()
        if queue[0] == "thumbnail" and thumbnail_state == "waiting":
            btn6_thread()
        if queue[0] == "comment" and comment_state == "waiting":
            btn7_thread()

    else:
        checkbox1.config(
            state=tk.NORMAL
        )
        checkbox3.config(
            state=tk.NORMAL
        )
        spinbox.config(
            state="readonly"
        )
        btn1.config(
            state=tk.NORMAL,
            text="動画情報を取得"
        )
        if video_state == "ready":
            btn2.config(
                state=tk.NORMAL,
                text="動画を保存"
            )
        btn4.config(
            state=tk.NORMAL
        )
        btn5.config(
            state=tk.NORMAL
        )
        if thumbnail_state == "ready":
            btn6.config(
                state=tk.NORMAL,
                text="サムネイルを保存"
            )
        if comment_state == "ready":
            btn7.config(
                state=tk.NORMAL,
                text="コメントを保存"
            )
        btn8.config(
            state=tk.NORMAL
        )


def btn6_push():

    global thumbnail_list, download_list, thumbnail_state

    queue.append("thumbnail")
    if thumbnail_state == "ready":
        thumbnail_list = copy.deepcopy(download_list)
        if debug == True:
            try:
                shutil.rmtree(place["thumbnail"])
                os.mkdir(place["thumbnail"])
            except:
                pass
        if os.path.exists("temp\\thumbnail"):
            shutil.rmtree("temp\\thumbnail")
            os.mkdir("temp\\thumbnail")
    if bool(thumbnail_list):
        btn11.config(
            state=tk.DISABLED
        )
        if bln3.get() or len(queue) < 2:
            checkbox1.config(
                state=tk.DISABLED
            )
            checkbox3.config(
                state=tk.DISABLED
            )
            spinbox.config(
                state=tk.DISABLED
            )
            btn1.config(
                state=tk.DISABLED,
                text="動画情報を取得(無効)"
            )
            btn4.config(
                state=tk.DISABLED
            )
            btn5.config(
                state=tk.DISABLED
            )
            btn8.config(
                state=tk.DISABLED
            )
            thread_btn6 = threading.Thread(target=btn6_thread, daemon=True)
            thread_btn6.start()
        else:
            btn6.config(
                state=tk.DISABLED,
                text="サムネイルを保存(待機中)"
            )
            thumbnail_state = "waiting"
    else:
        queue.remove("thumbnail")
        thumbnail_state = "ready"


def btn6_thread():

    global thumbnail_list, thumbnail_state

    thumbnail_state = "run"
    btn6.config(
        state=tk.DISABLED,
        text=f"サムネイルを保存中...   {len([i for i in range(len(thumbnail_list)) if thumbnail_list[i][5] == 'done'])} / {len(thumbnail_list)}"
    )

    for _ in range(number):
        b = [i for i in range(len(thumbnail_list))
             if thumbnail_list[i][5] == "not yet"]
        if bool(b):
            thumbnail_list[b[0]][5] = "in process"
            thread_thumbnail = threading.Thread(
                target=thumbnail, args=(b[0],), daemon=True)
            thread_thumbnail.start()


def thumbnail(a):

    global thumbnail_list, thumbnail_state

    thumbnail_list[a][6] = subprocess.Popen('yt-dlp -i --skip-download -o "temp\\thumbnail\\{}_({}).%(ext)s" --write-thumbnail --convert-thumbnails png --socket-timeout 60 --embed-thumbnail -R 10 --file-access-retries 10 --retry-sleep 5 --embed-metadata --xattrs -N 10 {}'.format(
        thumbnail_list[a][1], thumbnail_list[a][3], thumbnail_list[a][0],))

    thumbnail_list[a][6].wait()

    try:
        shutil.copy2("temp\\thumbnail\\{}_({}).png".format(thumbnail_list[a][1], thumbnail_list[a][3]), rename(
            "{}\\{}_({}).png".format(place["thumbnail"], thumbnail_list[a][1], thumbnail_list[a][3])))
    except:
        pass

    if thumbnail_list[a][5] != "not yet":
        thumbnail_list[a][5] = "done"

        btn6.config(
            state=tk.DISABLED,
            text=f"サムネイルを保存中...   {len([i for i in range(len(thumbnail_list)) if thumbnail_list[i][5] == 'done'])} / {len(download_list)}"
        )
    if len([i for i in range(len(thumbnail_list)) if thumbnail_list[i][5] == 'done']) == len(thumbnail_list):
        thumbnail_state = "ready"
        thread_notification = threading.Thread(
            target=notification, args=(3,), daemon=True)
        thread_notification.start()
        queue.remove("thumbnail")
        btn6.config(
            state=tk.NORMAL,
            text="サムネイルを保存"
        )
        btn11.config(
            state=tk.NORMAL
        )

        if bln3.get():
            if not queue:
                checkbox1.config(
                    state=tk.NORMAL
                )
                checkbox3.config(
                    state=tk.NORMAL
                )
                spinbox.config(
                    state="readonly"
                )
                btn1.config(
                    state=tk.NORMAL,
                    text="動画情報を取得"
                )
                btn2.config(
                    state=tk.NORMAL,
                    text="動画を保存"
                )
                btn3.config(
                    state=tk.NORMAL,
                    text="音声を保存"
                )
                btn4.config(
                    state=tk.NORMAL
                )
                btn5.config(
                    state=tk.NORMAL
                )
                btn7.config(
                    state=tk.NORMAL,
                    text="コメントを保存"
                )
                btn8.config(
                    state=tk.NORMAL
                )

        elif bool(queue):
            if queue[0] == "video":
                btn2_thread()
            elif queue[0] == "audio":
                btn3_thread()
            elif queue[0] == "comment":
                btn7_thread()

        else:
            checkbox1.config(
                state=tk.NORMAL
            )
            checkbox3.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            btn1.config(
                state=tk.NORMAL,
                text="動画情報を取得"
            )
            btn2.config(
                state=tk.NORMAL,
                text="動画を保存"
            )
            btn3.config(
                state=tk.NORMAL,
                text="音声を保存"
            )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            btn7.config(
                state=tk.NORMAL,
                text="コメントを保存"
            )
            btn8.config(
                state=tk.NORMAL
            )

    if thumbnail_list[a][5] != "not yet":
        b = [i for i in range(len(thumbnail_list))
             if thumbnail_list[i][5] == "not yet"]
        if bool(b):
            thumbnail_list[b[0]][5] = "in process"
            thread_thumbnail = threading.Thread(
                target=thumbnail, args=(b[0],), daemon=True)
            thread_thumbnail.start()


def thumbnail_menu(e):
    try:
        if thumbnail_state == "run" or thumbnail_state == "waiting":
            thumbnail_m.post(e.x_root, e.y_root)
    except:
        pass


def thumbnail_pause():

    global thumbnail_list, thumbnail_state

    thumbnail_state = "pause"
    try:
        queue.remove("thumbnail")
        b = [i for i in range(len(thumbnail_list))
             if thumbnail_list[i][5] == "in process"]
        for i in b:
            thumbnail_list[i][5] = "not yet"
            thumbnail_list[i][6].kill()
    except:
        pass
    btn6.config(
        state=tk.NORMAL,
        text="サムネイルを保存(一時停止中)"
    )
    btn11.config(
        state=tk.NORMAL
    )
    if bln3.get():
        if not queue:
            checkbox1.config(
                state=tk.NORMAL
            )
            checkbox3.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            if video_state == "ready":
                btn2.config(
                    state=tk.NORMAL,
                    text="動画を保存"
                )
            if audio_state == "ready":
                btn3.config(
                    state=tk.NORMAL,
                    text="音声を保存"
                )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            if comment_state == "ready":
                btn7.config(
                    state=tk.NORMAL,
                    text="コメントを保存"
                )
            btn8.config(
                state=tk.NORMAL
            )

    elif bool(queue):
        if queue[0] == "video" and video_state == "waiting":
            btn2_thread()
        elif queue[0] == "audio" and audio_state == "waiting":
            btn3_thread()
        elif queue[0] == "comment" and comment_state == "waiting":
            btn7_thread()

    else:
        checkbox1.config(
            state=tk.NORMAL
        )
        checkbox3.config(
            state=tk.NORMAL
        )
        spinbox.config(
            state="readonly"
        )
        if video_state == "ready":
            btn2.config(
                state=tk.NORMAL,
                text="動画を保存"
            )
        if audio_state == "ready":
            btn3.config(
                state=tk.NORMAL,
                text="音声を保存"
            )
        btn4.config(
            state=tk.NORMAL
        )
        btn5.config(
            state=tk.NORMAL
        )
        if comment_state == "ready":
            btn7.config(
                state=tk.NORMAL,
                text="コメントを保存"
            )
        btn8.config(
            state=tk.NORMAL
        )


def thumbnail_stop():

    global thumbnail_list, thumbnail_state

    thumbnail_state = "ready"
    try:
        queue.remove("thumbnail")
        b = [i for i in range(len(thumbnail_list))
             if thumbnail_list[i][5] == "in process"]
        for i in b:
            thumbnail_list[i][5] = "not yet"
            thumbnail_list[i][6].kill()
    except:
        pass
    btn6.config(
        state=tk.NORMAL,
        text="サムネイルを保存"
    )
    btn11.config(
        state=tk.NORMAL
    )
    if bln3.get():
        if not queue:
            checkbox1.config(
                state=tk.NORMAL
            )
            checkbox3.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            btn1.config(
                state=tk.NORMAL,
                text="動画情報を取得"
            )
            if video_state == "ready":
                btn2.config(
                    state=tk.NORMAL,
                    text="動画を保存"
                )
            if audio_state == "ready":
                btn3.config(
                    state=tk.NORMAL,
                    text="音声を保存"
                )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            if comment_state == "ready":
                btn7.config(
                    state=tk.NORMAL,
                    text="コメントを保存"
                )
            btn8.config(
                state=tk.NORMAL
            )

    elif bool(queue):
        if queue[0] == "video" and video_state == "waiting":
            btn2_thread()
        elif queue[0] == "audio" and audio_state == "waiting":
            btn3_thread()
        elif queue[0] == "comment" and comment_state == "waiting":
            btn7_thread()

    else:
        checkbox1.config(
            state=tk.NORMAL
        )
        checkbox3.config(
            state=tk.NORMAL
        )
        spinbox.config(
            state="readonly"
        )
        btn1.config(
            state=tk.NORMAL,
            text="動画情報を取得"
        )
        if video_state == "ready":
            btn2.config(
                state=tk.NORMAL,
                text="動画を保存"
            )
        if audio_state == "ready":
            btn3.config(
                state=tk.NORMAL,
                text="音声を保存"
            )
        btn4.config(
            state=tk.NORMAL
        )
        btn5.config(
            state=tk.NORMAL
        )
        if comment_state == "ready":
            btn7.config(
                state=tk.NORMAL,
                text="コメントを保存"
            )
        btn8.config(
            state=tk.NORMAL
        )


def btn7_push():

    global comment_list, download_list, comment_state

    queue.append("comment")
    if comment_state == "ready":
        comment_list = copy.deepcopy(download_list)
        if debug == True:
            try:
                shutil.rmtree(place["comment"])
                os.mkdir(place["comment"])
            except:
                pass
        if os.path.exists("temp\\comment"):
            shutil.rmtree("temp\\comment")
            os.mkdir("temp\\comment")
    if bool(comment_list):
        btn12.config(
            state=tk.DISABLED
        )
        if bln3.get() or len(queue) < 2:
            checkbox1.config(
                state=tk.DISABLED
            )
            checkbox3.config(
                state=tk.DISABLED
            )
            spinbox.config(
                state=tk.DISABLED
            )
            btn1.config(
                state=tk.DISABLED,
                text="動画情報を取得(無効)"
            )
            btn4.config(
                state=tk.DISABLED
            )
            btn5.config(
                state=tk.DISABLED
            )
            btn8.config(
                state=tk.DISABLED
            )
            thread_btn7 = threading.Thread(target=btn7_thread, daemon=True)
            thread_btn7.start()
        else:
            btn7.config(
                state=tk.DISABLED,
                text="コメントを保存(待機中)"
            )
            comment_state = "waiting"
    else:
        queue.remove("comment")
        comment_state = "ready"


def btn7_thread():

    global comment_list, comment_state

    comment_state = "run"
    btn7.config(
        state=tk.DISABLED,
        text=f"コメントを保存中...   {len([i for i in range(len(comment_list)) if comment_list[i][5] == 'done'])} / {len(download_list)}"
    )

    for _ in range(number):
        b = [i for i in range(len(comment_list))
             if comment_list[i][5] == 'not yet']
        if bool(b):
            comment_list[b[0]][5] = "in process"
            thread_comment = threading.Thread(
                target=comment, args=(b[0],), daemon=True)
            thread_comment.start()


def comment(a):

    global comment_list, comment_state

    comment_list[a][6] = subprocess.Popen('yt-dlp -i --skip-download --write-comments -o "temp\\comment\\{}_({}).%(ext)s" --socket-timeout 60 -R 10 --file-access-retries 10 --retry-sleep 5 -N 10 {} '.format(
        comment_list[a][1], comment_list[a][3], comment_list[a][0],), shell=True)

    comment_list[a][6].wait()

    try:
        with open("temp\\comment\\{}_({}).info.json".format(comment_list[a][1], comment_list[a][3]), "r", encoding="utf-8") as f:
            dict = json.load(f)
        with open("temp\\comment\\{}_({}).info.json".format(comment_list[a][1], comment_list[a][3]), "w", encoding="utf-8") as o:
            json.dump(dict, o, ensure_ascii=False, indent=4)
    except:
        pass

    try:
        shutil.copy2("temp\\comment\\{}_({}).info.json".format(comment_list[a][1], comment_list[a][3]), rename(
            "{}\\{}_({}).info.json".format(place["comment"], comment_list[a][1], comment_list[a][3])))
    except:
        pass

    if comment_list[a][5] != "not yet":
        comment_list[a][5] = "done"

        btn7.config(
            state=tk.DISABLED,
            text=f"コメントを保存中...   {len([i for i in range(len(comment_list)) if comment_list[i][5] == 'done'])} / {len(download_list)}"
        )
    if len([i for i in range(len(comment_list)) if comment_list[i][5] == 'done']) == len(download_list):
        comment_state = "ready"
        thread_notification = threading.Thread(
            target=notification, args=(4,), daemon=True)
        thread_notification.start()
        queue.remove("comment")
        btn7.config(
            state=tk.NORMAL,
            text="コメントを保存"
        )
        btn12.config(
            state=tk.NORMAL
        )

        if bln3.get():
            if not queue:
                checkbox1.config(
                    state=tk.NORMAL
                )
                checkbox3.config(
                    state=tk.NORMAL
                )
                spinbox.config(
                    state="readonly"
                )
                btn1.config(
                    state=tk.NORMAL,
                    text="動画情報を取得"
                )
                btn2.config(
                    state=tk.NORMAL,
                    text="動画を保存"
                )
                btn3.config(
                    state=tk.NORMAL,
                    text="音声を保存"
                )
                btn4.config(
                    state=tk.NORMAL
                )
                btn5.config(
                    state=tk.NORMAL
                )
                btn6.config(
                    state=tk.NORMAL,
                    text="サムネイルを保存"
                )
                btn8.config(
                    state=tk.NORMAL
                )

        elif bool(queue):
            if queue[0] == "video":
                btn2_thread()
            elif queue[0] == "audio":
                btn3_thread()
            elif queue[0] == "thumbnail":
                btn6_thread()
        else:
            checkbox1.config(
                state=tk.NORMAL
            )
            checkbox3.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            btn1.config(
                state=tk.NORMAL,
                text="動画情報を取得"
            )
            btn2.config(
                state=tk.NORMAL,
                text="動画を保存"
            )
            btn3.config(
                state=tk.NORMAL,
                text="音声を保存"
            )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            btn6.config(
                state=tk.NORMAL,
                text="サムネイルを保存"
            )
            btn8.config(
                state=tk.NORMAL
            )

    if comment_list[a][5] != "not yet":
        b = [i for i in range(len(comment_list))
             if comment_list[i][5] == 'not yet']
        if bool(b):
            comment_list[b[0]][5] = "in process"
            thread_comment = threading.Thread(
                target=comment, args=(b[0],), daemon=True)
            thread_comment.start()


def comment_menu(e):
    try:
        if comment_state == "run" or comment_state == "waiting":
            comment_m.post(e.x_root, e.y_root)
    except:
        pass


def comment_pause():

    global comment_list, comment_state

    comment_state = "pause"
    try:
        queue.remove("comment")
        b = [i for i in range(len(comment_list))
             if comment_list[i][5] == "in process"]
        for i in b:
            comment_list[i][5] = "not yet"
            subprocess.run(
                f"taskkill /F /PID {comment_list[i][6].pid} /T", shell=True)
    except:
        pass
    btn7.config(
        state=tk.NORMAL,
        text="コメントを保存(一時停止中)"
    )
    btn12.config(
        state=tk.NORMAL
    )

    if bln3.get():
        if not queue:
            checkbox1.config(
                state=tk.NORMAL
            )
            checkbox3.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            if video_state == "ready":
                btn2.config(
                    state=tk.NORMAL,
                    text="動画を保存"
                )
            if audio_state == "ready":
                btn3.config(
                    state=tk.NORMAL,
                    text="音声を保存"
                )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            if thumbnail_state == "ready":
                btn6.config(
                    state=tk.NORMAL,
                    text="サムネイルを保存"
                )
            btn8.config(
                state=tk.NORMAL
            )

    elif bool(queue):
        if queue[0] == "video" and video_state == "waiting":
            btn2_thread()
        elif queue[0] == "audio" and audio_state == "waiting":
            btn3_thread()
        elif queue[0] == "thumbnail" and thumbnail_state == "waiting":
            btn6_thread()
    else:
        checkbox1.config(
            state=tk.NORMAL
        )
        checkbox3.config(
            state=tk.NORMAL
        )
        spinbox.config(
            state="readonly"
        )
        if video_state == "ready":
            btn2.config(
                state=tk.NORMAL,
                text="動画を保存"
            )
        if audio_state == "ready":
            btn3.config(
                state=tk.NORMAL,
                text="音声を保存"
            )
        btn4.config(
            state=tk.NORMAL
        )
        btn5.config(
            state=tk.NORMAL
        )
        if thumbnail_state == "ready":
            btn6.config(
                state=tk.NORMAL,
                text="サムネイルを保存"
            )
        btn8.config(
            state=tk.NORMAL
        )


def comment_stop():

    global comment_list, comment_state

    comment_state = "ready"
    try:
        queue.remove("comment")
        b = [i for i in range(len(comment_list))
             if comment_list[i][5] == "in process"]
        for i in b:
            comment_list[i][5] = "not yet"
            subprocess.run(
                f"taskkill /F /PID {comment_list[i][6].pid} /T", shell=True)
    except:
        pass
    btn7.config(
        state=tk.NORMAL,
        text="コメントを保存"
    )
    btn12.config(
        state=tk.NORMAL
    )

    if bln3.get():
        if not queue:
            checkbox1.config(
                state=tk.NORMAL
            )
            checkbox3.config(
                state=tk.NORMAL
            )
            spinbox.config(
                state="readonly"
            )
            btn1.config(
                state=tk.NORMAL,
                text="動画情報を取得"
            )
            if video_state == "ready":
                btn2.config(
                    state=tk.NORMAL,
                    text="動画を保存"
                )
            if audio_state == "ready":
                btn3.config(
                    state=tk.NORMAL,
                    text="音声を保存"
                )
            btn4.config(
                state=tk.NORMAL
            )
            btn5.config(
                state=tk.NORMAL
            )
            if thumbnail_state == "ready":
                btn6.config(
                    state=tk.NORMAL,
                    text="サムネイルを保存"
                )
            btn8.config(
                state=tk.NORMAL
            )

    elif bool(queue):
        if queue[0] == "video" and video_state == "waiting":
            btn2_thread()
        elif queue[0] == "audio" and audio_state == "waiting":
            btn3_thread()
        elif queue[0] == "thumbnail" and thumbnail_state == "waiting":
            btn6_thread()
    else:
        checkbox1.config(
            state=tk.NORMAL
        )
        checkbox3.config(
            state=tk.NORMAL
        )
        spinbox.config(
            state="readonly"
        )
        btn1.config(
            state=tk.NORMAL,
            text="動画情報を取得"
        )
        if video_state == "ready":
            btn2.config(
                state=tk.NORMAL,
                text="動画を保存"
            )
        if audio_state == "ready":
            btn3.config(
                state=tk.NORMAL,
                text="音声を保存"
            )
        btn4.config(
            state=tk.NORMAL
        )
        btn5.config(
            state=tk.NORMAL
        )
        if thumbnail_state == "ready":
            btn6.config(
                state=tk.NORMAL,
                text="サムネイルを保存"
            )
        btn8.config(
            state=tk.NORMAL
        )


def btn8_push():

    thread_sptest = threading.Thread(target=sptest, daemon=True)
    thread_sptest.start()


def sptest():

    global number

    spinbox.config(
        state=tk.DISABLED
    )
    btn1.config(
        state=tk.DISABLED,
        text="動画情報を取得(無効)"
    )
    btn2.config(
        state=tk.DISABLED,
        text="動画を保存(無効)"
    )
    btn3.config(
        state=tk.DISABLED,
        text="音声を保存(無効)"
    )
    btn6.config(
        state=tk.DISABLED,
        text="サムネイルを保存(無効)"
    )
    btn7.config(
        state=tk.DISABLED,
        text="コメントを保存(無効)"
    )
    btn8.config(
        state=tk.DISABLED,
        text="測定中..."
    )

    try:
        for _ in range(10):
            try:
                servers = []
                stest = speedtest.Speedtest(secure=True)
                stest.get_servers(servers)
                stest.get_best_server()
                result = int(stest.download() / 8000000)
                if result == 0:
                    number = 1
                elif result <= os.cpu_count():
                    number = result
                else:
                    number = os.cpu_count()
            except:
                pass
            else:
                spinbox_str.set(number)
                break
    except:
        pass

    spinbox.config(
        state="readonly"
    )
    if temp_state[0] == "pause":
        btn1.config(
            state=tk.NORMAL,
            text=f"動画情報を取得(一時停止中)"
        )
    else:
        btn1.config(
            state=tk.NORMAL,
            text="動画情報を取得"
        )
    btn8.config(
        state=tk.NORMAL,
        text="回線速度測定"
    )
    if bool(download_list):
        if video_state == "pause":
            btn2.config(
                state=tk.NORMAL,
                text="動画を保存(一時停止中)"
            )
        else:
            btn2.config(
                state=tk.NORMAL,
                text="動画を保存"
            )
        if audio_state == "pause":
            btn3.config(
                state=tk.NORMAL,
                text="音声を保存(一時停止中)"
            )
        else:
            btn3.config(
                state=tk.NORMAL,
                text="音声を保存"
            )
        if thumbnail_state == "pause":
            btn6.config(
                state=tk.NORMAL,
                text="サムネイルを保存(一時停止中)"
            )
        else:
            btn6.config(
                state=tk.NORMAL,
                text="サムネイルを保存"
            )
        if comment_state == "pause":
            btn7.config(
                state=tk.NORMAL,
                text=f"コメントを保存(一時停止中)"
            )
        else:
            btn7.config(
                state=tk.NORMAL,
                text="コメントを保存"
            )


def btn9_push():
    file = filedialog.askdirectory(initialdir=place["video"])
    if file != "":
        place["video"] = file
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(place, f, ensure_ascii=False, indent=4)


def videofolder_menu(e):
    btn9_m.post(e.x_root, e.y_root)


def videofolder():
    subprocess.Popen(["explorer", place["video"]], shell=True)


def videofolder_delete():
    if messagebox.askyesno("確認", "フォルダーを空にしますか？"):
        shutil.rmtree(place["video"])
        os.mkdir(place["video"])


def btn10_push():
    file = filedialog.askdirectory(initialdir=place["audio"])
    if file != "":
        place["audio"] = file
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(place, f, ensure_ascii=False, indent=4)


def audiofolder_menu(e):
    btn10_m.post(e.x_root, e.y_root)


def audiofolder():
    subprocess.Popen(["explorer", place["audio"]], shell=True)


def audiofolder_delete():
    if messagebox.askyesno("確認", "フォルダーを空にしますか？"):
        shutil.rmtree(place["audio"])
        os.mkdir(place["audio"])


def btn11_push():
    file = filedialog.askdirectory(initialdir=place["thumbnail"])
    if file != "":
        place["thumbnail"] = file
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(place, f, ensure_ascii=False, indent=4)


def thumbnailfolder_menu(e):
    btn11_m.post(e.x_root, e.y_root)


def thumbnailfolder():
    subprocess.Popen(["explorer", place["thumbnail"]], shell=True)


def thumbnailfolder_delete():
    if messagebox.askyesno("確認", "フォルダーを空にしますか？"):
        shutil.rmtree(place["thumbnail"])
        os.mkdir(place["thumbnail"])


def btn12_push():
    file = filedialog.askdirectory(initialdir=place["comment"])
    if file != "":
        place["comment"] = file
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(place, f, ensure_ascii=False, indent=4)


def commentfolder_menu(e):
    btn12_m.post(e.x_root, e.y_root)


def commentfolder():
    subprocess.Popen(["explorer", place["comment"]], shell=True)


def commentfolder_delete():
    if messagebox.askyesno("確認", "フォルダーを空にしますか？"):
        shutil.rmtree(place["comment"])
        os.mkdir(place["comment"])


def click_L(c):

    global load, thumbnail_number

    if bool(data_list):
        if data_downloaded == len(data_list):
            if len(data_list) != 1:
                if c.x <= 400:
                    if thumbnail_number > 0:
                        thumbnail_number -= 1
                    else:
                        thumbnail_number = len(data_list) - 1
                    img = Image.open(
                        f"temp\\information\\{data_list[thumbnail_number][3]}.png")
                    w = img.width
                    h = img.height
                    if w / 16 >= h / 9:
                        img = img.resize(
                            (int(w * (800 / w)), int(h * (800 / w))))
                    else:
                        img = img.resize(
                            (int(w * (450 / h)), int(h * (450 / h))))
                    load = ImageTk.PhotoImage(img)
                    canvas.delete("data")
                    canvas.create_image(
                        400,
                        245,
                        image=load,
                        anchor=tk.CENTER,
                        tag="data"
                    )
                    canvas.create_text(
                        1,
                        1,
                        text=f" {thumbnail_number + 1} / {len(data_list)}   {data_list[thumbnail_number][1]}   ({data_list[thumbnail_number][2]})",
                        anchor=tk.NW,
                        font=("游ゴシック", 10),
                        tag="data"
                    )
                    bln1.set(data_list[thumbnail_number][4])

                else:
                    if len(data_list) - 1 > thumbnail_number:
                        thumbnail_number += 1
                    else:
                        thumbnail_number = 0
                    img = Image.open(
                        f"temp\\information\\{data_list[thumbnail_number][3]}.png")
                    w = img.width
                    h = img.height
                    if w / 16 >= h / 9:
                        img = img.resize(
                            (int(w * (800 / w)), int(h * (800 / w))))
                    else:
                        img = img.resize(
                            (int(w * (450 / h)), int(h * (450 / h))))
                    load = ImageTk.PhotoImage(img)
                    canvas.delete("data")
                    canvas.create_image(
                        400,
                        245,
                        image=load,
                        anchor=tk.CENTER,
                        tag="data"
                    )
                    canvas.create_text(
                        1,
                        1,
                        text=f" {thumbnail_number + 1} / {len(data_list)}   {data_list[thumbnail_number][1]}   ({data_list[thumbnail_number][2]})",
                        anchor=tk.NW,
                        font=("游ゴシック", 10),
                        tag="data"
                    )
                    bln1.set(data_list[thumbnail_number][4])


def click_R(c):

    global download_list

    if bool(data_list):
        if data_downloaded == len(data_list) and len(queue) == 0:
            if bln1.get():
                bln1.set(False)
                data_list[thumbnail_number][4] = False
            else:
                bln1.set(True)
                data_list[thumbnail_number][4] = True

            download_list = []
            for i in data_list:
                if i[4] == True:
                    download_list.append(i)
            lbl.configure(
                text=f"{str(len(download_list))} / {str(len(data_list))} 選択中"
            )


def Wheel(c):

    global load, thumbnail_number

    if bool(data_list):
        if data_downloaded == len(data_list):
            if len(data_list) != 1:
                if c.delta >= 0:
                    if thumbnail_number > 0:
                        thumbnail_number -= 1
                    else:
                        thumbnail_number = len(data_list) - 1
                    img = Image.open(
                        f"temp\\information\\{data_list[thumbnail_number][3]}.png")
                    w = img.width
                    h = img.height
                    if w / 16 >= h / 9:
                        img = img.resize(
                            (int(w * (800 / w)), int(h * (800 / w))))
                    else:
                        img = img.resize(
                            (int(w * (450 / h)), int(h * (450 / h))))
                    load = ImageTk.PhotoImage(img)
                    canvas.delete("data")
                    canvas.create_image(
                        400,
                        245,
                        image=load,
                        anchor=tk.CENTER,
                        tag="data"
                    )
                    canvas.create_text(
                        1,
                        1,
                        text=f" {thumbnail_number + 1} / {len(data_list)}   {data_list[thumbnail_number][1]}   ({data_list[thumbnail_number][2]})",
                        anchor=tk.NW,
                        font=("游ゴシック", 10),
                        tag="data"
                    )
                    bln1.set(data_list[thumbnail_number][4])

                else:
                    if len(data_list) - 1 > thumbnail_number:
                        thumbnail_number += 1
                    else:
                        thumbnail_number = 0
                    img = Image.open(
                        f"temp\\information\\{data_list[thumbnail_number][3]}.png")
                    w = img.width
                    h = img.height
                    if w / 16 >= h / 9:
                        img = img.resize(
                            (int(w * (800 / w)), int(h * (800 / w))))
                    else:
                        img = img.resize(
                            (int(w * (450 / h)), int(h * (450 / h))))
                    load = ImageTk.PhotoImage(img)
                    canvas.delete("data")
                    canvas.create_image(
                        400,
                        245,
                        image=load,
                        anchor=tk.CENTER,
                        tag="data"
                    )
                    canvas.create_text(
                        1,
                        1,
                        text=f" {thumbnail_number + 1} / {len(data_list)}   {data_list[thumbnail_number][1]}   ({data_list[thumbnail_number][2]})",
                        anchor=tk.NW,
                        font=("游ゴシック", 10),
                        tag="data"
                    )
                    bln1.set(data_list[thumbnail_number][4])


def check():

    global download_list

    data_list[thumbnail_number][4] = bln1.get()

    download_list = []
    for i in data_list:
        if i[4] == True:
            download_list.append(i)
    lbl.configure(
        text=f"{str(len(download_list))} / {str(len(data_list))} 選択中"
    )


def True_all():

    global data_list, download_list

    for i in range(len(data_list)):
        data_list[i][4] = True
    bln1.set(data_list[thumbnail_number][4])

    download_list = []
    for i in data_list:
        if i[4] == True:
            download_list.append(i)
    lbl.configure(
        text=f"{str(len(download_list))} / {str(len(data_list))} 選択中"
    )


def False_all():

    global data_list, download_list

    for i in range(len(data_list)):
        data_list[i][4] = False
    bln1.set(data_list[thumbnail_number][4])

    download_list = []
    for i in data_list:
        if i[4] == True:
            download_list.append(i)
    lbl.configure(
        text=f"{str(len(download_list))} / {str(len(data_list))} 選択中"
    )


def number_change():

    global number

    number = int(spinbox.get())


def notification(a):
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    process = psutil.Process(pid)
    process_path = process.name()
    if process_path != "python.exe":
        if a == 0:
            toast('Downloader', '動画情報のダウンロードが完了しました。', on_click=forground)
        elif a == 1:
            toast('Downloader', '動画のダウンロードが完了しました。', on_click=forground)
        elif a == 2:
            toast('Downloader', '音声のダウンロードが完了しました。', on_click=forground)
        elif a == 3:
            toast('Downloader', 'サムネイルのダウンロードが完了しました。', on_click=forground)
        else:
            toast('Downloader', 'コメントのダウンロードが完了しました。', on_click=forground)


def forground(a):
    root.deiconify()
    root.attributes("-topmost", True)
    root.attributes("-topmost", False)


def key_event(e):
    if btn1["state"] == "normal":
        if e.keysym == "Return":
            btn1_push()


def rename(file_path):
    if os.path.exists(file_path):
        name, ext = os.path.splitext(file_path)
        i = 1
        while True:
            new_name = "{} ({}){}".format(name, i, ext)
            if not os.path.exists(new_name):
                return new_name
            i += 1
    else:
        return file_path


data_list = []
download_list = []
queue = []
number = os.cpu_count()
temp_state = ["ready", None]
debug = True

if os.path.isfile("output.json"):
    with open("output.json", encoding="utf-8") as f:
        place = json.load(f)
else:
    place = {
        "video": "video",
        "audio": "audio",
        "thumbnail": "thumbnail",
        "comment": "comment"
    }
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(place, f, ensure_ascii=False, indent=4)

option = {
    "skip_download": "True",
    "socket_timeout": "60",
    "retries": "10",
    "file_access_retries": "10"
}

root = tk.Tk()
root.bind("<KeyPress>", key_event)
root.geometry("800x750")
root.title("Downloader")

try:
    windll.shcore.SetProcessDpiAwareness(True)
except:
    pass
root.resizable(width=False, height=False)

if os.path.exists("temp"):
    shutil.rmtree("temp")
    os.mkdir("temp")
else:
    os.makedirs("temp")
if os.path.exists("temp\\information"):
    shutil.rmtree("temp\\information")
    os.mkdir("temp\\information")
else:
    os.makedirs("temp\\information")
if os.path.exists("temp\\video"):
    shutil.rmtree("temp\\video")
    os.mkdir("temp\\video")
else:
    os.makedirs("temp\\video")
if os.path.exists("temp\\audio"):
    shutil.rmtree("temp\\audio")
    os.mkdir("temp\\audio")
else:
    os.makedirs("temp\\audio")
if os.path.exists("temp\\thumbnail"):
    shutil.rmtree("temp\\thumbnail")
    os.mkdir("temp\\thumbnail")
else:
    os.makedirs("temp\\thumbnail")
if os.path.exists("temp\\comment"):
    shutil.rmtree("temp\\comment")
    os.mkdir("temp\\comment")
else:
    os.makedirs("temp\\comment")

entry = tk.Entry(
    width=100
)
entry.place(x=400, y=50, anchor=tk.CENTER)
entry.focus_set()

lbl = tk.Label(
    width=25
)
lbl.place(x=650, y=85, anchor=tk.CENTER)

module = ("144p", "240p", "360p", "480p", "720p", "1080p(FHD)",
          "1440p(QHD)", "2160p(4K)", "4320p(8K)", "利用可能な最高値")
v = tk.StringVar()
v.set(module[9])
select = ttk.Combobox(
    width=25,
    state="readonly",
    textvariable=v,
    values=module
)
select.place(x=650, y=115, anchor=tk.CENTER)

spinbox_str = tk.StringVar()
spinbox_str.set(number)
spinbox = tk.Spinbox(
    textvariable=spinbox_str,
    width=10,
    from_=1,
    to=100,
    increment=1,
    state="readonly",
    command=number_change
)
spinbox.place(x=700, y=150, anchor=tk.CENTER)

btn8_push()

btn1 = tk.Button(
    width=30,
    text="動画情報を取得",
    command=btn1_push
)
btn1.place(x=400, y=100, anchor=tk.CENTER)
temp_m = tk.Menu(root, tearoff=0)
temp_m.add_command(label="一時停止", command=temp_pause)
temp_m.add_command(label="中止", command=temp_stop)
btn1.bind("<Button-3>", temp_menu)

btn2 = tk.Button(
    width=30,
    text="動画を保存(無効)",
    command=btn2_push,
    state=tk.DISABLED
)
btn2.place(x=400, y=150, anchor=tk.CENTER)
video_m = tk.Menu(root, tearoff=0)
video_m.add_command(label="一時停止", command=video_pause)
video_m.add_command(label="中止", command=video_stop)
btn2.bind("<Button-3>", video_menu)

btn3 = tk.Button(
    width=30,
    text="音声を保存(無効)",
    command=btn3_push,
    state=tk.DISABLED
)
btn3.place(x=400, y=200, anchor=tk.CENTER)
audio_m = tk.Menu(root, tearoff=0)
audio_m.add_command(label="一時停止", command=audio_pause)
audio_m.add_command(label="中止", command=audio_stop)
btn3.bind("<Button-3>", audio_menu)

btn4 = tk.Button(
    width=10,
    text="すべて選択",
    command=True_all,
    state=tk.DISABLED
)
btn4.place(x=600, y=200, anchor=tk.CENTER)

btn5 = tk.Button(
    width=10,
    text="選択解除",
    command=False_all,
    state=tk.DISABLED
)
btn5.place(x=700, y=200, anchor=tk.CENTER)

btn6 = tk.Button(
    width=30,
    text="サムネイルを保存(無効)",
    command=btn6_push,
    state=tk.DISABLED
)
btn6.place(x=150, y=150, anchor=tk.CENTER)
thumbnail_m = tk.Menu(root, tearoff=0)
thumbnail_m.add_command(label="一時停止", command=thumbnail_pause)
thumbnail_m.add_command(label="中止", command=thumbnail_stop)
btn6.bind("<Button-3>", thumbnail_menu)

btn7 = tk.Button(
    width=30,
    text="コメントを保存(無効)",
    command=btn7_push,
    state=tk.DISABLED
)
btn7.place(x=150, y=200, anchor=tk.CENTER)
comment_m = tk.Menu(root, tearoff=0)
comment_m.add_command(label="一時停止", command=comment_pause)
comment_m.add_command(label="中止", command=comment_stop)
btn7.bind("<Button-3>", comment_menu)

btn8 = tk.Button(
    width=10,
    text="回線速度測定",
    command=btn8_push,
    state=tk.NORMAL
)
btn8.place(x=600, y=150, anchor=tk.CENTER)

btn9 = tk.Button(
    width=20,
    text="動画の保存先指定",
    command=btn9_push,
    state=tk.NORMAL
)
btn9.place(x=130, y=250, anchor=tk.CENTER)
btn9_m = tk.Menu(root, tearoff=0)
btn9_m.add_command(label="フォルダを開く", command=videofolder)
btn9_m.add_command(label="フォルダを空にする", command=videofolder_delete)
btn9.bind("<Button-3>", videofolder_menu)

btn10 = tk.Button(
    width=20,
    text="音声の保存先指定",
    command=btn10_push,
    state=tk.NORMAL
)
btn10.place(x=310, y=250, anchor=tk.CENTER)
btn10_m = tk.Menu(root, tearoff=0)
btn10_m.add_command(label="フォルダを開く", command=audiofolder)
btn10_m.add_command(label="フォルダを空にする", command=audiofolder_delete)
btn10.bind("<Button-3>", audiofolder_menu)

btn11 = tk.Button(
    width=20,
    text="サムネイルの保存先指定",
    command=btn11_push,
    state=tk.NORMAL
)
btn11.place(x=490, y=250, anchor=tk.CENTER)
btn11_m = tk.Menu(root, tearoff=0)
btn11_m.add_command(label="フォルダを開く", command=thumbnailfolder)
btn11_m.add_command(label="フォルダを空にする", command=thumbnailfolder_delete)
btn11.bind("<Button-3>", thumbnailfolder_menu)

btn12 = tk.Button(
    width=20,
    text="コメントの保存先指定",
    command=btn12_push,
    state=tk.NORMAL
)
btn12.place(x=670, y=250, anchor=tk.CENTER)
btn12_m = tk.Menu(root, tearoff=0)
btn12_m.add_command(label="フォルダを開く", command=commentfolder)
btn12_m.add_command(label="フォルダを空にする", command=commentfolder_delete)
btn12.bind("<Button-3>", commentfolder_menu)


canvas = tk.Canvas(
    width=800,
    height=470,
    bg="gray80"
)
canvas.place(x=400, y=515, anchor=tk.CENTER)
canvas.bind("<Button-1>", click_L)
canvas.bind("<Button-3>", click_R)
canvas.bind("<MouseWheel>", Wheel)

bln1 = tk.BooleanVar()
checkbox1 = tk.Checkbutton(
    variable=bln1,
    command=check
)

bln2 = tk.BooleanVar()
checkbox2 = tk.Checkbutton(
    text="チャットデータを保存する(LIVE)",
    variable=bln2
)
checkbox2.place(x=150, y=85, anchor=tk.CENTER)

bln3 = tk.BooleanVar()
checkbox3 = tk.Checkbutton(
    text="同時ダウンロードを許可する",
    variable=bln3
)
checkbox3.place(x=150, y=115, anchor=tk.CENTER)

root.mainloop()
