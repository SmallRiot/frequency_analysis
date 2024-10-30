from django.shortcuts import render
from .forms import UploadFileForm
from .frequency_analysis import frequency_analysis
from django.http import FileResponse, HttpResponseNotFound
import os

# Функция для загрузки файла
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Обрабатываем загруженный файл
            file_path = handle_uploaded_file(request.FILES['file'])
            word_freq, bigram_freq, trigram_freq = frequency_analysis(file_path)
            return render(request, 'analysis/result.html', {
                'word_freq': word_freq,
                'bigram_freq': bigram_freq,
                'trigram_freq': trigram_freq
            })
    else:
        form = UploadFileForm()
    return render(request, 'analysis/upload.html', {'form': form})

# Сохранение файла
def handle_uploaded_file(f):
    file_path = 'uploaded_file.xlsx'
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path



def download_analysis_file(request):
    # Путь к файлу анализа
    file_path = 'static/frequency_analysis.xlsx'
    
    # Проверка наличия файла
    if os.path.exists(file_path):
        # Отправляем файл в виде ответа, с загрузкой
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='frequency_analysis.xlsx')
    else:
        # Если файл не найден, возвращаем сообщение об ошибке
        return HttpResponseNotFound("Файл не найден")