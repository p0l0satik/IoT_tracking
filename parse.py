import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def approx_hrm(arr):
    int_arr = [int(a) for a in arr]
    return sum(int_arr) / len(arr)


def get_period_aprox(kill, interval, file, pattern):
    res = []
    # time_H_M = datetime.strftime(kill, "%H:%M")
    with open(hrm) as file:
        line = file.readline()
        while(line.find(datetime.strftime(kill, "%H:%M:%S")) == -1):
            line = file.readline()
            if (not len(line)):
                return []

        for sec in range(interval):
            start = kill + timedelta(seconds=sec)
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

    final_res = []
    time_int = 60
    half = time_int // 2
    path_to_fig = "kills_hrm"
    if not os.path.exists(path_to_fig):
        os.mkdir(path_to_fig)
    for kill in kills:
        kill_time = datetime.strptime(kill, "%H:%M:%S")
        meas_start = kill_time - timedelta(seconds=half)
        res = get_period_aprox(meas_start, half, file, "hrm") + get_period_aprox(kill_time, half, file, "hrm")
        final_res.append(res)
        plt.clf()
        plt.plot(res)
        plt.savefig(os.path.join(path_to_fig, kill + ".png"))




    

    

            


