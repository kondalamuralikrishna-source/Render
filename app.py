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
    try:
        data = request.get_json(force=True) or {}
        script = data.get("script", "Hello, welcome to English tips!")
        word_tip = data.get("word_tip", "English Learning Tip")

        timestamp = int(time.time())
        audio_path = os.path.join(OUTPUT_DIR, f"audio_{timestamp}.mp3")
        video_name = f"reel_{timestamp}.mp4"
        video_path = os.path.join(OUTPUT_DIR, video_name)

        # 1. Generate Voiceover Audio
        tts = gTTS(text=script, lang="en")
        tts.save(audio_path)

        # 2. Build Video Components
        audio = AudioFileClip(audio_path)
        duration = audio.duration

        # Dark background (1080x1920 portrait)
        bg = ColorClip(size=(1080, 1920), color=(20, 20, 30), duration=duration)
        
        # Centered Text Overlay with explicit system font
        txt = TextClip(
            word_tip, 
            fontsize=45, 
            color='white', 
            font='Liberation-Sans',
            method='caption', 
            size=(900, None)
        ).set_duration(duration).set_pos('center')

        # Combine audio & visual layers
        video = CompositeVideoClip([bg, txt]).set_audio(audio)
        video.write_videofile(
            video_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac", 
            temp_audiofile=f"/tmp/temp_audio_{timestamp}.m4a", 
            remove_temp=True
        )

        # Close clips to free RAM resources on free tier
        audio.close()
        video.close()

        host_url = request.host_url.rstrip('/')
        return jsonify({"video_url": f"{host_url}/download/{video_name}"})

    except Exception as e:
        print(f"Error during render: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
