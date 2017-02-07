#!/usr/bin/env python
import os
from app import create_app
# from flask_script import Manager, Shell
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
if __name__ == '__main__':
    app.run(threaded=True)

# couldnt get it to work with the rest of the code
# I'm just gonna comment it out
# seems to work fine without it...

# manager = Manager(app)

# def make_shell_context():
#     return dict(app=app)

# manager.add_command("shell", Shell(make_context=make_shell_context))

# if __name__ == '__main__':
#     manager.run()
