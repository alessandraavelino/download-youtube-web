from flask import Flask, render_template, request, send_file
import re
import os
from pytubefix import YouTube
from pathlib import Path
from moviepy.editor import *
import time
import utils

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def downloadVideo():
    message = ''
    errorType = 0
    if request.method == 'POST' and 'video_url' in request.form:
        youtubeUrl = request.form["video_url"]
        start_time = request.form.get("initial")
        end_time = request.form.get("final")
        file_format = request.form.get("fileFormat")

        if youtubeUrl:
            # Validação da URL do YouTube
            validateVideoUrl = (
                r'(https?://)?(www\.)?'
                '(youtube|youtu|youtube-nocookie)\.(com|be)/'
                '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
            )
            validVideoUrl = re.match(validateVideoUrl, youtubeUrl)
            
            if validVideoUrl:
                url = YouTube(youtubeUrl)
                video = url.streams.get_highest_resolution()

                # Define a pasta de downloads padrão do usuário
                download_dir = os.path.join(Path.home(), "Downloads")
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)

                # Garante que o nome do arquivo seja seguro para o sistema operacional
                safe_filename = re.sub(r'[\\/*?:"<>|]', "", video.default_filename)
                filename = os.path.join(download_dir, safe_filename)
                
                # Baixa o vídeo e trata erro caso não encontre o arquivo
                try:
                    video.download(output_path=download_dir, filename=safe_filename)
                except Exception as e:
                    message = f"Erro ao baixar o vídeo: {str(e)}"
                    errorType = 0
                    return render_template('index.html', message=message, errorType=errorType)

                time.sleep(2)

                if file_format == "mp3":
                    output_path = download_dir
                    audio_stream = url.streams.filter(only_audio=True).first()
                    audio_filename = os.path.join(output_path, safe_filename.replace(".mp4", ".mp3"))

                    try:
                        audio_stream.download(output_path=output_path, filename=safe_filename)
                        os.rename(os.path.join(output_path, audio_stream.default_filename), audio_filename)
                    except Exception as e:
                        message = f"Erro ao baixar o áudio: {str(e)}"
                        errorType = 0
                        return render_template('index.html', message=message, errorType=errorType)
                    
                    time.sleep(2)

                    # Cortar o áudio se start_time e end_time forem especificados
                    if start_time and end_time:
                        audio_clip = AudioFileClip(audio_filename)
                        fstart_time = utils.converter(start_time)
                        fend_time = utils.converter(end_time)
                        
                        audio_clip = audio_clip.subclip(fstart_time, fend_time)

                        # Atualiza o nome do arquivo mp3
                        cut_filename = os.path.join(output_path, "cut_audio.mp3")
                        audio_clip.write_audiofile(cut_filename)
                        audio_clip.close()
                        audio_filename = cut_filename
                    
                    return send_file(audio_filename, as_attachment=True)
                
                else:
                    if start_time and end_time:
                        video_clip = VideoFileClip(filename)

                        # Define o tempo final para o corte
                        end_time = end_time if end_time else video_clip.duration

                        # Realiza o corte do vídeo
                        cut_clip = video_clip.subclip(start_time, end_time)

                        # Define o nome do arquivo para o vídeo cortado
                        cut_filename = os.path.join(download_dir, "cut_video.mp4")

                        # Salva o vídeo cortado
                        cut_clip.write_videofile(cut_filename, codec="libx264", audio_codec="aac")
                        video_clip.close()
                        cut_clip.close()

                        # Envia o arquivo de vídeo cortado como resposta
                        return send_file(cut_filename, as_attachment=True)

                message = "Vídeo baixado com sucesso!"
                errorType = 1

                time.sleep(2)

                return send_file(filename, as_attachment=True)
            else:
                message = "Erro: URL de vídeo inválida!"
                errorType = 0
        else:
            message = "Por favor, insira a URL do vídeo do YouTube."
            errorType = 0

    return render_template('index.html', message=message, errorType=errorType)

@app.route("/ads.txt", methods=["GET", "POST"])
def ads():
    return render_template('ads.txt')

if __name__ == "__main__":
    app.run(debug=True)
