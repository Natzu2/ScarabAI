import dearpygui.dearpygui as dpg
from utils import Theme
import time

class popUp:
    def __init__(self):
        pass

    def centered_popup(self, modal_id):
        # guarantee these commands happen in another frame
        dpg.split_frame()
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        width = dpg.get_item_width(modal_id)
        height = dpg.get_item_height(modal_id)
        return [(viewport_width // 2 - width // 2), (viewport_height // 2 - height // 2)]

    def show_info(self, title, message, large):
        # guarantee these commands happen in the same frame
        with dpg.mutex():
            with dpg.window(label=title, no_close=True, no_collapse=True, show=False, width=large, no_resize=True) as modal_id:
                dpg.add_text(message, color=(0,0,0,255))

        dpg.bind_item_theme(modal_id, Theme().getPopUpTheme())
        dpg.set_item_pos(modal_id, self.centered_popup(modal_id))
        dpg.configure_item(modal_id, show=True)
        time.sleep(4)
        dpg.delete_item(modal_id)