from PIL import Image


class ImageAttribute:
    def __init__(self, path):
        self.path = path
        img = Image.open(path)
        self.width = img.width
        self.height = img.height
