from os import listdir
from os.path import isfile, join, splitext
import re
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import random
import seaborn as sns
import sys
import math
import itertools

if (len(sys.argv) < 2):
    sys.exit('Please provide a KovaaK "/stats" path.')
path = sys.argv[1]
files = [f for f in listdir(path) if isfile(
    join(path, f)) and splitext(join(path, f))[1] == '.csv']
files.sort()
d = {}

for file in files:
    with open(f"{path}/{file}", newline='\n') as csvfile:
        for line in csvfile:
            filename = file.split(" - ")[0]
            date = re.findall(r'\d\d\d\d.\d\d.\d\d-\d\d.\d\d', file)[0]
            date = datetime.strptime(date, '%Y.%m.%d-%H.%M')
            date = date.timestamp()
            if "Score" in line:
                stripped = line.rstrip()
                score = re.findall(r'\d+.\d+', stripped)[0]
                score = float(score)
                if filename in d:
                    existing = d[filename]
                    existing.append({"date": date, "score": score})
                    d[filename] = existing
                else:
                    d[filename] = [{"date": date, "score": score}]


challenge_names = list(d.keys())

# filter challenges not played many times
for challenge_name in challenge_names:
    if len(d[challenge_name]) < 10:
        del(d[challenge_name])


def get_date(t):
    return t.get("date")


# sort d by most recently played date
# d = dict(sorted(d.items(), key=lambda item: max(
    # item[1], key=get_date).get("date")))

GRAPHS_PER_ROW = 7
rows = int(math.ceil(len(d)/GRAPHS_PER_ROW)
           ) if int(math.ceil(len(d)/GRAPHS_PER_ROW)) != 0 else 1
columns = math.ceil(len(d)/rows)
# fig, axes = plt.subplots(rows, columns, figsize=(12, 6), squeeze=False)
fig, axes = plt.subplots(rows, columns, squeeze=False, sharex=True)

palette = itertools.cycle(sns.color_palette())

d_keys = reversed([k[0] for k in list(sorted(d.items(), key=lambda item: max(
    item[1], key=get_date).get("date")))])

i = 0
row = 0
column = 0

for key in d_keys:
    values = d[key]
    scores = [d['score'] for d in values]
    dates = [d['date'] for d in values]

    ax = axes[row][column]
    sns.regplot(x=dates, y=scores, order=2,
                label=key, ax=ax, color=next(palette))
    xticks = ax.get_xticks()
    ax.set_xticklabels([datetime.fromtimestamp(tm).strftime('%Y-%m-%d') for tm in xticks],
                       rotation=30, fontsize=6)
    for t in ax.yaxis.get_major_ticks():
        t.label.set_fontsize(6)
    ax.set_title(key, fontsize=8)
    if (i % columns) == 0:
        ax.set_ylabel('Score', fontsize=8)

    if (column == columns - 1):
        column = 0
        row += 1
    else:
        column += 1

fig.set_size_inches(12, fig.get_figheight())
fig.tight_layout()

plt.show()
