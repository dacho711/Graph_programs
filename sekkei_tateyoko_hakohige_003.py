import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. データの読み込み
df = pd.read_csv(r'C:\Users\dacho\Documents\Graph_programs\sekkei_tateyoko_data.csv')

# 2. 描画位置（x座標）の設定
# 4つ並べるので、シンプルに [1, 2, 3, 4] に配置し、グループ間を少しだけ開けるなら [1, 2, 3.5, 4.5] などにします
numbers = [1, 2, 4, 5]
positions = list(map(lambda x: x / 2, numbers)) # 間隔のバランス調整

column_names = df.columns
labels = ['縦 1辺3mm', '横 1辺3mm', '縦 1辺6mm', '横 1辺6mm']
custom_colors = ['#7c1d8f', '#0000c4', '#7c1d8f', '#0000c4'] 

plt.rcParams['font.family'] = 'Yu Gothic'
plt.rcParams['font.size'] = 20

fig, ax = plt.subplots(figsize=(18, 6)) # グラフは1つだけ作成

# 3. 各カラムをループしてプロット
for i, col in enumerate(column_names):
    # 箱ひげ図
    sns.boxplot(y=df[col], ax=ax, positions=[positions[i]], 
                width=0.3, color=custom_colors[i], fliersize=0, zorder=1)
    
# y=30 の位置に赤い破線を引く場合
ax.axhline(y=36, color='#15571d', linestyle='--', linewidth=2)
# y=30 の位置に赤い破線を引く場合
ax.axhline(y=9, color='#15571d', linestyle='--', linewidth=2)

# 4. 軸と見た目の調整
ax.set_xticks(positions)
ax.set_xticklabels(labels)

# 縦軸は3mmから6mmまで全て入るようにオート、もしくは 0〜35mm程度に設定
ax.set_ylim(0, 35) 

# グラフの左右の余白
xpadding = 0.6
ax.set_xlim(min(positions)-xpadding, max(positions)+xpadding)
ax.set_ylim(4, 37)

ax.set_ylabel('測定値 (mm$^2$)')
ax.grid(axis='y', linestyle='--', alpha=0.7) # 高低差が激しいので補助線があると見やすいです

plt.show()