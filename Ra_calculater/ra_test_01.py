import pandas as pd
import numpy as np
import os
from scipy.ndimage import gaussian_filter1d

def calculate_ra_iso_gaussian(file_path, cutoff_mm=2.5):
    # (1. 2. データの読み込みと方向判別は前回と同じ)
    skip_rows = 0
    with open(file_path, 'r', encoding='shift_jis', errors='ignore') as f:
        for i, line in enumerate(f):
            if "[測定データ]" in line:
                skip_rows = i + 1
                break

    df = pd.read_csv(file_path, skiprows=skip_rows, encoding='shift_jis')
    df.columns = ['X', 'Y', 'Z']
    df = df.apply(pd.to_numeric, errors='coerce').dropna()
    df = df[df['Z'] != 999]

    x_points, y_points = df['X'].nunique(), df['Y'].nunique()
    main_axis, group_axis = ('X', 'Y') if x_points >= y_points else ('Y', 'X')

    # サンプリングピッチの計算 (mm単位に変換)
    sorted_pos = np.sort(df[main_axis].unique())
    pitch_mm = np.mean(np.diff(sorted_pos)) / 1000  # μm -> mm

    # ISO規定のガウシアン標準偏差 sigma の計算
    # 透過率50%となる周波数が λc となるように設定する
    # 変換式: sigma = (sqrt(ln(2)/2π)) * λc / pitch
    sigma = np.sqrt(np.log(2) / (2 * np.pi**2)) * (cutoff_mm / pitch_mm)

    print(f"--- ISO準拠解析 (ガウシアンフィルタ) ---")
    print(f"λc: {cutoff_mm} mm / Sigma: {sigma:.2f} points")
    print("-" * 55)

    ra_list = []
    line_groups = df.groupby(group_axis)
    
    for group_val, group in line_groups:
        group = group.sort_values(main_axis)
        z = group['Z'].values
        
        if len(z) < (sigma * 3): continue

        # 1. 最小二乗法で傾き除去 (F-演算)
        #z_detrended = z - np.polyval(np.polyfit(np.arange(len(z)), z, 1), np.arange(len(z)))
        z_detrended = z
        # 2. ガウシアンフィルタで「うねり(S-profile)」を抽出
        # mode='nearest'で端部の影響を緩和
        z_wavy = gaussian_filter1d(z_detrended, sigma=sigma, mode='nearest')

        # 3. 元のデータから「うねり」を引いて「粗さ(R-profile)」を抽出
        z_roughness = z_detrended - z_wavy

        ra = np.mean(np.abs(z_roughness))
        ra_list.append(ra)
        
        print(f"Line {group_val:8.1f} | Ra: {ra:.4f} μm")

    if ra_list:
        print("-" * 55)
        print(f"全列平均 Ra: {np.mean(ra_list):.4f} μm")

# 実行
calculate_ra_iso_gaussian(r"Z:\tamura\2026\E-Measure2_data\20%_square_L9\01_no9_20_hori.emd", cutoff_mm=2.5)
#target_file = r"Z:\tamura\2026\E-Measure2_data\20%_square_L9\01_no9_20_hori.emd"