import gradio as gr
import numpy as np

# JavaScript code is largely the same, but we must find the correct elements.
js_code = """
function trackMouseMovement(sketchpad_id, coords_id, path_id) {
    const sketchpad_container = document.getElementById(sketchpad_id);
    const coords_textbox = document.querySelector(`#${coords_id} textarea`);
    const path_textbox = document.querySelector(`#${path_id} textarea`);

    // In Gradio 2, the canvas is often directly inside the container
    const canvas = sketchpad_container.querySelector('canvas');

    if (!canvas || !coords_textbox || !path_textbox) {
        setTimeout(() => trackMouseMovement(sketchpad_id, coords_id, path_id), 500);
        return;
    }

    let isDrawing = false;
    let fullPath = [];

    canvas.addEventListener('mousedown', (e) => {
        isDrawing = true;
        fullPath = [];
        const coords = `X: ${e.offsetX}, Y: ${e.offsetY}`;
        coords_textbox.value = `Mouse Down at: ${coords}`;
        fullPath.push({x: e.offsetX, y: e.offsetY});
        path_textbox.value = '';
    });

    canvas.addEventListener('mousemove', (e) => {
        if (isDrawing) {
            const coords = `X: ${e.offsetX}, Y: ${e.offsetY}`;
            coords_textbox.value = `Drawing at: ${coords}`;
            fullPath.push({x: e.offsetX, y: e.offsetY});
        }
    });

    const stopDrawing = (e) => {
        if (isDrawing) {
            isDrawing = false;
            const coords = `X: ${e.offsetX}, Y: ${e.offsetY}`;
            coords_textbox.value = `Mouse Up at: ${coords}. Path finalized.`;
            path_textbox.value = JSON.stringify(fullPath, null, 2);
        }
    }

    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseleave', stopDrawing);
}

// The old way to run JS after load was often just to place it at the end
// or use window.onload, but we can try to get it to run after a delay.
// This is less reliable than the modern `gradio.render()`.
// For Gradio 2, we have to inject it and call it.
window.addEventListener('load', () => {
    trackMouseMovement('drawable-sketchpad', 'live-coords-output', 'final-path-output');
});
"""


def process_drawing(drawing):
    # In Gradio 2, Sketchpad just returns the numpy array of the drawing.
    return drawing


# Note: The `js` parameter does not exist in gr.Blocks in Gradio 2.
# It was injected via a now-deprecated argument. We will use gr.HTML to inject the script.
with gr.Blocks() as demo:
    gr.Markdown(
        """
        # Image Drawing and Mouse Tracking (Gradio 2.x Legacy Version)
        Draw on the blank sketchpad below.
        """
    )
    with gr.Row():
        with gr.Column():
            # Use gr.Sketchpad for drawing
            sketch_input = gr.Sketchpad(
                label="Draw on this sketchpad",
                elem_id="drawable-sketchpad"  # ID for JS
            )
            coords_output = gr.Textbox(
                label="Live Coordinates",
                interactive=False,
                elem_id="live-coords-output"  # ID for JS
            )
            path_output = gr.Textbox(
                label="Final Path",
                interactive=False,
                lines=5,
                elem_id="final-path-output"  # ID for JS
            )
        with gr.Column():
            image_output = gr.Image(label="Resulting Drawing")

    # Inject the JavaScript using a hidden gr.HTML component
    gr.HTML(f"<script>{js_code}</script>", visible=False)

    # Use the 'change' event for Sketchpad
    sketch_input.change(fn=process_drawing, inputs=sketch_input, outputs=image_output)

print(f"The Gradio version being used by this script is: {gr.__version__}")


demo.launch()