# Docker Manager

Utility for launching Docker containers from a GUI

![Docker Manager](docs/docker-manager.png)

## Usage

* Type an image name
* Select a version (tag) for the image
* Press the button to run the container
* Press the button a second time to stop the container

## Customization

Users can customize the widget by overloading the ``DockerManagerWidget.create_containers`` method and invoking the Docker client ``containers.run()`` method.
The ``utils`` module provides several common sets of keyword arguments to provide to the client's ``containers.run()`` method for launching containers with X11 support, as a non-root user, with access to USB devices, etc.
