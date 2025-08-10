
import pyttsx3

def text_to_speech_chinese(text):
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")

        # Print available voices to find a Chinese-compatible one
        for voice in voices:
            print(f"Voice: {voice.name}, ID: {voice.id}, Lang: {voice.languages}")

        # Set a Chinese-compatible voice (replace with the correct ID for your system)
        chinese_voice_id = "Huihui"  # Example: Replace with the actual voice ID
        for voice in voices:
            if chinese_voice_id in voice.name:
                engine.setProperty("voice", voice.id)
                break
        else:
            raise RuntimeError("No Chinese-compatible voice found.")

        # Set speech rate (optional)
        engine.setProperty("rate", 150)

        # Speak the text
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("Error in TTS:", e)

# Example usage
text_to_speech_chinese("你好，世界！")