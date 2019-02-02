import random
import matplotlib.pyplot as plt

# /////////////////////////////////////////////////////////////////////////////
# エンジニアのためのフィードバック制御入門
#   Philipp K. Janert 著
#   O'Reilly Japan, Inc.
# /////////////////////////////////////////////////////////////////////////////
# 第I部, 1章 フィードバック制御への誘い
#   1.6 シミュレーション用のコード
#     GitHub: https://github.com/oreillymedia/feedback_control_for_computer_systems/blob/master/ch01.py
# /////////////////////////////////////////////////////////////////////////////
# 変更点
#   出力されるデータを、dict型に格納した
#   格納したデータを、matplotlibで表示できるようにした
# /////////////////////////////////////////////////////////////////////////////


class Buffer:
    def __init__(self, max_wip, max_flow):

        self.queued = 0
        self.wip = 0                # work-in-progress ("ready pool")

        self.max_wip = max_wip
        self.max_flow = max_flow    #avg outflow is max_flow/2

    def work(self, u):

        # Add to ready pool
        u = max(0, int(round(u)))
        u = min(u, self.max_wip)
        self.wip += u

        # Transfer from ready pool to queue
        r = int(round(random.uniform(0, self.wip)))
        self.wip -= r
        self.queued += r

        # Release from queue to downstream process
        r = int(round(random.uniform(0, self.max_flow)))
        r = min(r, self.queued)
        self.queued -= r

        return self.queued


class Controller:
    def __init__(self, kp, ki):

        self.kp, self.ki = kp, ki
        self.i = 0                  # Cumulative error ("integral")

    def work(self, e):

        self.i += e

        return (self.kp * e + self.ki * self.i)


def open_loop(p, tm=5000):

    time_step = []
    set_point = []
    residues = []
    work_in_progress = []
    output = []

    def target(t):

        return 5.0
    
    for t in range(tm):
        u = target(t)
        y = p.work(u)

        # print(t, u, 0, u, y)
        time_step.append(t)
        set_point.append(u)
        residues.append(0)
        work_in_progress.append(u)
        output.append(y)

    open_data = {'time_step': time_step,
                 'set_point': set_point,
                 'residues': residues,
                 'work_in_progress': work_in_progress,
                 'output': output}

    return open_data


def closed_loop(c, p, tm=5000):

    time_step = []
    set_point = []
    residues = []
    work_in_progress = []
    output = []

    def setpoint(t):

        if t < 100:
            return 0
        if t < 300:
            return 50
        
        return 10

    y = 0
    for t in range(tm):
        r = setpoint(t)
        e = r - y
        u = c.work(e)
        y = p.work(u)

        # print(t, r, e, u, y)
        time_step.append(t)
        set_point.append(r)
        residues.append(e)
        work_in_progress.append(u)
        output.append(y)

    closed_data = {'time_step': time_step,
                   'set_point': set_point,
                   'residues': residues,
                   'work_in_progress': work_in_progress,
                   'output': output}

    return closed_data


# -----------------------------------------------------------------------------
# これ以降は、実行用コード
# -----------------------------------------------------------------------------

# バッファーと制御機の初期化
c = Controller(1.25, 0.01)
p = Buffer(50, 10)

# 開ループモードと閉ループモードの結果を格納
open_data = open_loop(p, 1000)
closed_data = closed_loop(c, p, 1000)

# グラフの初期化
fig = plt.figure(figsize=(10,6))
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

# 開ループモードのグラフ作成
ax1.plot(open_data['time_step'], open_data['set_point'], label='目標値')
ax1.plot(open_data['time_step'], open_data['output'], label='出力')
ax1.set_title("フィードバックなし")
ax1.set_xlabel("時間ステップ")
ax1.set_ylabel("バッファに依存する部品数")
ax1.grid(which='both', linestyle='--')
ax1.legend()

# 閉ループモードのグラフ作成
ax2.plot(closed_data['time_step'], closed_data['set_point'], label='目標値')
ax2.plot(closed_data['time_step'], closed_data['output'], label='出力')
ax2.set_title("フィードバックあり")
ax2.set_xlabel("時間ステップ")
ax2.set_ylabel("バッファに依存する部品数")
ax2.grid(which='both', linestyle='--')
ax2.legend()

# グラフの表示
fig.tight_layout()
plt.show()
