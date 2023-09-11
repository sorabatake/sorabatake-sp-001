import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from windrose import WindroseAxes

# 方角を角度に変換
def convert_wind_direction(direction):
    directions = {
        "東": 90,
        "東北東": 67.5,
        "北東": 45,
        "北北東": 22.5,
        "北": 0,
        "北北西": 337.5,
        "北西": 315,
        "西北西": 292.5,
        "西": 270,
        "西南西": 247.5,
        "南西": 225,
        "南南西": 202.5,
        "南": 180,
        "南南東": 157.5,
        "南東": 135,
        "東南東": 112.5
    }
    # 該当しない場合は0度を返す
    return directions.get(direction, 0)

def load_data(file_path):
    # データ読み込み
    df = pd.read_csv(file_path, encoding='shift_jis', skiprows=28, skipfooter=1, engine='python')
    # 0、1、3列目を抽出
    new_df = df.iloc[:, [0, 1, 3]]
    # 新しいカラム名を設定
    new_df.columns = ['Time', 'ws', 'wd']
    # datetime型に変換
    new_df['time'] = pd.to_datetime(new_df['Time'])
    # 不要な列の削除
    new_df = new_df.drop(['Time'], axis=1)
    return new_df

def plot_hourly_wind_speed(new_df):
    # 日ごとにデータを抽出してプロット
    for day in [8, 9, 10]:
        daily_data = new_df[new_df['time'].dt.day == day]
        day_str = str(day).zfill(2)
        plt.plot(daily_data['time'], daily_data['ws'], label=f'2023-08-{day_str}', marker='o')

    plt.xlabel('Month-Date Hour')
    plt.ylabel('Wind Speed[m/s]')
    plt.title('Hourly Wind Speed')
    plt.legend()
    plt.grid()

def plot_wind_rose(daily_data, day):
    # 角度をラジアンに変換
    wind_direction_degrees = np.array([convert_wind_direction(d) for d in daily_data['wd']])
    wind_direction_radians = np.deg2rad(wind_direction_degrees)

    # ベクトルの成分を計算
    wind_speed = daily_data['ws']

    # 風速データを0から1の範囲にスケーリング
    scaled_wind_speed = (wind_speed - wind_speed.min()) / (wind_speed.max() - wind_speed.min())

    # ベクトルの成分を計算
    u_component = scaled_wind_speed * np.sin(wind_direction_radians)
    v_component = scaled_wind_speed * np.cos(wind_direction_radians)

    # windroseをプロット
    fig = plt.figure(figsize=(8, 8))
    ax = WindroseAxes.from_ax(fig=fig)
    ax.bar(wind_direction_degrees, scaled_wind_speed, opening=0.8, edgecolor='white')

    ax.set_title(f'2023/08/{str(day).zfill(2)} Wind Rose', fontsize=15)
    ax.set_legend()
    #plt.savefig(f'202308{str(day).zfill(2)}_windrose.png')

if __name__ == "__main__":
    file_path = './amedas_dataset.csv'
    new_df = load_data(file_path)
    
    plt.figure(figsize=(10, 5))
    plot_hourly_wind_speed(new_df)
    for day in [8, 9, 10]:
        daily_data = new_df[new_df['time'].dt.day == day]
        plot_wind_rose(daily_data, day)
    
    plt.tight_layout()
    plt.show()
