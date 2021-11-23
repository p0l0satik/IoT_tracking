import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def approx_hrm(arr):
    int_arr = [int(a) for a in arr]
    return sum(int_arr) / len(arr)


def get_period_aprox(timestamp, interval, file, pattern):
    res = []
    # time_H_M = datetime.strftime(timestamp, "%H:%M")
    with open(hrm) as file:
        line = file.readline()
        while(line.find(datetime.strftime(timestamp, "%H:%M:%S")) == -1):
            line = file.readline()
            if (not len(line)):
                return []

        for sec in range(interval):
            start = timestamp + timedelta(seconds=sec)
            arr = []
            while(line.find(datetime.strftime(start, "%H:%M:%S")) > 0):
                val = line.split(",")[1]
                arr.append(val)
                line = file.readline()
                if (not len(line)):
                    return res
            if (len(arr)):
                if pattern == "hrm":
                    res.append(approx_hrm(arr))
            
        return res 

def parce_pattern(path_to_fig, time_int, timestamps, pat_type):
    final_res = []
    half = time_int // 2
    if not os.path.exists(path_to_fig):
        os.mkdir(path_to_fig)
    for timestamp in timestamps:
        timestamp_time = datetime.strptime(timestamp, "%H:%M:%S")
        meas_start = timestamp_time - timedelta(seconds=half)
        res = get_period_aprox(meas_start, half, file, pat_type) + get_period_aprox(timestamp_time, half, file, pat_type)
        final_res.append(res)
    return final_res
     

if __name__ == "__main__":
    # f = open("data/server_0.log", "r")
    path = os.path.join("data", "SCT")
    server_logs = os.path.join(path, "server_0.log")
    hrm = os.path.join(path, "hrm.csv")
    kills = []
    with open(server_logs) as file:
        for line in file:
            if (line.find("dium") > 0  and line.find("killed") > 0):
                time = line[15:23]
                kills.append(time)

    kills_parsed = parce_pattern("kills_hrm", 60, kills, "hrm")
    for n, stamp in enumerate(kills):
        plt.clf()
        plt.plot(kills_parsed[n])
        plt.savefig(os.path.join("kills_hrm", stamp + ".png"))




    

    

            


