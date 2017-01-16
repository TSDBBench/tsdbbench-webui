## TSDBBench Web UI middleware

Python 3.6, Apache Libcloud, Flask

## Installation

1. Create virtual environment: <br />
  a) navigate to project's folder <br />
  b) Linux: python -m venv venv (basically, the same for Win) <br />

2. Activate virtual environment: <br />
   Linux: source venv/bin/activate <br />
   Windows: venv\Scripts\activate.bat <br />

3. Install using pip: pip install -r requirements.txt <br />
4. Run: python manage.py runserver <br />
5. Connect using localhost:5000 <br />

## Project's structure

app/ - application
  main/ - routes <br />
  static/ - static files <br />
  templates/ - Jinja2 templates <br />
  libcloud_utils.py - libcloud wrapper <br />
  ssh_utils.py - ssh-related methods <br />
config.py - configuration files <br />
manage.py - launcher <br />

