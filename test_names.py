import csv

with open('german_general_final.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    print("Точные названия колонок:")
    for i, col in enumerate(reader.fieldnames):
        print(f"{i}: '{col}'")
        # Выводим ASCII коды для отладки
        print(f"   Коды: {[ord(c) for c in col]}")