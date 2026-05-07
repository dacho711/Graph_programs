import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def create_l9_final_report_plot(csv_file="yoko_youin.csv"):
    try:
        # CSV読み込み（1行目が因子名、その下に合計値3つ）
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: {csv_file} が見つかりません。")
        return

    factors_data = []
    all_values = []

    for column_name in df.columns:
        raw_values = df[column_name].tolist()
        if len(raw_values) < 3: continue
        # 合計を3で割って平均を算出
        avgs = [v / 3 for v in raw_values[:3]]
        factors_data.append({'name': column_name, 'avgs': avgs})
        all_values.extend(avgs)

    overall_mean = np.mean(all_values)

    # 図のサイズ調整（因子の数に応じて横に伸ばす）
    num_factors = len(factors_data)
    fig, ax = plt.subplots(figsize=(10/1.2, 4/1.2), dpi=200)
    
    plt.rcParams["font.family"] = "serif"
    
    # 全体平均の点線
    #plt.axhline(y=overall_mean, color='gray', linestyle='--', alpha=0.6, linewidth=1.2)

    x_step = 1      # L1-L2, L2-L3の間隔
    x_margin = 2  # 因子間の間隔
    current_x = 1
    trans = ax.get_xaxis_transform()

    for f in factors_data:
        x_points = [current_x, current_x + x_step, current_x + x_step * 2]
        y_points = f['avgs']
        
        # 折れ線プロット
        plt.plot(x_points, y_points, marker='o', ms=10, mfc="#1911B1", color='#1911B1', linewidth=2.5, zorder=3)

        # 水準ラベル (L1, L2, L3)
        for j in range(3):
            plt.text(x=x_points[j], y=-0.08, s=f'L$_{j+1}$', 
                     transform=trans, ha='center', va='top', fontsize=12)
        
        # 各因子の名前（L1~L3の下）
        center_x = current_x + x_step
        plt.text(x=center_x, y=-0.18, s=f['name'], 
                 transform=trans, ha='center', va='top', fontsize=14, fontweight='normal')

        current_x += (x_step * 2) + x_margin

    # 【追加】一番下に「Control Factors」というラベルを配置
    total_width = current_x - x_margin + 5
    plt.text(x=total_width/2.5, y=-0.32, s='Process Parameters', 
             transform=trans, ha='center', va='top', fontsize=16, fontweight='normal')

    # Y軸ラベルと見た目の調整
    plt.ylabel('Mean Response', fontsize=16, fontfamily='serif')
    #plt.ylabel(r"$R_{\mathrm{a}}$ [μm]",fontsize=16, fontweight="normal")
    plt.ylim(min(all_values)*0.85, max(all_values)*1.15)
    plt.xlim(0, total_width)
    plt.xticks([]) # X軸の目盛り数値は非表示
    plt.grid(axis='y', linestyle=':', alpha=0.5)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    # 下側に大きな余白を作る（ラベルが切れないように）
    plt.subplots_adjust(bottom=0.3)
    
    plt.savefig("l9_final_control_factors.png", dpi=300, bbox_inches='tight')
    print("保存完了: l9_final_control_factors.png")
    plt.show()

if __name__ == "__main__":
    create_l9_final_report_plot()