import csv
from flask import Flask, request, jsonify

# Создаём Flask-приложение
app = Flask(__name__)

# Список для хранения данных в памяти
data = []

# Загрузка данных из LE.txt
with open('LE.txt', 'r', encoding='latin1', errors='replace') as f:
    # Читаем файл как таблицу с табуляцией
    reader = csv.DictReader(f, fieldnames=['serial', 'name', 'z1', 'z2', 'z3', 'z4', 'z5', 'empty', 'price', 'brand', 'price2'], delimiter='\t')
    for row in reader:
        data.append(row)

@app.route('/spare-parts', methods=['GET'])
def get_spare_parts():
    # Копируем данные, чтобы не изменять исходный список
    filtered = data[:]
    # Читаем параметры запроса
    name = request.args.get('name')
    sn = request.args.get('sn')
    # Фильтрация по названию
    if name:
        filtered = [d for d in filtered if name.lower() in d['name'].lower()]
    # Фильтрация по серийному номеру
    if sn:
        filtered = [d for d in filtered if sn in d['serial']]
    
    # Сортировка, если передан параметр sort
    sort = request.args.get('sort')
    if sort:
        reverse = sort.startswith('-')
        key = sort.lstrip('-')
        if key == 'price':
            filtered.sort(key=lambda x: float(x['price'].replace(',', '.')) if x['price'] else 0, reverse=reverse)
        elif key == 'name':
            filtered.sort(key=lambda x: x['name'], reverse=reverse)
    
    # Пагинация: по 30 элементов на страницу
    page = int(request.args.get('page', 1))
    per_page = 30
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]
    return jsonify(paginated)

@app.route('/spare-parts/search/<query>', methods=['GET'])
def search(query):
    # Поиск по строке query в названии или серийном номере
    filtered = [d for d in data if query.lower() in d['name'].lower() or query in d['serial']]
    
    # Сортировка результатов поиска по цене, если указан параметр sort
    sort = request.args.get('sort')
    if sort:
        reverse = sort.startswith('-')
        key = sort.lstrip('-')
        if key == 'price':
            filtered.sort(key=lambda x: float(x['price'].replace(',', '.')) if x['price'] else 0, reverse=reverse)
    
    # Пагинация результатов поиска
    page = int(request.args.get('page', 1))
    per_page = 30
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]
    return jsonify(paginated)

if __name__ == '__main__':
    # Запуск сервера на порту 3300
    app.run(debug=True, port=3300)
