import pandas as pd
import numpy as np
import os
import glob  # ファイル検索用
from scipy.ndimage import gaussian_filter1d

def calculate_ra_iso_gaussian(file_path, cutoff_mm=2.5):
    """
    1ファイルあたりの解析処理（前回と同じロジック）
    """
    try:
        # --- 1. ファイルの読み込み ---
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

        if df.empty:
            return None

        # --- 2. 軸判定とパラメータ設定 ---
        x_points, y_points = df['X'].nunique(), df['Y'].nunique()
        main_axis, group_axis = ('X', 'Y') if x_points >= y_points else ('Y', 'X')

        sorted_pos = np.sort(df[main_axis].unique())
        pitch_mm = np.mean(np.diff(sorted_pos)) / 1000
        
        # ISOガウシアンフィルタのsigma計算
        iso_const = np.sqrt(np.log(2) / (2 * np.pi**2))
        sigma = iso_const * (cutoff_mm / pitch_mm)

        # --- 3. ラインごとの解析 ---
        ra_list = []
        for _, group in df.groupby(group_axis):
            group = group.sort_values(main_axis)
            z = group['Z'].values
            if len(z) < (sigma * 3): continue

            # 傾き補正
            x_idx = np.arange(len(z))
            z_detrended = z - np.polyval(np.polyfit(x_idx, z, 1), x_idx)

            # ガウシアンフィルタ（うねり除去）
            z_wavy = gaussian_filter1d(z_detrended, sigma=sigma, mode='nearest')
            z_roughness = z_detrended - z_wavy

            ra_list.append(np.mean(np.abs(z_roughness)))

        if ra_list:
            return np.mean(ra_list)
        return None

    except Exception as e:
        print(f"  [!] 解析エラー ({os.path.basename(file_path)}): {e}")
        return None

# --- メイン処理：フォルダ内一括ループ ---

# 1. 対象フォルダのパスを指定
target_dir = r"Z:\tamura\2026\E-Measure2_data\20%_square_L9\vertical_20_L9"

# 2. フォルダ内の .emd ファイルをすべて取得
files = glob.glob(os.path.join(target_dir, "*.emd"))

print(f"解析開始: {len(files)} 個のファイルが見つかりました\n")
print(f"{'ファイル名':<40} | {'平均 Ra (μm)':>12}")
print("-" * 60)

# 3. ループ実行
for f_path in files:
    file_name = os.path.basename(f_path)
    avg_ra = calculate_ra_iso_gaussian(f_path, cutoff_mm=2.5)
    
    if avg_ra is not None:
        print(f"{file_name:<40} | {avg_ra:12.4f}")
    else:
        print(f"{file_name:<40} | 解析スキップ")

print("-" * 60)
print("すべての解析が終了しました。")