"""フレームの時間管理と、移動成分を除いた振動の解析。"""

from collections import deque
import math
import time

import numpy as np

_num_frame = 0  # 処理済みフレームとコマ落ちを合わせた累計
_dropped_frame = 0


def frame_dropped():
    # 公開関数を呼ぶたびに、累計とコマ落ち数を1ずつ加算する。
    global _num_frame, _dropped_frame
    _num_frame += 1
    _dropped_frame += 1


def reset_frames():
    global _num_frame, _dropped_frame
    _num_frame = 0
    _dropped_frame = 0


def dropped_rate():
    return 100 * _dropped_frame / _num_frame if _num_frame else 0.0


# loop終了を待つ関数
def wait_loop_end(framerate, begin_time):
    """begin_timeはtime.monotonic()の値。超過した周期をコマ落ちとして数える。"""
    global _num_frame
    if framerate <= 0:
        raise ValueError("フレームレートは正の値を指定してください。")
    duration = time.monotonic() - begin_time
    interval = 1 / framerate
    _num_frame += 1
    if duration > interval:
        # loopが終了すべき時間を過ぎている場合は、超過した周期をコマ落ち扱いにする。
        for _ in range(max(1, math.ceil(duration / interval) - 1)):
            frame_dropped()
        return False
    # loopが終了すべき時間まで、残っている時間だけ待つ。
    time.sleep(max(0, interval - duration))
    return True


class MotionAnalysis:
    """一定コマ数ごとに平均移動量を求め、次の区間の移動成分を除く。"""

    def __init__(self, window=50, history_limit=2000):
        if window <= 0:
            raise ValueError("取得するコマ数は正の値を指定してください。")
        self.window = window
        self.history_limit = history_limit
        self.reset()

    def reset(self):
        # 区間の移動量、振動の平均、描画用の履歴をそれぞれ初期化する。
        self.samples = 0
        self.block_samples = 0
        self.previous = None
        self.origin = None
        self.velocity = np.zeros(2)
        self.movement = np.zeros(2)
        self.vibration = np.zeros(2)
        self.amplitude_sum = 0.0
        self.mean_amplitude = 0.0
        self.angle = None
        self.history = deque(maxlen=self.history_limit)
        self.angles = deque(maxlen=self.history_limit)

    def update(self, x, y):
        position = np.array([x, y], dtype=float)
        if self.previous is None:
            self.origin = position.copy()
            self.previous = position.copy()
        elif self.block_samples == self.window:
            # 前の区間の平均移動量を、次の区間の1コマあたりの移動量にする。
            self.velocity = self.movement / self.window
            self.origin = self.previous.copy()
            self.movement[:] = 0
            self.block_samples = 0
            self.amplitude_sum = 0.0

        self.movement += position - self.previous
        self.block_samples += 1
        self.samples += 1
        # 平均移動を続けた場合の予測位置との差を振動として扱う。
        expected = self.origin + self.velocity * self.block_samples
        self.vibration = position - expected
        # X・Yの振動から振幅を求め、現在の区間内の平均を計算する。
        self.amplitude_sum += float(np.linalg.norm(self.vibration))
        self.mean_amplitude = self.amplitude_sum / self.block_samples
        self.history.append((self.samples, *self.vibration))
        self.previous = position

        # 元のatan(y/x)による角度の定義を維持する。
        vx, vy = (int(value) for value in self.vibration)
        self.angle = math.degrees(math.atan(vy / vx)) if vx else None
        if self.angle is not None:
            self.angles.append(int(self.angle))
        return self.vibration.copy()
