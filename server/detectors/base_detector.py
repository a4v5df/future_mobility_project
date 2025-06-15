from typing import List
import numpy as np

class BaseDetector:
    def detect(self, frame: np.ndarray) -> List:
        raise NotImplementedError
