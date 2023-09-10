import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# pathの定義
data_dir = './windspeed_data/'

# 現地データのヒストグラムによる可視化
def plot_hist(fname):
    file_parts = os.path.splitext(os.path.basename(fname))[0].split('_')
    wind_type = file_parts[0]
    date_time = file_parts[1]
    date = date_time[2:4]
    time = date_time[4:8]
    if 'eastws' == wind_type:
        histdata = np.load(os.path.join(data_dir, 'eastws_08' +date +time +'.npy'))
    else:
        histdata = np.load(os.path.join(data_dir, 'southws_08' +date +time+'.npy'))
    plt.figure()
    sns.histplot(histdata, kde=True, bins=10)
    
    # 横軸の範囲は最小〜最大風速(m/s)にする
    plt.xlim(0, 12)
    plt.xlabel('Wind speed[m/s]', fontsize=15)
    plt.ylabel('Count', fontsize=15)
    plt.title(wind_type +' 2023/08/'+date+' '+time, fontsize=15)
    plt.grid()
    

# plot_hist関数の呼び出し
fname = glob.glob(os.path.join(data_dir, '*.npy'))
[plot_hist(f) for f in fname]