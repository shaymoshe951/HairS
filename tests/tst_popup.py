import gradio as gr
import time


# Alternative approach using Tabs instead of visibility toggling
def delete_item(item_id):
    print(f"Deleting item {item_id}...")
    time.sleep(1)
    return (
        "main_tab",  # Switch back to main tab
        f"Successfully deleted item {item_id}!",  # Update status
        gr.update(visible=False)  # Hide main content after deletion
    )


with gr.Blocks() as demo:
    gr.Markdown("## Modal Dialog using Tabs (Gradio 5.33.0 Compatible)")

    status_textbox = gr.Textbox(label="Status", interactive=False)
    item_to_delete = gr.State("ID-12345")

    with gr.Tabs(selected="main_tab") as tabs:
        # Main content tab
        with gr.Tab("Main", id="main_tab"):
            with gr.Group() as main_content_group:
                gr.Markdown("You are about to perform a destructive action.")
                delete_button = gr.Button("Delete Item", variant="stop")

        # Modal tab (hidden by default)
        with gr.Tab("", id="modal_tab", visible=False):
            gr.Markdown("### ⚠️ Are you sure?")
            gr.Markdown("This action cannot be undone. Are you sure you want to delete this item?")
            with gr.Row():
                cancel_button = gr.Button("Cancel")
                confirm_button = gr.Button("Yes, I'm Sure", variant="stop")

    # Event handlers
    delete_button.click(
        fn=lambda: "modal_tab",  # Switch to modal tab
        outputs=tabs
    )

    cancel_button.click(
        fn=lambda: "main_tab",  # Switch back to main tab
        outputs=tabs
    )

    confirm_button.click(
        fn=delete_item,
        inputs=item_to_delete,
        outputs=[tabs, status_textbox, main_content_group]
    )


# Alternative approach using Accordion
def create_accordion_modal():
    with gr.Blocks() as demo2:
        gr.Markdown("## Modal Dialog using Accordion (Alternative)")

        status_textbox = gr.Textbox(label="Status", interactive=False)
        item_to_delete = gr.State("ID-12345")

        # Main content
        with gr.Group() as main_content:
            gr.Markdown("You are about to perform a destructive action.")
            delete_button = gr.Button("Delete Item", variant="stop")

        # Modal as accordion (closed by default)
        with gr.Accordion("Confirm Delete", open=False, visible=False) as modal_accordion:
            gr.Markdown("### ⚠️ Are you sure?")
            gr.Markdown("This action cannot be undone. Are you sure you want to delete this item?")
            with gr.Row():
                cancel_button = gr.Button("Cancel")
                confirm_button = gr.Button("Yes, I'm Sure", variant="stop")

        def show_confirmation():
            return gr.update(visible=True, open=True)

        def hide_confirmation():
            return gr.update(visible=False, open=False)

        def delete_and_hide(item_id):
            print(f"Deleting item {item_id}...")
            time.sleep(1)
            return (
                gr.update(visible=False, open=False),  # Hide accordion
                gr.update(visible=False),  # Hide main content
                f"Successfully deleted item {item_id}!"  # Update status
            )

        # Event handlers
        delete_button.click(show_confirmation, outputs=modal_accordion)
        cancel_button.click(hide_confirmation, outputs=modal_accordion)
        confirm_button.click(
            delete_and_hide,
            inputs=item_to_delete,
            outputs=[modal_accordion, main_content, status_textbox]
        )

    return demo2


# Pure CSS/HTML approach (most reliable)
def create_html_modal():
    modal_html = """
    <div id="custom-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 10000;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3>⚠️ Are you sure?</h3>
            <p>This action cannot be undone. Are you sure you want to delete this item?</p>
            <button onclick="hideModal()" style="margin-right: 10px; padding: 8px 16px;">Cancel</button>
            <button onclick="confirmDelete()" style="padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 4px;">Yes, I'm Sure</button>
        </div>
    </div>
    <script>
        function showModal() {
            document.getElementById('custom-modal').style.display = 'block';
        }
        function hideModal() {
            document.getElementById('custom-modal').style.display = 'none';
        }
        function confirmDelete() {
            // Trigger Gradio function here
            hideModal();
            // You would need to connect this to your Gradio function
        }
    </script>
    """

    with gr.Blocks() as demo3:
        gr.Markdown("## Pure HTML Modal (Most Reliable)")
        gr.HTML(modal_html)

        status_textbox = gr.Textbox(label="Status", interactive=False)

        with gr.Group():
            gr.Markdown("You are about to perform a destructive action.")
            delete_button = gr.Button("Delete Item", variant="stop")

        delete_button.click(
            fn=None,
            js="showModal()"  # Call JavaScript function directly
        )

    return demo3


if __name__ == "__main__":
    print("Choose which version to run:")
    print("1. Tabs-based modal")
    print("2. Accordion-based modal")
    print("3. HTML/JS modal")

    choice = input("Enter choice (1-3): ").strip()

    if choice == "2":
        demo = create_accordion_modal()
    elif choice == "3":
        demo = create_html_modal()
    else:
        pass  # Use the default tabs version

    demo.launch()