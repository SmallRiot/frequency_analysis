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
            file = request.FILES['file']
            file_path = f'static/{file.name}'
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Обновляем вызов frequency_analysis
            word_freq, bigram_meaningful, bigram_non_meaningful, trigram_meaningful, trigram_non_meaningful = frequency_analysis(file_path)

            context = {
                'word_freq': word_freq,
                'bigram_meaningful': bigram_meaningful,
                'bigram_non_meaningful': bigram_non_meaningful,
                'trigram_meaningful': trigram_meaningful,
                'trigram_non_meaningful': trigram_non_meaningful,
            }

            return render(request, 'analysis/result.html', context)
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