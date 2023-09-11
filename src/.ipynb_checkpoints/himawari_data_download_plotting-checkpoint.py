import os
import urllib.request
import tarfile
import bz2
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import ftplib
import pandas as pd

def download_file(url, filename, server, band, ftp=False):
    if not os.path.isfile(filename):
        print(f"*** ファイルをダウンロードしています: {filename}")
        if ftp:
            with ftplib.FTP(server) as ftp:
                ftp.login('', '')  # anonymousユーザーでログイン
                ftp.cwd(f'gridded/FD/V20190123/{filename[0:6]}/{band.upper()}')
                with open(filename, 'wb') as fhandle:
                    ftp.retrbinary(f'RETR {filename}', fhandle.write)
        else:
            urllib.request.urlretrieve(url, filename)

def main():
    # 日付範囲と時間範囲(UTC)を指定
    start_date = "20230808"
    end_date = "20230810"
    start_hour = 0
    end_hour = 23
    
    # 千葉大学のサーバ    
    server = "hmwr829gr.cr.chiba-u.ac.jp"
    tail = "fld.geoss.bz2"
    band = "tir"
    ch = "01"
    lon_min, lon_max = 85, 205
    lat_min, lat_max = -60, 60
    pixel_num = 6000
    # ひまわりデータの範囲
    extent_hmwr = (lon_min, lon_max, lat_min, lat_max)

    # データのダウンロードとプロット
    for date in pd.date_range(start=start_date, end=end_date):
        for hour in range(start_hour, end_hour + 1):
            time = f"{hour:02d}00"
            date_time = f"{date.strftime('%Y%m%d')}{time}"

            fname_hmwr = f"{date_time}.{band}.{ch}.{tail}"
            url_hmwr = f'ftp://{server}/{date_time[0:6]}/{band.upper()}/{fname_hmwr}'
            download_file(url_hmwr, fname_hmwr, server, band, ftp=True)
            
              # count2tbbテーブルファイルのダウンロードと解凍
            fname_cnt2tbb = 'count2tbb_v103.tgz'
            url = f'http://www.cr.chiba-u.jp/databases/GEO/H8_9/FD/{fname_cnt2tbb}'

            # ファイルのダウンロード
            if not os.path.isfile(fname_cnt2tbb):
                print("*** 変換テーブルをダウンロードしています：", fname_cnt2tbb)
                urllib.request.urlretrieve(url, fname_cnt2tbb)

            # ファイルの解凍
            if not os.path.isdir(f'count2tbb_v103'):
                print("*** 変換テーブルを解凍しています")
                with tarfile.open(fname_cnt2tbb, "r:gz") as tarin:
                    tarin.extractall()

            # カウント値から黒体放射輝度温度(TBB)への変換テーブルの読み込み
            _, cnt2tbb = np.loadtxt(f'count2tbb_v103/{band}.{ch}', unpack=True)

            #  bz2を使用して，ひまわり画像を開く。
            with bz2.open(fname_hmwr) as bz2fin:
                buf_cnt = bz2fin.read()
                data_cnt = np.frombuffer(buf_cnt, dtype='>u2').reshape(pixel_num, pixel_num)
                
                # 画像データを変換テーブルで変換する
                data_tbb = cnt2tbb[data_cnt]  

            # プロット
            fig = plt.figure(figsize=(294/25.4, 210/25.4))
            out_fig_path = f'{date_time}-himawari_{band}{ch}.png'

            fig.text(0.10, 0.97, f"{date_time} UTC", fontsize=14)
            fig.text(0.10, 0.94, f"BAND:{band}, CH:{ch}", fontsize=14)
            
            mapcrs = ccrs.NorthPolarStereo(central_longitude=140.0, true_scale_latitude=60.0)
            ax = fig.add_axes([0.10, 0.10, 0.75, 0.75], projection=mapcrs)
            ax.add_feature(cfeature.COASTLINE, linewidth=0.5, color="green")
            ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle=':', color="green")
            ax.set_extent([117.0, 156.0, 18.0, 61.0], ccrs.PlateCarree())
            ax.imshow(data_tbb, origin='upper', extent=extent_hmwr, interpolation='none', cmap="gray_r",
                      transform=ccrs.PlateCarree())

            gl = ax.gridlines(xlocs=np.arange(100, 180, 10), ylocs=np.arange(10, 90, 10),
                              linestyle='dashed', color='green', linewidth=0.5, draw_labels=True, x_inline=False, y_inline=False)
            gl.top_labels = False
            gl.right_labels = False

            # 図の保存
            plt.savefig(out_fig_path)

if __name__ == "__main__":
    main()
