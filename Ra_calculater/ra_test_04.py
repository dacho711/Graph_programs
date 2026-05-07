import pandas as pd
import numpy as np
import os
import glob
from scipy.ndimage import gaussian_filter1d

def calculate_ra_iso(file_path, cutoff_mm=2.5, eval_lengths=5):
    """
    ISO 4287 / ISO 16610 準拠 Ra計算
    - ガウシアンフィルタ使用
    - 評価長さ = eval_lengths × cutoff
    - 各サンプリング長さごとにRaを算出し平均
    """

    try:
        # --- 1. ファイル読み込み ---
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

        # --- 2. 軸判定 ---
        x_points, y_points = df['X'].nunique(), df['Y'].nunique()
        main_axis, group_axis = ('X', 'Y') if x_points >= y_points else ('Y', 'X')

        sorted_pos = np.sort(df[main_axis].unique())
        pitch_mm = np.mean(np.diff(sorted_pos)) / 1000.0

        # --- 3. ISOガウシアンフィルタ設定 ---
        iso_const = np.sqrt(np.log(2) / (2 * np.pi**2))
        sigma = iso_const * (cutoff_mm / pitch_mm)

        # --- 4. 評価長さ設定 ---
        sampling_points = int(np.round(cutoff_mm / pitch_mm))  # λc
        total_points = sampling_points * eval_lengths          # 5λc

        ra_all_lines = []

        # --- 5. ラインごと処理 ---
        for _, group in df.groupby(group_axis):

            group = group.sort_values(main_axis)
            z = group['Z'].values

            # 長さチェック
            if len(z) < total_points:
                continue

            # --- 5-1. 中央から評価長さを切り出し ---
            start = (len(z) - total_points) // 2
            z_eval = z[start:start + total_points]

            # --- 5-2. 傾き補正 ---
            x_idx = np.arange(len(z_eval))
            z_detrended = z_eval - np.polyval(np.polyfit(x_idx, z_eval, 1), x_idx)

            # --- 5-3. ガウシアンフィルタ ---
            z_wavy = gaussian_filter1d(z_detrended, sigma=sigma, mode='reflect')
            z_roughness = z_detrended - z_wavy

            # --- 5-4. サンプリング長さごとにRa ---
            ra_segments = []

            for i in range(eval_lengths):
                seg = z_roughness[i * sampling_points:(i + 1) * sampling_points]
                if len(seg) == sampling_points:
                    ra_segments.append(np.mean(np.abs(seg)))

            if ra_segments:
                ra_all_lines.append(np.mean(ra_segments))

        if ra_all_lines:
            return np.mean(ra_all_lines)

        return None

    except Exception as e:
        print(f"[!] エラー {os.path.basename(file_path)}: {e}")
        return None


# --- メイン処理 ---
target_dir = r"Z:\tamura\2026\Kinari_Project\E-Measure2_data\20%_so_L9_EMeasure_data\20%_so_L9_horizontal"
output_csv = os.path.join(target_dir, "analysis_results_iso.csv")

files = glob.glob(os.path.join(target_dir, "*.emd"))
results = []

print(f"解析開始: {len(files)} 件")

for f_path in files:
    file_name = os.path.basename(f_path)
    ra = calculate_ra_iso(f_path, cutoff_mm=2.5)

    if ra is not None:
        results.append({"FileName": file_name, "Ra_um": ra})
        print(f"完了: {file_name} → Ra: {ra:.4f} μm")
    else:
        print(f"スキップ: {file_name}")

if results:
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print("\n保存完了:", output_csv)
else:
    print("\n結果なし")