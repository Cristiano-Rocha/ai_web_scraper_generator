import json
import os


def open_file(file_path: str):
    try:
        with open(file_path, encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File not found in '{file_path}'")
    except json.JSONDecodeError:
        print(f"JSON decode error in '{file_path}'")
        return {}

def dict_to_markdown(data: dict , indent_level=0) -> str:
    markdown_output = ""
    indent = "  " * indent_level
    for key, value in data.items():
        markdown_output += f"{indent}- **{key}:** "
        if isinstance(value, dict):
            markdown_output += "\n" + dict_to_markdown(value, indent_level + 1)
        elif isinstance(value, list):
            markdown_output += "\n" + list_to_markdown(value, indent_level + 1)
        else:
            markdown_output += f"{value}\n"
    return markdown_output

def list_to_markdown(data_list, indent_level=0):
    markdown_output = ""
    indent = "  " * indent_level
    for item in data_list:
        markdown_output += f"{indent}- "
        if isinstance(item, dict):
            markdown_output += "\n" + dict_to_markdown(item, indent_level + 1)
        elif isinstance(item, list):
            markdown_output += "\n" + list_to_markdown(item, indent_level + 1)
        else:
            markdown_output += f"{item}\n"
    return markdown_output


def convert_json_to_mkd(file_path: str) -> str:
    try:
        filename = os.path.splitext(os.path.basename(file_path))[0]
        data = open_file(file_path)
        if not data or 'log' not in data or 'entries' not in data['log']:
            print(f"Warning: File '{file_path}' does not contain any log")
            return

        markdown_content = ''
        for i in reversed(range(len(data['log']['entries']))):
            entry = data['log']['entries'][i]
            del entry['request']['cookies']
            del entry['response']['cookies']
            del entry['_securityDetails']
            if '.js' in entry['request']['url']:
                data['log']['entries'].pop(i)
            for header in entry['response']['headers']:
                if header['name'] == 'content-type':
                    if header['value'] not in ['text/html; charset=UTF-8', "application/json;charset=utf-8",'application/json']:
                        data['log']['entries'].pop(i)
                        continue
            markdown_content += dict_to_markdown(entry) + '\n'
        file_path_markdown = os.path.join(os.path.dirname(file_path), f'{filename}.md')
        with open(file_path_markdown, 'w', encoding="utf-8") as file:
            file.write(markdown_content)
        return markdown_content
    except Exception as e:
        print(e)

