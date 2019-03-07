import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=\
    "/data/pycharm_projects/audiobook_assistant/audiobook-assistant-9703181ebcfe.json"
from google.cloud import texttospeech
import subprocess


class SpeechSynthesizer(object):
    def __init__(self, lang_code='en-US', name='en-US-Wavenet-B', audio_path='output.mp3'):
        self.client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.types.VoiceSelectionParams(
            language_code=lang_code,
            name=name
            # language_code='ru-RU',
            # name='ru-RU-Wavenet-B'
        )
        self.audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.MP3)
        self.audio_path = audio_path

    def synthesize(self, text):
        # Set the text input to be synthesized
        synthesis_input = texttospeech.types.SynthesisInput(text=text)
        response = self.client.synthesize_speech(synthesis_input, self.voice, self.audio_config)

        # The response's audio_content is binary.
        with open(self.audio_path, 'wb') as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            print('Audio content written to file "{}"'.format(self.audio_path))

    def speak(self, text):
        self.synthesize(text)
        subprocess.Popen(['mpg123', '-q', self.audio_path]).wait()


if __name__ == '__main__':
    # # Instantiates a client
    # client = texttospeech.TextToSpeechClient()
    #
    # # Set the text input to be synthesized
    # synthesis_input = texttospeech.types.SynthesisInput(text="Привет, как дела?")
    #
    # # Build the voice request, select the language code ("en-US") and the ssml
    # # voice gender ("neutral")
    # # voice = texttospeech.types.VoiceSelectionParams(
    # #     language_code='en-US',
    # #     ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
    # voice = texttospeech.types.VoiceSelectionParams(
    #     # language_code = 'en-GB',
    #     # name = 'en-GB-Wavenet-A'
    #     language_code = 'ru-RU',
    #     name = 'ru-RU-Wavenet-B'
    # )
    #
    #
    # # Select the type of audio file you want returned
    # audio_config = texttospeech.types.AudioConfig(
    #     audio_encoding=texttospeech.enums.AudioEncoding.MP3)
    #
    # # Perform the text-to-speech request on the text input with the selected
    # # voice parameters and audio file type
    # response = client.synthesize_speech(synthesis_input, voice, audio_config)
    #
    # # The response's audio_content is binary.
    # with open('output.mp3', 'wb') as out:
    #     # Write the response to the output file.
    #     out.write(response.audio_content)
    #     print('Audio content written to file "output.mp3"')

    EnSpeaker = SpeechSynthesizer(lang_code='en-US', name='en-US-Wavenet-B', audio_path='outputEnB.mp3')
    EnSpeaker.synthesize('preconceived opinion that is not based on reason or actual experience.')
    RuSpeaker = SpeechSynthesizer(lang_code='ru-RU', name='ru-RU-Wavenet-C', audio_path='outputRuC.mp3')
    RuSpeaker.speak('Ставший привычным ложный взгляд на что-нибудь')