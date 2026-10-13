"""测试引导：把项目根目录与 wheels 中的依赖（openpyxl 等）加入 sys.path。

无需 pip：wheel 是 zip，可直接被 zipimport 导入。
"""

import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

for whl in glob.glob(os.path.join(ROOT, "wheels", "*.whl")):
    if whl not in sys.path:
        sys.path.insert(0, whl)
