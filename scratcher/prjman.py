import sys

sys.path.append("../")

import csv
from utils import json_to_file
from api import scratch_client
from tools import Sorter, Tracker
from converter import AstConverter


class ProjectManager:

    """Scratch作品を管理するためのクラス

    Args:
        __ID (int): 現在管理しているScratch作品のID
        __project (dictionary): 現在管理しているScratch作品全体のプログラム
        __start_splites (boolean): 先頭のスプライトがステージかどうかの判定
        __sprites (dictionary): 現在管理しているScratch作品のスプライトのプログラム
        __opcodes (dictionary): opcodeをリストで取得
        __blocks (dictionary): 現在管理しているScratch作品のスプライトに含まれるスプライトのブロック
        __description（str）: 現在管理しているScratch作品の使用方法
    """

    def __init__(self, id):
        """ProjectManagerの初期化

        Args:
            id (int): 対象とするScratch作品のID
        """

        try:
            self.__ID = id
            self.__project = scratch_client.get_project(self.__ID)
            self.__head_blocks = self.__project["targets"][1]["blocks"]
            self.__start_splites = self.__project["targets"][0]["isStage"]
            try:
                self.__sprites = self.__project["targets"]
            except Exception as e:
                print(e)
            # self.__sprites = self.__project["targets"]
            # print(self.__sprites)
            self.__blocks = [block_data for block_data in self.__project["targets"][1]["blocks"].values()]
            self.__opcodes = []
            for block_opcode in self.__blocks:
                self.__opcodes.append(block_opcode['opcode'])
            # print(self.__opcodes)
            # self.__blocks = list(map(self.__format_blocks, self.__project["targets"]))
            self.__description = scratch_client.get_description(self.__ID)
        except Exception as e:
            print(e)

    def get_id(self):
        """管理しているScratch作品のIDを取得

        Returns:
            int: 保持しているScratch作品のIDを返す
        """

        return self.__ID

    def get_project(self):
        """現在管理している作品のプログラムを取得

        Returns:
            dictionary: 現在管理している作品のプログラムを返す
        """
        return self.__project

    def get_head_blocks(self):
        """現在管理しているスプライトに含まれるスプライトのブロックを取得

        Returns:
            dictionary: 現在管理しているスプライトに含まれるスプライトのブロックを返す
        """
        return self.__head_blocks

    def get_blocks(self):
        """現在管理しているスプライトに含まれるスプライトのブロックを取得

        Returns:
            dictionary: 現在管理しているスプライトに含まれるスプライトのブロックを返す
        """
        return self.__blocks

    def get_description(self):
        """現在管理しているScratch作品の使用方法を取得

        Returns:
            str: 現在管理しているScratch作品の使用方法を返す
        """
        return self.__description

    def get_blocks_length(self):
        """現在管理しているスプライトに含まれるスプライトのブロックの数を取得

        Returns:
            int: 現在管理しているスプライトに含まれるスプライトのブロックの数を返す
        """

        return len(self.__blocks)
    
    # def get_all_blocks_length(self):
    #     """現在管理している全スプライトに含まれるブロック数の合計を取得

    #     Returns:
    #         int: 現在管理している全スプライトに含まれるブロック数の合計を返す
    #     """
        
    #     length = 0
    #     for target in self.__sprites:
    #         # if isinstance(target["blocks"], list):
    #         #     length += len(target["blocks"])
    #         length += len(self.__blocks)

    #     return length

    def get_all_blocks_length(self):
        """現在管理している全スプライトに含まれるブロック数の合計を取得

        Returns:
            int: 現在管理している全スプライトに含まれるブロック数の合計を返す
        """
        
        length = 0
        for target in self.__sprites:
            # 各スプライトの blocks が辞書型であるかを確認し、そのキー数を合計
            if isinstance(target["blocks"], dict):
                length += len(target["blocks"])
            else:
                print(f"スプライト {target['name']} に 'blocks' が存在しないか、適切な形式ではありません")

        return length

    
    def get_sprites_length(self):
        """作品のスプライト数を取得
        
        Retuens:
            int: 作品のスプライト数を返す
        """

        return len(self.__sprites)
    
    def get_blocks_type_length(self):
        """作品のブロックの種類数を取得
        
        Retuens:
            int: ブロックの種類数を返す
        """

        # # opcodeの種類数を取得する
        unique_opcodes = set(self.__opcodes)
        opcode_count = len(unique_opcodes)
        return opcode_count
    

    def get_ast(self, path=""):
        """現在管理しているブロックをASTに変換して取得

        Args:
            path (str, optional): ASTをファイルに保存する際のパス. 保存しない場合は指定なしでよい.

        Returns:
            dictionary: 現在管理しているブロックをASTに変換したJSONを返す
        """

        ast_conv = AstConverter(self.__project)
        result = ast_conv.get_ast(path)
        return result

    def get_sorted_blocks(self, dir_path=None):
        """現在管理しているブロックを命令処理順にソートして取得

        Args:
            dir_path (str, optional): ソートしたブロックをファイルに保存する場合のディレクトリのパス. 保存しない場合は指定なしでよい.

        Returns:
            Dataframe: 現在管理しているブロックを命令処理順にソートしたDataframeを返す
        """

        sorter = Sorter(self.__project)
        if dir_path:
            sorter.sort_blocks()
            sorter.to_csv(dir_path)
            return
        else:
            return sorter.sort_blocks()

    def get_coordinate(self, dir_path=None):
        """現在管理しているスプライトの移動軌跡を算出し，座標データを取得

        Args:
            dir_path (str, optional): 座標データをファイルに保存する場合のディレクトリのパス. 保存しない場合は指定なしでよい.

        Returns:
            DAtaframe: 現在管理しているスプライトの移動軌跡を算出し，座標データを返す
        """

        tracker = Tracker(self.get_sorted_blocks())
        if dir_path:
            tracker.get_coordinate()
            tracker.to_csv(dir_path)
            return
        else:
            return tracker.get_coordinate()

    def to_json(self, dir_path=".", type="project"):
        """プログラムのJsonファイルを保存

        Args:
            dir_path (str, optional): jsonファイルを保存する際のディレクトリのパス. 指定なしだと直下に保存.
            type (str, optional): 保存するJsonの粒度を指定．project or sprite or blocks. デフォルトはproject.
        """

        match (type):
            case "project":
                json_to_file(self.__project, f"{dir_path}/{self.__ID}.json")
            case "sprite":
                json_to_file(self.__sprites, f"{dir_path}/{self.__ID}_sprite.json")
            case "blocks":
                json_to_file(self.__blocks, f"{dir_path}/{self.__ID}_blocks.json")

    def is_dataset(self, ava_path="utils/filter/filter.csv"):
        """フィルタリング用関数

        Args:
            ava_path (str, optional): フィルタリング用CSVのパス. Defaults to "utils/filter/filter.csv".

        Returns:
            boolean: フィルタリングに引っかかったか否かを返す．True -> 引っかかっていない　False -> 引っかかった
        """
        ava_blocks = []
        # フィルタリング用CSVの読み込み
        with open(ava_path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row in reader:
                ava_blocks.append(row)

        isDataset = self.__filter_json(ava_blocks)
        return isDataset

    # Private関数

    # フィルタリング
    def __filter_json(self, ava_blocks):
        for k in self.__blocks:
            for block, ava in ava_blocks:
                if self.__blocks[k]["opcode"] == block and int(ava) == 0:
                    return False
        return True

    def __format_blocks(target):
        return {"isStage": target["isStage"], "blocks": target["blocks"]}
