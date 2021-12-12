import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import ast
import numpy as np
import cv2
import pandas as pd
def approx_hrm(arr):
    int_arr = [int(*a) for a in arr]
    return sum(int_arr) / len(arr)

def approx_keys(arr):
    keys_n = {}
    for keys_s in arr:
        # print(keys_s)
        for s in keys_s:
            
            # k = ast.literal_eval(s)

            k = s.strip("\n")
            k = k.strip('}"')
            k = k.strip('"{')
            k = k.strip("'")


            if not (k in keys_n.keys()):
                keys_n[k] = 1
            else:
                keys_n[k] += 1
    return keys_n

def approx_mxy(arr):
    d = []
    dxyz = [a for a in arr]
    for xyz in dxyz:
        for delta in xyz:
            d.append(abs(int(delta)))
    return sum(d)

def approx_exy(arr):
    res = []
    for val in arr:
        x, y = [round(float(num)) for num in val]
        if x < 0 or x >= 1920 or y < 0 or y >= 1080:
            continue
        res.append((x, y))
    return res


def get_period_aprox(f, step, pattern):
    res = []
    with open(f) as file:
        line = file.readline()
        line = file.readline()
        while(len(line)):
            timestamp_s = line.split("T")[1].split(".")[0]
            # print(timestamp_s)
            timestamp = datetime.strptime(timestamp_s, "%H:%M:%S")

            for k in range(1000 // step):
                start = timestamp + timedelta(milliseconds=(k) *step)
                stop = timestamp + timedelta(milliseconds=(k+1)*step)
                arr = []
                while(start <= datetime.strptime(line.split("T")[1].split(",")[0], "%H:%M:%S.%f") < stop ):
                    val = line.split(",")[1:]
                    arr.append(val)
                    line = file.readline()
                    if (not len(line)):
                        return res
                # print(start, stop)
                if pattern == "hrm":
                    if (len(arr)):
                        res.append((timestamp_s, k, approx_hrm(arr)))
                if pattern == "keys":
                    res.append((timestamp_s, k, approx_keys(arr)))
                if pattern == "mxy":
                    res.append((timestamp_s, k, approx_mxy(arr)))
                if pattern == "eye":
                    res.append((timestamp_s, k, approx_exy(arr)))
        return res 

def get_period_aprox2(f, timestamp, step, file, pattern):
    res = []
    with open(f) as file:
        line = file.readline()
        while(line.find(datetime.strftime(timestamp, "%H:%M:%S")) == -1):
            line = file.readline()
            if (not len(line)):
                return []

        for k in range(1000 / step):
            start = timestamp
            if (k):
                stop = timestamp + timedelta(miliseconds=(k-1) *step)
            stop = timestamp + timedelta(miliseconds=k*step)
            arr = []
            while(start <= datetime.strftime(line.split("T")[1].split(",")[0], "%H:%M:%S.%f") <= stop ):
                val = line.split(",")[1:]
                arr.append(val)
                line = file.readline()
                if (not len(line)):
                    return res
            
            if pattern == "hrm":
                if (len(arr)):
                    res.append(approx_hrm(arr))
            if pattern == "keys":
                res.append(approx_keys(arr))
            if pattern == "mxy":
                res.append(approx_mxy(arr))
            if pattern == "eye":
                res += approx_exy(arr)
        return res 

def parce_pattern(f, time_int, timestamps, pat_type):
    final_res = []
    half = time_int // 2
    for timestamp in timestamps:
        timestamp_time = datetime.strptime(timestamp, "%H:%M:%S")
        meas_start = timestamp_time - timedelta(seconds=half)
        res = get_period_aprox(f, meas_start, half, file, pat_type) + get_period_aprox(f, timestamp_time, half, file, pat_type)
        final_res.append(res)
    return final_res
     

if __name__ == "__main__":
    path = os.path.join("data", "All_Log")
    server_logs = os.path.join(path, "server_0.log")
    hrm = os.path.join(path, "hrm.csv")
    mkey = os.path.join(path, "mkey.csv")
    keys = os.path.join(path, "key.csv")

    mxy = os.path.join(path, "mxy.csv")
    emg = os.path.join(path, "emg.csv")

    eye = os.path.join(path, "eyetracker.csv")

    kills = []
    with open(server_logs) as file:
        for line in file:
            if (line.find("dium") > 0  and line.find("killed") > 0):
                time = line[15:23]
                kills.append(time)
    
    step = 200

    #EMG
    emg2 = os.path.join(path, "emg2.csv")
    with open(emg) as rd:
        with open(emg2, "w") as wrt:
            for line in rd:
                arr = line.split(",")
                val = arr[-1][12:]
                val = val.strip("}\n")
                H = int(arr[3])
                M = int(arr[4])
                S = int(arr[5])
                ms = arr[9].split(": ")[1]
                timestamp = datetime.strptime(str(H)+":" +str(M)+ ":" +str(S), "%H:%M:%S")
                stime = datetime.strftime(timestamp, "%H:%M:%S")
                new_line = "2021-11-23T"+stime+"."+str(ms)+","+val+"\n"
                wrt.write(new_line)

    res = []
    res_hrm = get_period_aprox(hrm, step, "hrm")
    res.append(res_hrm)
    res_emg = get_period_aprox(hrm, step, "hrm")
    res.append(res_emg)

    res_mkey = get_period_aprox(mkey, step, "keys")
    res.append(res_mkey)
    res_keys = get_period_aprox(keys, step, "keys")
    res.append(res_keys)


    res_mxy = get_period_aprox(mxy, step, "mxy")
    res.append(res_mxy)
    res_eye = get_period_aprox(eye, step, "eye")
    res.append(res_eye)


    min_stamp = min([res_hrm[0][0], res_emg[0][0], res_mkey[0][0], res_keys[0][0], res_mxy[0][0], res_eye[0][0]])
    max_stamp = max([res_hrm[-1][0], res_emg[-1][0], res_mkey[-1][0], res_keys[-1][0], res_mxy[-1][0], res_eye[-1][0]])

    # print([res_hrm[0][0], res_emg[0][0], res_mkey[0][0], res_keys[0][0], res_mxy[0][0], res_eye[0][0]], min_stamp)
    # print([res_hrm[-1][0], res_emg[-1][0], res_mkey[-1][0], res_keys[-1][0], res_mxy[-1][0], res_eye[-1][0]], max_stamp)
    # print(len(res_mxy), len(res_keys), len(res_eye) )
    start_time = datetime.strptime(min_stamp, "%H:%M:%S")
    stop_time = datetime.strptime(max_stamp, "%H:%M:%S")
    
    pd_arr = [[], [], [], [], [], [], []]

    k = [0, 0, 0, 0, 0, 0]
    while(start_time < stop_time):
        stime = datetime.strftime(start_time, "%H:%M:%S")
        for st in range(5):
            for n, k_k in enumerate(k):
                # print("a")
                if (len(res[n])>k_k):
                    tup = res[n][k_k]
                    if tup[0] == stime and tup[1] == st:
                        pd_arr[n].append(tup[2])
                        k[n]+=1
                    else:
                        pd_arr[n].append(None)
                else:
                    pd_arr[n].append(None)
            pd_arr[6].append(stime+":"+str(st))

        start_time = start_time + timedelta(seconds=1)
        # print(start_time)
    # print(pd_arr[0:5])
    # print(np.array(pd_arr).shape)
    d = {'timestamp':pd_arr[6], 'hrm':pd_arr[0], 'emg':pd_arr[1], 'mkey':pd_arr[2], 'keys':pd_arr[3], 'mxy':pd_arr[4], 'eye':pd_arr[5]}
    df = pd.DataFrame(data=d)
    df.to_csv("all.csv", index=False)
    df2 = pd.read_csv("all.csv")
    print(df2.head())


    ##HRM
    # path_to_fig = "kills_hrm"
    # kills_parsed_hrm = parce_pattern(hrm, 60, kills, "hrm")
    # if not os.path.exists(path_to_fig):
    #     os.mkdir(path_to_fig)
    # for n, stamp in enumerate(kills):
    #     plt.clf()
    #     plt.plot(kills_parsed_hrm[n])
    #     plt.savefig(os.path.join(path_to_fig, stamp + ".png"))

    ##MKEYS
    # path_to_fig = "kills_mkey"
    # mkey2 = os.path.join(path, "mkey_upd.csv")
    # with open(mkey) as rd:
    #     with open(mkey2, "w") as wrt:
    #         for line in rd:
    #             if (line.find("{}") == -1):
    #                 wrt.write(line)
    
    # if not os.path.exists(path_to_fig):
    #     os.mkdir(path_to_fig)
    # kills_parsed_mkey = parce_pattern(mkey2, 60, kills, "keys")
    # print(len(kills_parsed_mkey))
    # for n, stamp in enumerate(kills):
    #     left = []
    #     right = []
    #     for d in kills_parsed_mkey[n]:
    #         if ("LEFT" in d.keys()):
    #             left.append(d["LEFT"])
    #         else:
    #             left.append(0)

    #         if ("RIGHT" in d.keys()):
    #             right.append(d["RIGHT"])
    #         else:
    #             right.append(0)
    #     plt.clf()
    #     plt.plot(left)
    #     plt.plot(right)
    #     plt.legend(["LEFT", "RIGHT"])
    #     plt.savefig(os.path.join(path_to_fig, stamp + ".png"))

    ##KEYS
    # path_to_fig = "kills_key"
    # keys2 = os.path.join(path, "key_upd.csv")
    # with open(keys) as rd:
    #     with open(keys2, "w") as wrt:
    #         for line in rd:
    #             # print(line)
    #             if (line.find("{}") == -1):
    #                 wrt.write(line)
    
    # if not os.path.exists(path_to_fig):
    #     os.mkdir(path_to_fig)
    # parced = parce_pattern(keys2, 60, kills, "keys")
    # for n, stamp in enumerate(kills):
        
    #     keys_capt = ["W", "A", "S", "D", "SPACE", "LSHIFT", "LCONTROL"]
    #     keys_capt_n = {}
    #     for l in keys_capt:
    #         keys_capt_n[l] = []
    #     # print(parced[n])
    #     # break
    #     for d in parced[n]:
    #         for k in keys_capt:
    #             if (k in d.keys()):
    #                 keys_capt_n[k].append(d[k])
    #             else:
    #                 keys_capt_n[k].append(0)

    #     folder = os.path.join(path_to_fig, stamp)
    #     if not os.path.exists(folder):
    #         os.mkdir(folder)
    #     for l in keys_capt:
    #         plt.clf()
    #         plt.plot(keys_capt_n[l])
    #         plt.legend(l)
    #         plt.savefig(os.path.join(folder, l+ ".png"))
    
    ##MXY
    # path_to_fig = "kills_mxy"
    # mxy2 = os.path.join(path, "mxy2.csv")
    # with open(mxy) as rd:
    #     with open(mxy2, "w") as wrt:
    #         for line in rd:
    #             if (line.find(",0,0,0") == -1):
    #                 wrt.write(line)
    
    # if not os.path.exists(path_to_fig):
    #     os.mkdir(path_to_fig)
    # parced = parce_pattern(mxy2, 60, kills, "mxy")
    # for n, stamp in enumerate(kills):
    #     plt.clf()
    #     plt.plot(parced[n])
    #     plt.savefig(os.path.join(path_to_fig, stamp + ".png"))

    ##EYES
    # path_to_fig = "kills_eye"
    
    # if not os.path.exists(path_to_fig):
    #     os.mkdir(path_to_fig)
    # parced = parce_pattern(eye, 60, kills, "eye")
    # for n, stamp in enumerate(kills):
    #     img = np.zeros((1080, 1920), dtype=np.uint8)
    #     # print(len(parced[n]))
    #     for x, y in parced[n]:
    #         img[y][x] += 1
    #         # print(img[x][y])

    #     # print(img)
    #     img *= 100
    #     cv2.imwrite(os.path.join(path_to_fig, stamp + ".png"), img)

    ##EMG
    # path_to_fig = "kills_emg"
    # emg2 = os.path.join(path, "emg2.csv")
    # with open(emg) as rd:
    #     with open(emg2, "w") as wrt:
    #         for line in rd:
    #             arr = line.split(",")
    #             val = arr[-1][12:]
    #             val = val.strip("}\n")
    #             H = int(arr[3])
    #             M = int(arr[4])
    #             S = int(arr[5])
    #             timestamp = datetime.strptime(str(H)+":" +str(M)+ ":" +str(S), "%H:%M:%S")
    #             stime = datetime.strftime(timestamp, "%H:%M:%S")
    #             new_line = "2021-11-23T"+stime+","+val+"\n"
    #             wrt.write(new_line)
    # parced = parce_pattern(hrm, 60, kills, "hrm")
    # if not os.path.exists(path_to_fig):
    #     os.mkdir(path_to_fig)
    # for n, stamp in enumerate(kills):
    #     plt.clf()
    #     plt.plot(parced[n])
    #     plt.savefig(os.path.join(path_to_fig, stamp + ".png"))
    # parced = parce_pattern(mxy2, 60, kills, "mxy")
    # for n, stamp in enumerate(kills):
    #     plt.clf()
    #     plt.plot(parced[n])
    #     plt.savefig(os.path.join(path_to_fig, stamp + ".png"))



    

    

            


