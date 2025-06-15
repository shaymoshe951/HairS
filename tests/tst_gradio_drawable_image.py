import gradio as gr
import numpy as np
from PIL import Image, ImageDraw
import io
import base64


def create_drawing_interface():
    # Sample image - you can replace this with your own image loading logic
    def load_sample_image():
        # Create a simple sample image or load your own
        img = Image.new('RGB', (800, 600), color='lightblue')
        draw = ImageDraw.Draw(img)
        draw.rectangle([100, 100, 700, 500], outline='navy', width=3)
        draw.text((350, 300), "Draw on me!", fill='navy')
        return img

    # HTML and JavaScript for drawing functionality
    drawing_html = """
    <div id="drawing-container" style="position: relative; display: inline-block;">
        <canvas id="drawing-canvas" style="border: 2px solid #333; cursor: crosshair;"></canvas>
    </div>

    <script>
    (function() {
        const canvas = document.getElementById('drawing-canvas');
        const ctx = canvas.getContext('2d');
        let isDrawing = false;
        let lastX = 0;
        let lastY = 0;
        let drawingData = [];

        // Set canvas size
        canvas.width = 800;
        canvas.height = 600;

        // Load background image
        const img = new Image();
        img.onload = function() {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        };

        // Set drawing style
        ctx.strokeStyle = '#ff0000';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        function startDrawing(e) {
            isDrawing = true;
            const rect = canvas.getBoundingClientRect();
            lastX = e.clientX - rect.left;
            lastY = e.clientY - rect.top;

            // Start new stroke
            drawingData.push({
                type: 'start',
                x: lastX,
                y: lastY,
                timestamp: Date.now()
            });

            ctx.beginPath();
            ctx.moveTo(lastX, lastY);
        }

        function draw(e) {
            if (!isDrawing) return;

            const rect = canvas.getBoundingClientRect();
            const currentX = e.clientX - rect.left;
            const currentY = e.clientY - rect.top;

            // Record mouse movement
            drawingData.push({
                type: 'move',
                x: currentX,
                y: currentY,
                timestamp: Date.now()
            });

            ctx.lineTo(currentX, currentY);
            ctx.stroke();

            lastX = currentX;
            lastY = currentY;
        }

        function stopDrawing() {
            if (!isDrawing) return;
            isDrawing = false;

            drawingData.push({
                type: 'end',
                timestamp: Date.now()
            });

            // Log drawing data (you can process this data as needed)
            console.log('Drawing data:', drawingData);

            // You can send this data to Python backend if needed
            // For example, using a custom Gradio event
        }

        // Mouse events
        canvas.addEventListener('mousedown', startDrawing);
        canvas.addEventListener('mousemove', draw);
        canvas.addEventListener('mouseup', stopDrawing);
        canvas.addEventListener('mouseout', stopDrawing);

        // Touch events for mobile support
        canvas.addEventListener('touchstart', function(e) {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousedown', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            canvas.dispatchEvent(mouseEvent);
        });

        canvas.addEventListener('touchmove', function(e) {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent('mousemove', {
                clientX: touch.clientX,
                clientY: touch.clientY
            });
            canvas.dispatchEvent(mouseEvent);
        });

        canvas.addEventListener('touchend', function(e) {
            e.preventDefault();
            const mouseEvent = new MouseEvent('mouseup', {});
            canvas.dispatchEvent(mouseEvent);
        });

        // Function to load background image
        window.loadBackgroundImage = function(imageData) {
            img.src = 'data:image/png;base64,' + imageData;
        };

        // Function to clear canvas
        window.clearCanvas = function() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (img.complete) {
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            }
            drawingData = [];
        };

        // Function to get canvas data
        window.getCanvasData = function() {
            return canvas.toDataURL();
        };

        // Load initial sample image
        img.src = 'data:image/svg+xml;base64,' + btoa(`
            <svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
                <rect width="800" height="600" fill="lightblue"/>
                <rect x="100" y="100" width="600" height="400" fill="none" stroke="navy" stroke-width="3"/>
                <text x="350" y="320" font-family="Arial" font-size="24" fill="navy" text-anchor="middle">Draw on me!</text>
            </svg>
        `);

    })();
    </script>
    """

    def clear_drawing():
        return gr.HTML(drawing_html + "<script>if(window.clearCanvas) window.clearCanvas();</script>")

    def upload_image(image):
        if image is not None:
            # Convert PIL image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            return gr.HTML(
                drawing_html + f"<script>if(window.loadBackgroundImage) window.loadBackgroundImage('{img_str}');</script>")
        return gr.HTML(drawing_html)

    # Create Gradio interface
    with gr.Blocks(title="Image Drawing Interface") as demo:
        gr.Markdown("# Image Drawing Interface")
        gr.Markdown("Upload an image and draw on it with your mouse. Mouse movements are tracked during drawing.")

        with gr.Row():
            with gr.Column():
                image_input = gr.Image(type="pil", label="Upload Background Image (optional)")
                clear_btn = gr.Button("Clear Drawing", variant="secondary")

            with gr.Column():
                drawing_area = gr.HTML(drawing_html, label="Drawing Area")

        # Event handlers
        image_input.change(
            fn=upload_image,
            inputs=[image_input],
            outputs=[drawing_area]
        )

        clear_btn.click(
            fn=clear_drawing,
            outputs=[drawing_area]
        )

    return demo


# Create and launch the interface
if __name__ == "__main__":
    demo = create_drawing_interface()
    demo.launch()