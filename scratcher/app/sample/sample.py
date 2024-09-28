import sys
import json
import os
import csv
import glob
from collections import Counter

sys.path.append("../../")

from api import scratch_client
from api import drscratch_analyzer
import prjman
from prjman import ProjectManager
from collections import defaultdict

def extract_ids_from_files(directory):
    """ディレクトリ内のJSONファイルからauthor ID、project ID、remix root IDを抽出
    Args:
        directory (str): JSONファイルが含まれるディレクトリのパス
    Returns:
        author ID、project ID、remix root IDのリスト
    """
    author_ids = []
    project_ids = []
    remix_root_ids = []
    # file_error = 0
    # decode_error = 0
    # program_error = 0
    author_project_count = defaultdict(int)
    author_projects = defaultdict(list)
    file_pattern = os.path.join(directory, '*.json')

    for file_path in glob.glob(file_pattern): ## ファイル網羅
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if isinstance(data, list):
                        for project in data: ## ファイル内の作品1つずつ網羅
                            if (
                                "author" in project and
                                "id" in project and
                                "id" in project["author"] and
                                project["id"] > 276751787 and ## scratch3.0
                                "remix" in project and
                                "root" in project["remix"]
                            ):
                                author_id = project["author"]["id"]
                                project_id = project["id"]
                                remix_root_id = project["remix"]["root"]
                                
                                author_project_count[author_id] += 1
                                author_projects[author_id].append((project_id, remix_root_id))
                    else:
                        print(f"ファイルのデータ形式が予期しない形式: {file_path}")
                        # file_error += 1 
            except json.JSONDecodeError:
                print(f"JSONのデコードエラーが発生: {file_path}")
                # decode_error += 1
            except Exception as e:
                print(f"ファイルの読み込み中にエラーが発生 {file_path}: {e}")
                # program_error += 1

    for author_id, count in author_project_count.items():
        if count >= 20:
            for project_id, remix_root_id in author_projects[author_id]:
                author_ids.append(author_id)
                project_ids.append(project_id)
                remix_root_ids.append(remix_root_id)

    if not author_ids or not project_ids or not remix_root_ids:
        print("指定されたディレクトリには有効なデータがない")

    # print("file_error: " + str(file_error))
    # print("decode_error: " + str(decode_error))
    # print("program_error: " + str(program_error))
    return author_ids, project_ids, remix_root_ids

def extract_metrics(project_ids, author_ids, remix_root_ids):
    """ScratchプロジェクトIDのリストからメトリクスを抽出
    Args:
        project_ids (list): ScratchプロジェクトIDのリスト
        author_ids (list): プロジェクトIDに対応するauthorIDのリスト
        remix_root_ids (list): プロジェクトIDに対応するremixrootIDのリスト
    Returns:
        tuple: ブロック数、ブロック種類数、およびスプライト数のリスト
    """
    blocks_lengths = []
    block_types_lengths = []
    sprites_lengths = []
    # API_error = 0

    i = 0
    while i < len(project_ids):
        try:
            project_id = project_ids[i]
            project_manager = ProjectManager(project_id)
            blocks_lengths.append(project_manager.get_all_blocks_length())
            block_types_lengths.append(project_manager.get_blocks_type_length())
            sprites_lengths.append(project_manager.get_sprites_length())

            # print("blocks count = " + str(blocks_lengths[-1]))
            # print("blockType = " + str(block_types_lengths[-1]))
            # print("sprites count = " + str(sprites_lengths[-1]))
            i += 1
        except IndexError:
            print(f"プロジェクトID {project_id} の処理中にインデックスエラーが発生　リストから削除")
            del project_ids[i]
            del author_ids[i]
            del remix_root_ids[i]
            # API_error += 1
            i += 1
        except Exception as e:
            print(f"プロジェクトID {project_id} の処理中にエラーが発生　リストから削除: {e}")
            del project_ids[i]
            del author_ids[i]
            del remix_root_ids[i]
            # API_error += 1
            i += 1

    # print("API_eroor = " + str(API_error))
    return blocks_lengths.copy(), block_types_lengths.copy(), sprites_lengths.copy()

def save_project_json(project_ids, directory):
    """プロジェクトJSONをファイルに保存
    Args:
        project_id (int): プロジェクトID
        directory (str): 保存先ディレクトリのパス
    """
    # program_error = 0

    i = 0
    while i < len(project_ids):
        project_id = project_ids[i]
        project_json = scratch_client.get_project(project_id)
        if project_json:
            file_path = os.path.join(directory, f"{project_id}.json")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(project_json, f, ensure_ascii=False, indent=4)
                print(f"プロジェクトID {project_id} のJSONを {file_path} に保存")
                i += 1
            except Exception as e:
                print(f"プロジェクトID {project_id} のJSONを保存中にエラー発生")
                print(e)
                i += 1
                # program_error += 1
        else:
            print(f"プロジェクトID {project_id} のJSONを取得不可")
            i += 1
            # project_error += 1
    # print("program_error = " + str(program_error))
    # print("project_error = " + str(project_error))
        
def save_ct_score_file(project_ids, json_directory, ct_directory):
    """プロジェクトCTスコアをファイルに保存
    Args:
        project_id (int): プロジェクトID
        json_directory (str): 作品ディレクトリのパス
        ct_directory (str): CTスコアの保存先ディレクトリのパス
    """
    i = 0
    while i < len(project_ids):
        try:
            project_id = project_ids[i]
            mastery = drscratch_analyzer.Mastery()
            mastery.process(os.path.join(json_directory, f"{project_id}.json"))
            mastery.analyze(os.path.join(ct_directory, f"{project_id}＿ct.json"))
            i += 1
        except Exception as e:
            print(f"プロジェクトID {project_id} のct_JSONを保存中にエラー発生")
            print(e)
            i += 1


def count_files_in_directory(directory, pattern="*"):
    """指定されたディレクトリ内のファイル数をカウント
    Args:
        directory (str): ディレクトリのパス
        pattern (str): ファイルパターン（デフォルトは全ファイルを対象）
    Returns:
        int: ディレクトリ内のファイル数
    """
    file_pattern = os.path.join(directory, pattern)
    files = glob.glob(file_pattern)
    return len(files)

def process_specific_json_files(folder_path, project_ids):
    # スコアを作品IDごとに辞書に格納
    ctscore_result = {
        "Logic": {},
        "FlowControl": {},
        "Synchronization": {},
        "Abstraction": {},
        "DataRepresentation": {},
        "UserInteractivity": {},
        "Parallelism": {},
        "CTScore": {}
    }
    i = 0
    
    # 指定された作品IDリストに基づき、それぞれの "作品ID_ct.json" ファイルを読み込む
    for project_id in project_ids:
        file_name = f'{project_id}_ct.json'  # 作品IDに基づいたファイル名を生成
        file_path = os.path.join(folder_path, file_name)
        
        # ファイルが存在するか確認
        if os.path.exists(file_path):
            # JSONファイルを読み込む
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # 作品IDごとに処理
            if str(project_id) in data:
                values = data[i]
                
                # それぞれのスコアを作品IDに紐づけて保存
                ctscore_result["Logic"][i] = values["Logic"]["MaxScore"]
                ctscore_result["FlowControl"][i] = values["FlowControl"]["MaxScore"]
                ctscore_result["Synchronization"][i] = values["Synchronization"]["MaxScore"]
                ctscore_result["Abstraction"][i] = values["Abstraction"]["MaxScore"]
                ctscore_result["DataRepresentation"][i] = values["DataRepresentation"]["MaxScore"]
                ctscore_result["UserInteractivity"][i] = values["UserInteractivity"]["MaxScore"]
                ctscore_result["Parallelism"][i] = values["Parallelism"]["MaxScore"]
                ctscore_result["CTScore"][i] = values.get("CTScore", 0)  # CTScoreを取得、無ければ0
                i += 1
        else:
            print(f"File for {project_id} not found.")
            i += 1
    
    return ctscore_result


def save_to_csv(author_ids, project_ids, remix_root_ids, blocks_lengths, block_types_lengths, sprites_lengths, ct_score_result, csv_file_path):
    # CSVファイルの保存先ディレクトリを確認・作成
    csv_directory = os.path.dirname(csv_file_path)
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)
    
    # CSVファイルにデータを書き込む
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # ヘッダーを記入
        writer.writerow(["作者ID", "作品ID", "リミックス元ID", "ブロック数", "ブロックの種類数", "スプライト数", "論理", "制御フロー", "同期", "抽象化", "データ表現", "ユーザとの対話性", "並列処理", "CTスコア"])
        
        # 各データをまとめて書き込む
        for i in range(len(project_ids)):
            writer.writerow([
                author_ids[i],                                # 作者ID
                project_ids[i],                               # 作品ID
                remix_root_ids[i],                            # リミックス元ID
                blocks_lengths[i],                            # ブロック数
                block_types_lengths[i],                       # ブロックの種類数
                sprites_lengths[i],                           # スプライト数
                ct_score_result["Logic"][i],                  # 論理
                ct_score_result["FlowControl"][i],            # 制御フロー
                ct_score_result["Synchronization"][i],        # 同期
                ct_score_result["Abstraction"][i],            # 抽象化
                ct_score_result["DataRepresentation"][i],     # データ表現
                ct_score_result["UserInteractivity"][i],      # ユーザとの対話性
                ct_score_result["Parallelism"][i],            # 並列処理
                ct_score_result["CTScore"][i]                 # CTスコア
            ])

# 使用
# 作者IDと作品IDとリミックス元ID取得
directory = '../../dataset/projects'
author_ids, project_ids, remix_root_ids = extract_ids_from_files(directory)
print(len(project_ids))

# ブロック数，ブロックの種類数，スプライト数取得
blocks_lengths, block_types_lengths, sprites_lengths = extract_metrics(project_ids, author_ids, remix_root_ids)

# 作品をjsonファイルに保存
json_directory = '../../dataset/projects_json'
remix_json_directory = '../../dataset/projects_remix_json'
# 作品保存
save_project_json(project_ids, json_directory)
# リミックス作品の保存
save_project_json(remix_root_ids, remix_json_directory)

# 作品のCT_SCOREを取得し，ファイルに保存
ct_directory = '../../dataset/projects_ct'
remix_ct_directory = '../../dataset/projects_remix_ct'

# 作品のCTスコアファイルの保存
save_ct_score_file(remix_root_ids, json_directory, ct_directory)
# リミックス作品のCTスコアファイルの保存
save_ct_score_file(remix_root_ids, remix_json_directory, remix_ct_directory)

ct_score_result = process_specific_json_files(ct_directory, project_ids)
remix_ct_score_result = process_specific_json_files(remix_ct_directory, remix_root_ids)

csv_file_path = '../../dataset'

# csv ni hozon
save_to_csv(author_ids, project_ids, remix_root_ids, blocks_lengths, block_types_lengths, sprites_lengths, ct_score_result, csv_file_path)

# ファイル数確認
# print("all_projects: " + str(count_files_in_directory(save_directory)))
# print("ctscore_projects: " + str(count_files_in_directory(ct_directory)))
# メトリクス抽出
# def extract_metrics(project_ids):
#     blocks_lengths = []
#     block_types_lengths = []
#     sprites_lengths = []

#     for project_id in project_ids:
#         project_manager = ProjectManager(project_id)
#         blocks_lengths.append(project_manager.get_all_blocks_length())
#         block_types_lengths.append(project_manager.get_blocks_type_length())
#         sprites_lengths.append(project_manager.get_sprites_length())
#         print("blocks count = " + str(blocks_lengths[-1]))
#         print("blockType =" + str(block_types_lengths[-1]))
#         print("sprites count = " + str(sprites_lengths[-1]))
#     return blocks_lengths.copy(), block_types_lengths.copy(), sprites_lengths.copy()

# # csvに保存
# def save_to_csv(author_ids, project_ids, blocks_lengths, block_types_lengths, sprites_lengths, ct_score, output_file):
#     with open(output_file, 'w', newline='') as csvfile:
#         csvwriter = csv.writer(csvfile)
#         csvwriter.writerow(['Author_ID', 'Project_ID', 'remix_root_ID', 'Blocks_length', 'BlockType_length', 'Sprites_length'])  # ヘッダー行を書き込む
#         for author_id, project_id, remix_root_id, blocks_length, block_types_length, sprites_length in zip(author_ids, project_ids, remix_root_ids, blocks_lengths, block_types_lengths, sprites_lengths):
#             csvwriter.writerow([author_id, project_id, remix_root_id, blocks_length, block_types_length, sprites_length])

#     # # # CTスコア合計点数を取得
#     # mastery = drscratch_analyzer.Mastery()
#     # mastery.process("../../sample_json/797975999.json")
#     # mastery.analyze("./out.json")

#     with open('out.json', 'r', encoding='utf-8') as file:
#         data = json.load(file)
#     # # CTScoreの値をint型の変数に格納
#     ct_score = data["CTScore"]

    # # 出力
    # print("blocks count = " + str(blocks_length))
    # print("blockType =" + str(blockType_length))
    # print("sprites count = " + str(sprites_length))
    # print("CTscore = " + str(ct_score))


# プロジェクトの大元のリミックス元とそこから何回派生しているか
# PM = scratch_client.get_remix_parent(sample_id2)
# if PM:
#     # print("parent_id: " + str(PM["parent_id"]))
#     # print("deep: " + str(PM["deep"]))
#     with open('data/test_PM_' + str(sample_id2) + '.json', 'w') as f:
#         json.dump(str(PM), f, indent=2)

# print("metaData: " + str(MD))
# jsonファイルに出力
# with open('data/test_MD_' + str(sample_id2) + '.json', 'w') as f:
#     json.dump(str(MD), f, indent=2)

# リミックスしていたら1個前のプロジェクトのID出力
# parentが1個前
# if MD["remix"]["parent"]:
#     # print("parent_id: " + str(MD["remix"]["parent"]))
#     with open('data/test_MD_' + str(sample_id2) + '.json', 'w') as f:
#         json.dump(str(MD["remix"]["parent"]), f, indent=2)