import os

work_dir = os.path.dirname(os.path.abspath('.'))
log_lines_limit = 10000


# Функция для поиска файлов *.log в указанной директории
def find_log_files(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.log')]


def count_lines(file_path):
    with open(file_path, 'r') as f:
        return len(f.readlines())


def clear_logs():
    dirs = [d for d in os.listdir(work_dir) if not d.startswith('.') and os.path.isdir(os.path.join(work_dir, d))]
    # Перебираем каждую директорию
    for dir_name in dirs:
        # Полный путь к текущей директории
        current_dir = os.path.join(work_dir, dir_name)

        # Находим файлы *.log в текущей директории
        for log_file in find_log_files(current_dir):
            file_path = os.path.join(current_dir, log_file)
            if count_lines(file_path) > log_lines_limit:
                # Очищаем содержимое файла
                with open(file_path, 'w') as f:
                    f.write("")
