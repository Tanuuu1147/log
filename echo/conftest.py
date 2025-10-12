import pytest
import subprocess
import time
import socket


@pytest.fixture(scope="session")
def host():
    return "127.0.0.1"


@pytest.fixture(scope="session")
def port():
    return 5000


@pytest.fixture(scope="session", autouse=True)
def server(host, port):
    # Проверяем, что порт свободен
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
        except OSError:
            # Порт занят, возможно сервер уже запущен
            pass
    
    # Запускаем наш сервер
    proc = subprocess.Popen(["python3", "echo_server.py"])
    
    # Ждем, пока сервер запустится
    time.sleep(1)
    
    # Проверяем, что сервер доступен
    for _ in range(10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                break
        except ConnectionRefusedError:
            time.sleep(0.5)
    
    yield
    
    # Завершаем процесс сервера
    proc.terminate()
    proc.wait()