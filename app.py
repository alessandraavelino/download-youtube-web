from flask import Flask, render_template, request, send_file
import re, os
from pytube import YouTube
from pathlib import Path
from moviepy.editor import *
import moviepy.editor as mp
import time
import utils

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
                
                time.sleep(2)

                if file_format == "mp3":
                    output_path = "Downloads"
                    audio_stream = url.streams.filter(only_audio=True).first()
                    audio_stream.download(output_path=output_path)
                    # Renomeando o arquivo para ter a extensão .mp3
                    default_filename = audio_stream.default_filename
                    mp3_filename = os.path.join(output_path, default_filename.split('.')[0] + ".mp3")
                    os.rename(os.path.join(output_path, default_filename), mp3_filename)
                    
                    time.sleep(2)

                    # Cortar o áudio se start_time e end_time forem especificados
                    if start_time and end_time:
                        audio_clip = AudioFileClip(mp3_filename)
                        fstart_time = utils.converter(start_time)
                        fend_time = utils.converter(end_time)
                        
                        audio_clip = audio_clip.subclip(fstart_time, fend_time)

                        # Atualiza o nome do arquivo mp3
                        mp3_filename_cut = os.path.join(output_path, "cut_audio.mp3")
                        audio_clip.write_audiofile(mp3_filename_cut)
                        mp3_filename = mp3_filename_cut
                    
                    # Enviando o arquivo mp3 como resposta
                    return send_file(mp3_filename, as_attachment=True)
                
                else:
                    if start_time and end_time:
                        video_clip = VideoFileClip(filename)

                        # Define os tempos de início e fim do corte
                        end_time = end_time if end_time is not None else video_clip.duration

                        # Realiza o corte do vídeo
                        cut_clip = video_clip.subclip(start_time, end_time)

                        # Define o nome do arquivo para o vídeo cortado
                        cut_filename = "Downloads/cut_video.mp4"

                        # Salva o vídeo cortado
                        cut_clip.write_videofile(cut_filename, codec="libx264", audio_codec="aac")

                        # Fecha o vídeo original
                        video_clip.close()

                        # Envia o arquivo de vídeo cortado como resposta
                        return send_file(cut_filename, as_attachment=True)

                                    
                message = "Vídeo baixado com sucesso!"
                errorType = 1

                time.sleep(2)

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