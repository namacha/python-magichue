import pathlib
import sys

_here = here = pathlib.Path(__file__).resolve().parent
sys.path.append(str(_here.parent))
import pytest
