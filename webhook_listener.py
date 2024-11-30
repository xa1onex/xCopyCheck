from flask import Flask, request
import os
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    data = request.get_json()

    # Проверка, что это событие push в главную ветку
    if data['ref'] == 'refs/heads/main':  # Убедись, что это push в главную ветку
        print("Обновление репозитория...")
        # Обновляем локальный репозиторий
        subprocess.run(['git', 'pull', 'origin', 'main'])
        # Перезапускаем бота
        subprocess.run(['pkill', '-f', 'python main.py'])
        subprocess.run(['python', 'main.py'])

    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)