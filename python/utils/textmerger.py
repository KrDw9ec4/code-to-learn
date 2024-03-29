import shutil


class TextMerger:
    def __init__(self, left_text, right_text):
        self.left_lines = left_text.splitlines()
        self.right_lines = right_text.splitlines()
        self.merged_lines = []

    def merge(self):
        left_index = 0
        right_index = 0

        while left_index < len(self.left_lines) or right_index < len(self.right_lines):
            if left_index >= len(self.left_lines) or right_index >= len(self.right_lines):
                self.handle_out_range(left_index, right_index)
                break
            elif self.left_lines[left_index] == self.right_lines[right_index]:
                self.merged_lines.append(self.left_lines[left_index])
                left_index += 1
                right_index += 1
            else:
                print(f"{self.left_lines[left_index-2]}")
                print(f"{self.left_lines[left_index-1]}")
                print("\033[92m" + f"{self.left_lines[left_index]}" + "\033[0m")
                print(f"{self.left_lines[left_index+1]}")
                print(f"{self.left_lines[left_index+2]}")
                print("=" * shutil.get_terminal_size().columns)
                print(f"{self.right_lines[right_index-2]}")
                print(f"{self.right_lines[right_index-1]}")
                print("\033[92m" + f"{self.right_lines[right_index]}" + "\033[0m")
                print(f"{self.right_lines[right_index+1]}")
                print(f"{self.right_lines[right_index+2]}")
                left_index, right_index = self.handle_conflict(left_index, right_index)
        return '\n'.join(self.merged_lines)

    def handle_conflict(self, left_index, right_index):
        match input("\033[91m"+f"Conflict: 第 {left_index + 1} 行在左右两边不一致，选择解决方案（L/R/LA/LD/RA/RD/I）> "+"\033[0m").lower():
            case 'l':
                self.merged_lines.append(self.left_lines[left_index])
                left_index += 1
                right_index += 1
                return left_index, right_index
            case 'r':
                self.merged_lines.append(self.right_lines[right_index])
                left_index += 1
                right_index += 1
                return left_index, right_index
            case 'la':
                self.merged_lines.append(self.left_lines[left_index])
                left_index += 1
                return left_index, right_index
            case 'ld':
                right_index += 1
                return left_index, right_index
            case 'ra':
                self.merged_lines.append(self.right_lines[right_index])
                right_index += 1
                return left_index, right_index
            case 'rd':
                left_index += 1
                return left_index, right_index
            case 'i':
                user_input = input("手动处理冲突：\n")
                self.merged_lines.append(user_input)
                left_index += 1
                right_index += 1
                return left_index, right_index
            case _:
                self.print_help()
                print("\n无法识别的输入，可选的选项：L/R/LA/LD/RA/RD/I")

    def handle_out_range(self, left_index, right_index):
        if left_index >= len(self.left_lines):
            self.handle_out_range_conflict(self.right_lines, right_index)
        else:
            self.handle_out_range_conflict(self.left_lines, left_index)

    def handle_out_range_conflict(self, lines, index):
        while index < len(lines):
            print(f"{index}:> {lines[index]}")
            index += 1
        # 输入一个数组（空格分隔），作为索引将 lines 对应元素添加到 merged_lines 中
        user_input_list = [eval(i) for i in input("输入要添加的行的索引（空格分隔）：").split()]
        for i in user_input_list:
            self.merged_lines.append(lines[i])

    def print_help():

        abbr_list = ['l', 'r', 'la', 'ld', 'ra', 'rd', 'i']

        method_dict = {
            'l': 'LEFT',
            'r': 'RIGHT',
            'la': 'LEFT ADD',
            'ld': 'LEFT DELETE',
            'ra': 'RIGHT ADD',
            'rd': 'RIGHT DELETE',
            'i': 'INPUT',
        }

        description_dict = {
            'l': '选择左边的内容。',
            'r': '选择右边的内容。',
            'la': '左边增加了一行且选择左边的内容。',
            'ld': '左边删除了一行且选择左边的内容。',
            'ra': '右边增加了一行且选择右边的内容。',
            'rd': '右边删除了一行且选择右边的内容。',
            'i': '手动输入内容。',
        }

        width = 54
        abbr_width = 6
        method_width = 16
        description_width = width - abbr_width - method_width

        header_fmt = f"{{:<{abbr_width}}}{{:<{method_width}}}{{:<{description_width}}}"
        fmt = f"{{:<{abbr_width}}}{{:<{method_width}}}{{:<{description_width}}}"

        print('=' * width)

        print(header_fmt.format('ABBR', 'METHOD', 'DESCRIPTION'))

        print('-' * width)

        for abbr in abbr_list:
            print(fmt.format(abbr, method_dict[abbr], description_dict[abbr]))

        print('=' * width)
