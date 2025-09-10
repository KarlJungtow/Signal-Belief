How to run experiment:
Install Python
During installation, check the box “Add Python to PATH.”

Install pip and virtualenv (if not already installed) in the terminal:

python -m pip install --upgrade pip
python -m pip install virtualenv

Go to your experiment folder in the terminal/command prompt using cd {your Folders path}.

Create a virtual environment:
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows


Install oTree in that environment:
pip install otree


Run your project:
otree devserver


Then open your browser at http://localhost:8000
