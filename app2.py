# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from gtts import gTTS
import os

class PronounceApp(App):
    def build(self):
        # Kivy automatically loads 'pronounce.kv'
        return BoxLayout()

    def pronounce_word(self, word):
        # This method is called from the buttons in pronounce.kv
        tts = gTTS(word)
        tts.save(f"{word}.mp3")
        os.system(f"start {word}.mp3")  # Adjust command based on OS, e.g., 'open' for Mac, 'termux-media-player' for Android

# Run the app
if __name__ == '__main__':
    PronounceApp().run()
