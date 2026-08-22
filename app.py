import os
import time
import gc
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

        # 1. Generate Voiceover
        tts = gTTS(text=script, lang="en")
        tts.save(audio_path)

        # 2. Build Video Components
        audio = AudioFileClip(audio_path)
        duration = audio.duration

        # Use lower resolution canvas (720x1280) to save RAM
        bg = ColorClip(size=(720, 1280), color=(20, 20, 30), duration=duration)
        
        txt = TextClip(
            word_tip, 
            fontsize=36, 
            color='white', 
            font='Liberation-Sans',
            method='caption', 
            size=(600, None)
        ).set_duration(duration).set_pos('center')

        # Combine audio & visual layers
        video = CompositeVideoClip([bg, txt]).set_audio(audio)
        
        # 3. Write output file with memory limits
        video.write_videofile(
            video_path, 
            fps=20,                       # Reduced FPS saves RAM
            codec="libx264", 
            audio_codec="aac", 
            preset="ultrafast",           # Reduces CPU and RAM spikes
            threads=1,                    # Limits thread count to prevent memory leaks
            temp_audiofile=f"/tmp/temp_{timestamp}.m4a", 
            remove_temp=True
        )

        # Clean up memory explicitly
        audio.close()
        video.close()
        gc.collect()

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
