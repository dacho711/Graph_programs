import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import japanize_matplotlib

# 1. データの読み込み
df = pd.read_csv(r'C:\Users\dacho\Documents\Graph_programs\sekkei_tateyoko_data.csv')

# 2. 描画位置（x座標）の設定
numbers = [1, 2, 3, 4] # グループ間をより強調するため間隔を少し広げました
positions = list(map(lambda x: x / 2, numbers))

column_names = df.columns
# 表示用のラベル
labels = ['縦 1辺3mm', '横 1辺3mm', '縦 1辺6mm', '横 1辺6mm']

plt.rcParams['font.family'] = 'meiryo'
plt.rcParams['font.size'] = 20

fig, (ax_top, ax_bottom) = plt.subplots(2, 1, sharex=True, figsize=(16, 5))
fig.subplots_adjust(hspace=0.15)

# 3. 各カラムをループしてプロット
colors = ['#7c1d8f', '#0000c4', '#7c1d8f', '#0000c4']

for i, col in enumerate(column_names):
    # --- 箱ひげ図の描画 ---
    # fliersize=0 で箱ひげ図標準の外れ値を消し、stripplotと重ならないようにします
    sns.boxplot(y=df[col], ax=ax_top, positions=[positions[i]], 
                width=0.2, color=colors[i], fliersize=0, zorder=1, medianprops={"linewidth":1, 'color':'white'})
    sns.boxplot(y=df[col], ax=ax_bottom, positions=[positions[i]], 
                width=0.2, color=colors[i], fliersize=0, zorder=1, medianprops={"linewidth":1, 'color':'white'})
    
print(df)

# 4. 横軸の見た目を整える
ax_bottom.set_xticks(positions)
ax_bottom.set_xticklabels(labels) # 日本語ラベルを適用
xpadding = 0.5 # 左右の余白を少し広めに設定
ax_bottom.set_xlim(min(positions)-xpadding, max(positions)+xpadding)

# 5. 縦軸の範囲設定
range_size = 7
ax_top.set_ylim(26, 26 + range_size)
ax_bottom.set_ylim(4, 4 + range_size)

# 6. Broken Axis（省略線）の装飾
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

ax_bottom.set_ylabel('')
ax_top.set_ylabel('')
#ax_top.set_title('測定結果の比較（3mm vs 6mm）')

plt.show()