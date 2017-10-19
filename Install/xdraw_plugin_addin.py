import pythonaddins
import pythonaddins


# from xdraw import XDraw


class Settings:
    elevation_map = None
    path_map = None


class ImageSelectFilter(object):
    def __str__(self):
        return "*.tif, *.tiff, *.png"

    def __call__(self, filename):
        if os.path.isfile(filename) and filename.lower().endswith((".tiff", ".tif", ".png")):
            return True
        return False


class CalculateBtn(object):
    """Implementation for xdraw_plugin_addin.button (Button)"""

    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        # XDraw.xdraw()
        print("nothing")


class LoadElevationBtn(object):
    """Implementation for xdraw_plugin_addin.loadelevationbtn (Button)"""

    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        Settings.elevation_map = pythonaddins.OpenDialog("Select the elevation data...", False, ".", "Select",
                                                         ImageSelectFilter(), "Elevation map - *.tif, *.tiff, *.png")


class LoadPathBtn(object):
    """Implementation for xdraw_plugin_addin.loadpathbtn (Button)"""

    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        Settings.path_map = pythonaddins.OpenDialog("Select the path data...", False, ".", "Select",
                                                    ImageSelectFilter(), "Path map - *.tif, *.tiff, *.png")

