cd C:\repos\space-invaders
python -m venv .venv
.\.venv\Scripts\activate
python --version
python -c "import sys; print(sys.executable)"
python -m pip install pygame-ce
python -m pip uninstall pygame-ce


py install 3.12
py list # shows both py 3.14 and 3.12
deactivate
cd .\space-invaders\
Remove-Item -Recurse -Force .venv
py -3.12 -m venv .venv
.\.venv\Scripts\activate
python --version # shows 3.12
python -m pip install pygame
pip list

Ctrl + Shift + P, type Python: Select Interpreter, choose 3.12 # make sure it's in the .venv

python -c "import sys; print(sys.executable)"
python -c "import pygame; print(pygame.__version__)"

# Ctrl + Shift + P: Developer: Reload window

python -m pip list

python -m pip install numpy
python -m pip install gymnasium
python -c "import gymnasium; print(gymnasium.__version__)"

python -m pip install stable-baselines3
python -c "import stable_baselines3; print(stable_baselines3.__version__)"