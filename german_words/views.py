from django.shortcuts import render, redirect
from books.models import Book
from german_words.models import GermanWord
from services.text_processor import (
    find_snippet_in_book, 
    final_wordlist,
    parse_noun_declension,
    parse_verb_page,
    related_words
)
from .forms import SnippetForm


def home(request):
    """Страница с формой для ввода первых и последних 5 слов"""
    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            first_five = form.cleaned_data['first_five']
            last_five = form.cleaned_data['last_five']

            request.session['first_five'] = first_five
            request.session['last_five'] = last_five

            return redirect('german_words:words')
    else:
        form = SnippetForm()

    return render(request, 'home.html', {'form': form})


def words(request):
    """Страница со списком слов из отрывка"""
    first_five = request.session.get('first_five')
    last_five = request.session.get('last_five')

    if not first_five or not last_five:
        return redirect('german_words:home')

    book = Book.objects.first()
    if not book or not book.file_path:
        return render(request, 'error.html', {'message': 'Книга не найдена'})

    snippet = find_snippet_in_book(book.file_path, first_five, last_five)
    if snippet is None:
        return render(request, 'error.html', {'message': 'Отрывок не найден'})

    verbs, nouns = final_wordlist(snippet)
    all_words = verbs + nouns
    
    if not all_words:
        return render(request, 'error.html', {'message': 'В отрывке не найдено слов'})

    words_with_translations = []
    for word in all_words:
        try:
            german_word = GermanWord.objects.get(german_word__iexact=word)
            words_with_translations.append({
                'word': word,
                'translation': german_word.russian_translation,
            })
        except GermanWord.DoesNotExist:
            continue

    del request.session['first_five']
    del request.session['last_five']

    return render(request, 'words.html', {'words': words_with_translations})


def grammar_page(request, word):
    """Страница с грамматикой для слова"""
    result = parse_verb_page(word)
    if "Кажется, такого слова нет" in result:
        result = parse_noun_declension(word)
    
    return render(request, 'grammar.html', {'word': word, 'grammar': result})


def synonyms_page(request, word):
    """Страница с синонимами для слова"""
    synonyms = related_words(word, n=5)
    return render(request, 'synonyms.html', {'word': word, 'synonyms': synonyms})
