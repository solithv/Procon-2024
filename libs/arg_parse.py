import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-l", "--log", type=str, default="./logs", help="ログの出力先")

parser.add_argument(
    "-r", "--retry", type=int, default=10, help="APIリクエストの再試行回数"
)
parser.add_argument(
    "-i", "--interval", type=int, default=10, help="APIリクエストの再試行待機時間"
)
parser.add_argument(
    "-d", "--debug", action="store_true", help="デバッグ(オフライン)モード"
)
parser.add_argument(
    "-p", "--post-debugger", "--post_debugger", action="store_true", help="デバッガーのサーバへdumpとlogをポストする"
)
parser.add_argument(
    "-j", "--json", type=str, help="入力する問題フォーマットのjsonファイルパス"
)
parser.add_argument(
    "-f",
    "--force",
    action="store_true",
    help="問題フォーマットが入力されていてもボードをランダム生成する",
)
parser.add_argument(
    "-x",
    "--width",
    type=int,
    help="ボードの横幅 問題フォーマットが入力された場合は無視される",
)
parser.add_argument(
    "-y",
    "--height",
    type=int,
    help="ボードの縦幅 問題フォーマットが入力された場合は無視される",
)
parser.add_argument("-s", "--seed", type=int, help="ボードのランダム生成用シード値")
