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
        
        print(file_format)
        print(youtubeUrl)

        if youtubeUrl:
            # Validação da URL do YouTube
            validateVideoUrl = (
                r'(https?://)?(www\.)?'
                '(youtube|youtu|youtube-nocookie)\.(com|be)/'
                '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
            )
            validVideoUrl = re.match(validateVideoUrl, youtubeUrl)

            if validVideoUrl:
                # Configurações do yt-dlp
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': 'Downloads/%(title)s.%(ext)s',
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(youtubeUrl, download=True)
                    video_title = info_dict.get("title", None)
                    video_filename = f"Downloads/{video_title}.mp4"

                time.sleep(5)

                # Se o formato for MP3
                if file_format == "mp3":
                    output_path = "Downloads"
                    audio_stream_opts = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'outtmpl': output_path + '/%(title)s.%(ext)s'
                    }

                    with yt_dlp.YoutubeDL(audio_stream_opts) as ydl:
                        info_dict = ydl.extract_info(youtubeUrl, download=True)
                        mp3_filename = os.path.join(output_path, f"{info_dict['title']}.mp3")
                    
                    time.sleep(2)

                    # Cortar o áudio, se necessário
                    if start_time and end_time:
                        audio_clip = AudioFileClip(mp3_filename)
                        fstart_time = utils.converter(start_time)
                        fend_time = utils.converter(end_time)
                        
                        audio_clip = audio_clip.subclip(fstart_time, fend_time)

                        # Nome do arquivo cortado
                        mp3_filename_cut = os.path.join(output_path, "cut_audio.mp3")
                        audio_clip.write_audiofile(mp3_filename_cut)
                        mp3_filename = mp3_filename_cut
                    
                    # Envia o arquivo mp3 como resposta
                    return send_file(mp3_filename, as_attachment=True)

                else:
                    # Se for vídeo e se os tempos de início e fim forem especificados
                    if start_time and end_time:
                        video_clip = VideoFileClip(video_filename)

                        # Definindo os tempos de corte
                        end_time = end_time if end_time is not None else video_clip.duration

                        # Realiza o corte do vídeo
                        cut_clip = video_clip.subclip(start_time, end_time)

                        # Nome do arquivo de vídeo cortado
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

                return send_file(video_filename, as_attachment=True)
            
            else:
                message = "Erro ao baixar mídia! URL inválida."
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