"""Веб-интерфейс для управления Redis.

Запуск: python redis_web.py
Затем откройте http://localhost:5000 в браузере.
"""

from flask import Flask, render_template_string, request, redirect, url_for
import redis

app = Flask(__name__)

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# HTML-шаблоны (inline для простоты)
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Redis Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .action-btn { margin: 5px; padding: 5px 10px; background: #007bff; color: white; border: none; cursor: pointer; }
        .delete-btn { background: #dc3545; }
        .clear-btn { background: #ffc107; color: black; }
    </style>
</head>
<body>
    <h1>Redis Manager</h1>
    <form method="post" action="{{ url_for('clear_all') }}">
        <button type="submit" class="action-btn clear-btn" onclick="return confirm('Очистить всю базу?')">Очистить всю базу</button>
    </form>
    <h2>Ключи и значения</h2>
    <table>
        <tr><th>Ключ</th><th>Тип</th><th>Значение</th><th>Действия</th></tr>
        {% for key, info in keys.items() %}
        <tr>
            <td>{{ key }}</td>
            <td>{{ info.type }}</td>
            <td>
                {% if info.type == 'string' %}
                    {{ info.value }}
                {% elif info.type == 'list' %}
                    Список ({{ info.count }} элементов)
                {% elif info.type == 'set' %}
                    Множество ({{ info.count }} элементов)
                {% else %}
                    Не поддерживается
                {% endif %}
            </td>
            <td>
                <form method="post" action="{{ url_for('delete_key') }}" style="display:inline;">
                    <input type="hidden" name="key" value="{{ key }}">
                    <button type="submit" class="action-btn delete-btn" onclick="return confirm('Удалить ключ {{ key }}?')">Удалить</button>
                </form>
                {% if info.type in ['list', 'set'] %}
                <a href="{{ url_for('view_key', key=key) }}"><button class="action-btn">Просмотреть</button></a>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </table>
    {% if not keys %}
    <p>Redis пуст.</p>
    {% endif %}
</body>
</html>
"""

KEY_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ключ: {{ key }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        pre { background: #f4f4f4; padding: 10px; border: 1px solid #ddd; }
        .back-btn { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Ключ: {{ key }}</h1>
    <p>Тип: {{ key_type }}</p>
    <h2>Значение:</h2>
    <pre>{{ value }}</pre>
    <a href="{{ url_for('index') }}"><button class="back-btn">Назад</button></a>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    keys = {}
    for key in r.keys('*'):
        key_type = r.type(key)
        if key_type == 'string':
            keys[key] = {'type': 'string', 'value': r.get(key), 'count': None}
        elif key_type == 'list':
            count = r.llen(key)
            keys[key] = {'type': 'list', 'value': None, 'count': count}
        elif key_type == 'set':
            count = r.scard(key)
            keys[key] = {'type': 'set', 'value': None, 'count': count}
        else:
            keys[key] = {'type': key_type, 'value': None, 'count': None}
    return render_template_string(INDEX_TEMPLATE, keys=keys)

@app.route('/key/<key>', methods=['GET'])
def view_key(key):
    if not r.exists(key):
        return "Ключ не найден", 404
    key_type = r.type(key)
    if key_type == 'list':
        value = '\n'.join(f"[{i}]: {item}" for i, item in enumerate(r.lrange(key, 0, -1)))
    elif key_type == 'set':
        value = '\n'.join(r.smembers(key))
    else:
        value = "Тип данных не поддерживается для детального просмотра."
    return render_template_string(KEY_DETAIL_TEMPLATE, key=key, key_type=key_type, value=value)

@app.route('/delete', methods=['POST'])
def delete_key():
    key = request.form['key']
    r.delete(key)
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear_all():
    r.flushdb()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)