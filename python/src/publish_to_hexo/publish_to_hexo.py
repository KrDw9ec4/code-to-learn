import sys
import os
import yaml
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import utils.frontmatter as fm  # noqa

# config.yml 路径
config_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'config.yml')

# 检查 config.yml 是否存在，不存在则生成
if not os.path.exists(config_path):
    with open(config_path, 'w') as f:
        yaml.dump({'post_path': str(input("请输入要文章的存储路径："))}, f)

# 读取 config.yml
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
    dest_path = config['post_path']

# 从命令行获取文件路径
src_path = sys.argv[1]

# 读取文章元数据
frontmatter, content = fm.parser(src_path)
kvdict = fm.yaml2dict(frontmatter)
print(f"文章标题为：{kvdict["title"]}")

# 更改文章元数据
update_key_list = [("created", "date"), ("modified", "updated")]
for key0, key1 in update_key_list:
    kvdict = fm.updateKey(kvdict, key0, key1)
if "publish" in kvdict["tags"]:
    fm.updateValue(kvdict, "tags", "publish", "DELETE")

# 生成并创建新的文件
file_name = str(input("请输入要保存的文件名："))
dest_file_path = os.path.join(dest_path, file_name)
post = fm.merge2post(fm.dict2yaml(kvdict), content)
with open(dest_file_path, 'w', encoding='utf-8') as f:
    f.write(post)
