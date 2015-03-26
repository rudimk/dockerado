import json
import docker
import datetime


def datetimeFromTimestamp(timestamp):
    """ Returns a datetime object from a given timestamp
    """
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def getContainers(all=False, statusCheck=False):
    """ Returns a list of container objects in JSON
    """
    client = docker.Client()
    containers = []

    try:
        containers = client.containers(all=all)
        if not statusCheck:
            for container in containers:
                container['Id'] = container['Id'][:12]
                container['Created'] = datetime.datetime.fromtimestamp(container['Created']).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass

    return containers


def getImages():
    """ Returns a list of image objects in JSON
    """
    client = docker.Client()
    images = []

    try:
        currentImages = client.images()
        for image in currentImages:
            betterImage = {}
            betterImage['Repositories'] = list(set([repo.split(':')[0] for repo in image['RepoTags']]))
            betterImage['Tags'] = [repo.split(':')[1] for repo in image['RepoTags']]
            betterImage['Image'] = image['Id'][:12]
            betterImage['Created'] = datetimeFromTimestamp(image['Created'])
            betterImage['Size'] = "{0:.1f} MB".format(image['VirtualSize'] / 1000.0 / 1000.0)
            images.append(betterImage)
    except Exception:
        pass

    return images


def dockerBuildThread(buildOptions, socketio):

    dockerDirectory = buildOptions['dir']
    tag = buildOptions['tag']
    quiet = buildOptions['quiet']
    nocache = buildOptions['nocache']
    rm = buildOptions['rm']

    client = docker.Client()
    buildLog = client.build(path=dockerDirectory,
                            tag=tag,
                            nocache=nocache,
                            rm=rm,
                            quiet=quiet,
                            stream=True)

    for line in buildLog:
        line = json.loads(line)['stream']
        socketio.emit('log', {"log": line})

    socketio.emit('log', {"log": "\nBuild finished."})


def isDockerRunning():
    """ Returns True if docker is running
    """
    isUp = False
    client = docker.Client()

    try:
        client.containers(all=all)
        isUp = True
    except Exception:
        pass

    return isUp
