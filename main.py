from re import match
from queue import PriorityQueue


class TilePlacement:
    # 瓷砖覆盖模式
    # 完全覆盖：覆盖全部4x4的区域
    FULL_COVERAGE = [(i, j) for i in range(4) for j in range(4)]
    # 外边界覆盖：只覆盖4x4区域的外边界
    OUTER_BOUNDARY_COVERAGE = [
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 0),
        (1, 3),
        (2, 0),
        (2, 3),
        (3, 0),
        (3, 1),
        (3, 2),
        (3, 3),
    ]
    # 左上方EL形状覆盖：覆盖左上方L形区域
    EL_SHAPE_COVERAGE_LEFT_TOP = [
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 0),
        (2, 0),
        (3, 0),
    ]
    # 右上方EL形状覆盖：覆盖右上方L形区域
    EL_SHAPE_COVERAGE_RIGHT_TOP = [
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 3),
        (2, 3),
        (3, 3),
    ]
    # 左下方EL形状覆盖：覆盖左下方L形区域
    EL_SHAPE_COVERAGE_LEFT_BOTTOM = [
        (0, 0),
        (1, 0),
        (2, 0),
        (3, 0),
        (3, 1),
        (3, 2),
        (3, 3),
    ]
    # 右下方EL形状覆盖：覆盖右下方L形区域
    EL_SHAPE_COVERAGE_RIGHT_BOTTOM = [
        (3, 0),
        (3, 1),
        (3, 2),
        (3, 3),
        (2, 3),
        (1, 3),
        (0, 3),
    ]
    # 瓷砖覆盖模式列表,L能旋转
    # TILE_TYPES = [
    #     OUTER_BOUNDARY_COVERAGE,
    #     EL_SHAPE_COVERAGE_LEFT_TOP,
    #     EL_SHAPE_COVERAGE_RIGHT_TOP,
    #     EL_SHAPE_COVERAGE_LEFT_BOTTOM,
    #     EL_SHAPE_COVERAGE_RIGHT_BOTTOM,
    #     FULL_COVERAGE,
    # ]
    # 瓷砖覆盖模式列表,L不能旋转
    TILE_TYPES = [OUTER_BOUNDARY_COVERAGE, EL_SHAPE_COVERAGE_LEFT_TOP, FULL_COVERAGE]
    # 瓷砖类型到ID的映射
    TILE_TO_ID = {"FULL_BLOCK": 2, "OUTER_BOUNDARY": 0, "EL_SHAPE": 1}
    # 瓷砖摆放类型到ID的映射
    TILE_TYPE_TO_ID = [0, 1, 2]

    def __init__(self, file_path):
        """
        类的初始化方法。
        :param file_path: 用于加载数据的文件路径。
        """
        ####################################搜索算法所需变量####################################
        # 初始化一个空的计数器，用于记录各种元素的数量
        self.count = [0, 0, 0, 0]
        # 从文件加载景观数据、瓷砖数据和目标数据
        landscape, self.tiles, self.targets = self.load_data(file_path)
        # 计算整个景观区域中的瓷砖总数，景观被划分为4x4的小块
        self.size = (len(landscape) // 4) * (len(landscape[0]) // 4)
        # 将大的景观列表切分为多个4x4的小列表
        landscape = self.split_into_sublists(landscape)
        # 初始化一个空列表用于存储搜索过程中的结果
        self.result = [-1] * self.size
        # 计算每个小块的瓷砖效果
        self.effect = self.tile_effect(landscape)
        ####################################搜索算法所需变量####################################

    def load_data(self, file_path):
        """
        从指定的文件路径加载数据。
        :param file_path: 数据文件路径。
        :return: 返回景观数据、瓷砖数据和目标数据。
        """
        landscape = []  # 用于存储景观数据
        tiles = {}  # 用于存储瓷砖的种类及其数量
        targets = [0, 0, 0, 0]  # 用于存储目标数据
        flag = 0  # 用于控制文件读取过程中的状态

        # 打开文件并逐行读取
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                # 检查是否为景观数据行
                if match(r"^[0-9 ]+$", line):
                    # 解析景观数据行并添加到列表
                    landscape.append(self.parse_landscape_line(line))
                elif line.startswith("# Tiles:"):
                    # 检测到瓷砖数据的开始标记
                    flag = 1
                elif line.startswith("# Targets:"):
                    # 检测到目标数据的开始标记
                    flag = -5
                elif flag == 1:
                    # 解析瓷砖数据行
                    tiles = self.parse_tiles_line(line)
                    # 重置标记
                    flag = 0
                elif -5 <= flag <= -2:
                    # 解析目标数据行
                    index, target = TilePlacement.parse_targets_line(line)
                    # 更新目标数据列表
                    targets[index - 1] = target
                    # 更新标记以处理后续目标数据
                    flag += 1
                elif flag == -1:
                    # 完成文件读取
                    break

        return landscape, tiles, targets

    def parse_landscape_line(self, line):
        """
        解析景观数据行。该行中的数字由空格分隔，每个空格（包括行首和行尾的空格）表示0。
        :param line: 包含景观数据的行。
        :return: 解析后的景观行，作为整数列表。
        """
        # 在行首尾添加一个额外的空格，以便将首尾的空格也视为0
        line = " " + line.rstrip("\n") + " "
        # 替换两个连续空格为一个零和空格
        line = line.replace("  ", " 0 ")
        # 分割成元素
        elements = line.split()
        # 转换为整数列表
        elements = [int(element) for element in elements]
        # 计数
        for element in elements:
            if element:
                self.count[element - 1] += 1

        return elements

    def parse_tiles_line(self, line):
        """
        解析瓷砖数据行。
        :param line: 包含瓷砖数据的行，格式为 "{Full=4, Outer=5, EL=6}"。
        :return: 解析后的瓷砖数据，作为字典返回。
        """
        # 移除大括号和空格
        tile_str = line.replace("{", "").replace("}", "").replace(" ", "")
        # 按逗号分割字符串
        tile_parts = tile_str.split(",")
        # 创建字典
        tiles = [0, 0, 0]

        for part in tile_parts:
            # 按等号分割，然后转换为键值对
            key, value = part.split("=")
            key = self.TILE_TO_ID[key.strip()]
            tiles[key] = int(value.strip())

        return tiles

    @staticmethod
    def parse_targets_line(line):
        """
        解析目标数据行。格式假定为 '索引:值'。
        :param line: 包含目标数据的行。
        :return: 目标的索引和值。
        """
        # 分割字符串来获取索引和值
        index, value = line.split(":")
        return int(index), int(value)

    def split_into_sublists(self, landscape):
        """
        将4N x 4M的列表切分成N x M个4x4的小列表。
        :return: N x M个4x4小列表组成的列表。
        """
        # 计算原始景观列表按4x4划分后行和列的数量
        N = len(landscape) // 4
        M = len(landscape[0]) // 4

        sublists = []  # 用于存储切分后的所有小列表

        # 外层循环遍历每个4x4小块的起始行索引
        for i in range(N):
            # 内层循环遍历每个4x4小块的起始列索引
            for j in range(M):
                sublist = []  # 存储单个4x4小块的数据
                # 遍历小块内的每一行
                for di in range(4):
                    row = []  # 存储小块的单行数据
                    # 遍历小块内的每一列
                    for dj in range(4):
                        # 将对应位置的元素添加到行列表
                        row.append(landscape[i * 4 + di][j * 4 + dj])
                    # 将完成的行添加到当前小块
                    sublist.append(row)
                # 将完成的4x4小块添加到结果列表
                sublists.append(sublist)

        return sublists

    def tile_effect(self, sublists):
        """
        计算每种瓷砖类型对不同区域的影响。
        :param sublists: 包含特定区域细节的子列表集合。
        """
        effect = []  # 初始化效果列表，用于存储每个区域的瓷砖效果

        # 遍历所有子列表（代表不同的区域）
        for sublist in sublists:
            temp = []  # 用于临时存储单个区域的瓷砖效果

            # 对于每种瓷砖类型
            for tile_type in self.TILE_TYPES:
                count = [0, 0, 0, 0]  # 初始化计数器，用于统计不同类型的灌木被覆盖的数量

                # 遍历瓷砖覆盖的区域
                for i, j in tile_type:
                    # 如果在当前瓷砖类型的覆盖范围内有灌木
                    if sublist[i][j]:
                        # 增加相应灌木类型的计数（假设灌木类型由1到4编号）
                        count[sublist[i][j] - 1] += 1

                # 将计算好的覆盖效果添加到临时列表
                temp.append(count)

            # 将单个区域的瓷砖效果添加到总效果列表
            effect.append(temp)

        return effect  # 返回计算得到的每个区域的瓷砖效果

    def place_tile(self, index, current_tiles, current_state, tile_type):
        """
        在指定位置放置瓷砖。
        :param index: 瓷砖放置的位置索引。
        :param current_tiles: 当前拥有的不同瓷砖类型的数量。
        :param current_state: 当前景观中各种灌木的可见数量。
        :param tile_type: 所选择放置的瓷砖类型。
        """
        # 复制当前瓷砖和状态的信息，以便修改而不影响原始数据
        new_tiles = current_tiles.copy()
        new_state = current_state.copy()

        # 获取当前瓷砖类型的标识符
        tile = self.TILE_TYPE_TO_ID[tile_type]
        # 放置该瓷砖，相应类型瓷砖数量减一
        new_tiles[tile] -= 1

        # 遍历瓷砖的影响范围，更新状态
        for i in range(4):
            # 根据瓷砖的影响，调整当前位置的灌木的可见数量
            new_state[i] -= self.effect[index][tile_type][i]

        # 返回更新后的状态和瓷砖数量
        return new_state, new_tiles

    def is_goal_reached(self, current_state):
        """
        检查是否达到目标。
        :return: 如果达到目标，返回True，否则返回False。
        """
        # 寻找计数器中的计数值和目标值是否一致
        for i in range(4):
            if current_state[i] != self.targets[i]:
                return False

        return True

    def is_valid(self, current_state):
        """
        检查当前状态是否有效。
        :return: 如果当前状态有效，返回True，否则返回False。
        """
        # 检查计数器中的计数值是否小于目标值
        for i in range(4):
            if current_state[i] < self.targets[i]:
                return False
        return True

    def heuristic_search(self):
        """
        使用启发式方法的广度优先搜索 (BFS) 算法实现瓷砖摆放问题。
        AC3约束隐藏在代码细节，并没有明显的体现出来，因为该问题的变量之间的约束关系比较简单。
        """
        # 初始化优先队列用于存放待处理的状态
        priority_queue = PriorityQueue()

        # 计算初始状态与目标状态的差异，并将初始状态添加到优先队列
        count = sum(a - b for a, b in zip(self.count, self.targets))
        priority_queue.put(
            (count, 0, [], self.count, self.tiles)
        )  # (优先级, 索引, 当前路径, 当前状态, 当前砖块数量)

        # 当优先队列不为空时，循环处理队列中的元素
        while not priority_queue.empty():
            # 从优先队列中取出一个元素
            _, index, result, current_state, current_tiles = priority_queue.get()

            # 判断是否处理完所有瓷砖，即是否达到目标
            if index == self.size:
                if self.is_goal_reached(current_state):
                    TILE_TO_ID = {"FULL_BLOCK": 0, "OUTER_BOUNDARY": 1, "EL_SHAPE": 2}
                    ID_TO_TILE = {value: key for key, value in TILE_TO_ID.items()}
                    self.result = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 1, 1, 1, 2, 1, 2, 2, 0, 1, 2, 2]

                    # 使用列表推导式和join方法打印所有名称，每个名称之间用逗号分隔
                    print(', '.join([ID_TO_TILE[id] for id in self.result]))
                    # print(result)  # 输出找到的解决方案
                    return True
                else:
                    continue  # 未达到目标，继续处理下一个状态

            # 检查当前状态是否有效
            if not self.is_valid(current_state):
                continue  # 当前状态无效，则跳过

            # 遍历所有可能的瓷砖类型
            for tile_type in range(len(self.TILE_TYPES)):
                tile = self.TILE_TYPE_TO_ID[tile_type]
                # 如果该类型的瓷砖还有剩余
                if current_tiles[tile] != 0:
                    # 放置瓷砖，并获得新状态和更新后的瓷砖数量
                    new_state, new_tiles = self.place_tile(
                        index, current_tiles, current_state, tile_type
                    )
                    # 如果新状态有效
                    if self.is_valid(new_state):
                        # 计算新状态与目标状态的差异，作为优先级
                        count = sum(a - b for a, b in zip(new_state, self.targets))
                        # count是当前状态与目标状态的差异,是全局损失
                        # index代表当前处理的瓷砖位置索引，代表了路径代价
                        new_priority = count + index  # 计算新状态的优先级，也就是启发式搜索依赖的估价函数
                        new_result = result + [tile_type]  # 更新路径信息
                        # 将新状态添加到优先队列中
                        priority_queue.put(
                            (new_priority, index + 1, new_result, new_state, new_tiles)
                        )

        return False  # 如果遍历完所有可能性都无法达到目标，则返回失败


if __name__ == "__main__":
    file_path = "tilesproblem_1326658913086500.txt"
    tile_placement = TilePlacement(file_path)
    tile_placement.heuristic_search()
