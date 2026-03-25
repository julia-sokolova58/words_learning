# german_words/views.py
from django.shortcuts import render, redirect
from books.models import Book
from german_words.models import GermanWord
from services.text_processor import find_snippet_in_book, final_wordlist
from .forms import SnippetForm


def home(request):
    """Страница с формой для ввода первых и последних 5 слов"""
    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            first_five = form.cleaned_data['first_five']
            last_five = form.cleaned_data['last_five']

            # Сохраняем в сессии
            request.session['first_five'] = first_five
            request.session['last_five'] = last_five

            # Перенаправляем на страницу с результатами
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

    # Получаем два списка: глаголы и существительные
    verbs, nouns = final_wordlist(snippet)
    
    # Объединяем (сначала глаголы, потом существительные)
    all_words = nouns
    
    if not all_words:
        return render(request, 'error.html', {'message': 'В отрывке не найдено слов'})

    # Ищем переводы
    words_with_translations = []
    for word in all_words:
        try:
            german_word = GermanWord.objects.get(german_word=word)
            words_with_translations.append({
                'word': word,
                'translation': german_word.russian_translation,
            })
        except GermanWord.DoesNotExist:
            # Если слова нет в базе, пропускаем
            continue

    # Очищаем сессию
    del request.session['first_five']
    del request.session['last_five']

    return render(request, 'words.html', {'words': words_with_translations})