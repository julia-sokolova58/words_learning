# services/text_processor.py
import spacy
from collections import Counter

# Загружаем модель spaCy один раз
try:
    nlp = spacy.load("de_core_news_sm")
except OSError:
    print("Модель de_core_news_sm не найдена. Установите её командой: python -m spacy download de_core_news_sm")
    raise


def find_snippet_in_book(book_path, first_five, last_five):
    """
    Ищет отрывок в тексте книги по точному совпадению первых и последних 5 слов.
    Возвращает строку отрывка или None.
    """
    with open(book_path, 'r', encoding='utf-8') as f:
        text = f.read()

    first_pos = text.find(first_five)
    if first_pos == -1:
        return None

    last_pos = text.find(last_five, first_pos)
    if last_pos == -1:
        return None

    return text[first_pos:last_pos + len(last_five)]


def process_snippet(snippet):
    """
    Принимает отрывок текста, возвращает список лемм (сохраняя регистр).
    """
    doc = nlp(snippet)
    lemmas = []
    for token in doc:
        if not token.is_stop and not token.is_space and token.is_alpha:
            lemmas.append(token.lemma_)
    return lemmas


def get_grammar_info(word):
    """
    Возвращает POS и MORPH для слова в том виде, как их выдаёт spaCy.
    """
    doc = nlp(word)
    if not doc:
        return {'error': 'Слово не найдено'}

    token = doc[0]
    
    return {
        'word': word,
        'pos': token.pos_,
        'morph': str(token.morph),
    }


def get_word_frequencies_from_text(text):
    """
    Возвращает Counter с частотами слов в тексте.
    Используется для парсинга книги.
    """
    tokens = text.split()
    cleaned_tokens = []
    for token in tokens:
        token = token.strip('.,;:!?()[]{}«»“”…\'"')
        if token and len(token) >= 2:
            cleaned_tokens.append(token)
    return Counter(cleaned_tokens)


# ========== Word2Vec (для синонимов) ==========
_word2vec_model = None

def _load_word2vec_model():
    """Ленивая загрузка модели word2vec (только при необходимости)"""
    global _word2vec_model
    if _word2vec_model is None:
        try:
            from gensim.models import KeyedVectors
            from huggingface_hub import hf_hub_download
            model_path = hf_hub_download(
                repo_id="Word2vec/german_model",
                filename="german.model"
            )
            _word2vec_model = KeyedVectors.load_word2vec_format(
                model_path, binary=True, unicode_errors="ignore"
            )
        except ImportError:
            print("Модуль gensim или huggingface_hub не установлен. Установите: pip install gensim huggingface_hub")
            return None
        except Exception as e:
            print(f"Ошибка загрузки модели word2vec: {e}")
            return None
    return _word2vec_model


def get_synonyms(word, topn=5):
    """
    Возвращает список синонимов для слова (через word2vec).
    Если модель не загружена, возвращает пустой список.
    """
    model = _load_word2vec_model()
    if model is None:
        return []
    
    try:
        similar = model.most_similar(word, topn=topn)
        return [w for w, _ in similar]
    except KeyError:
        return []