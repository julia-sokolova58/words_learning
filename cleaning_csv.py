import csv
from collections import OrderedDict

def clean_csv_duplicates(input_file, output_file):
    """Удаляет дубликаты из CSV с правильной обработкой BOM"""
    
    words_dict = OrderedDict()
    
    # Используем utf-8-sig для удаления BOM
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        print("Колонки после очистки BOM:", reader.fieldnames)
        
        for row in reader:
            german_word = row['Немецкое слово'].strip("'\"")
            russian_translation = row['Перевод на русский'].strip("'\"")
            
            # Если слово уже есть, пропускаем дубликат
            if german_word not in words_dict:
                words_dict[german_word] = row
            else:
                print(f"Дубликат: '{german_word}' - пропущен")
    
    # Сохраняем очищенный файл
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(words_dict.values())
    
    # Подсчет строк с правильной кодировкой
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        total_lines = sum(1 for _ in f) - 1  # минус заголовок
    
    print(f"\n📊 Результат:")
    print(f"   Было строк: {total_lines}")
    print(f"   Уникальных слов: {len(words_dict)}")
    
    return output_file

if __name__ == '__main__':
    clean_csv_duplicates('german_general_final.csv', 'cleaned_words.csv')