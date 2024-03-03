from flask import Flask, render_template, request, send_file
import re, os
from pytube import YouTube
from pathlib import Path

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<h1>Olá mundo</h1>"

@app.route("/download", methods=["GET", "POST"])
def downloadVideo():
    message = ''
    errorType = 0
    if request.method == 'POST' and 'video_url' in request.form:
        youtubeUrl = request.form["video_url"]
        print(youtubeUrl)
        if (youtubeUrl):
            validateVideoUrl = (
                r'(https?://)?(www\.)?'
                '(youtube|youtu|youtube-nocookie)\.(com|be)/'
                '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
            )
            validVideoUrl = re.match(validateVideoUrl, youtubeUrl)
            if validVideoUrl:
                url = YouTube(youtubeUrl)
                video = url.streams.get_highest_resolution()
                filename = video.default_filename
                video.download(filename=filename)

                message = "Vídeo baixado com sucesso!"
                errorType = 1
                
                return send_file(filename, as_attachment=True)
            else:
                message = "Erro ao baixar mídia!"
                errorType = 0
        else:
            message = "Digite a URL do Vídeo do YouTube"
            errorType = 0

    return render_template('index.html', message=message, errorType=errorType)

if __name__ == "__main__":
    app.run()
