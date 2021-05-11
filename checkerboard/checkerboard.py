"""
This module is an example of a barebones QWidget plugin for napari

It implements the ``napari_experimental_provide_dock_widget`` hook
specification.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs.
"""
from napari_plugin_engine import napari_hook_implementation
from magicgui import magic_factory
import numpy as np
import itk
from qtpy.QtWidgets import QMessageBox


def error(message):
    e = QMessageBox()
    label = QMessageBox()
    e.setText(message)
    e.setIcon(QMessageBox.Critical)
    e.setWindowTitle("Error")
    e.show()
    return e


@magic_factory(call_button="create checkerboard", pattern={"max": 20,
               "step": 1})
def checkerboard(image1: "napari.types.ImageData",
                 image2: "napari.types.ImageData",
                 pattern: int = 3) -> 'napari.types.LayerDataTuple':
    if image1 is None or image2 is None:
        print("No images selected for registration.")
        return error("No images selected for registration.")

    image1 = np.asarray(image1).astype(np.float32)
    image2 = np.asarray(image2).astype(np.float32)

    itk_image1 = itk.GetImageFromArray(image1)
    itk_image2 = itk.GetImageFromArray(image2)
    input1 = itk_image1
    input2 = itk_image2

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

    checkerboard_filter = itk.CheckerBoardImageFilter.New(input1, input2)

    dimension = itk_image1.GetImageDimension()
    checker_pattern = [pattern] * dimension
    checkerboard_filter.SetCheckerPattern(checker_pattern)
    checkerboard_filter.Update()
    checkerboard = checkerboard_filter.GetOutput()

    return np.asarray(checkerboard).astype(np.float32), {'name': 'checkerboard'}


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return checkerboard
