import pandas as pd
from collections import Counter
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import stanza

# Загружаем русскую модель для Stanza
# stanza.download('ru')
nlp = stanza.Pipeline('ru')

# Наш список стоп-слов (предлоги, союзы и прочие ненужные слова)
custom_stop_words = set([
    "и", "в", "на", "по", "с", "у", "для", "о", "при", "к", "из", "от", 
    "до", "над", "под", "за", "без", "между", "а", "но", "что", "как", 
    "бы", "же", "ли", "или", "не", "то", "все", "это", "так", "тоже", 
    "там", "здесь", "когда", "чтобы", "если", "до", "после", "перед"
])

# Функция для нормализации фраз с помощью Stanza
def normalize_phrase(phrase):
    if "ии" in phrase.lower():
        return phrase  # Если "ИИ" в фразе, возвращаем фразу без изменений (Оно его делает в ослика Иа из Винни Пуха)
    
    doc = nlp(phrase)
    normalized_words = [word.lemma for sent in doc.sentences for word in sent.words]
    return ' '.join(normalized_words)

# Функция для предобработки текста
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    normalized_text = normalize_phrase(text)
    return normalized_text

def extract_phrases(text, n):
    words = text.split()
    phrases = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
    return phrases

def generate_wordcloud(word_counter):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_counter)
    wordcloud.to_file("static/wordcloud.png")

def save_results_to_excel(word_freq, bigram_freq, trigram_freq):
    df_word_freq = pd.DataFrame(list(word_freq.items()), columns=['Word', 'Frequency'])
    df_bigram_freq = pd.DataFrame(list(bigram_freq.items()), columns=['Bigram', 'Frequency'])
    df_trigram_freq = pd.DataFrame(list(trigram_freq.items()), columns=['Trigram', 'Frequency'])

    # Сохраняем результаты в Excel
    with pd.ExcelWriter('static/frequency_analysis.xlsx') as writer:
        df_word_freq.to_excel(writer, sheet_name='Words', index=False)
        df_bigram_freq.to_excel(writer, sheet_name='Bigrams', index=False)
        df_trigram_freq.to_excel(writer, sheet_name='Trigrams', index=False)

def frequency_analysis(file_path):
    df = pd.read_excel(file_path)
    comments = df.iloc[:, 0].dropna().apply(preprocess_text)

    word_counter = Counter()
    bigram_counter = Counter()
    trigram_counter = Counter()

    for comment in comments:
        words = comment.split()
        word_counter.update(words)
        bigram_counter.update(extract_phrases(comment, 2))
        trigram_counter.update(extract_phrases(comment, 3))

    word_freq = {word: count for word, count in word_counter.items() if count > 1 and word not in custom_stop_words}
    bigram_freq = {phrase: count for phrase, count in bigram_counter.items() if count > 2}
    trigram_freq = {phrase: count for phrase, count in trigram_counter.items() if count > 2}

    # Генерация облака слов
    filtered_word_counter = {word: count for word, count in word_counter.items() if word not in custom_stop_words}
    generate_wordcloud(filtered_word_counter)

    # Сохраняем результаты анализа в файл Excel
    save_results_to_excel(word_freq, bigram_freq, trigram_freq)

    return word_freq, bigram_freq, trigram_freq


