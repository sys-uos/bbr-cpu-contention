**How to reproduce**:
1) Clone, and extract dataset `results/data.tar.xz` (decompressed size: 584 MB).
2) Run the `results/plots/figure_*.ipynb` notebooks (tested with Python 3.12.3 kernel).
3) Pdf plots are generated into `results/plots/figures`. 
4) Some notebooks can generate multiple plots from the paper, e.g. `figure_7_14.ipynb`. Use the switch in the first code cell to control which figure is produced.


**Detailed dependencies**:
```
# install required packages
sudo apt install -y git xz-utils python3.12 python3.12-venv python3-pip texlive-luatex texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended lmodern cm-super

# clone this repository
git clone https://github.com/sys-uos/bbr-cpu-contention/
cd bbr-cpu-contention/

# extract the dataset
tar -xJf results/data.tar.xz -C results/

# create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# install pip and python dependencies
python -m pip install --upgrade pip
python -m pip install numpy pandas matplotlib seaborn jupyter ipykernel
```
