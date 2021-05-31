from napari_plugin_engine import napari_hook_implementation
from magicgui import magic_factory
import numpy as np
import itk
import checkerboard.utils as utils
from itk_napari_conversion import image_from_image_layer
from itk_napari_conversion import image_layer_from_image


def on_init(widget):
    """
    Initializes widget layout.
    """
    widget.native.setStyleSheet("QWidget{font-size: 12pt;}")


@magic_factory(widget_init=on_init, layout='vertical',
               call_button="create checkerboard",
               pattern={"max": 20, "step": 1,
                        "tooltip": "Select the gridsize of the checkerboard"})
def checkerboard(image1: "napari.layers.Image",
                 image2: "napari.layers.Image",
                 pattern: int = 3) -> 'napari.layers.Image':
    """
    Takes user input images and returns a checkerboard blend of the images.
    """
    if image1 is None or image2 is None:
        print("No images selected for registration.")
        return error("No images selected for registration.")

    # Convert image layer to itk_image
    itk_image1 = image_from_image_layer(image1)
    itk_image2 = image_from_image_layer(image2)
    itk_image1 = itk_image1.astype(itk.F)
    itk_image2 = itk_image2.astype(itk.F)

    region_image1 = itk_image1.GetLargestPossibleRegion()
    region_image2 = itk_image2.GetLargestPossibleRegion()
    same_physical_space = \
        np.allclose(np.array(itk_image1.GetOrigin()),
                    np.array(itk_image2.GetOrigin())) and \
        np.allclose(np.array(itk_image1.GetSpacing()),
                    np.array(itk_image2.GetSpacing())) and \
        itk_image1.GetDirection() == itk_image2.GetDirection() and \
        np.allclose(np.array(region_image1.GetIndex()),
                    np.array(region_image2.GetIndex())) and \
        np.allclose(np.array(region_image1.GetSize()), np.array(
                             region_image2.GetSize()))
    if not same_physical_space:
        upsample_image2 = True
        if itk_image1.GetSpacing() != itk_image2.GetSpacing():
            min1 = min(itk_image1.GetSpacing())
            min2 = min(itk_image2.GetSpacing())
            if min2 < min1:
                upsample_image2 = False
        else:
            size1 = max(itk.size(itk_image1))
            size2 = max(itk.size(itk_image1))
            if size2 > size1:
                upsample_image2 = False

        if upsample_image2:
            resampler = itk.ResampleImageFilter.New(itk_image2)
            resampler.UseReferenceImageOn()
            resampler.SetReferenceImage(itk_image1)
            resampler.Update()
            input2 = resampler.GetOutput()
        else:
            resampler = itk.ResampleImageFilter.New(itk_image1)
            resampler.UseReferenceImageOn()
            resampler.SetReferenceImage(itk_image2)
            resampler.Update()
            input1 = resampler.GetOutput()
    else:
        input1 = itk_image1
        input2 = itk_image2

    checkerboard_filter = itk.CheckerBoardImageFilter.New(input1, input2)

    dimension = itk_image1.GetImageDimension()
    checker_pattern = [pattern] * dimension
    checkerboard_filter.SetCheckerPattern(checker_pattern)
    checkerboard_filter.Update()
    checkerboard = checkerboard_filter.GetOutput()

    layer = image_layer_from_image(checkerboard)
    layer.name = "checkerboard " + image1.name + " " + image2.name
    return layer


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return checkerboard, {'area': 'bottom'}
