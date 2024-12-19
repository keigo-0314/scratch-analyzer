import sys
import json
import os
import csv
import glob
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns # type: ignore
from matplotlib import rcParams

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
            except json.JSONDecodeError:
                print(f"JSONのデコードエラーが発生: {file_path}")
            except Exception as e:
                print(f"ファイルの読み込み中にエラーが発生 {file_path}: {e}")

    for author_id, count in author_project_count.items():
        if count >= 20:
            for project_id, remix_root_id in author_projects[author_id]:
                author_ids.append(author_id)
                project_ids.append(project_id)
                remix_root_ids.append(remix_root_id)

    if not author_ids or not project_ids or not remix_root_ids:
        print("指定されたディレクトリには有効なデータがない")
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

    i = 0
    while i < len(project_ids):
        try:
            project_id = project_ids[i]
            project_manager = ProjectManager(project_id)
            blocks_lengths.append(project_manager.get_all_blocks_length())
            block_types_lengths.append(project_manager.get_blocks_type_length())
            sprites_lengths.append(project_manager.get_sprites_length())

            print("blocks count = " + str(blocks_lengths[i]))
            print("blockType = " + str(block_types_lengths[-1]))
            print("sprites count = " + str(sprites_lengths[-1]))
            i += 1
        except IndexError:
            print(f"プロジェクトID {project_id} の処理中にインデックスエラーが発生　リストから削除")
            project_ids.pop(i)
            author_ids.pop(i)
            remix_root_ids.pop(i)
        except Exception as e:
            print(f"プロジェクトID {project_id} の処理中にエラーが発生　リストから削除: {e}")
            project_ids.pop(i)
            author_ids.pop(i)
            remix_root_ids.pop(i)

    return blocks_lengths.copy(), block_types_lengths.copy(), sprites_lengths.copy()

def save_project_json(project_ids, directory):
    """プロジェクトJSONをファイルに保存
    Args:
        project_id (int): プロジェクトID
        directory (str): 保存先ディレクトリのパス
    """

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
                project_ids.pop(i)
                author_ids.pop(i)
                remix_root_ids.pop(i)
                blocks_lengths.pop(i)
                block_types_lengths.pop(i)
                sprites_lengths.pop(i)
        else:
            print(f"プロジェクトID {project_id} のJSONを取得不可")
            project_ids.pop(i)
            author_ids.pop(i)
            remix_root_ids.pop(i)
            blocks_lengths.pop(i)
            block_types_lengths.pop(i)
            sprites_lengths.pop(i)
        
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
            mastery.analyze(os.path.join(ct_directory, f"{project_id}_ct.json"))
            i += 1
        except Exception as e:
            print(f"プロジェクトID {project_id} のct_JSONを保存中にエラー発生")
            project_ids.pop(i)
            author_ids.pop(i)
            remix_root_ids.pop(i)
            blocks_lengths.pop(i)
            block_types_lengths.pop(i)
            sprites_lengths.pop(i)
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

def make_list_CTscore(ct_directory, project_ids):
    # スコアを作品IDごとにリストに格納
    Logic = []
    FlowControl = []
    Synchronization = []
    Abstraction = []
    DataRepresentation = []
    UserInteractivity = []
    Parallelism = []
    CTScore = []
    
    # 指定された作品IDリストに基づき、それぞれの "作品ID_ct.json" ファイルを読み込む
    for project_id in project_ids:
        file_name = f'{project_id}_ct.json'  # 作品IDに基づいたファイル名を生成
        file_path = os.path.join(ct_directory, file_name)
        
        # ファイルが存在するか確認
        if os.path.exists(file_path):
            # JSONファイルを読み込む
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            # それぞれのスコアをリストに追加
            Logic.append(data["Logic"]["MaxScore"])
            FlowControl.append(data["FlowControl"]["MaxScore"])
            Synchronization.append(data["Synchronization"]["MaxScore"])
            Abstraction.append(data["Abstraction"]["MaxScore"])
            DataRepresentation.append(data["DataRepresentation"]["MaxScore"])
            UserInteractivity.append(data["UserInteractivity"]["MaxScore"])
            Parallelism.append(data["Parallelism"]["MaxScore"])
            CTScore.append(data.get("CTScore", 0))  # CTScoreを取得、無ければ0

            ct_score_value = data.get("CTScore", 0)
            # print(f"Project ID: {project_id}, CTScore: {ct_score_value}")
        else:
            print(f"File for {project_id} not found.")
    
    return Logic, FlowControl, Synchronization, Abstraction, DataRepresentation, UserInteractivity, Parallelism, CTScore

def saveProjects(project_ids, directory):## 作品保存
    """作品IDのリストから作品保存をする"""
    # 保存先ディレクトリの確認・作成
    if not os.path.exists(directory):
        os.makedirs(directory)

    i = 0
    while i < len(project_ids):
        project_id = project_ids[i]

        # プロジェクトJSONデータの取得
        project_json = scratch_client.get_project(project_id)
        if project_json:
            # JSONファイルのパスを設定して保存
            file_path = os.path.join(directory, f"{project_id}.json")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(project_json, f, ensure_ascii=False, indent=4)
                print(f"プロジェクトID {project_id} のJSONを {file_path} に保存しました")
                i += 1
            except Exception as e:
                print(f"プロジェクトID {project_id} の保存中にエラーが発生しました: {e}")
                project_ids.pop(i)  # JSONが取得できない場合、IDをリストから削除
        else:
            print(f"プロジェクトID {project_id} のJSONを保存できませんでした")
            project_ids.pop(i)  # JSONが取得できない場合、IDをリストから削除
        
def saveCtscore(project_ids, json_directory, ct_directory):## CTscoreを保存
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
            mastery.analyze(os.path.join(ct_directory, f"{project_id}_ct.json"))
            i += 1
        except Exception as e:
            print(f"プロジェクトID {project_id} のct_JSONを保存中にエラー発生")
            project_ids.pop(i)
            print(e)

def save_to_csv(author_ids, project_ids, remix_root_ids, blocks_lengths, block_types_lengths, sprites_lengths, Logic, FlowControl, Synchronization, Abstraction, DataRepresentation, UserInteractivity, Parallelism, CTScore, csv_file_path):
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
                author_ids[i],             # 作者ID
                project_ids[i],            # 作品ID
                remix_root_ids[i],         # リミックス元ID
                blocks_lengths[i],         # ブロック数
                block_types_lengths[i],    # ブロックの種類数
                sprites_lengths[i],        # スプライト数
                Logic[i],                  # 論理
                FlowControl[i],            # 制御フロー
                Synchronization[i],        # 同期
                Abstraction[i],            # 抽象化
                DataRepresentation[i],     # データ表現
                UserInteractivity[i],      # ユーザとの対話性
                Parallelism[i],            # 並列処理
                CTScore[i]                 # CTスコア
            ])

def plot_boxplot_from_csv(csv_file_path, columns, output_image_path=None):
    """
    CSVファイルから指定された列の箱ひげ図を作成して表示する
    
    Args:
        csv_file_path (str): CSVファイルのパス
        columns (list): 箱ひげ図を描画する対象の列名リスト
        output_image_path (str): 保存先の画像パス（オプション）
    """
    # CSVファイルを読み込む
    data = pd.read_csv(csv_file_path)
    
    # 箱ひげ図を描画
    plt.figure(figsize=(2, 6))  # グラフのサイズを指定
    sns.boxplot(data=data[columns], palette=["#ADD8E6"] * len(columns))
    # plt.ylim(0, data[columns].max().max())  # 各列の最大値を取得し、それに基づいて範囲を設定
    # グラフのタイトルとラベルを設定
    plt.title('Boxplot of Selected Columns', fontsize=16)
    plt.xlabel('Metrics', fontsize=12)
    plt.ylabel('Values', fontsize=12)
    
    # グラフを表示
    plt.tight_layout()
    if output_image_path:
        plt.savefig(output_image_path)  # 画像として保存（任意）
    plt.show()

def makeHistgram(csv_file_path, save_path):## ヒストグラム作成
    # データの読み込み
    df = pd.read_csv(csv_file_path)
    # 項目ごとに条件設定
    detailed_columns = ["ブロック数", "ブロックの種類数", "スプライト数"]
    simple_columns = ["論理", "制御フロー", "同期", "抽象化", 
                    "データ表現", "ユーザとの対話性", "並列処理"]
    score_column = "CTスコア"
    # グラフの作成
    fig, axes = plt.subplots(len(detailed_columns) + len(simple_columns) + 1, 1, figsize=(8, 40))
    fig.tight_layout(pad=3.0)
    # 0～3点の1刻みヒストグラム
    for j, column in enumerate(simple_columns):
        ax = axes[len(detailed_columns) + j]
        ax.hist(df[column], bins=range(0, 5), color='lightgreen', edgecolor='black', align='left')
        ax.set_xticks(range(0, 4))
        ax.set_ylim(0, 25000)  # 縦軸の最大値を設定
    # 0～21点の1刻みヒストグラム（"CTスコア"）
    axes[-1].hist(df[score_column], bins=range(0, 23), color='salmon', edgecolor='black', align='left')
    axes[-1].set_xticks(range(0, 22))
    # グラフの保存
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"ヒストグラムが {save_path} に保存されました。")
    # 必要に応じてグラフを表示
    plt.show()

def filtered_csv_remix(csv_file_path, save_path): ## リミックス作品だけをcsvに保存
    # データ読み込み
    df = pd.read_csv(csv_file_path)
    # リミックス元IDがある作品だけをフィルタリング
    df["リミックス元ID"] = df["リミックス元ID"].astype(str)
    filtered_df = df[(df["リミックス元ID"] != "nan") & (df["リミックス元ID"].str.strip() != "")]
    # フィルタリングしたデータをCSVに保存
    filtered_df.to_csv(save_path, index=False, encoding="utf-8-sig")
    # デバッグ出力
    print(f"リミックス元IDがある作品を保存しました: {save_path}")

def saveCSV(project_ids, ct_directory, csv_file_path):## csvにCTスコア保存
    # スコアを作品IDごとにリストに格納
    Logic = []
    FlowControl = []
    Synchronization = []
    Abstraction = []
    DataRepresentation = []
    UserInteractivity = []
    Parallelism = []
    CTScore = []
    # 指定された作品IDリストに基づき、それぞれの "作品ID_ct.json" ファイルを読み込む
    for project_id in project_ids:
        file_name = f'{project_id}_ct.json'  # 作品IDに基づいたファイル名を生成
        file_path = os.path.join(ct_directory, file_name)
        # ファイルが存在するか確認
        if os.path.exists(file_path):
            # JSONファイルを読み込む
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            # それぞれのスコアをリストに追加
            Logic.append(data["Logic"]["MaxScore"])
            FlowControl.append(data["FlowControl"]["MaxScore"])
            Synchronization.append(data["Synchronization"]["MaxScore"])
            Abstraction.append(data["Abstraction"]["MaxScore"])
            DataRepresentation.append(data["DataRepresentation"]["MaxScore"])
            UserInteractivity.append(data["UserInteractivity"]["MaxScore"])
            Parallelism.append(data["Parallelism"]["MaxScore"])
            CTScore.append(data.get("CTScore", 0))  # CTScoreを取得、無ければ0
            ct_score_value = data.get("CTScore", 0)
            # print(f"Project ID: {project_id}, CTScore: {ct_score_value}")
        else:
            print(f"File for {project_id} not found.")
    # CSVファイルの保存先ディレクトリを確認・作成
    csv_directory = os.path.dirname(csv_file_path)
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)
    # CSVファイルにデータを書き込む
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # ヘッダーを記入
        writer.writerow(["作品ID", "論理", "制御フロー", "同期", "抽象化", "データ表現", "ユーザとの対話性", "並列処理", "CTスコア"])
        # 各データをまとめて書き込む
        for i in range(len(project_ids)):
            writer.writerow([
                project_ids[i],            # 作品ID
                Logic[i],                  # 論理
                FlowControl[i],            # 制御フロー
                Synchronization[i],        # 同期
                Abstraction[i],            # 抽象化
                DataRepresentation[i],     # データ表現
                UserInteractivity[i],      # ユーザとの対話性
                Parallelism[i],            # 並列処理
                CTScore[i]                 # CTスコア
            ])


# 使用
# 作者IDと作品IDとリミックス元ID取得
directory = '../../dataset/16000data/projects'
author_ids, project_ids, remix_root_ids = extract_ids_from_files(directory)
print("1:" + str(len(project_ids)))

# ブロック数，ブロックの種類数，スプライト数取得
blocks_lengths, block_types_lengths, sprites_lengths = extract_metrics(project_ids, author_ids, remix_root_ids)
print("2:" + str(len(project_ids)))
print("2:" + str(len(blocks_lengths)))

# 作品をjsonファイルに保存
json_directory = '../../dataset/16000data/projects_json'
remix_json_directory = '../../dataset/16000data/projects_remix_json'

# 作品保存
save_project_json(project_ids, json_directory)
print("3:" + str(len(project_ids)))
print("3:" + str(len(blocks_lengths)))

# リミックス作品の保存
# save_project_json(remix_root_ids, remix_json_directory)
# print("4:" + str(len(project_ids)))
# print(len((remix_root_ids)))

# 作品のCT_SCOREを取得し，ファイルに保存
ct_directory = '../../dataset/16000data/projects_ct'
# remix_ct_directory = '../../dataset/16000data/projects_remix_ct'

# 作品のCTスコアファイルの保存
save_ct_score_file(project_ids, json_directory, ct_directory)
print("5:" + str(len(project_ids)))
print("5:" + str(len(blocks_lengths)))

# リミックス作品のCTスコアファイルの保存
# save_ct_score_file(remix_root_ids, remix_json_directory, remix_ct_directory)
# print("6:" + str(len(project_ids)))
# print(len((remix_root_ids)))

# スコアをリスト化
Logic, FlowControl, Synchronization, Abstraction, DataRepresentation, UserInteractivity, Parallelism, CTScore = make_list_CTscore(ct_directory, project_ids)
print("CTscore :" + str(len((CTScore))))
print("7:" + str(len(project_ids)))
print("7:" + str(len(blocks_lengths)))

# csvに保存
csv_file_path = '../../dataset/16000data/data.csv'
save_to_csv(author_ids, project_ids, remix_root_ids, blocks_lengths, block_types_lengths, sprites_lengths, Logic, FlowControl, Synchronization, Abstraction, DataRepresentation, UserInteractivity, Parallelism, CTScore, csv_file_path)

##filecount
# directory = '../../dataset/16000data/projects'
# print(count_files_in_directory(directory))

## 箱ひげ図の保存
# plot_boxplot_from_csv(csv_file_path, "ブロック数", '../../dataset/hakohigezu/countblock.png')
# plot_boxplot_from_csv(csv_file_path, "ブロックの種類数", '../../dataset/hakohigezu/typeblock.png')
# plot_boxplot_from_csv(csv_file_path, "スプライト数", '../../dataset/hakohigezu/sprite.png')
# plot_boxplot_from_csv(csv_file_path, "論理", '../../dataset/hakohigezu/ronri.png')
# plot_boxplot_from_csv(csv_file_path, "制御フロー", '../../dataset/hakohigezu/seigyohuro-.png')
# plot_boxplot_from_csv(csv_file_path, "同期", '../../dataset/hakohigezu/douki.png')
# plot_boxplot_from_csv(csv_file_path, "抽象化", '../../dataset/hakohigezu/tyuusyouka.png')
# plot_boxplot_from_csv(csv_file_path, "データ表現", '../../dataset/hakohigezu/de-tahyougen.png')
# plot_boxplot_from_csv(csv_file_path, "ユーザとの対話性", '../../dataset/hakohigezu/yu-zataiwasei.png')
# plot_boxplot_from_csv(csv_file_path, "並列処理", '../../dataset/hakohigezu/heiretusyori.png')
# plot_boxplot_from_csv(csv_file_path, "CTスコア", '../../dataset/hakohigezu/CTscore.png')

## リミックス元作品の保存
# df = pd.read_csv('../../dataset/data2.csv', dtype={"リミックス元ID": str})
# project_ids = df["リミックス元ID"].dropna().unique().tolist()
# directory = '../../dataset/remix_json'
# saveProjects(project_ids, directory)

## csvデータを読み込む際に,リミックス元ID列を文字列型として指定
# df = pd.read_csv('../../dataset/data2.csv', dtype={"リミックス元ID": str})
## リミックス元ID列から重複を削除し、NaN（空白セル）を除去してリストに変換
# remix_ids = df["リミックス元ID"].dropna().unique().tolist()
## リストを表示
# print(remix_ids)
# json_directory = '../../dataset/remix_json'
# saveProjects(remix_ids, json_directory)
# ct_directory = ('../../dataset/remix_ct')
# save_ct_score_file(remix_ids, json_directory, ct_directory)

## リミックス元IDの出現回数をカウントし、多い順にソート
# remix_counts = df["リミックス元ID"].value_counts().reset_index()
# remix_counts.columns = ["リミックス元ID", "出現回数"]
## 出現回数が多い順に並べたデータを新しいCSVファイルに保存
# remix_counts.to_csv("remix_counts.csv", index=False)

## ブロック数，ブロックの種類数，スプライト数を出力させる
# mastery = drscratch_analyzer.Mastery()
# mastery.process(file_path)
# mastery.analyze(os.path.join(directory, f"{project_id}_ct.json"))
# project_manager = ProjectManager(project_id)
# print(project_manager.get_all_blocks_length())
# print(project_manager.get_blocks_type_length())
# print(project_manager.get_sprites_length())

## 対象の作品をリミックスした作品をcsvから抽出してまとめる
# CSVファイルの読み込み
# df = pd.read_csv('../../dataset/data.csv', dtype={"リミックス元ID": str})
# リミックス元IDが 'remixNo' のものだけをフィルタリング
# filtered_df = df[df["リミックス元ID"] == "536199882"]
# 抽出したデータを新しいCSVファイルに保存
# filtered_df.to_csv("536199882_data.csv", index=False)
# print("リミックス元IDがremixNoのデータを'remixNo_data.csv'に保存しました。")

# # CSVファイルのパス
# csv_file_path = "../../dataset/8000data/filtered_remix_data.csv"
# # グラフの保存先
# save_path = "../../dataset/8000data/remixhistograms.png"
# makeHistgram(csv_file_path, save_path)

# リミックス元作品の保存
# df = pd.read_csv('../../dataset/8000data/filtered_remix_data.csv', dtype={"リミックス元ID": str})
# project_ids = df["リミックス元ID"].dropna().unique().tolist()
# project_ids = [project_id.rstrip('.0') if isinstance(project_id, str) and project_id.endswith('.0') else project_id for project_id in project_ids]
# save_directory = ('../../dataset/8000data/remix_parent')
# ct_directory = ('../../dataset/8000data/remix_parent_ct')
# csv_file_path = ("../../dataset/8000data/remixparent_data.csv")
# save_directory = ('../../dataset/8000data/remix_parent_histgrams')
# saveProjects(project_ids, save_directory)
# saveCtscore(project_ids, save_directory, ct_directory)
# saveCSV(project_ids, ct_directory, csv_file_path)

# makeHistgram(csv_file_path, save_directory)


# リミックス元IDが何件あるかを調べる
# csv_file_path = "../../dataset/8000data/filtered_remix_data.csv"  # CSVファイルのパスを指定してください
# df = pd.read_csv(csv_file_path, dtype={"リミックス元ID": str})  # リミックス元IDを文字列として扱う
# # リミックス元IDの重複を除いてカウント
# unique_remix_ids = df["リミックス元ID"].dropna().unique()  # NaNを除外して一意の値を取得
# count_unique_remix_ids = len(unique_remix_ids)
# # 結果を表示
# print(f"リミックス元IDの一意の件数: {count_unique_remix_ids}")
## 保存数と一致するかを見る
# print(count_files_in_directory(save_directory))

## CSVファイルのエラー箇所の確認
# csv_file_path = "../../dataset/8000data/filtered_remix_data.csv"
# try:
#     df = pd.read_csv(csv_file_path, dtype={"リミックス元ID": str})
# except Exception as e:
#     print(f"CSV読み込みエラー: {e}")