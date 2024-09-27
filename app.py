from flask import Flask, render_template, request, send_file
import re, os
from pytube import YouTube
from pathlib import Path
from moviepy.editor import *
import moviepy.editor as mp
import time
import utils
import yt_dlp

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def downloadVideo():
    message = ''
    errorType = 0

    if request.method == 'POST' and 'video_url' in request.form:
        youtubeUrl = request.form["video_url"]
        start_time = str(request.form["initial"])
        end_time = str(request.form["final"])
        file_format = request.form.get("fileFormat")

        print(f"Formato do arquivo: {file_format}")
        print(f"URL do YouTube: {youtubeUrl}")

        if youtubeUrl:
            validateVideoUrl = (
                r'(https?://)?(www\.)?'
                '(youtube|youtu|youtube-nocookie)\.(com|be)/'
                '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
            )
            validVideoUrl = re.match(validateVideoUrl, youtubeUrl)

            if validVideoUrl:
                try:
                    ydl_opts = {
                        'format': 'bestvideo+bestaudio/best',
                        'outtmpl': 'Downloads/%(title)s.%(ext)s',
                        'proxy': 'https://songslicer.onrender.com',  # Substitua pelo seu proxy
                    }

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([youtubeUrl])

                    filename = os.path.join("Downloads", "cut_video.mp4")  # Ajuste conforme o nome do arquivo

                    # Se o formato for mp3
                    if file_format == "mp3":
                        # Converta o vídeo para mp3 aqui, se necessário
                        pass

                    message = "Vídeo baixado com sucesso!"
                    errorType = 1

                    return send_file(filename, as_attachment=True)

                except Exception as e:
                    message = f"Erro ao baixar a mídia: {str(e)}"
                    errorType = 0
            else:
                message = "URL do vídeo inválida!"
                errorType = 0
        else:
            message = "Digite a URL do Vídeo do YouTube"
            errorType = 0

    return render_template('index.html', message=message, errorType=errorType)
@app.route("/ads.txt", methods=["GET", "POST"])
def ads():
    return render_template('ads.txt')

if __name__ == "__main__":
    app.run(debug=True)