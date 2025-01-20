import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import seaborn as sns

def seikei(input_csv, output_csv): # リミックス元IDに.0がついていたので消去するプログラム
    if not os.path.exists(input_csv):
        print(f"Error: Input file {input_csv} does not exist.")
        return

    # CSVファイルの処理
    with open(input_csv, mode="r", encoding="utf-8") as infile, open(output_csv, mode="w", encoding="utf-8", newline="") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # ヘッダー行をコピー
        try:
            header = next(reader)
            writer.writerow(header)
        except StopIteration:
            print(f"Error: {input_csv} is empty.")
            return

        # データ行を処理
        for row in reader:
            # リミックス元ID（3列目）の ".0" を削除
            if len(row) > 2:  # 必要な列が存在するか確認
                row[2] = row[2].replace(".0", "")
            writer.writerow(row)

    print(f"Processed file saved to {output_csv}")

def csvint(input_csv, output_csv): #csvの値をintに
    # 入力ファイルと出力ファイルの指定
    # CSVファイルを読み込む
    data = []
    with open(input_csv, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader)  # ヘッダーを取得
        for row in reader:
            # 各値を文字列化（空の値も含む）
            data.append([int(value) if value != "" else "" for value in row])

    # 新しいCSVファイルに保存する
    with open(output_csv, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)  # すべての値をダブルクォートで囲む
        writer.writerow(header)  # ヘッダーを書き込む
        writer.writerows(data)   # データを書き込む

    print(f"すべての値が文字列として '{output_csv}' に保存されました。")   

def takeRemixAuthor(alldata_csv, remix_source_id, output_csv): #リミックス元作品が同じものでリミックスユーザのリミックス前後のオリジナル作品を取得
    try:
        # データ読み込み
        df = pd.read_csv(alldata_csv)
    except Exception as e:
        print(f"CSVの読み込み中にエラーが発生しました: {e}")
        return

    # リミックス元IDが指定されたものに一致する作品を抽出
    filtered_data = df[df['リミックス元ID'] == remix_source_id]
    if filtered_data.empty:
        print("該当するリミックス元IDの作品が見つかりませんでした。")
        return

    # 抽出した作者IDのリスト
    authors = filtered_data['作者ID'].unique()

    # 前後の作品を抽出
    def get_adjacent_nan_works(author_id, data, remix_source_id):
        author_works = data[data['作者ID'] == author_id].sort_values(by='作品ID').reset_index(drop=True)

        # リミックス元IDが一致する作品を取得
        remix_works = author_works[author_works['リミックス元ID'] == remix_source_id]
        if remix_works.empty:
            return pd.DataFrame()

        adjacent_works = []

        for _, remix_work in remix_works.iterrows():
            # 現在の作品（リミックス元IDが一致するもの）
            adjacent_works.append(remix_work)

            # リミックス前の作品: 条件を満たすものを取得
            prev_work = author_works[
                (author_works['作品ID'] < remix_work['作品ID']) &
                (pd.isna(author_works['リミックス元ID']))  # リミックス元IDがNaN
            ]
            if not prev_work.empty:
                # CTスコアが最も高い作品を選択
                prev_work = prev_work.loc[prev_work['CTスコア'].idxmax()]
                adjacent_works.append(prev_work)

            # リミックス後の作品: 条件を満たすものを取得
            next_work = author_works[
                (author_works['作品ID'] > remix_work['作品ID']) &
                (pd.isna(author_works['リミックス元ID']))  # リミックス元IDがNaN
            ]
            if not next_work.empty:
                # 最も直後の作品を選択
                next_work = next_work.iloc[0]
                adjacent_works.append(next_work)

        return pd.DataFrame(adjacent_works).drop_duplicates()

    # 結果を格納するリスト
    result = []
    for author_id in authors:
        adjacent_nan_works = get_adjacent_nan_works(author_id, df, remix_source_id)
        if not adjacent_nan_works.empty:
            result.append(adjacent_nan_works)

    # 結果をデータフレームに変換
    if result:
        result_df = pd.concat(result, ignore_index=True)
    else:
        print("該当するデータが見つかりませんでした。")
        return

    # データ型を調整
    result_df = result_df.apply(lambda col: col.astype(int) if col.dtype == 'float' and col.apply(float.is_integer).all() else col)

    # 結果をCSVファイルに保存
    try:
        result_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"結果を {output_csv} に保存しました。")
    except Exception as e:
        print(f"CSVの書き込み中にエラーが発生しました: {e}")

def plot_remix_transition(csv_file, output_dir): #散布図でリミックス前→リミックス→リミックス後をプロット
    # CSVファイルを読み込む
    df = pd.read_csv(csv_file)

    # 各項目のリミックス前→リミックス→リミックス後の推移をプロットする
    columns = ['論理', '制御フロー', '同期', '抽象化', 'データ表現', 'ユーザとの対話性', '並列処理', 'CTスコア']

    # カラーマップの準備
    unique_users = df['作者ID'].unique()
    cmap = plt.get_cmap('tab20', len(unique_users))  # 'tab20'は複数の色を提供するカラーマップ

    for col in columns:
        plt.figure(figsize=(10, 6))
        plt.title(f'{col}のリミックス前・リミックス後の推移')
        plt.xlabel('作品の状態')
        plt.ylabel(f'{col}のスコア')

        # 各ユーザーのデータをプロット
        for i, user_id in enumerate(unique_users):
            user_data = df[df['作者ID'] == user_id].sort_values('作品ID')

            # リミックス前：作品IDが最も小さいもの
            remix_before = user_data.iloc[0]
            remix_scores_before = remix_before[col]

            # リミックス後：作品IDが最も大きいもの
            remix_after = user_data.iloc[-1]
            remix_scores_after = remix_after[col]

            # リミックス：その間の作品
            remix = user_data.iloc[1:-1]
            remix_scores = remix[col].values

            # 各点のx, yの値
            x_values = ['リミックス前', 'リミックス', 'リミックス後']
            y_values = [remix_scores_before, remix_scores.mean() if len(remix_scores) > 0 else 0, remix_scores_after]

            # 重なり具合をチェックするためにx, yのペアを計算
            points = list(zip(x_values, y_values))

            # 重なり具合を数える
            point_counts = defaultdict(int)
            for point in points:
                point_counts[point] += 1
            
            # 各点のサイズを計算
            sizes = [50 + point_counts[point] * 20 for point in points]

            # ユーザーごとの色を取得
            color = cmap(i)

            # 点のプロット
            for point, size in zip(points, sizes):
                plt.scatter(point[0], point[1], s=size, marker='o', color=color, zorder=5)

            # それぞれのスコアをプロット
            plt.plot(x_values, y_values, linewidth=2, marker='o', markersize=8, color=color, zorder=2)

        # グラフの設定
        plt.grid(True)

        # 保存
        save_path = f'{output_dir}/{col}_transition.png'
        plt.savefig(save_path, dpi=100, bbox_inches='tight')

        # グラフを閉じる
        plt.close()

def plot_remix_transition_boxplot(csv_file, output_dir):#箱ひげ図でリミックス前→リミックス→リミックス後をプロット
    # CSVファイルを読み込む
    df = pd.read_csv(csv_file)

    # 各項目のリミックス前→リミックス→リミックス後の推移をプロットする
    columns = ['論理', '制御フロー', '同期', '抽象化', 'データ表現', 'ユーザとの対話性', '並列処理', 'CTスコア']
    for col in columns:
        plt.figure(figsize=(10, 6))
        plt.title(f'{col}のリミックス前・リミックス後の推移')
        plt.xlabel('作品の状態')
        plt.ylabel(f'{col}のスコア')

        # データを格納するリスト
        data = {'リミックス前': [], 'リミックス': [], 'リミックス後': []}
        
        # 各ユーザーのデータを処理
        for user_id in df['作者ID'].unique():
            user_data = df[df['作者ID'] == user_id].sort_values('作品ID')

            # リミックス前：作品IDが最も小さいもの
            remix_before = user_data.iloc[0]
            remix_scores_before = remix_before[col]

            # リミックス後：作品IDが最も大きいもの
            remix_after = user_data.iloc[-1]
            remix_scores_after = remix_after[col]

            # リミックス：その間の作品
            remix = user_data.iloc[1:-1]
            remix_scores = remix[col].values

            # データを格納
            data['リミックス前'].append(remix_scores_before)
            data['リミックス後'].append(remix_scores_after)
            if len(remix_scores) > 0:
                data['リミックス'].append(remix_scores.mean())
        
        # 箱ひげ図を描く
        ax = sns.boxplot(data=[data['リミックス前'], data['リミックス'], data['リミックス後']],
                         palette="coolwarm", linewidth=2.5)  # 線の太さを調整
        
        # 箱の色やその他のプロパティを調整
        for box in ax.artists:
            box.set_edgecolor('black')  # 箱の縁を黒く
            box.set_linewidth(2)  # 箱の縁の太さを変更

        # x軸のラベルを設定
        ax.set_xticklabels(['リミックス前', 'リミックス', 'リミックス後'])

        # グラフの設定
        plt.grid(True)

        # 保存
        save_path = f'{output_dir}/{col}_boxplot_transition.png'
        plt.savefig(save_path, dpi=100, bbox_inches='tight')

        # グラフを閉じる
        plt.close()

def focusUser(user_id, input_file, output_dir):
    # 必要な列名
    score_columns = ['Logic', 'ControlFlow', 'Synchronization', 'Abstraction', 'DataRepresentation', 'UserInteraction', 'ParallelProcessing', 'CTScore']
    column_mapping = {
        '作者ID': 'AuthorID',
        '作品ID': 'ProjectID',
        'リミックス元ID': 'RemixSourceID',
        'ブロック数': 'BlockCount',
        'ブロックの種類数': 'BlockTypeCount',
        'スプライト数': 'SpriteCount',
        '論理': 'Logic',
        '制御フロー': 'ControlFlow',
        '同期': 'Synchronization',
        '抽象化': 'Abstraction',
        'データ表現': 'DataRepresentation',
        'ユーザとの対話性': 'UserInteraction',
        '並列処理': 'ParallelProcessing',
        'CTスコア': 'CTScore'
    }
    
    # CSVファイルを読み込む
    df = pd.read_csv(input_file)

    # 列名の英語化
    df.rename(columns=column_mapping, inplace=True)

    # 列名の確認
    print(df.columns)  # ここで列名が正しく英語になっているか確認

    # ユーザーのデータを取得
    user_data = df[df['AuthorID'] == user_id].sort_values('ProjectID')

    # 結果を格納するリスト
    result_rows = []

    # リミックスごとのデータ処理
    for _, remix_row in user_data[user_data['RemixSourceID'].notna()].iterrows():
        # リミックス前: リミックスより前のオリジナル作品でCTスコアが最大のもの
        pre_data = user_data[
            (user_data['RemixSourceID'].isna()) & (user_data['ProjectID'] < remix_row['ProjectID'])
        ]
        if not pre_data.empty:
            pre_data = pre_data.loc[pre_data['CTScore'].idxmax()]
            pre_data = pre_data.to_dict()
            pre_data['Category'] = 'Pre'
            pre_data['RemixID'] = remix_row['ProjectID']
            result_rows.append(pre_data)

        # リミックス: 現在のリミックスデータ
        remix_data = remix_row.to_dict()
        remix_data['Category'] = 'Remix'
        remix_data['RemixID'] = remix_row['ProjectID']
        result_rows.append(remix_data)

        # リミックス後: リミックス直後の最初のオリジナル作品
        post_data = user_data[
            (user_data['RemixSourceID'].isna()) & (user_data['ProjectID'] > remix_row['ProjectID'])
        ]
        if not post_data.empty:
            post_data = post_data.iloc[0]
            post_data = post_data.to_dict()
            post_data['Category'] = 'Post'
            post_data['RemixID'] = remix_row['ProjectID']
            result_rows.append(post_data)

    # データフレーム化
    result_data = pd.DataFrame(result_rows)

    # 整数型に変換
    int_columns = ['ProjectID', 'AuthorID', 'RemixSourceID', 'RemixID']
    for col in int_columns:
        if col in result_data.columns:
            result_data[col] = result_data[col].fillna(0).astype(int)

    # ここで小数点を取り除く処理
    result_data = result_data.applymap(lambda x: int(x) if isinstance(x, float) and x.is_integer() else x)

    # カテゴリの確認: Pre, Remix, Post が存在するか確認
    if not all(cat in result_data['Category'].values for cat in ['Pre', 'Remix', 'Post']):
        print("Pre, Remix, Post のすべてのカテゴリが揃っていないため、処理を中止します。")
        return  # メソッドから脱出して処理を中止

    # ディレクトリ作成: user_id のフォルダを作成
    user_output_dir = os.path.join(output_dir, str(user_id))
    os.makedirs(user_output_dir, exist_ok=True)

    # CSV保存: user_id フォルダ内に保存
    output_csv_path = os.path.join(user_output_dir, f"{user_id}_result.csv")
    result_data.to_csv(output_csv_path, index=False, quoting=1)  # quoting=1 で引用符を適切に設定

    # 各スコアの箱ひげ図をプロット
    for col in score_columns:
        plt.figure(figsize=(10, 6))

        # 各カテゴリごとのデータ
        pre_scores = result_data[result_data['Category'] == 'Pre'][col]
        remix_scores = result_data[result_data['Category'] == 'Remix'][col]
        post_scores = result_data[result_data['Category'] == 'Post'][col]

        # 各カテゴリにデータがある場合のみ箱ひげ図を描画
        if not pre_scores.empty:
            sns.boxplot(x=['Pre']*len(pre_scores), y=pre_scores, color='lightblue', width=0.5, linewidth=2.5)
        if not remix_scores.empty:
            sns.boxplot(x=['Remix']*len(remix_scores), y=remix_scores, color='orange', width=0.5, linewidth=2.5)
        if not post_scores.empty:
            sns.boxplot(x=['Post']*len(post_scores), y=post_scores, color='lightgreen', width=0.5, linewidth=2.5)

        # タイトルとラベルの設定（フォントなし）
        plt.title(f"{col} by Category", fontsize=14)
        plt.xlabel("Category", fontsize=12)
        plt.ylabel(f"{col} Score", fontsize=12)

        # 横軸ラベルを手動で設定（フォントに依存しない方法）
        plt.xticks([0, 1, 2], ['Pre', 'Remix', 'Post'], rotation=0)

        # 縦軸の範囲設定
        if col == 'CTScore':
            plt.ylim(0, 21)  # CTスコアの縦軸範囲を0から21に設定
        else:
            plt.ylim(0, 3)  # 他のスコアの縦軸範囲を0から3に設定

        # グリッド表示
        plt.grid(True)

        # 保存: user_id フォルダ内に保存
        save_path = os.path.join(user_output_dir, f"{col}_boxplot.png")
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()

    print(f"結果を {output_csv_path} に保存し、箱ひげ図を {user_output_dir} に保存しました。")

    
# remix_csv1 = "../../dataset/plotdata/dataset/remix_data1.csv"
# remix_csv = "/works/dataset/remix_data.csv"
alldata_csv1 = "../../dataset/plotdata/dataset/data1.csv"
# alldata_csv = "/works/dataset/data.csv"
# output_csv = "../../dataset/plotdata/dataset/127661441focus.csv"
output_dir = "../../dataset/plotdata/graph"
# リミックス元IDが一致するものだけをフィルタリング
# remix_source_id = "598658475"
# remix_source_id = "536199882"
# remix_source_id = 167865349
# user_id = 134513566
saveGraph = "../../dataset/plotdata/graph"
# remix_source_id = "411683888"
# remix_source_id = "1078744793"

# takeRemixAuthor(alldata_csv1, remix_source_id, output_csv)
# plot_remix_transition(output_csv, output_dir)
# plot_remix_transition_boxplot(output_csv, output_dir)


# CSVデータを読み込む（CSVファイルの場合はpd.read_csvを使って読み込みます）
df = pd.read_csv(alldata_csv1)
# リミックス元IDが存在する作品（リミックスした作品）のみを抽出
remixed_df = df[df['リミックス元ID'].notna()]
# 作者ごとにリミックスした回数をカウント
remix_counts_per_author = remixed_df['作者ID'].value_counts()
# リミックス回数が3回以上の作者IDを取得
authors_in_range = remix_counts_per_author[(remix_counts_per_author >= 3) & (remix_counts_per_author < 18)].index
for author_id in authors_in_range:
    focusUser(author_id, alldata_csv1, saveGraph)

# csvint(remix_csv, remix_csv1)
# csvint(alldata_csv, alldata_csv1)
# df1 = pd.read_csv(remix_csv1)
# print("リミックス元IDのデータ型:", df1["リミックス元ID"].dtype)


# ## debag

# # 列名と型を確認
# print("列名:", df1.columns)
# print("リミックス元IDの型:", df1["リミックス元ID"].dtype)
# # リミックス元IDの型を文字列に変換
# df1["リミックス元ID"] = df1["リミックス元ID"].astype(str)
# # 型の再確認
# print("リミックス元IDの型（変換後）:", df1["リミックス元ID"].dtype)
# # フィルタリング
# remix_data = df1[df1["リミックス元ID"] == remix_source_id]
# # 結果の確認
# if remix_data.empty:
#     print(f"リミックス元ID {remix_source_id} の作品が見つかりませんでした。")
# else:
#     print("リミックス元IDに一致する作品:", remix_data)

# # デバッグ用: 列名とデータ型を表示
# print("列名と型:")
# print(df1.dtypes)

# # リミックス元IDを文字列に変換
# df1["リミックス元ID"] = df1["リミックス元ID"].astype(str)
# remix_source_id = str(remix_source_id)

# # デバッグ用: リミックス元IDのユニーク値を確認
# print("リミックス元IDのユニーク値:", df1["リミックス元ID"].unique())

# # リミックス元IDが指定された行を抽出
# remix_data = df1[df1["リミックス元ID"] == remix_source_id]

# # デバッグ用: 抽出結果を表示
# print("リミックスデータ:")
# print(remix_data)



