# Sliding Puzzle Solver using traditional search
## [GUI is a work in progress, but you can check it out here](https://sliding-puzzle.fly.dev/)
## [Tree visualization example](./Source.gv.pdf)
## Setup Instructions

1. Install [graphviz](https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/7.0.4/windows_10_cmake_Release_graphviz-install-7.0.4-win64.exe), and add it to system PATH  
   ![add graphviz to windows PATH](README.d/graphviz-path.png)
2. Install Pipenv, or use conda/mamba if you prefer  
   ```pip install pipenv```
3. Install project environment & dependencies  
   ```pipenv install```

## Running the Project

1. cd to project dir.  
2. Switch to project venv  
   ```pipenv shell```
3. run it!!!  
   ```python app.py``` for GUI  
   or ```python main.py``` for Graphviz tree  
**or**  
2. run the project directly through pipenv  
   ```pipenv run python app.py```  
   ```pipenv run python main.py```
