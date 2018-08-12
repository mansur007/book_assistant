
filename="$1"

ffmpeg -i $filename.mp3 -acodec pcm_s16le -ac 1 -ar 16000 $filename.wav

tr ' ' '\n' < $filename > $filename.words

python -m aeneas.tools.execute_task $filename.mp3 $filename "task_language=eng|is_text_type=plain|os_task_file_format=aud" $filename.uttmap.aud

python -m aeneas.tools.execute_task $filename.mp3 $filename.words "task_language=eng|is_text_type=plain|os_task_file_format=aud" $filename.wmap.aud --presets-word -r="tts_l1=espeak|tts_l2=aws|tts_l3=aws"
