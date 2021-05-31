from checkerboard import napari_experimental_provide_dock_widget
from checkerboard import checkerboard
import itk
import pytest
import numpy as np
from itk_napari_conversion import image_layer_from_image
from itk_napari_conversion import image_from_image_layer
import napari

# this is your plugin name declared in your napari.plugins entry point
MY_PLUGIN_NAME = "napari-checkerboard"
# the name of your widget(s)
MY_WIDGET_NAMES = ["Example Q Widget", "example_magic_widget"]


# Helper functions
def image_generator(x1, x2, y1, y2, data_dir='none'):
    image = np.zeros([100, 100], np.float32)
    image[y1:y2, x1:x2] = 1
    image = itk.image_view_from_array(image)
    image = image_layer_from_image(image)
    return image


def checkerboard_filter(*args, **kwargs):
    cb_filter = checkerboard.checkerboard()
    return cb_filter(*args, **kwargs)


# @pytest.mark.parametrize("widget_name", MY_WIDGET_NAMES)
# def test_something_with_viewer(widget_name, make_napari_viewer):
#     viewer = make_napari_viewer()
#     num_dw = len(viewer.window._dock_widgets)
#     viewer.window.add_plugin_dock_widget(
#         plugin_name=MY_PLUGIN_NAME, widget_name=widget_name
#     )
#     assert len(viewer.window._dock_widgets) == num_dw + 1

# Test widget function
def test_dock_widget():
    assert checkerboard.napari_experimental_provide_dock_widget() is not None


def test_checkerboard():
    image1 = image_generator(25, 75, 25, 75)
    image2 = image_generator(1, 51, 10, 60)
    result_image = checkerboard_filter(image1, image2, pattern=4)
    assert isinstance(result_image, napari.layers.Image)
