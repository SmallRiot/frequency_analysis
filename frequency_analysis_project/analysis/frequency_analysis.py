import pandas as pd
from collections import Counter
import re
from wordcloud import WordCloud
import stanza
from nltk.corpus import stopwords

# Инициализация Stanza для русского языка
nlp = stanza.Pipeline('ru')

# Список стоп-слов для удаления ненужных слов
custom_stop_words = set(stopwords.words("russian"))

# Словари для классификации по темам
classification_dict = {
    "финансы": ["деньги", "оплата", "счет", "долг", "кредит", "банк"],
    "обслуживание": ["персонал", "сервис", "качество", "поддержка", "вежливость"],
    "документы": ["заявление", "документ", "паспорт", "удостоверение", "свидетельство"],
    "продукты": ["товар", "продукт", "услуга", "ассортимент", "качество"],
}

# Функция классификации по словарям
def classify_phrase(phrase):
    for category, keywords in classification_dict.items():
        if any(word in phrase for word in keywords):
            return category
    return None  # Если ничего не найдено, возвращаем None

# Функция нормализации фраз с помощью Stanza
def normalize_phrase(phrase):
    if "ии" in phrase.lower():
        return phrase  # Если "ИИ" в фразе, возвращаем фразу без изменений
    
    doc = nlp(phrase)
    normalized_words = [word.lemma for sent in doc.sentences for word in sent.words]
    return ' '.join(normalized_words)

# Функция предобработки текста
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    normalized_text = normalize_phrase(text)
    return normalized_text

# Функция для извлечения n-грамм из текста
def extract_phrases(text, n):
    words = text.split()
    return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]

# Генерация облака слов
def generate_wordcloud(word_counter):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_counter)
    wordcloud.to_file("static/wordcloud.png")

# Основная функция анализа
def frequency_analysis(file_path):
    # Чтение Excel файла
    df = pd.read_excel(file_path)
    comments = df.iloc[:, 0].dropna().apply(preprocess_text)

    # Инициализация счетчиков
    word_counter = Counter()
    bigram_counter = Counter()
    trigram_counter = Counter()

    for comment in comments:
        words = comment.split()
        word_counter.update(words)
        bigram_counter.update(extract_phrases(comment, 2))
        trigram_counter.update(extract_phrases(comment, 3))

    # Фильтрация по частоте и удаление стоп-слов
    word_freq = {word: count for word, count in word_counter.items() if count > 1 and word not in custom_stop_words}

    # Разделение биграмм по категориям и "несмысловым"
    bigram_meaningful = {}
    bigram_non_meaningful = {}
    for phrase, count in bigram_counter.items():
        category = classify_phrase(phrase)
        if category and count > 2:
            if category not in bigram_meaningful:
                bigram_meaningful[category] = []
            bigram_meaningful[category].append((phrase, count))
        elif count > 2:
            bigram_non_meaningful[phrase] = count

    # Разделение триграмм по категориям и "несмысловым"
    trigram_meaningful = {}
    trigram_non_meaningful = {}
    for phrase, count in trigram_counter.items():
        category = classify_phrase(phrase)
        if category and count > 2:
            if category not in trigram_meaningful:
                trigram_meaningful[category] = []
            trigram_meaningful[category].append((phrase, count))
        elif count > 2:
            trigram_non_meaningful[phrase] = count

    # Генерация облака слов
    filtered_word_counter = {word: count for word, count in word_counter.items() if word not in custom_stop_words}
    generate_wordcloud(filtered_word_counter)

    # Возврат данных для отображения и сохранения в Excel
    return word_freq, bigram_meaningful, bigram_non_meaningful, trigram_meaningful, trigram_non_meaningful
