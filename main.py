import re
import sys
import math
import toml


# Функция для вычисления постфиксных выражений
def evaluate_expression(expression, constants):
    tokens = expression.split()
    stack = []

    for token in tokens:
        if token.isdigit():  # Если токен - число
            stack.append(int(token))
        elif token in constants:  # Если токен - константа
            stack.append(constants[token])
        elif token == '+':
            stack.append(stack.pop() + stack.pop())
        elif token == '-':
            b, a = stack.pop(), stack.pop()
            stack.append(a - b)
        elif token == 'mod()':
            b, a = stack.pop(), stack.pop()
            stack.append(a % b)
        elif token == 'sqrt()':
            stack.append(math.sqrt(stack.pop()))
        elif token == 'max()':
            stack.append(max(stack.pop(), stack.pop(), stack.pop()))  # Исправление для max()
    return stack[0] if stack else None


# Функция для парсинга конфигурационного языка
def parse_config(text):
    config = {}
    constants = {}  # Словарь для хранения констант

    lines = text.splitlines()
    current_dict = None
    inside_block = False
    block_content = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Обработка констант
        def_match = re.match(r'\(def (\w+) (.+?)\);', line)
        if def_match:
            name, value = def_match.groups()
            result = evaluate_expression(value, constants)
            if result is not None:
                constants[name] = result
            else:
                print(f"Error in constant definition: {line}")
            continue

        # Обработка вложенных блоков
        if line == "begin":
            inside_block = True
            block_content = []
            continue
        elif line == "end" and inside_block:
            inside_block = False
            # Рекурсивно вызываем parse_config для содержимого блока
            block_dict = parse_config('\n'.join(block_content))
            if current_dict is not None:
                current_dict.update(block_dict)
            else:
                config.update(block_dict)
            continue

        # Добавление содержимого блока
        if inside_block:
            block_content.append(line)
            continue

        # Обработка выражений в фигурных скобках
        expr_match = re.match(r'(\w+)\s*:=\s*\{(.*?)\};?', line)
        if expr_match:
            name, expression = expr_match.groups()
            result = evaluate_expression(expression, constants)
            if result is not None:
                if current_dict is not None:
                    current_dict[name] = result
                else:
                    config[name] = result
            else:
                print(f"Error in expression: {line}")
            continue

        # Обработка обычных ключ-значений
        kv_match = re.match(r'(\w+)\s*:=\s*(.+?);', line)
        if kv_match:
            name, value = kv_match.groups()
            value = value.strip()

            if value == 'true':
                value = True
            elif value == 'false':
                value = False
            elif value.startswith("'") and value.endswith("'"):
                value = value.strip("'")
            elif value.isdigit():
                value = int(value)

            if current_dict is not None:
                current_dict[name] = value
            else:
                config[name] = value
            continue

        # Обработка вложенных словарей
        dict_match = re.match(r'(\w+)\s*:=\s*\{(.*?)\};?', line)
        if dict_match:
            name, content = dict_match.groups()
            sub_dict = parse_config(content)
            if current_dict is not None:
                current_dict[name] = sub_dict
            else:
                config[name] = sub_dict
            continue

    return config


# Функция для вывода в формат TOML
def convert_to_toml(config):
    toml_str = ""

    for key, value in config.items():
        if isinstance(value, dict):
            toml_str += f'[{key}]\n'
            toml_str += convert_to_toml(value)
        elif isinstance(value, bool):
            toml_str += f'{key} = {str(value).lower()}\n'
        elif isinstance(value, int):
            toml_str += f'{key} = {value}\n'
        elif isinstance(value, str):
            toml_str += f'{key} = "{value}"\n'
        else:
            print(f"Unsupported type for {key}: {type(value)}")

    return toml_str


if __name__ == "__main__":
    # Чтение данных с stdin
    input_text = sys.stdin.read()

    # Парсинг конфигурации
    config = parse_config(input_text)

    # Преобразование в формат TOML
    toml_output = convert_to_toml(config)

    # Вывод результата на stdout
    sys.stdout.write(toml_output)
