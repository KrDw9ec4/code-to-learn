import subprocess
import yaml
import sys
import os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import utils.frontmatter as fm  # noqa
from utils.textmerger import TextMerger as tm  # noqa


def find_file(title, path):
    """
    递归查找指定目录下的文件，返回文件路径。

    Args:
        title (str): 文件名。
        path (str): 查找目录。

    Returns:
        str: 文件路径。
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            frontmatter = fm.parser(os.path.join(root, file))[0]
            kvdict = fm.yaml2dict(frontmatter)
            if kvdict["title"] == title:
                return os.path.join(root, file)
        else:
            raise FileNotFoundError(f"找不到文件：{title}")


# config.yml 路径
config_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'config.yml')

# 检查 config.yml 是否存在，不存在则生成
if not os.path.exists(config_path):
    with open(config_path, 'w') as f:
        yaml.dump({'hexo_path': str(input("请输入 hexo 的工作路径："))}, f)
        yaml.dump({'post_path': str(input("请输入文章的存储路径（source/_post）："))}, f)
        yaml.dump({'deploy_command': str(input("请输入 hexo 的部署命令："))}, f)

# 读取 config.yml
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
    hexo_path = config['post_path']
    obsidian_publish_path = config['obsidian_publish_path']

# 从命令行获取标题，找到相应的文件路径
title = sys.argv[1]
hexo_blog_path = find_file(title, hexo_path)
obsidian_note_path = find_file(title, obsidian_publish_path)

# 对 hexo 和 obsidian 的文件进行解析
hexo_blog_frontmatter, hexo_blog_content = fm.parser(hexo_blog_path)
obsidian_note_frontmatter, obsidian_note_content = fm.parser(obsidian_note_path)
hexo_blog_kvdict = fm.yaml2dict(hexo_blog_frontmatter)
obsidian_note_kvdict = fm.yaml2dict(obsidian_note_frontmatter)

# 合并 content 正文内容，三种模式：hexo 优先、obsidian 优先、合并
match input("优先合并（hexo/obsidian/SYNC）：").lower():
    case 'hexo':
        mergedText = hexo_blog_content
    case 'obsidian':
        mergedText = obsidian_note_content
    case _:
        TextMerger = tm(hexo_blog_content, obsidian_note_content)
        mergedText = TextMerger.merge()

# 是否写入 hexo 和 Obsidian
modified_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
print(f"修改时间：{modified_time}")
match input("写入到（hexo/obsidian/ALL）：").lower():
    case 'hexo':
        fm.updateValue(hexo_blog_kvdict, 'updated', modified_time, 'UPDATE')
        hexo_blog = fm.merge2post(fm.dict2yaml(hexo_blog_kvdict), mergedText)
        with open(hexo_blog_path, 'w', encoding='utf-8') as f:
            f.write(hexo_blog)
    case 'obsidian':
        fm.updateValue(obsidian_note_kvdict, 'modified', modified_time, 'UPDATE')
        obsidian_note = fm.merge2post(fm.dict2yaml(obsidian_note_kvdict), mergedText)
        with open(obsidian_note_path, 'w', encoding='utf-8') as f:
            f.write(obsidian_note)
    case 'test':
        pass
    case _:
        fm.updateValue(hexo_blog_kvdict, 'updated', modified_time, 'UPDATE')
        hexo_blog = fm.merge2post(fm.dict2yaml(hexo_blog_kvdict), mergedText)
        with open(hexo_blog_path, 'w', encoding='utf-8') as f:
            f.write(hexo_blog)
        fm.updateValue(obsidian_note_kvdict, 'modified', modified_time, 'UPDATE')
        obsidian_note = fm.merge2post(fm.dict2yaml(obsidian_note_kvdict), mergedText)
        with open(obsidian_note_path, 'w', encoding='utf-8') as f:
            f.write(obsidian_note)

# 确认是否部署
if str(input("是否部署到 hexo？（y/n）：")).lower() == "y":
    os.chdir(config['hexo_path'])
    subprocess.run(config['deploy_command'], shell=True)

input("按任意键退出")
