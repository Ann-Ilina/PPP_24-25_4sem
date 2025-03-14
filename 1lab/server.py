import json
import socket
import logging
import psutil

# Настройка логирования
logging.basicConfig(filename='server.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# Логируются только сообщения уровня INFO и выше.


def get_process_info():
    """Получает информацию о всех процессах и 
       возвращает её в виде списка словарей."""
    processes = []
    # Итерируется по всем процессам и получает их PID, имя и статус.
    for proc in psutil.process_iter(['pid', 'name', 'status']): 
        try:
            process_info = proc.info
            processes.append(process_info)
        # Игнорируем процессы, которые недоступны
        # (например, завершенные или системные).
        except (psutil.NoSuchProcess, psutil.AccessDenied,
                psutil.ZombieProcess):
            continue
    return processes


def save_to_json(data, filename='processes.json'):
    """Сохраняет данные в JSON файл."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    logging.info(f"Данные сохранены в файл {filename}")


def handle_client(conn, addr):
    """Обрабатывает запросы клиента."""
    logging.info(f"Подключен клиент: {addr}")
    print(f"Клиент {addr} подключен.")
    try:
        while True:
            try:
                # Получаем команду от клиента
                command = conn.recv(1024).decode('utf-8').strip()
                if not command:
                    break

                if command == "update":
                    print(f"Клиент {addr} запросил обновление информации о процессах.")
                    processes = get_process_info()
                    save_to_json(processes)
                    with open('processes.json', 'rb') as f:
                        file_data = f.read()
                    conn.sendall(file_data)  # Отправляем данные
                    print(f"Файл processes.json отправлен клиенту {addr}.")
                    logging.info(f"Клиенту {addr} отправлен файл processes.json")
                    break  # Закрываем соединение после отправки данных

                elif command.startswith("signal"):
                    _, pid, sig = command.split()
                    print(f"Клиент {addr} запросил отправку сигнала {sig} процессу {pid}.")
                    try:
                        proc = psutil.Process(int(pid))
                        if sig == "1":
                            proc.suspend()  # SIGSTOP (приостановка процесса)
                            response = f"Процесс {pid} приостановлен."
                        elif sig == "2":
                            proc.resume()  # SIGCONT (возобновление процесса)
                            response = f"Процесс {pid} возобновлен."
                        elif sig == "9":
                            proc.kill()  # SIGKILL (убийство процесса)
                            response = f"Процесс {pid} убит."
                        else:
                            response = f"Неверный сигнал: {sig}."
                        conn.sendall(response.encode('utf-8'))  # Отправляем ответ
                        print(f"Ответ отправлен клиенту {addr}: {response}")
                        logging.info(f"Клиент {addr} отправил сигнал {sig} процессу {pid}")
                        break  # Закрываем соединение после отправки ответа
                    except psutil.NoSuchProcess:
                        response = f"Процесс {pid} не найден."
                        conn.sendall(response.encode('utf-8'))
                        print(f"Ошибка: процесс {pid} не найден.")
                    except psutil.AccessDenied:
                        response = f"Нет прав для отправки сигнала процессу {pid}."
                        conn.sendall(response.encode('utf-8'))
                        print(f"Ошибка: нет прав для отправки сигнала процессу {pid}.")
                    except Exception as e:
                        response = f"Ошибка: {e}."
                        conn.sendall(response.encode('utf-8'))
                        print(f"Ошибка при обработке запроса от {addr}: {e}")
                        break  # Закрываем соединение при ошибке

            except ConnectionResetError:
                print(f"Клиент {addr} разорвал соединение.")
                logging.error(f"Клиент {addr} разорвал соединение.")
                break
            except Exception as e:
                logging.error(f"Ошибка при обработке запроса от {addr}: {e}")
                print(f"Ошибка при обработке запроса от {addr}: {e}")
                break

    finally:
        conn.close()  # Закрываем соединение
        print(f"Клиент {addr} отключен.")
        logging.info(f"Клиент {addr} отключен")
               

def start_server(host='127.0.0.1', port=65432):
    """Запускает сервер и ожидает подключения клиентов."""
    # Создаем TCP-сокет.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Привязываем сокет к указанному адресу и порту.
        s.bind((host, port))
        # Начинаем прослушивание входящих соединений.
        s.listen()
        print(f"Сервер запущен на {host}:{port}. Ожидание подключений...")
        logging.info(f"Сервер запущен на {host}:{port}")
        while True:
            # Принимаем подключение от клиента и возвращаем
            # объект соединения и адрес клиента.
            conn, addr = s.accept()
            handle_client(conn, addr)


if __name__ == "__main__":
    start_server()
