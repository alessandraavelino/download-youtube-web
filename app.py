from flask import Flask, render_template, request, send_file
import re, os
from pytube import YouTube
from pathlib import Path
from moviepy.editor import *
import moviepy.editor as mp

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def downloadVideo():
    message = ''
    errorType = 0
    if request.method == 'POST' and 'video_url' in request.form:
        youtubeUrl = request.form["video_url"]
        file_format = request.form.get("fileFormat")
        print(file_format)

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

                filename = os.path.join("Downloads", video.default_filename)
                video.download(filename=filename)
                

                if file_format == "mp3":
                    downloads_directory = "Downloads"
                    current_directory = os.getcwd()

                    downloads_path = os.path.join(current_directory, downloads_directory)

                    if os.path.exists(downloads_path) and os.path.isdir(downloads_path):
                        for filename in os.listdir(downloads_path):

                            if filename.endswith(".mp4"):
                                mp4_path = os.path.join(downloads_path, filename)
                                mp3_path = os.path.join(downloads_path, os.path.splitext(filename)[0] + ".mp3")      
                                video = mp.AudioFileClip(mp4_path)
                                video.write_audiofile(mp3_path)
                                os.remove(mp4_path)

                                message = "Vídeo baixado com sucesso!"
                                errorType = 1

                                return send_file(mp3_path, as_attachment=True)
                                    
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
    app.run(debug=True)
