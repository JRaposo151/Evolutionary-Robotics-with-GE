# test_unpickle.py
import numpy as np
import pickle
from pathlib import Path

print("python:", __import__('sys').version.splitlines()[0])
print("numpy:", np.__version__)

p = Path("../Controller_testing/robots_ind/best_gen_000.pkl")
if not p.exists():
    print("Pickle not found:", p.resolve())
else:
    try:
        with p.open("rb") as f:
            obj = pickle.load(f)
        print("Unpickled OK. type:", type(obj))
    except Exception as e:
        print("Unpickle failed:", repr(e))
