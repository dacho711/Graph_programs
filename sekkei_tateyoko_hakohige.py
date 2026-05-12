import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. データの読み込み
df = pd.read_csv(r'C:\Users\dacho\Documents\Graph_programs\sekkei_tateyoko_data.csv')

# 2. 描画位置（x座標）を数値で設定する
# 例えば 3mm系を [1, 2]、6mm系を [5, 6] に置くと、間の間隔が大きく開きます
numbers = [1, 2, 4, 5]
positions = list(map(lambda x: x / 3, numbers))

column_names = df.columns # ['3mm_縦', '3mm_横', '6mm_縦', '6mm_横']

plt.rcParams['font.family'] = 'MS Gothic'
fig, (ax_top, ax_bottom) = plt.subplots(2, 1, sharex=True, figsize=(9, 7))
fig.subplots_adjust(hspace=0.15)

# 3. 各カラムをループして、指定した位置(positions)にプロット
colors = sns.color_palette("Set3", n_colors=4)

for i, col in enumerate(column_names):
    # 上下の軸それぞれに箱ひげ図を描画
    # positions[i] でx軸の具体的な位置を指定
    sns.boxplot(y=df[col], ax=ax_top, positions=[positions[i]], width=0.2, color=colors[i])
    sns.boxplot(y=df[col], ax=ax_bottom, positions=[positions[i]], width=0.2, color=colors[i])
    
    
# 4. 横軸の見た目を整える
ax_bottom.set_xticks(positions)
ax_bottom.set_xticklabels(column_names)
xpadding = 0.3
ax_bottom.set_xlim(min(positions)-xpadding, max(positions)+xpadding) # グラフの左右に余白を作る

# 5. 縦軸の範囲設定 (以前と同様)
range_size = 7
ax_top.set_ylim(26, 26 + range_size)
ax_bottom.set_ylim(4, 4 + range_size)

# 6. Broken Axis の装飾
ax_top.spines['bottom'].set_visible(False)
ax_bottom.spines['top'].set_visible(False)
ax_top.tick_params(labelbottom=False, bottom=False)

d = .015
kwargs = dict(transform=ax_top.transAxes, color='k', clip_on=False)
ax_top.plot((-d, +d), (-d, +d), **kwargs)
ax_top.plot((1 - d, 1 + d), (-d, +d), **kwargs)
kwargs.update(transform=ax_bottom.transAxes)
ax_bottom.plot((-d, +d), (1 - d, 1 + d), **kwargs)
ax_bottom.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

plt.show()