#!/usr/bin/python
# -*- coding: utf8 -*-

from app import create_app, socketio
import os

app = create_app()

if __name__ == '__main__':
    print(os.path.abspath("static"))
    socketio.run(app, host='0.0.0.0', port=4041)

    