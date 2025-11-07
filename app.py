from flask import Flask, render_template, request, send_file
import subprocess
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("input_file")
        if not file:
            return "No file uploaded!"

        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        # Read form fields
        title = request.form.get("title", "Untitled")
        artist = request.form.get("artist", "")
        album = request.form.get("album", "")
        genre = request.form.get("genre", "")
        year = request.form.get("year", "")
        comment = request.form.get("comment", "")
        copyright_ = request.form.get("copyright", "")
        text_overlay = request.form.get("text_overlay", "@TowsifAktar")

        enable_text = "enable='lt(mod(t,60),60)'" if request.form.get("enable_text") else ""
        enable_metadata = bool(request.form.get("enable_metadata"))

        output_name = f"processed_{filename}"
        output_path = os.path.join(OUTPUT_FOLDER, output_name)

        # Build FFmpeg command
        cmd = [
            "ffmpeg", "-i", input_path,
            "-filter_complex",
            f"[0:v]scale=1.0*iw:-1, crop=ih*9/16:ih:(iw-ih*9/16)/2:(ih-ih)/2, scale=720:1280, split[txt][orig];"
            f"[txt]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"fontsize=20:fontcolor=gray:x=(w-text_w)/2+20:y=abs(mod(t*100\\,2*h)-h/2):"
            f"text='{text_overlay}':{enable_text}[txt];[txt][orig]overlay",
            "-c:v", "libx264",
            "-c:a", "copy",
            "-preset", "ultrafast"
        ]

        # Add metadata if enabled
        if enable_metadata:
            cmd += [
                "-metadata", f"TITLE={title}",
                "-metadata", f"ARTIST={artist}",
                "-metadata", f"ALBUM={album}",
                "-metadata", f"GENRE={genre}",
                "-metadata", f"YEAR={year}",
                "-metadata", f"COMMENT={comment}",
                "-metadata", f"COPYRIGHT={copyright_}",
            ]

        cmd.append(output_path)

        subprocess.run(cmd)

        return send_file(output_path, as_attachment=True)

    return render_template("index.html")
    

if __name__ == "__main__":
    app.run(debug=True)
