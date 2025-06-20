import gradio as gr
import time
# import threading
from functools import partial

# Global variables for progress tracking
current_progress = 0

class SyncedTaskWithProgress:
    """
    Custom progress bar that can be used to track the progress of a synchronous function.
    This class extends gr.Progress to provide a way to update the progress bar.
    Example usage:
        def my_func(text_to_show):
        global current_progress
        print(text_to_show)
        current_progress = 0
        for i in range(100):
            time.sleep(0.05)  # Simulate work
            current_progress = i + 1
            task_message = f"Processing... {current_progress}%"
        print("Done...")

    stwp = SyncedTaskWithProgress(slider_progress_bar, update_progress_function)
    stwp.configure_sync_task(start_btn, long_task_function, {'text_to_show': "This is a long task"})
    """
    def __init__(self, progress_bar, get_status_fn):
        super().__init__()
        self.progress_bar = progress_bar
        # Timer component for periodic updates
        self.timer = gr.Timer(1, active=False)
        self.get_status_fn = get_status_fn

        # Timer tick event for updating progress
        self.timer.tick(
            fn=get_status_fn,
            outputs=[self.progress_bar]
        )

        self._gradio_blocks_to_disable_during_task = []


    def _run_sync_function_with_progress(self, work_fn, work_func_kwargs):
        """
        Does the following (in this order):
         * Disable UI except the cancel button
         * Activate a progress bar in the background to check progress
         * Run the "work" function syncronously,
         * Once finished, re-enable the UI and update the progress bar to 100%
         * Return the result of the function
        """
        global current_progress

        def disable_ui():
            if self._gradio_blocks_to_disable_during_task:
                for block in self._gradio_blocks_to_disable_during_task:
                    block.update(interactive=False)
            # return gr.update(interactive=False)

        def enable_ui():
            if self._gradio_blocks_to_disable_during_task:
                for block in self._gradio_blocks_to_disable_during_task:
                    block.update(interactive=True)
            # return gr.update(interactive=True)

        disable_ui()

        # Simulate work with progress updates
        work_fn(**work_func_kwargs)

        enable_ui()

    def configure_sync_task(self, start_btn, work_fn, work_func_kwargs=None, gradio_blocks_to_interact=None, gradio_blocks_to_disable_during_task=None):

        self._gradio_blocks_to_disable_during_task = gradio_blocks_to_disable_during_task

        # Start button click event
        def start_timer():
            # print("Starting timer...")
            return gr.Timer(active=True)

        def stop_timer():
            # print("Stropping timer...")
            return gr.Timer(active=False)  # Stop the timer

        # Create a partial function with the work function and its arguments
        run_sync_partial = partial(
            self._run_sync_function_with_progress,
            work_fn=work_fn,
            work_func_kwargs=work_func_kwargs,
        )

        inputs_blocks, output_blocks = [], []
        if gradio_blocks_to_interact:
            inputs_blocks = gradio_blocks_to_interact['inputs']
            outputs_blocks = gradio_blocks_to_interact['outputs']

        start_btn.click(
            start_timer,
            outputs=[self.timer],
        ).then(
            fn=run_sync_partial,
            inputs=inputs_blocks,
            outputs=outputs_blocks,
        ).then(
            stop_timer,
            outputs=[self.timer],
        )


# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Progress Bar with Timer - Gradio 5.33")

    with gr.Column():
        start_btn = gr.Button("Start Task", variant="primary", scale=1)
        status_text = gr.Textbox(label="Status", value="Ready", interactive=False)
        slider1 = gr.Slider()
        btn_test = gr.Button("Test show text", variant="primary", scale=1)
        cancel_btn = gr.Button("Cancel", variant="primary", scale=1)
        btn_test.click(
            fn=lambda: "This is a test message",
            outputs=status_text
        )

    def update_progress():
        global current_progress
        # print(f"Current my_cnt: {SyncFunctionProgress.my_cnt}%")
        # SyncFunctionProgress.my_cnt = SyncFunctionProgress.my_cnt + 1
        if current_progress < 100:
            return gr.update(value=current_progress)
        else:
            return gr.update(value=100)


    def my_func(text_to_show):
        global current_progress
        print(text_to_show)
        current_progress = 0
        for i in range(100):
            time.sleep(0.05)  # Simulate work
            current_progress = i + 1
            task_message = f"Processing... {current_progress}%"
        print("Done...")

    def cancel_func():
        print("Cancelling...")
        time.sleep(2)
        print("Cancelled.")

    sfp = SyncedTaskWithProgress(slider1, update_progress)
    sfp.configure_sync_task(start_btn, my_func, {'text_to_show': "This is a long task"})
    cancel_btn.click(cancel_func)

if __name__ == "__main__":
    # Run the main demo with Timer
    demo.launch()