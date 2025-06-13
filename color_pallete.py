import os

from PIL import Image

hair_color_dict = {
    "1.1": {"Category": "Cool / Ash", "Code": "1.1", "Name": "Blue Black", "Description": "Very dark with a blue undertone"},
    "4.1": {"Category": "Cool / Ash", "Code": "4.1", "Name": "Ash Brown", "Description": "Medium brown with ash undertones"},
    "5.1": {"Category": "Cool / Ash", "Code": "5.1", "Name": "Light Ash Brown", "Description": "Slightly lighter ash brown"},
    "6.1": {"Category": "Cool / Ash", "Code": "6.1", "Name": "Dark Ash Blonde", "Description": "Cool-toned dark blonde"},
    "7.1": {"Category": "Cool / Ash", "Code": "7.1", "Name": "Ash Blonde", "Description": "Medium blonde with silvery undertones"},
    "8.1": {"Category": "Cool / Ash", "Code": "8.1", "Name": "Light Ash Blonde", "Description": "Light cool blonde"},
    "9.3": {"Category": "Golden / Warm", "Code": "9.3", "Name": "Very Light Golden Blonde", "Description": "Warm pale blonde"},
    "8.03": {"Category": "Golden / Warm", "Code": "8.03", "Name": "Light Natural-Golden Blonde", "Description": "Natural golden tone"},
    "8.3": {"Category": "Golden / Warm", "Code": "8.3", "Name": "Light Golden Blonde", "Description": "Golden light blonde"},
    "7.3": {"Category": "Golden / Warm", "Code": "7.3", "Name": "Dark Golden Blonde", "Description": "Warm golden dark blonde"},
    "6.34": {"Category": "Golden / Warm", "Code": "6.34", "Name": "Light Brown with Gold-Copper", "Description": "Golden-copper brown"},
    "6.3": {"Category": "Golden / Warm", "Code": "6.3", "Name": "Light Golden Brown", "Description": "Warm light brown"},
    "8.8": {"Category": "Mocha", "Code": "8.8", "Name": "Light Mocha Blonde", "Description": "Medium-light blonde with mocha tone"},
    "7.8": {"Category": "Mocha", "Code": "7.8", "Name": "Mocha Blonde", "Description": "Slightly darker mocha blonde"},
    "6.8": {"Category": "Mocha", "Code": "6.8", "Name": "Dark Mocha Blonde", "Description": "Deep warm blonde with mocha"},
    "5.8": {"Category": "Mocha", "Code": "5.8", "Name": "Light Mocha Brown", "Description": "Rich warm light brown"},
    "4.8": {"Category": "Mocha", "Code": "4.8", "Name": "Mocha Brown", "Description": "Warm medium brown"},
    "4.2": {"Category": "Fashion", "Code": "4.2", "Name": "Intense Violet Brown", "Description": "Deep brown with purple tone"},
    "9.22": {"Category": "Fashion", "Code": "9.22", "Name": "Very Light Blonde – Deep Iris", "Description": "Pale blonde with violet/iridescent"},
    "9.2": {"Category": "Fashion", "Code": "9.2", "Name": "Very Light Blonde – Iridescent Ash", "Description": "Pale ash with iridescent tones"},
    "9": {"Category": "Classic", "Code": "9", "Name": "Very Light Blonde", "Description": ""},
    "8": {"Category": "Classic", "Code": "8", "Name": "Light Blonde", "Description": ""},
    "7": {"Category": "Classic", "Code": "7", "Name": "Dark Blonde", "Description": ""},
    "6": {"Category": "Classic", "Code": "6", "Name": "Light Brown", "Description": ""},
    "5": {"Category": "Classic", "Code": "5", "Name": "Medium Brown", "Description": ""},
    "4": {"Category": "Classic", "Code": "4", "Name": "Dark Brown", "Description": ""},
    "3": {"Category": "Classic", "Code": "3", "Name": "Very Dark Brown", "Description": ""},
    "1": {"Category": "Classic", "Code": "1", "Name": "Black", "Description": ""},
}

class ColorPalette:
    def __init__(self, resolution = 128):
        self.resolution = resolution
        self.colors = hair_color_dict
        self.update_color_images()

    def get_color_by_code(self, code):
        return self.colors.get(code, None)

    def get_all_colors(self):
        return self.colors

    def get_colors_by_category(self, category):
        return {code: details for code, details in self.colors.items() if details["Category"] == category}

    def get_all_categories(self):
        return set(details["Category"] for details in self.colors.values())

    def update_color_images(self):
        """Returns a dictionary of color codes to image paths."""
        # Get all images from the colors dictionary
        folder = r"./resources/hair_colors"
        # Get all files in the folder
        files = os.listdir(folder)
        for file in files:
            if file.endswith(".png"):
                code = file.replace(".png", "")
                if code in self.colors:
                    self.colors[code]["Image"] = Image.open(os.path.join(folder, file)).resize((self.resolution, self.resolution))
                    self.colors[code]["path"] = os.path.join(folder, file)
                else:
                    print(f"Warning: Color code {code} not found in color dictionary.")

    def get_color_image(self, code):
        """Returns the image for a given color code."""
        color = self.get_color_by_code(code)
        if color and "Image" in color:
            return color["Image"]
        else:
            print(f"Warning: No image found for color code {code}.")
            return None

    def get_color_path(self, code):
        """Returns the image for a given color code."""
        color = self.get_color_by_code(code)
        if color and "path" in color:
            return color["path"]
        else:
            print(f"Warning: No image found for color code {code}.")
            return None