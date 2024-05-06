# Author: Velma Anyona
# Date: 04 / 03 / 2024
# Organization: University of Rochester Electrical and Computer Engineering Department
# Description:
#   A basic GUI setup to write drink recipes to a orders.txt file
#


from kivy.core.window import Window
Window.fullscreen = 'auto'
from kivy.config import Config 
Config.set('graphics', 'resizable', False)
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout 
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Rectangle
import time

class CustomKeyboard(GridLayout):
    def __init__(self, input_field, **kwargs):
        super(CustomKeyboard, self).__init__(**kwargs)
        self.input_field = input_field
        self.cols = 4
        for i in range(1, 10):
            self.add_widget(Button(text=str(i), on_press=self.add_to_input))
        self.add_widget(Button(text="0", on_press=self.add_to_input))
        self.add_widget(Button(text=".", on_press=self.add_to_input))
        self.add_widget(Button(text="Enter", on_press=self.save_percentage))
        self.add_widget(Button(text="Clear", on_press=self.clear_input))

    def add_to_input(self, instance):
        self.input_field.text += instance.text

    def save_percentage(self, instance):
        app = App.get_running_app()
        app.add_percentage(self.input_field.text)
        percent = app.save_percentages(self.input_field.text)
        app.total_percentage(percent)
        self.input_field.text = ""

    def clear_input(self, instance):
        self.input_field.text = ""

class SmartSip(App):
    def build(self):
        self.choices = []
        self.percentages = []
        self.total = 0
        self.window = 1  # Track the current window
        
        self.layout = BoxLayout(orientation='vertical')
        self.window_layout = GridLayout(cols=2, spacing=10, padding=10)
        self.window_layout.bind(pos=self.update_rect, size=self.update_rect)
        with self.window_layout.canvas.before:
            self.rect = Rectangle(source='bub2.jpg',size=self.window_layout.size,
                           pos=self.window_layout.pos)
            

        self.layout.add_widget(self.window_layout)
        
        self.update_window()

        return self.layout
    
    def update_rect(self, instance, value):
            self.rect.pos = instance.pos
            self.rect.size = instance.size
    

    def update_window(self):
        self.window_layout.clear_widgets()

        if self.window == 1:
            self.window_layout.add_widget(Widget())
            self.window_layout.add_widget(Widget())
            self.window_layout.add_widget(Label(text="Welcome to SmartSip!", font_size= 30,
                                                halign='center', size_hint=(1, 1)))
            #self.window_layout.add_widget(Widget())
            #self.window_layout.add_widget(Widget())
            self.window_layout.add_widget(Widget())
            self.window_layout.add_widget(Widget())
            #self.window_layout.add_widget(Button(text="Select a Drink!", on_press=self.custom_window, size_hint=(0.7, 0.7), 
                                                 #size=(250, 250), background_normal='widget.png', background_color=(.5, .5, .5, 1)))
            self.window_layout.add_widget(Button(text="Start!", on_press=self.select_window, size_hint=(0.8, 0.8), 
                                                 size=(250, 250), background_normal='rbutton.png', background_down = 'down2.png')) #background_color=(.5, 0.5, .5, 1)))
            #self.window_layout.add_widget(Widget())

        elif self.window == 2:
            options = ["Milk", "Coffee", "Non-Dairy"]
            self.placeholder_btn = Button(text="Select to see your choices", on_press=self.selected_options, background_normal='option.png', background_color=(.5, .5, .5, 1))
            for option in options:
                btn = Button(text=option, on_press=self.add_choice, background_normal='option.png', background_color=(.5, .5, .5, 1))
                self.window_layout.add_widget(btn)
            self.window_layout.add_widget(self.placeholder_btn)
            #self.window_layout.add_widget(Widget())
            
            self.keyboard_input = TextInput(multiline=False)
            self.window_layout.add_widget(self.keyboard_input)
            self.window_layout.add_widget(CustomKeyboard(input_field=self.keyboard_input))
            self.window_layout.add_widget(Widget())
            self.window_layout.add_widget(Button(text="Finish", on_press=self.damage_control, background_normal = 'widget.png', 
                                                 background_down = 'down2.png', 
                                                 ))#border = (30, 30, 30, 30), size_hint=(0.7, 0.7)))#, pos_hint={"x":0.3, "y":0.45}))
        elif self.window == 3:
            # Add existing buttons
            self.window_layout.add_widget(Button(text="Latte", on_press=self.add_choice, 
                                                 background_normal='widget.png', background_color=(.5, .5, .5, 1)))
            self.window_layout.add_widget(Button(text="Americano", on_press=self.add_choice, 
                                                 background_normal='widget.png', background_color=(.5, .5, .5, 1)))
            self.window_layout.add_widget(Button(text="Coffee", on_press=self.add_choice, 
                                                 background_normal='widget.png', background_color=(.5, .5, .5, 1)))
            fill_spinner = Spinner(text='Select Fill Percentage', values=('10', '20', '30', '40', '50', '60', '70', '80', '90', '100'), 
                                   on_text=self.add_choice, background_normal='widget.png', background_color=(.1, .8, .1, 1), size_hint=(0.5, 0.7))
            fill_spinner.bind(text=self.on_spinner_select)  # Bind spinner selection to method
            
            # Add the spinner to the layout
            self.window_layout.add_widget(fill_spinner)
            self.window_layout.add_widget(Widget())
            self.window_layout.add_widget(Button(text="Finish", on_press=self.finish_order, background_normal = 'rbutton.png', 
                                                 background_down = 'down2.png', size_hint=(0.7, 0.7), 
                                                 border = (30, 30, 30, 30), pos_hint={"x":0.35, "y":0.3}))

        elif self.window == 4:
            self.window_layout.add_widget(Label(text="Enjoy your Drink!", font_size= 80, size_hint=(1, 0.5)))
            Clock.schedule_once(self.return_to_home, 10)

        elif self.window == 5:
            self.window_layout.add_widget(Label(text="Really o_o!\n Make sure your total amount is between 1 - 100.", 
                                                halign='center', font_size= 30, size_hint=(1, 0.5), color=(1, 0, 0, 1)))
            Clock.schedule_once(self.return_to_home, 3)

        elif self.window == 6:
            self.window_layout.add_widget(Label(text="Select Item before entering the amount \nthen press enter and continuing", 
                                                halign='center', font_size= 30, size_hint=(1, 0.5), color=(1, 0, 0, 1)))
            Clock.schedule_once(self.return_to_select, 3)

    def add_choice(self, instance):
        instance.background_color = (1, 1, 1, 1)  # Change color when clicked
        self.choices.append(instance.text)

    def add_percentage(self, percentage):
        self.choices.append(':' + percentage + '\n')

    def on_spinner_select(self, spinner, text):
        if len(self.choices) > 1:
            self.choices.pop()
        text = ":" + text
        self.choices.append(text)

    def save_percentages(self, percentage):
        try: 
            self.percentages.append(float(percentage))
        except ValueError:
            if percentage == '':
                percentage = 0
                self.percentages.append(float(percentage))

    def total_percentage(self, instance):
        self.total = sum(self.percentages)

    def custom_window(self, instance):
        self.window += 2
        self.update_window()

    def select_window(self, instance):
        self.window += 1
        self.update_window()
        
    def selected_options(self, instance):
        if self.choices:
            options_text = ''.join(self.choices)
            self.placeholder_btn.text = options_text
        else:
            self.placeholder_btn.text = "No selections yet!"
            #time.sleep(1.5)
            Clock.schedule_once(lambda dt: 1.5)
            self.placeholder_btn.text = "Select to see your choices"

    def damage_control(self, instance):
        #self.window += 1
        if self.total <= 0 or self.total > 100:
            self.window +=3
        elif self.total <= 100:
            self.get_order()
            # print("Your choices:", order)
            self.window +=2
        check = ["Milk", "Water", "Coffee", "Non-Dairy"]
        found = any(item in check for item in self.choices)

        if found:
            # At least one item from self.choices is in the check list
            for item in self.choices:
                if item in check and (self.choices.index(item) % 2 != 0) or (len(self.choices) <= 1):
                    self.percentages = []
                    self.window = 6
                    self.choices = []
                    break  # Exit the loop if an item is found
                else:
                    #order = self.choices
                    #print("Your choices:", self.choices)
                    #self.get_order()
                    pass
        #         #self.window +=2
        else:
            # None of the items from self.choices are in the check list
            self.percentages = []
            self.choices = []
            self.window = 2
        #self.get_order()
        self.update_window()

    def finish_order(self, instance):
        item = []
        check = ['Americano', 'Latte', 'Coffee']
        found = any(items in check for items in self.choices)
        for items in self.choices:
            if items in check:
                item.append(items)
        if (len(self.choices) > 2 or len(self.choices)==0) or len(item) > 1 or not found:
            self.choices = []
            item = []
            self.percentages = []
            self.window = 3
            self.update_window()
        else:
            order = self.choices
            #print("Your choices:", order)
            self.get_order()
            self.window += 1
            self.update_window()

    def return_to_select(self, dt):
        self.window = 2
        self.choices = []
        self.percentages = []
        self.update_window()

    def return_to_home(self, dt):
        self.window = 1
        self.choices = []
        self.percentages = []
        self.update_window()

    def get_order(self):
        
        with open("orders.txt", "w") as file:
            file.write(''.join(self.choices))
        #return self.choices

if __name__ == "__main__":
    SmartSip().run()
