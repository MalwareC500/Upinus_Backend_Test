from flask import Flask, request, send_from_directory, send_file
from flask_socketio import SocketIO
import os

socketio = SocketIO()


def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__, static_folder=os.getcwd() + "/static", static_url_path='/static')
    #app.debug = debug
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
    # @app.route('/download/<path:path>', methods=['GET'])
    # def send_file(path):
    #     print(path)
    #     # print(path)
    #     # return 'abc'
    #     return send_from_directory("static", 'result.zip')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app, async_mode='threading')
    return app

