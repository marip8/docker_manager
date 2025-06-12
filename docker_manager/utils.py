import os
from docker.models.images import Image


def create_image_map(image: Image) -> dict[str, set[str]]:
    """ Creates a dictionary of image repository names to image tags

    """
    image_map = dict()
    for tag in image.tags:
        sub_tags = tag.split(':')
        image_name = ''.join(sub_tags[:-1])
        tag_name = sub_tags[-1]

        if image_name in image_map:
            image_map[image_name].add(tag_name)
        else:
            image_map[image_name] = {tag_name}

    return image_map


def update_recursive(d: dict, u: dict) -> dict:
    """ Recursively updates one dictionary with the contents of another

    """
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = update_recursive(d.get(k, {}), v)
        else:
            d[k] = v

    return d


def create_non_root_user_kwargs() -> dict:
    """ Creates Docker run keyword arguments for mounting an image as a non-root user

    """
    return {
        'user': f'{os.getuid()}:{os.getgid()}',
    }


def create_sudo_group_add_kwargs() -> dict:
    """ Creates Docker run keyword arguments for adding the user of the container to the ``sudo`` group

    """
    return {
        'group_add': [
            'sudo',
        ],
        'volumes': {
            '/etc/localtime': {
                'bind': '/etc/localtime',
                'mode': 'ro'
            },
            '/etc/hosts': {
                'bind': '/etc/hosts'
            },
            '/etc/passwd': {
                'bind': '/etc/passwd',
                'mode': 'ro'
            },
            '/etc/group': {
                'bind': '/etc/group',
                'mode': 'ro'
            },
            '/etc/shadow': {
                'bind': '/etc/shadow'
            }
        },
    }


def create_ros2_kwargs() -> dict:
    """ Creates Docker run keyword arguments for setting ROS2 environment variables

    """
    return {
        'environment': {
            'ROS_LOG_DIR': os.path.join('tmp', '.ros'),
            'ROS_LOCALHOST_ONLY': os.getenv('ROS_LOCALHOST_ONLY'),
            'ROS_DOMAIN_ID': os.getenv('ROS_DOMAIN_ID'),
        }
    }


def create_x11_kwargs() -> dict:
    """ Creates Docker run keyword arguments for utilizing the host's X11 server

    """
    kwargs = {
        'environment': {
            'DISPLAY': os.getenv('DISPLAY'),
            'XAUTHORITY': os.getenv('XAUTHORITY'),
        },
        'volumes': {
            '/tmp/.X11-unix': {
                'bind': '/tmp/.X11-unix'
            },
        }
    }

    # Add user kwargs
    kwargs.update(create_non_root_user_kwargs())

    return kwargs


def create_usb_kwargs() -> dict:
    """ Creates Docker run keyword arguments for using USB devices

    """
    return {
        # TODO: include privileged?
        # 'privileged': True,
        'tty': True,
        'volumes': {
            '/dev': {
                'bind': '/dev'
            },
        }
    }
