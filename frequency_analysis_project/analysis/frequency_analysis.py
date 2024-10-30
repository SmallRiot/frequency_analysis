import pandas as pd
from collections import Counter
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import stanza
from nltk.corpus import stopwords

# Загружаем русскую модель для Stanza (раскомментируйте, чтобы загрузить в первый раз)
# stanza.download('ru')
# Инициализация Stanza для обработки русского языка
nlp = stanza.Pipeline('ru')

# Наш список стоп-слов (предлоги, союзы и прочие ненужные слова, которые нужно исключить)
custom_stop_words = set(stopwords.words("russian"))

# Функция для нормализации фраз с помощью Stanza
def normalize_phrase(phrase):
    # Проверяем, есть ли "ИИ" в фразе, если да — возвращаем фразу без изменений
    if "ии" in phrase.lower():
        return phrase
    
    # Обработка текста с помощью Stanza и лемматизация слов
    doc = nlp(phrase)
    normalized_words = [word.lemma for sent in doc.sentences for word in sent.words]
    return ' '.join(normalized_words)  # Возвращаем нормализованный текст

# Функция для предобработки текста
def preprocess_text(text):
    text = text.lower()  # Приводим текст к нижнему регистру
    text = re.sub(r'[^\w\s]', '', text)  # Убираем все знаки препинания
    normalized_text = normalize_phrase(text)  # Применяем нормализацию
    return normalized_text

# Функция для извлечения фраз (n-грамм) заданной длины из текста
def extract_phrases(text, n):
    words = text.split()
    phrases = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
    return phrases

# Функция для генерации облака слов
def generate_wordcloud(word_counter):
    # Создаем облако слов на основе частот слов
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_counter)
    wordcloud.to_file("static/wordcloud.png")  # Сохраняем изображение облака слов

# Функция для сохранения результатов анализа в Excel-файл
def save_results_to_excel(word_freq, bigram_freq, trigram_freq):
    df_word_freq = pd.DataFrame(list(word_freq.items()), columns=['Word', 'Frequency'])
    df_bigram_freq = pd.DataFrame(list(bigram_freq.items()), columns=['Bigram', 'Frequency'])
    df_trigram_freq = pd.DataFrame(list(trigram_freq.items()), columns=['Trigram', 'Frequency'])

    # Сохраняем результаты в разные листы Excel-файла
    with pd.ExcelWriter('static/frequency_analysis.xlsx') as writer:
        df_word_freq.to_excel(writer, sheet_name='Words', index=False)
        df_bigram_freq.to_excel(writer, sheet_name='Bigrams', index=False)
        df_trigram_freq.to_excel(writer, sheet_name='Trigrams', index=False)

# Основная функция для анализа частоты слов, биграмм и триграмм в комментариях
def frequency_analysis(file_path):
    # Читаем файл Excel и получаем комментарии
    df = pd.read_excel(file_path)
    comments = df.iloc[:, 0].dropna().apply(preprocess_text)  # Применяем предобработку текста

    # Счетчики для слов, биграмм и триграмм
    word_counter = Counter()
    bigram_counter = Counter()
    trigram_counter = Counter()

    # Обрабатываем каждый комментарий
    for comment in comments:
        words = comment.split()
        word_counter.update(words)  # Обновляем счетчик слов
        bigram_counter.update(extract_phrases(comment, 2))  # Обновляем счетчик биграмм
        trigram_counter.update(extract_phrases(comment, 3))  # Обновляем счетчик триграмм

    # Фильтрация частот слов, биграмм и триграмм
    word_freq = {word: count for word, count in word_counter.items() if count > 1 and word not in custom_stop_words}
    bigram_freq = {phrase: count for phrase, count in bigram_counter.items() if count > 2}
    trigram_freq = {phrase: count for phrase, count in trigram_counter.items() if count > 2}

    # Генерация облака слов без стоп-слов
    filtered_word_counter = {word: count for word, count in word_counter.items() if word not in custom_stop_words}
    generate_wordcloud(filtered_word_counter)

    # Сохраняем результаты анализа в файл Excel
    save_results_to_excel(word_freq, bigram_freq, trigram_freq)

    # Возвращаем результаты анализа
    return word_freq, bigram_freq, trigram_freq
