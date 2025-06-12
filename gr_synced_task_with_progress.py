import gradio as gr
from functools import partial

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
    def __init__(self, progress_bar, get_status_fn, flag_is_visible_when_non_active=False):
        super().__init__()
        self.progress_bar = progress_bar
        # Timer component for periodic updates
        self.timer = gr.Timer(1, active=False)
        self.get_status_fn = get_status_fn
        self._flag_is_visible_when_non_active = flag_is_visible_when_non_active

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
        if work_func_kwargs:
            run_sync_partial = partial(
                self._run_sync_function_with_progress,
                work_fn=work_fn,
                work_func_kwargs=work_func_kwargs,
            )
        else:
            run_sync_partial = work_fn

        inputs_blocks, output_blocks = [], []
        if gradio_blocks_to_interact:
            inputs_blocks = gradio_blocks_to_interact['inputs']
            outputs_blocks = gradio_blocks_to_interact['outputs']

        start_btn.click(
            start_timer,
            outputs=[self.timer],
        ).then(
            fn=lambda: gr.update(visible=True),
            inputs=[],
            outputs=[self.progress_bar],
        ).then(
            fn=run_sync_partial,
            inputs=inputs_blocks,
            outputs=outputs_blocks,
        ).then(
            stop_timer,
            outputs=[self.timer],
        ).then(
            fn=lambda: gr.update(visible=self._flag_is_visible_when_non_active),
            inputs=[],
            outputs=[self.progress_bar],
        )

