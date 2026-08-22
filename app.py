import os
import time
from flask import Flask, request, jsonify, send_from_directory
from gtts import gTTS
from moviepy.editor import ColorClip, TextClip, AudioFileClip, CompositeVideoClip

app = Flask(__name__)
OUTPUT_DIR = "/tmp/renders"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/render", methods=["POST"])
def render():
    data = request.json
    script = data.get("script", "")
    word_tip = data.get("word_tip", "")

    timestamp = int(time.time())
    audio_path = f"{OUTPUT_DIR}/audio_{timestamp}.mp3"
    video_name = f"reel_{timestamp}.mp4"
    video_path = f"{OUTPUT_DIR}/{video_name}"

    # Generate Voiceover
    tts = gTTS(text=script, lang="en")
    tts.save(audio_path)

    # Render 1080x1920 Video
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    bg = ColorClip(size=(1080, 1920), color=(20, 20, 30), duration=duration)
    txt = TextClip(word_tip, fontsize=50, color='white', method='caption', size=(900, None)).set_duration(duration).set_pos('center')

    video = CompositeVideoClip([bg, txt]).set_audio(audio)
    video.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac")

    # Return Direct Video URL
    host_url = request.host_url.rstrip('/')
    return jsonify({"video_url": f"{host_url}/download/{video_name}"})

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
