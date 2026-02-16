from dearpygui.dearpygui import *


class Theme:
    def __init__(self):
        self.catgory = mvThemeCat_Core
    def getTheme(self):
        with font_registry():
            default_font = add_font("data/Montserrat-Regular.ttf", 24, tag="ttf-menu")
            hipper_font = add_font("data/Montserrat-Regular.ttf", 45, tag="tff-commands")
        with theme() as global_theme:
            with theme_component(mvAll):
                #add_theme_color(mvThemeCol_Text, (0,0,0,255), category=self.catgory)
                add_theme_color(mvThemeCol_WindowBg, (46,73,87,255), category=self.catgory)
                add_theme_style(mvStyleVar_FrameRounding, 6, category=self.catgory)
                add_theme_style(mvStyleVar_FrameBorderSize, 1, category=self.catgory)
                add_theme_color(mvThemeCol_Border,(0,0,0,255), category=self.catgory)
                add_theme_color(mvThemeCol_BorderShadow,(255,255,255,0), category=self.catgory)
                bind_font(default_font)
                
                #Tab bar styles#############################################################
                add_theme_color(mvThemeCol_Tab, (203,115,36,255), category=self.catgory)
                add_theme_color(mvThemeCol_TabHovered, (247,159,17,255), category=self.catgory)
                add_theme_color(mvThemeCol_TabActive, (255,131,0,255), category=self.catgory)

                #Windows styles
                add_theme_color(mvThemeCol_Text, (0,0,0,255), category=self.catgory)
                add_theme_color(mvThemeCol_PopupBg, (255,255,255,255), category=self.catgory)

                #Buttons and textBox styles
                add_theme_color(mvThemeCol_Button, (233, 131, 0, 255), category=self.catgory)
                add_theme_color(mvThemeCol_ButtonHovered, (143, 184, 56, 255), category=self.catgory)
                add_theme_color(mvThemeCol_FrameBg, (255, 255, 255, 255), category=self.catgory)
                add_theme_color(mvThemeCol_FrameBgHovered, (143, 184, 56, 255), category=self.catgory)
                
                #scroll
                add_theme_color(mvThemeCol_ScrollbarBg, (241,241,241,255), category=self.catgory)
                add_theme_color(mvThemeCol_ScrollbarGrab, (193,193,193,255), category=self.catgory)
                add_theme_color(mvThemeCol_ScrollbarGrabHovered, (168,168,168,255), category=self.catgory)
                add_theme_color(mvThemeCol_ScrollbarGrabActive, (120,120,120,255), category=self.catgory)
                
                #Table Headers
                add_theme_color(mvThemeCol_TableHeaderBg, (44, 139, 71, 255), category=self.catgory)
            
            with theme_component(mvProgressBar):
                add_theme_color(mvThemeCol_PlotHistogram, (233, 131, 0, 255), category=self.catgory)
            with theme_component(mvButton):
                add_theme_color(mvThemeCol_Text, (255, 255, 255, 255), category=self.catgory)
        return global_theme
    
    def getExitTheme(self):
        with theme() as button_theme:
            with theme_component(mvButton):
                add_theme_color(mvThemeCol_Button, (255,0,0,255), category=self.catgory)
                add_theme_color(mvThemeCol_ButtonHovered,(200,0,0,255),category=self.catgory)
        return button_theme
    
    def getModalTheme(self):
        with theme() as modal_theme:
            with theme_component(mvAll):
                add_theme_color(mvThemeCol_TitleBg,(37,37,38,255),category=self.catgory)
                add_theme_color(mvThemeCol_FrameBg,(37,37,38,255),category=self.catgory)
                add_theme_color(mvThemeCol_Button, (156,156,156,255), category=self.catgory)
                add_theme_color(mvThemeCol_ButtonHovered,(205,205,205,255),category=self.catgory)
        return modal_theme

    def getSelectTheme(self):
            with theme() as select_theme:
                with theme_component(mvAll):
                    #Button Styles
                    add_theme_color(mvThemeCol_Button, (233, 131, 0, 255), category=self.catgory)
                    add_theme_color(mvThemeCol_ButtonHovered, (233, 131, 0, 200), category=self.catgory)
                    #Frame Styles
                    add_theme_color(mvThemeCol_FrameBg, (255, 255, 255, 245), category=self.catgory)
                    add_theme_color(mvThemeCol_FrameBgHovered, (233, 131, 0, 175), category=self.catgory)
                    add_theme_color(mvThemeCol_PopupBg, (255, 255, 255, 245), category=self.catgory)
                    add_theme_color(mvThemeCol_Header, (255, 255, 255, 245), category=self.catgory)
                    add_theme_color(mvThemeCol_HeaderHovered, (233, 131, 0, 175), category=self.catgory)
                    #scroll
                    add_theme_color(mvThemeCol_ScrollbarBg, (241,241,241,255), category=self.catgory)
                    add_theme_color(mvThemeCol_ScrollbarGrab, (193,193,193,255), category=self.catgory)
                    add_theme_color(mvThemeCol_ScrollbarGrabHovered, (168,168,168,255), category=self.catgory)
                    add_theme_color(mvThemeCol_ScrollbarGrabActive, (120,120,120,255), category=self.catgory)
            return select_theme
        
    def getPopUpTheme(self):
        with theme() as popup_theme:
            with theme_component(mvAll):
                add_theme_color(mvThemeCol_Text, (0,0,0,255), category=self.catgory)
                add_theme_color(mvThemeCol_WindowBg, (255,255,255, 250), category=self.catgory)
                add_theme_color(mvThemeCol_TitleBg, (233, 131, 0, 250), category=self.catgory)
                add_theme_color(mvThemeCol_TitleBgActive,(233, 131, 0, 250), category=self.catgory)
                add_theme_style(mvStyleVar_FrameRounding, 6, category=self.catgory)
                add_theme_style(mvStyleVar_FrameBorderSize, 1, category=self.catgory)
                add_theme_style(mvStyleVar_WindowTitleAlign, x=0.50, y=0.50, category=self.catgory)
        return popup_theme

    def getWhiteText(self):
        with theme() as white_text:
            with theme_component(mvAll):
                add_theme_color(mvThemeCol_Text, (255,255,255,255), category=self.catgory)
        return white_text   

    def getBlackText(self):
        with theme() as black_text:
            with theme_component(mvAll):
                add_theme_color(mvThemeCol_Text, (0,0,0,255), category=self.catgory)
        return black_text        