
import re
from collections import OrderedDict
import yaml


def parser(path):
    """
    接受一个文件路径，读取并返回 frontmatter 和 content。

    Args:
        path (str): 文件路径。

    Returns:
        tuple: 包含前置元数据和内容的元组。

    """
    PATTERN = re.compile(r'^---\s*\n(.*?)^---\s*\n(.*)', re.DOTALL | re.MULTILINE)
    with open(path, 'r', encoding='utf-8') as file:
        if match := PATTERN.match(file.read()):
            frontmatter = match.group(1)
            content = match.group(2)
            return frontmatter, content


def yaml2dict(string):
    """
    将 YAML 字符串转换为有序字典 ordeddict。

    Args:
        string (str): YAML 字符串。

    Returns:
        OrderedDict: 转换后的有序字典。

    """
    kvdict = OrderedDict()
    key = None
    for line in string.split('\n'):
        if line:
            if match := re.match(r'^(\w+):\s*(.*)$', line):
                key = match.group(1)
                value = match.group(2)
                if value:
                    kvdict[key] = value
                else:
                    kvdict[key] = []
            elif key:
                if match := re.match(r'^\s*-\s*(?:\"|\')(.*)(?:\"|\')$', line):
                    kvdict[key].append(match.group(1))
    return kvdict


def dict2yaml(dict):
    """
    将有序字典转换为 YAML 字符串。

    Args:
        dict (OrderedDict): 有序字典。

    Returns:
        str: 转换后的 YAML 字符串。

    """
    yaml_str = ''
    for key, value in dict.items():
        yaml_str += yaml.dump({key: value}, allow_unicode=True, default_style='')
    yaml_str = re.sub(r'(?m)^- ', r'  - ', yaml_str)
    yaml_str = re.sub(r'\'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\'', r'\1', yaml_str)
    return yaml_str


def merge2post(frontmatter, content):
    """
    将 frontmatter 和 content 合并为完整的文章。

    Args:
        frontmatter (str): 前置元数据。
        content (str): 内容。

    Returns:
        str: 合并后的文章。

    """
    return f'---\n{frontmatter}---\n\n{content}'


def updateKey(kvdict, key, repl):
    """
    更新有序字典中的键名。

    Args:
        kvdict (OrderedDict): 有序字典。
        key (str): 要更新的键名。
        repl (str): 更新后的键名。

    Returns:
        OrderedDict: 更新后的有序字典。

    """
    newdict = OrderedDict()
    for k, v in kvdict.items():
        if k == key:
            newdict[repl] = v
        else:
            newdict[k] = v
    return newdict


def updateValue(kvdict, key, value, mode):
    """
    更新有序字典中的键值。

    Args:
        kvdict (OrderedDict): 有序字典。
        key (str): 要更新的键名。
        value (str or list): 更新后的键值。
        mode (str): 更新模式，可选值为 'UPDATE', 'DELETE', 'APPEND', 'REGEX'。

    Returns:
        OrderedDict: 更新后的有序字典。

    Raises:
        ValueError: 当 mode 参数不是 'UPDATE', 'DELETE', 'APPEND', 'REGEX' 之一时抛出异常。

    """
    match mode:
        case 'UPDATE':
            kvdict[key] = value
        case 'DELETE':
            if isinstance(kvdict[key], list):
                kvdict[key].remove(value)
            elif isinstance(kvdict[key], str):
                kvdict[key] = ''
        case 'APPEND':
            if isinstance(value, str):
                kvdict[key].append(value)
            elif isinstance(value, list):
                kvdict[key].extend(value)
        case 'DELETE':
            del kvdict[key]
        case 'REGEX':
            regex, repl = value
            if isinstance(kvdict[key], str):
                kvdict[key] = re.sub(regex, repl, kvdict[key])
            elif isinstance(kvdict[key], list):
                kvdict[key] = [re.sub(regex, repl, item) for item in kvdict[key]]
        case _:
            raise ValueError('mode 参数只能是 UPDATE, APPEND, REGEX 三者之一')
