# Scratcher

## Document
[Scratcher/Document](https://hyphen-o.github.io/scratch-analyzer/)

## 本ライブラリを使う主な目的

- Scratch のデータを json, csv 形式で取得
- Scratch データをより使いやすい形に変換
- Scratch データを用いた類似度算出（DTW や編集距離）

## Setup

`git clone https://github.com/keigo-0314/scratch-analyzer.git`

**ローカルで実行する**

※Mac の方

1. インストールしたプロジェクトのルートディレクトリに移動
2. `make setup`

※Windows の方

1. インストールしたプロジェクトのルートディレクトリに移動
2. `pip install setuptools wheel`
3. `python setup.py sdist bdist_wheel`

※共通

- どちらの場合も上記のコマンドを実行すると，ルートディレクト内に`dist`ディレクトリが作成される．
- パッケージをインストールする際は，

`pip install {このプロジェクトまでのPATH}/dist/scratcher-{dist内のバージョン参照}.tar.gz`

**Docker で実行する**

1. インストールしたプロジェクトのルートディレクトリに移動
2. `make up`
3. `make exec`

## モジュールの解説（整理済みのモジュールのみ記載しています）

```src

├── dtw
│   ├── __init__.py
│   └── dtw.py #DTWを算出するためのモジュール
├── animation
|   ├── __init__.py
|   └── animater.py #ScratchスプライトからアニメーションGIFを生成するためのモジュール
├── api
│   ├── __init__.py
|   ├── google_client.py #GoogleFormAPIを叩くためのモジュール
│   ├── scratch_client.py #ScratchAPIを叩くためのモジュール
|   └── drscratch_analuzer.py #DrScratchAPIを叩くためのモジュール
├── __init__.py
├── tools
│   ├── sorter.py #Scratchプログラムを命令処理順にソートするモジュール
│   ├── collector.py
│   ├── __init__.py
│   └── tracker.py #スプライトの移動軌跡を算出するモジュール
├── converter
│   ├── __init__.py
│   └── ast_converter.py #ScratchプログラムをASTに変換するためのモジュール
├── config
│   ├── filter.csv #フィルタリング用CSVファイル
│   ├── constants.json #定数管理のためのファイル
│   └── sim.csv #抽象化用CSVファイル
├── edit
│   ├── __init__.py
│   └── edit.py #編集距離を算出するためのモジュール
├── utils
│   ├── dfman.py #データフレームを管理するためのモジュール
│   ├── fileman.py #ファイル管理するためのモジュール
│   ├── parallelizer.py #並列化処理するためのモジュール
│   ├── draw_graph.py #図を描画するためのモジュール
|   ├── env.py #env管理するためのモジュール
│   ├── util.py #汎用関数
│   ├── cmd_runnner.py #コマンド実行用モジュール
│   └── __init__.py
└── prjman.py #Scratchプログラムを管理するためのモジュール
```
