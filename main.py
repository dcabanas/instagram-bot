from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, StringProperty
from kivy.core.window import Window


url = StringProperty('')
class InstaBot(Widget):
    url_text_input = ObjectProperty()

    def submit_url(self):
        global url
        url = self.url_text_input.text
        App.get_running_app().stop()


class InstaBotApp(App):
    def build(self):
        Window.size = (950, 350)
        return InstaBot()

def start():
    InstaBotApp().run()

