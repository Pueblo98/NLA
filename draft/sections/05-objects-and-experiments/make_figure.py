"""Draw proposed geometry only. No mesh or deformation is computed.
Run with Python and matplotlib; output is committed so LaTeX can build alone.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

ROOT = Path(__file__).resolve().parent


def main():
    cases = json.loads((ROOT / 'cases.json').read_text())
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'pdf.fonttype': 42})
    fig, ax = plt.subplots(figsize=(9.2, 2.7))
    offsets = [0.0, 1.65, 4.3]
    labels = ['S: square control', 'R: longer rectangle', 'H: central opening']
    for obj, offset, label in zip(cases['objects'], offsets, labels):
        outer = [(x + offset, y) for x, y in obj['outer_ccw_m']]
        ax.add_patch(Polygon(outer, facecolor='#e9eef3', edgecolor='#26394a', lw=1.3))
        for hole in obj['holes_cw_m']:
            ax.add_patch(Polygon([(x + offset, y) for x, y in hole],
                                 facecolor='white', edgecolor='#26394a', lw=1.2))
        L = obj['right_x_m']
        ax.plot([offset, offset], [0, 1], color='#276393', lw=3)
        for y in [0.08, 0.24, 0.40, 0.56, 0.72, 0.88]:
            ax.plot([offset - .1, offset], [y - .07, y], color='#276393', lw=1)
        ax.plot([offset + L, offset + L], [0, 1], color='#b33d36', lw=2)
        for y in [.15, .5, .85]:
            ax.annotate('', (offset + L + .27, y), (offset + L, y),
                        arrowprops={'arrowstyle': '->', 'color': '#b33d36', 'lw': 1.4})
        ax.text(offset + L / 2, 1.17, label, ha='center', fontsize=10)
        ax.annotate('', (offset, -.18), (offset + L, -.18),
                    arrowprops={'arrowstyle': '<->', 'color': '#3b4956', 'lw': .8})
        ax.text(offset + L / 2, -.23, f'{L:g} m', ha='center', va='top')
    ax.annotate('', (-.25, 0), (-.25, 1),
                arrowprops={'arrowstyle': '<->', 'color': '#3b4956', 'lw': .8})
    ax.text(-.34, .5, '1 m', ha='center', va='center', rotation=90)
    ax.annotate('0.2 m opening', (4.8, .4), (4.8, .12), ha='center',
                arrowprops={'arrowstyle': '-', 'color': '#3b4956', 'lw': .8}, fontsize=9)
    ax.set(xlim=(-.5, 5.65), ylim=(-.4, 1.4), aspect='equal')
    ax.axis('off')
    fig.tight_layout(pad=.1)
    (ROOT / 'figures').mkdir(exist_ok=True)
    fig.savefig(ROOT / 'figures/objects.pdf', bbox_inches='tight')
    fig.savefig(ROOT / 'figures/objects.png', dpi=170, bbox_inches='tight')
    plt.close(fig)
    print('Created figures/objects.pdf and objects.png from cases.json; schematic only.')


if __name__ == '__main__':
    main()
