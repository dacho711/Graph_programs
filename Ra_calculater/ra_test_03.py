import pandas as pd
import numpy as np
import os
import glob
from scipy.ndimage import gaussian_filter1d

def calculate_ra_iso_gaussian(file_path, cutoff_mm=2.5):
    """
    1ファイルあたりの解析処理。Raを算出して返す。
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

        if df.empty: return None

        # --- 2. 軸判定とパラメータ設定 ---
        x_points, y_points = df['X'].nunique(), df['Y'].nunique()
        main_axis, group_axis = ('X', 'Y') if x_points >= y_points else ('Y', 'X')
        
        sorted_pos = np.sort(df[main_axis].unique())
        pitch_mm = np.mean(np.diff(sorted_pos)) / 1000
        
        # ガウシアンフィルタ用sigma (ISO準拠)
        iso_const = np.sqrt(np.log(2) / (2 * np.pi**2))
        sigma = iso_const * (cutoff_mm / pitch_mm)

        # --- 3. ラインごとの解析 ---
        ra_values = []
        for _, group in df.groupby(group_axis):
            group = group.sort_values(main_axis)
            z = group['Z'].values
            if len(z) < (sigma * 3): continue

            # 傾き補正 (1次)
            z_detrended = z - np.polyval(np.polyfit(np.arange(len(z)), z, 1), np.arange(len(z)))
            # ガウシアンフィルタ
            z_wavy = gaussian_filter1d(z_detrended, sigma=sigma, mode='nearest')
            z_roughness = z_detrended - z_wavy
            
            ra_values.append(np.mean(np.abs(z_roughness)))

        if ra_values:
            return np.mean(ra_values)
        return None

    except Exception as e:
        print(f"  [!] エラー {os.path.basename(file_path)}: {e}")
        return None

# --- メイン処理 ---

# 1. 設定
target_dir = r"Z:\tamura\2026\E-Measure2_data\55%_square_L9_EMeasure_data\horizontal_square_55_L9"
output_csv = os.path.join(target_dir, "analysis_results_hori.csv")

# 2. ファイル収集
files = glob.glob(os.path.join(target_dir, "*.emd"))
results = []

print(f"解析開始: {len(files)} 件のファイルを処理します...")

# 3. ループ処理
for f_path in files:
    file_name = os.path.basename(f_path)
    avg_ra = calculate_ra_iso_gaussian(f_path, cutoff_mm=2.5)
    
    if avg_ra is not None:
        results.append({"FileName": file_name, "Ra_um": avg_ra})
        print(f" 完了: {file_name} -> Ra: {avg_ra:.4f} μm")
    else:
        print(f" スキップ: {file_name}")

# 4. 結果をDataFrameにまとめてCSV保存
if results:
    df_results = pd.DataFrame(results)
    # CSV書き出し (encoding='utf-8-sig' にするとExcelで文字化けしません)
    df_results.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print("\n" + "="*50)
    print(f"全解析が終了しました。")
    print(f"結果保存先: {output_csv}")
    print("="*50)
else:
    print("\n解析結果がありませんでした。")