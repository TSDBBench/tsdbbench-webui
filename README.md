## TSDBBench Web UI middleware

Python 3.6, Apache Libcloud, Flask

## Installation

1. Create virtual environment:
  a) navigate to project's folder
  b) Linux: python -m venv venv (basically, the same for Win)

2. Activate virtual environment:
   Linux: source venv/bin/activate
   Windows: venv\Scripts\activate.bat

3. Install using pip: pip install -r requirements.txt

4. Run: python manage.py runserver
5. Connect using localhost:5000

## Project's structure

app/ - application
  main/ - routes
  static/ - static files
  templates/ - Jinja2 templates
  libcloud_utils.py - libcloud wrapper
  ssh_utils.py - ssh-related methods
config.py - configuration files
manage.py - launcher

