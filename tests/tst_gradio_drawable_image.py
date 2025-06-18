import gradio as gr
import time

from PIL import Image
import numpy as np


def sleep(im):
    time.sleep(5)
    return [im["background"], im["layers"][0], im["layers"][1], im["composite"]]


def predict(im):
    return im["composite"]


with gr.Blocks() as demo:
    with gr.Row():
        # Add height and width to the ImageEditor?
        im = gr.ImageEditor(
            type="numpy",
            crop_size="1:1",
            brush=gr.Brush(colors=["#ff0000", "#00ff00", "#0000ff", "#000000", "#ffffff"], default_size=3, default_color="#000000"),
            value = np.array(Image.new("RGB", (512, 512), (128, 200, 200))) ,
        )
        im_preview = gr.Image()
    n_upload = gr.Number(0, label="Number of upload events", step=1)
    n_change = gr.Number(0, label="Number of change events", step=1)
    n_input = gr.Number(0, label="Number of input events", step=1)

    # im.upload(lambda x: x + 1, outputs=n_upload, inputs=n_upload)
    # # im.change(lambda x: x + 1, outputs=n_change, inputs=n_change)
    # im.input(lambda x: x + 1, outputs=n_input, inputs=n_input)
    im.change(predict, outputs=im_preview, inputs=im, show_progress="hidden")

if __name__ == "__main__":
    demo.launch(debug=True)