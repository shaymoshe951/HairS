
from models.bisenet_model import BiSeNet
import torch
from torchvision import transforms
from PIL import Image

class HairMaskGenerator:
    def __init__(self, model_path='./models/79999_iter.pth'):
        """
        Initialize the HairMaskGenerator with the path to the pre-trained BiSeNet model.
        """
        self.model_path = model_path
        self.net = BiSeNet(n_classes=19)
        self.net.load_state_dict(torch.load(self.model_path))
        self.net.eval()
        self.to_tensor = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize([0.5]*3, [0.5]*3)
        ])

    def generate_hair_mask(self, image):
        """
        Generate a hair mask from an image using the pre-trained BiSeNet model.
        The mask will highlight the hair region in the image.

        :param image: PIL Image object
        :return: numpy array representing the hair mask
        """
        img_tensor = self.to_tensor(image).unsqueeze(0)

        with torch.no_grad():
            out = self.net(img_tensor)[0]
            parsing = out.squeeze(0).argmax(0).numpy()
            hair_mask = (parsing == 17).astype("uint8") * 255

        return hair_mask

def generate_hair_mask(image):
    """
    Generate a hair mask from an image using a pre-trained BiSeNet model.
    The mask will highlight the hair region in the image.
    """
    # Ensure the model path is correct
    model_path = './models/79999_iter.pth'



# Load image
# img = Image.open("C:/Users/Lab/Downloads/my_pics/Shay0_ChatGPT Image Apr 25, 2025, 09_29_38 PM_part1.jpg").convert("RGB")
# to_tensor = transforms.Compose([
#     transforms.Resize((512, 512)),
#     transforms.ToTensor(),
#     transforms.Normalize([0.5]*3, [0.5]*3)
# ])
# img_tensor = to_tensor(img).unsqueeze(0)

# # Load model
# net = BiSeNet(n_classes=19)
# net.load_state_dict(torch.load('./models/79999_iter.pth'))
# net.eval()

# # Predict
# with torch.no_grad():
#     out = net(img_tensor)[0]
#     parsing = out.squeeze(0).argmax(0).numpy()
#     hair_mask = (parsing == 17).astype("uint8") * 255
#
# print("Here")