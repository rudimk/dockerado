import threading

from flask import Flask, jsonify
from flask.ext.mako import MakoTemplates, render_template
from flask.ext.socketio import SocketIO

from utils import getContainers, getImages, isDockerRunning, dockerBuildThread

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.template_folder = "templates"

mako = MakoTemplates(app)
socketio = SocketIO(app)


@socketio.on('connected')
def connected(event):
    print("DockerAdmin connected")


@socketio.on('build')
def build(buildOptions):
    """ Build a new docker image
    """
    print("Starting build")
    threading.Thread(target=dockerBuildThread, args=(buildOptions, socketio)).start()
    print("Build running")


@app.route('/images')
def images():
    """ View for docker images
    """
    images = {"images": getImages()}
    return jsonify(images)


@app.route('/containers')
def containers():
    """ View for docker containers
    """
    containers = {"containers": getContainers(all=True)}
    return jsonify(containers)


@app.route('/status')
def status():
    """ Gets the status of docker.
    """
    isUp = isDockerRunning()
    status = "Running" if isUp else "Stopped"
    statusColour = "green" if isUp else "red"

    return jsonify({"status": status, "colour": statusColour})

@app.route('/')
def index():
    """ Homepage
    """
    return render_template('index.mako')


if __name__ == '__main__':
    socketio.run(app)


