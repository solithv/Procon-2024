# PROCON-2024
第35回 全国高等専門学校プログラミングコンテスト 競技部門 「シン・よみがえれ世界遺産」<br/>
東京都立産業技術高等専門学校 荒川キャンパス チーム: "; DROP TABLE teams; --"

## 目次

1. [概要](#概要)
2. [インストール](#インストール)
2. [使用方法](#使用方法)

## 概要

本リポジトリは第35回高専プロコン競技部門「シン・よみがえれ世界遺産」のために作成されました。<br/>
2点交換を主軸としたアルゴリズムにより、確実にボードを修復することを主眼において開発されています。

## インストール

Windows, MacOS, Linuxにて動作確認されています

### 前提条件

- Python >= 3.11
- numpy
- ray
- requests
- python-dotenv

### インストール手順

#### 依存関係のインストール
```bash
pip install -r requirements.txt
```

#### .envファイルの作成
.env_sampleを参考に環境に合わせて.envファイルを作成してください
- URL: APIへのアクセスURL
- TOKEN: アクセストークン

## 使用方法

```bash
python main.py [コマンドライン引数]
```

### コマンドライン引数

| 引数 | 説明  | 型| デフォルト値 | 必須 |
|------|------|---|--------------|------|
| `-l`, `--log` | ログの出力先パスを指定 | str | './logs' | No |
| `-r`, `--retry` | APIアクセスの再試行回数 | int | 10 | No |
| `-i`, `--interval` | APIアクセスの再試行待機時間 | float | 0.5 | No |
| `-d`, `--debug` | デバッグ(オフライン)モードフラグ | - | False | No |
| `-j`, `--json` | 入力する問題フォーマットのjsonファイルパス | str | - | No |
| `-f`, `--force` | 問題フォーマットが入力されていてもボードをランダム生成 | - | False | No |
| `-x`, `--width` | ボードの横幅 未指定の場合[8-256]の範囲でランダム決定 | int | - | No |
| `-y`, `--height` | ボードの縦幅 未指定の場合[8-256]の範囲でランダム決定 | int | - | No |
| `-s`, `--seed` | ボードのランダム生成用シード値 | int | - | No |
| `-h`, `--help` | ヘルプメッセージを表示 | - | - | No |