import gradio as gr
import os
from PIL import Image, ImageOps, ImageDraw

from auto1111_if import color_modification, get_progress, adding_hair_modification
from color_pallete import ColorPalette
from hair_utils import HairMaskGenerator
from vers_image import VersImage
from gr_synced_task_with_progress import SyncedTaskWithProgress
import numpy as np

def resize_image(img, present_resolution = 512):
    old_ratio = 1.2
    new_ratio = (1.6 + old_ratio) / 2.0
    nw = int(img.width * new_ratio / old_ratio)
    # Create a new blank RGB image with black padding
    pad_width_offset = (nw - img.width) // 2
    padded_img = ImageOps.expand(img,
                                 border=(pad_width_offset, 0, pad_width_offset, 0), fill='black')
    new_img = padded_img.resize((present_resolution, present_resolution))
    return new_img


def load_images():
    # Load images from a directory
    image_dir = "C:/Users/Lab/Downloads/my_pics"

    images = []
    for filename in os.listdir(image_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(image_dir, filename)
            img = Image.open(img_path)
            images.append(resize_image(img))

    return images


# Define the total number of screens
NUM_SCREENS = 3
color_pallete = ColorPalette()
color_pallete_categories = sorted(color_pallete.get_all_categories())
hair_mask_generator = HairMaskGenerator()


# --- 1. State Management ---
# We need to store two pieces of state:
# a) The current screen index (e.g., 0, 1, 2)
# b) The data collected from the user across all screens. A dictionary is great for this.

def create_initial_state():
    """Returns the initial state for the app."""
    return 0, {}  # screen_index, user_data


# --- 2. Logic for Navigation and Data Handling ---

def change_screen(screen_index, direction, user_data, working_images):
    """
    This is the core function that handles screen transitions and data saving.
    It's triggered by the 'Next' and 'Previous' buttons.
    """
    # --- Data Saving ---
    # Save the input from the *previous* screen before changing the index.
    if direction == "next":
        if screen_index == 0:
            if 'images' in user_data:
                working_images = user_data['images']


        # Move to the next screen
        screen_index += 1
    elif direction == "prev":
        # Move to the previous screen
        screen_index -= 1

    # --- UI Updates ---
    # Create a list of visibility updates for all screens.
    # Start by hiding all of them.
    screen_updates = [gr.update(visible=False)] * NUM_SCREENS

    # Set the new current screen to be visible.
    if 0 <= screen_index < NUM_SCREENS:
        screen_updates[screen_index] = gr.update(visible=True)

    # --- Button Visibility ---
    # Control the visibility of the 'Previous' and 'Next' buttons.
    prev_btn_update = gr.update(visible=screen_index > 0)
    next_btn_update = gr.update(visible=screen_index < NUM_SCREENS - 1)

    # # --- Summary Generation ---
    # # If we are on the last screen, generate the summary.
    # summary_text = ""
    # if screen_index == NUM_SCREENS - 1:
    #     name = user_data.get('name', 'N/A')
    #     options = ", ".join(user_data.get('options', [])) or "None"
    #     summary_text = f"## Installation Summary\n\n" \
    #                    f"**Name:** {name}\n\n" \
    #                    f"**Selected Options:** {options}\n\n" \
    #                    f"Ready to proceed!"

    # --- Return all updates ---
    # The order of returned values must match the order of the `outputs` list in the .click() event.
    return [screen_index, user_data] + screen_updates + [prev_btn_update, next_btn_update] + [working_images]

def apply_colors(user_data, working_images):
    """
    Apply the selected colors to the working images.
    This function is a placeholder and should be replaced with actual processing logic.
    """
    # For now, just return the working images as is.
    # In a real application, you would apply the selected colors to the images here.
    if 'images' in user_data:
        cur_image = user_data['images'][-1]  # Get the last selected image
    else:
        raise ValueError("No images selected in user_data.")
    if 'selected_color_code' in user_data:
        selected_color_code = user_data['selected_color_code']
    else:
        print("No color selected, returning original image.")
        return working_images
    selected_color_name = color_pallete.get_color_by_code(selected_color_code)["Name"]
    hair_mask = hair_mask_generator.generate_hair_mask(cur_image)
    print(f"Applying color: {selected_color_name} to the hair mask.")
    colored_image = color_modification(VersImage.from_image(cur_image), VersImage.from_numpy(hair_mask), selected_color_name)
    if colored_image is None:
        raise Exception("Operation failed, check that the automatic1111 server is running.")
    working_images.append(colored_image.image)
    return working_images

def apply_edits(drawing_canvas, user_data, working_images):
    """
    Apply the edits made on the drawing canvas to the working images.
    This function is a placeholder and should be replaced with actual processing logic.
    """
    if 'images' in user_data and len(user_data['images']) > 0:
        cur_image = user_data['images'][-1]  # Get the last selected image
    else:
        raise ValueError("No images selected in user_data.")

    if drawing_canvas is None or 'background' not in drawing_canvas or 'composite' not in drawing_canvas:
        return working_images
    background_img = drawing_canvas['background']
    comp_img = drawing_canvas['composite']
    if background_img is None or comp_img is None:
        return working_images
    xor_img = np.bitwise_xor(background_img,
                             comp_img)
    drawing_mask = (xor_img.sum(axis=2) > 0)
    if drawing_mask.sum() == 0:
        print("No drawing mask found, returning original image.")
        return working_images

    hair_mask = hair_mask_generator.generate_hair_mask(cur_image)
    hair = np.array(cur_image) * (hair_mask[:,:, None] > 0)  # Apply hair mask to the current image

    # # Debug
    # Image.fromarray((drawing_mask * 255).astype(np.uint8)).save("C:/Users/Lab/Downloads/drawing_mask.png")
    # Image.fromarray(hair.astype(np.uint8)).save("C:/Users/Lab/Downloads/hair_only.png")
    # cur_image.save("C:/Users/Lab/Downloads/background_image.png")

    # # Apply the drawing mask to the current image
    # edited_image = Image.fromarray(np.array(cur_image) * drawing_mask[:, :, None])
    #
    modified_image = adding_hair_modification(VersImage.from_image(cur_image), VersImage.from_image(Image.fromarray(hair.astype(np.uint8))), VersImage.from_image(Image.fromarray((drawing_mask * 255).astype(np.uint8))))
    working_images.append(modified_image.image)
    return working_images

# --- 3. Gradio UI Layout ---


with gr.Blocks(theme=gr.themes.Soft(), css="footer {display: none !important}") as demo:
    gr.Markdown("# Hair Styles")

    # Initialize state variables
    screen_index = gr.State(0)
    user_data = gr.State({})

    working_images = gr.State([])

    @gr.render(inputs=working_images)
    def render_working_images(images):
        with gr.Row():
            # print("Rendering working images...", len(images))
            for ind, img in enumerate(images):
                gr.Image(interactive=False, value=img, scale=0, show_label=False, show_download_button=False, show_fullscreen_button=False)
                if ind < len(images) - 1: # One more image at least
                    gr.Image(interactive=False, value=r"./resources/right_arrow.png", scale=0, show_label=False, show_download_button=False, show_fullscreen_button=False)

    progress_bar = gr.Slider(visible=False)
    gstwp = SyncedTaskWithProgress(progress_bar, get_progress, flag_is_visible_when_non_active=False)

    def on_gallery_img_select(evt: gr.SelectData, user_data):
        img_url = evt.value['image']['path']
        img = Image.open(img_url)
        user_data['images'] = [img]

        return user_data

    # --- Screen 1: Base Picture Selection ---
    with gr.Column(visible=True) as screen1:
        gr.Markdown("## Select Picture")
        # gr.Markdown("Please enter your name to personalize the installation.")
        gallery = gr.Gallery(label="Image Gallery", show_label=True, columns=4, value=load_images())
        gallery.select(fn=on_gallery_img_select, inputs=user_data, outputs=user_data)

    # --- Screen 2: Colors ---
    with gr.Column(visible=False) as screen2:
        gr.Markdown("## Color change")
        gr.Markdown("Select color or next to skip.")
        color_code_list = {}
        for category in color_pallete_categories:
            with gr.Tab(category):
                gr.Markdown(f"### {category}")
                colors_in_category = color_pallete.get_colors_by_category(category)
                imgs, color_code_list_per_category = [], []
                for img_index, color in enumerate(colors_in_category):
                    color_img = color_pallete.get_color_image(color)
                    if color_img:
                        imgs.append(color_img)
                        color_code_list_per_category.append(color)
                color_code_list[category] = gr.State(value=color_code_list_per_category)

                gallery_colors = gr.Gallery(
                    value=imgs,
                    scale=0,
                    container=False,
                    columns=8,
                    height=color_pallete.resolution*2,
                    object_fit="none",  # This is the key parameter!
                )
                def on_gallery_color_select(color_code_list_per_category ,user_data, evt: gr.SelectData):
                    # print("index=",evt.index)
                    # print("color=",color_code_list_per_category[evt.index])
                    user_data['selected_color_code'] = color_code_list_per_category[evt.index]
                    return user_data
                gallery_colors.select(fn=on_gallery_color_select, inputs = [color_code_list[category],user_data], outputs = [user_data])


                # Add a button to apply the selected colors
                apply_button = gr.Button("Apply Colors", variant="primary")
                gstwp.configure_sync_task(apply_button, apply_colors, work_func_kwargs={},
                                          gradio_blocks_to_interact={'inputs': [user_data, working_images], 'outputs': [working_images]})



    # --- Screen 3: Summary ---
    with gr.Column(visible=False) as screen3:
        gr.Markdown("## Minor edits")
        gr.Markdown("Draw on the image to extend/reduce hair line.")
        drawing_canvas = gr.ImageEditor(
            type="numpy",
            crop_size="1:1",
            brush=gr.Brush(colors=["#ff0000", "#00ff00", "#0000ff", "#000000", "#ffffff"], default_size=3,
                           default_color="#000000"),
            value=lambda user_data: np.array(user_data['images'][-1]) if 'images' in user_data and len(user_data['images']) > 0 else None,
            inputs=user_data,
            sources = None,
            eraser = None,
        )
        apply_edits_button = gr.Button("Apply Edits", variant="primary")
        gstwp.configure_sync_task(apply_edits_button, apply_edits, work_func_kwargs={},
                                  gradio_blocks_to_interact={'inputs': [drawing_canvas, user_data, working_images],
                                                             'outputs': [working_images]})


        # def process_drawing(image_data, user_data):
        #     if image_data is None or 'background' not in image_data or 'composite' not in image_data:
        #         return user_data
        #     background_img = image_data['background']
        #     comp_img = image_data['composite']
        #     if background_img is None or comp_img is None:
        #         return user_data
        #     xor_img = np.bitwise_xor(background_img,
        #                              comp_img)
        #     drawing_mask = (xor_img.sum(axis=2) > 0)
        #     if drawing_mask.sum() > 0:
        #         user_data['drawing_mask_np'] = drawing_mask
        #
        #     return user_data

        # drawing_canvas.change(
        #     fn=process_drawing,
        #     inputs=[drawing_canvas, user_data],
        #     outputs=[user_data]
        # )


    # --- Navigation Buttons ---
    with gr.Row():
        prev_button = gr.Button("Previous", visible=False)
        next_button = gr.Button("Next")
        # We could add a "Finish" button that is only visible on the last screen.
        # finish_button = gr.Button("Finish", variant="primary", visible=False)

    # --- 4. Event Listeners ---

    # Gather all screen components and inputs into lists for easier handling.
    all_screens = [screen1, screen2, screen3]
    all_inputs = [working_images]

    # When the "Next" button is clicked
    next_button.click(
        fn=change_screen,
        inputs=[screen_index, gr.State("next"), user_data] + all_inputs,
        outputs=[screen_index, user_data] + all_screens + [prev_button, next_button] + [working_images]
    )

    # When the "Previous" button is clicked
    prev_button.click(
        fn=change_screen,
        inputs=[screen_index, gr.State("prev"), user_data] + all_inputs,
        outputs=[screen_index, user_data] + all_screens + [prev_button, next_button]+ [working_images]
    )

    # Reset the state when the app loads/reloads
    demo.load(
        fn=create_initial_state,
        inputs=None,
        outputs=[screen_index, user_data]
    )

if __name__ == "__main__":
    demo.launch(server_port=7861)

