"""カメラの設定、読み取り、切り替えを担当する。"""

import sys
import time

import cv2


class Camera:
    def __init__(self, width=1920, height=1080, fps=15, count=2):
        self.width = width
        self.height = height
        self.fps = fps
        self.count = count
        self.index = 0
        self.capture = None
        self._first_frame = None

    def open(self, index=0):
        # 新しいカメラを開けたことを確認してから、現在のカメラを解放する。
        backend = cv2.CAP_AVFOUNDATION if sys.platform == 'darwin' else cv2.CAP_ANY
        for configure in (True, False):
            capture = cv2.VideoCapture(index, backend)
            try:
                if not capture.isOpened():
                    raise RuntimeError(f"カメラ {index} を開けませんでした。")
                if configure:
                    # 解像度とフレームレートを要求する。対応する値はカメラによって異なる。
                    capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                    capture.set(cv2.CAP_PROP_FPS, self.fps)
                # 開けても直後には画像が届かない場合があるため、最大3秒待つ。
                frame = self._wait_frame(capture, timeout=3)
            except (RuntimeError, cv2.error):
                capture.release()
                if configure:
                    print('画像を取得できないため、カメラの標準設定で再試行します。')
                    continue
                raise RuntimeError(
                    f"カメラ {index} から画像を取得できません。"
                    'macOSのカメラ権限と、他のアプリで使用中でないかを確認してください。'
                ) from None

            self.close()
            self.capture = capture
            self.index = index
            self._first_frame = frame
            height, width = frame.shape[:2]
            print(f'カメラ {index}: {width}×{height} / 設定FPS: {capture.get(cv2.CAP_PROP_FPS):g}')
            return

    def _wait_frame(self, capture, timeout):
        # 一時的な取得失敗は再試行する。画像が届かない場合は期限を設けて終了する。
        deadline = time.monotonic() + timeout
        while True:
            success, frame = capture.read()
            if success and frame is not None and frame.size:
                return frame
            if time.monotonic() >= deadline:
                raise RuntimeError('カメラから画像を取得できませんでした。')
            time.sleep(0.05)

    def read(self):
        # 取得に失敗した画像が、そのまま色変換へ渡されないようにする。
        if self.capture is None:
            raise RuntimeError("カメラが開かれていません。")
        if self._first_frame is not None:
            frame = self._first_frame
            self._first_frame = None
            return frame
        return self._wait_frame(self.capture, timeout=2)

    def switch(self):
        # 最後のカメラの次は、最初のカメラに戻る。
        self.open((self.index + 1) % self.count)

    def close(self):
        self._first_frame = None
        if self.capture is not None:
            self.capture.release()
            self.capture = None
