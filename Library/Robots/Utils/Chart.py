from io import BytesIO
from matplotlib import pyplot as plt

def gantt(ranges, opt_color="#1f77b4", val_color="#2ca02c", test_color="#ff7f0e"):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 4))

    entries = []
    for index, ((opt_start, opt_stop), (val_or_test_start, val_or_test_stop)) in enumerate(ranges, start=1):
        label, color = ("Testing", test_color) if index == len(ranges) else ("Validation", val_color)
        entries.append((f"WF{index}: {label}", val_or_test_start, (val_or_test_stop - val_or_test_start).days, color))
        entries.append((f"WF{index}: Optimization", opt_start, (opt_stop - opt_start).days, opt_color))

    grouped_entries = [entries[i:i+2] for i in range(0, len(entries), 2)]
    ordered_entries = [item for group in grouped_entries[::-1] for item in group]

    y_labels = [label for label, _, _, _ in ordered_entries]
    starts = [start for _, start, _, _ in ordered_entries]
    durations = [duration for _, _, duration, _ in ordered_entries]
    colors = [color for _, _, _, color in ordered_entries]

    y_pos = list(range(len(y_labels)))

    for i in range(len(y_labels)):
        ax.barh(y_pos[i], durations[i], left=starts[i], height=0.5, color=colors[i], edgecolor='white')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels)
    ax.xaxis_date()
    ax.set_title("Walk-Forward Analysis Gantt Chart", fontsize=14, pad=15)
    ax.tick_params(colors='white', labelsize=10)
    ax.title.set_color('white')
    ax.set_facecolor("#121212")
    fig.patch.set_facecolor('#121212')

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf