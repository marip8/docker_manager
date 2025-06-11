from datetime import datetime
from docker.errors import APIError
import docker
from importlib.resources import files
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtWidgets import QWidget, QCompleter, QApplication, QMessageBox, QFileDialog
from PyQt5.uic import loadUi

from .utils import create_image_map


class DockerManagerWidget(QWidget):
    """ Widget for launching Docker containers

    """

    def __init__(self, parent: QWidget = None):
        """
        :param parent:
        """
        super().__init__(parent)

        # Load the UI objects from file
        ui_file = files('docker_manager.ui').joinpath('docker_manager_widget.ui')
        loadUi(ui_file, self)

        # Parse the available images to extract tags from the images matching the input image name
        self._client = docker.from_env()

        # Stop all running containers and prune stopped controllers
        for container in self._client.containers.list():
            container.stop()
        self._client.containers.prune()

        # Add a callback for running the image with docker compose
        self.push_button_run.clicked.connect(self._on_run)

        # Add a callback
        self.line_edit_image.editingFinished.connect(self._on_image_name_changed)

        # Populate a list of image names to tag names for those images
        self._image_map = self._create_image_map()

        # Add a completer to the line edit that knows about the existing names
        self.line_edit_image.setCompleter(QCompleter(self._image_map.keys()))

    def __del__(self):
        self._stop_containers()
        self._client.close()

    def _create_image_map(self):
        """"""
        image_map = {}
        for image in self._client.images.list():
            image_map.update(create_image_map(image))

        return image_map

    def get_full_image_name(self):
        """ Gets the full image name from the UI

        """
        return f'{self.line_edit_image.text()}:{self.combo_box_version.currentText()}'

    def create_containers(self):
        """ Creates a container based on the UI

        Override this method to launch containers in a specific manner
        """
        self._client.containers.run(
            name='container',
            image=self.get_full_image_name(),
            detach=True,
        )

    def _on_image_name_changed(self):
        """

        """
        self.combo_box_version.clear()
        image_name = self.line_edit_image.text()

        # Check for empty image name
        if image_name is None or image_name == '':
            return

        if not image_name in self._image_map:
            print(f'Pulling image \'{image_name}\'...')
            try:
                image = self._client.images.pull(image_name)
                self._image_map.update(create_image_map(image))
            except APIError as e:
                QMessageBox.warning(self, 'Pull Error', str(e))
                return

        for tag_name in self._image_map[image_name]:
            sub_tags = tag_name.split(':')
            self.combo_box_version.addItem(sub_tags[-1])

    def _on_run(self, clicked: bool):
        """

        """
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        if clicked:
            try:
                self.create_containers()
            except APIError as e:
                QMessageBox.warning(self, 'Container Error', str(e))
                self.push_button_run.clicked.emit(False)

            for container in self._client.containers.list(all=True):
                print(f'Container \'{container.name}\' - Status: {container.status}')
        else:
            self._stop_containers()
        QApplication.restoreOverrideCursor()

    def _stop_containers(self):
        """

        """
        if len(self._client.containers.list(all=True)) == 0:
            return

        # Stop running containers
        for container in self._client.containers.list():
            print(f'Stopping container \'{container.name}\'...')
            container.stop()

        ret = QMessageBox.question(self, 'Save logs?', 'Would you like to save the container logs?')
        if ret == QMessageBox.Yes:
            save_dir = QFileDialog.getExistingDirectory(self, 'Log save directory', QDir.tempPath())
            if QDir(save_dir).exists():
                stamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                for container in self._client.containers.list(all=True):
                    with open(f'{save_dir}/{container.name}_{stamp}.log', 'w') as f:
                        for line in container.logs(stream=True):
                            f.write(line.decode('utf-8'))

        # Prune the containers
        self._client.containers.prune()
