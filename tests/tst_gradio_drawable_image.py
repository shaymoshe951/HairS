import gradio as gr
import numpy as np
from PIL import Image, ImageDraw
import json


def create_drawing_interface():
    # Create a sample background image
    def create_sample_image():
        img = Image.new('RGB', (512, 512), color='lightblue')
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, 462, 462], outline='navy', width=3)
        draw.text((200, 250), "Draw on me!", fill='navy', anchor="mm")
        return img

    # Function to handle drawing updates
    def process_drawing(image_data):
        try:
            if image_data is None:
                return "No drawing data", []

            # Handle different types of image data from ImageEditor
            img = None
            if isinstance(image_data, dict):
                # ImageEditor returns a dict with 'background' and 'layers' or 'composite'
                if 'composite' in image_data:
                    img = image_data['composite']
                elif 'background' in image_data:
                    img = image_data['background']
                else:
                    # Try to get the first available image
                    for key in image_data:
                        if hasattr(image_data[key], 'convert'):
                            img = image_data[key]
                            break
            else:
                img = image_data

            if img is None:
                return "No valid image data found", []

            # Convert to numpy array to analyze
            try:
                if hasattr(img, 'convert'):
                    img_array = np.array(img.convert('RGB'))
                else:
                    img_array = np.array(img)

                # Check if array has proper dimensions
                if img_array.size == 0 or len(img_array.shape) < 2:
                    return "Invalid image dimensions", []

                height, width = img_array.shape[:2]

            except Exception as e:
                return f"Error converting image: {str(e)}", []

            # Find drawn pixels (look for non-background colors)
            drawn_pixels = []
            background_color = [173, 216, 230]  # Light blue RGB
            tolerance = 30  # Color tolerance

            # Sample every 5th pixel to avoid performance issues
            step = 5
            for y in range(0, height, step):
                for x in range(0, width, step):
                    if y < height and x < width:
                        pixel = img_array[y, x]

                        # Check if pixel is significantly different from background
                        color_diff = sum(abs(pixel[i] - background_color[i]) for i in range(3))
                        if color_diff > tolerance:
                            drawn_pixels.append({
                                "x": int(x),
                                "y": int(y),
                                "color": pixel.tolist()
                            })

            info = f"Drawing analysis: Found {len(drawn_pixels)} modified pixels (sampled every {step} pixels)"
            return info, drawn_pixels[:50]  # Return first 50 pixels to avoid overwhelming display

        except Exception as e:
            return f"Error processing drawing: {str(e)}", []

    # Function to reset the canvas
    def reset_canvas():
        return create_sample_image()

    # Function to load custom background
    def load_background(uploaded_image):
        if uploaded_image is not None:
            # Resize to standard size for consistency
            img = uploaded_image.resize((512, 512))
            return img
        return create_sample_image()

    # Create the Gradio interface
    with gr.Blocks(title="Interactive Drawing on Image") as demo:
        gr.Markdown("# Interactive Drawing Interface")
        gr.Markdown("Draw on the image below. The interface will track your drawing and show pixel coordinates.")

        with gr.Row():
            with gr.Column(scale=1):
                # Upload section
                gr.Markdown("### Upload Background Image (Optional)")
                upload_input = gr.Image(
                    type="pil",
                    label="Upload your image",
                    height=200
                )

                # Control buttons
                reset_btn = gr.Button("Reset Canvas", variant="secondary")

                # Information display
                gr.Markdown("### Drawing Information")
                drawing_info = gr.Textbox(
                    label="Drawing Status",
                    value="Start drawing to see information",
                    interactive=False
                )

                # Pixel coordinates display
                pixel_coords = gr.JSON(
                    label="Sample Drawn Pixels (x, y, [r,g,b])",
                    value=[]
                )

            with gr.Column(scale=2):
                # Main drawing area
                gr.Markdown("### Drawing Canvas")
                gr.Markdown("Use the drawing tools below to draw on the image. Click and drag to draw.")

                # This is the key component - ImageEditor allows drawing
                drawing_canvas = gr.ImageEditor(
                    label="Draw on the image",
                    type="pil",
                    brush=gr.Brush(colors=["#ff0000", "#00ff00", "#0000ff", "#000000", "#ffffff"]),
                    value=create_sample_image(),
                    height=512,
                    width=512
                )

        # Event handlers
        upload_input.change(
            fn=load_background,
            inputs=[upload_input],
            outputs=[drawing_canvas]
        )

        reset_btn.click(
            fn=reset_canvas,
            outputs=[drawing_canvas]
        )

        # Track drawing changes
        drawing_canvas.change(
            fn=process_drawing,
            inputs=[drawing_canvas],
            outputs=[drawing_info, pixel_coords]
        )

        # Instructions
        gr.Markdown("""
        ### Instructions:
        1. **Upload Image**: Optionally upload your own background image
        2. **Select Tool**: Use the brush tool in the image editor
        3. **Choose Color**: Pick a color from the palette
        4. **Draw**: Click and drag on the image to draw
        5. **Monitor**: Watch the drawing information update as you draw
        6. **Reset**: Use the reset button to start over

        ### Features:
        - Real-time drawing detection
        - Pixel coordinate tracking
        - Multiple brush colors
        - Custom background images
        - Drawing analysis and feedback
        """)

    return demo


# Alternative approach using Sketchpad (if you prefer a more drawing-focused interface)
def create_sketchpad_interface():
    def analyze_sketch(sketch_data):
        if sketch_data is None:
            return "No sketch data"

        # Convert sketch to image and analyze
        if hasattr(sketch_data, 'convert'):
            img_array = np.array(sketch_data.convert('RGB'))
            non_white_pixels = np.sum(img_array < 250, axis=2) > 0
            drawn_pixel_count = np.sum(non_white_pixels)
            return f"Sketch analyzed: {drawn_pixel_count} pixels drawn"

        return "Sketch received"

    with gr.Blocks(title="Sketchpad Drawing Interface") as demo:
        gr.Markdown("# Sketchpad Drawing Interface")
        gr.Markdown("Use the sketchpad below to draw. This provides a clean drawing experience.")

        with gr.Row():
            with gr.Column():
                # Sketchpad for pure drawing
                sketchpad = gr.Sketchpad(
                    label="Draw here",
                    height=400,
                    width=400
                )

                clear_sketch_btn = gr.Button("Clear Sketch")

            with gr.Column():
                sketch_info = gr.Textbox(
                    label="Sketch Analysis",
                    value="Start drawing...",
                    interactive=False
                )

        # Event handlers
        sketchpad.change(
            fn=analyze_sketch,
            inputs=[sketchpad],
            outputs=[sketch_info]
        )

        clear_sketch_btn.click(
            fn=lambda: None,
            outputs=[sketchpad]
        )

    return demo


# Main execution
if __name__ == "__main__":
    # Choose which interface to run
    print("Choose interface:")
    print("1. Image Editor (draw on background image)")
    print("2. Sketchpad (pure drawing)")

    choice = input("Enter 1 or 2 (default 1): ").strip()

    if choice == "2":
        demo = create_sketchpad_interface()
    else:
        demo = create_drawing_interface()

    demo.launch(debug=True)