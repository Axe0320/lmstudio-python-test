import csv
import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path

# main.py が置かれているフォルダ
BASE_DIR = Path(__file__).resolve().parent

# .env と CSV のパス（main.py の場所を基準とする）
ENV_PATH = BASE_DIR / ".env"
CSV_PATH = BASE_DIR / "LocalLLM_Test.csv"

# 分類対象の文章
INPUT_TEXT = """ガチャの期限を勘違いして200連分の石を無駄にした…
半年かけて貯めたのに…"""

# 感情分類の指示
SYSTEM_PROMPT = """あなたはSNS文章の感情分類を行うAIです。
入力された文章を、次のP、N、Ntのいずれかに分類してください。

次の形式で日本語で回答してください。
感情: （分類ラベル）
理由: （短い説明）

分類ラベル以外の新しい感情カテゴリは作らないでください。"""


def load_env():
    """.env を読み込む（外部ライブラリ不要）。"""
    if not ENV_PATH.exists():
        raise FileNotFoundError(
            f".env が見つかりません: {ENV_PATH}"
        )

    with ENV_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            # 空行とコメントを無視
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # 値の前後にある引用符を除去
            if (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in ("'", '"')
            ):
                value = value[1:-1]

            # 既存の環境変数があれば、そちらを優先
            if key:
                os.environ.setdefault(key, value)

    api_url = os.getenv("API_URL")
    model_name = os.getenv("MODEL_NAME")

    if not api_url or not model_name:
        raise ValueError(
            ".env に API_URL と MODEL_NAME を設定してください。"
        )

    return api_url, model_name


def classify_emotion(api_url, model_name):
    """LM Studio の API で文章を分類する。"""
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": INPUT_TEXT,
            },
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
    }

    request = urllib.request.Request(
        api_url,
        data=json.dumps(
            payload, ensure_ascii=False
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=180) as response:
        result = json.loads(
            response.read().decode("utf-8")
        )

    answer = result["choices"][0]["message"].get("content", "")

    if not answer or not answer.strip():
        raise ValueError(
            "LLMから分類結果が返されませんでした。"
        )

    return answer.strip()


def parse_answer(answer):
    """LLMの回答から分類ラベルと理由を取り出す。"""
    label = "不明"
    reason = ""

    for line in answer.splitlines():
        line = line.strip()

        if line.startswith(("感情:", "感情：")):
            candidate = line[3:].strip()

            if candidate in {"P", "N", "Nt"}:
                label = candidate

        elif line.startswith(("理由:", "理由：")):
            reason = line[3:].strip()

    # 理由の抽出に失敗した場合も、元の回答を残す
    if not reason:
        reason = answer

    return label, reason


def save_to_csv(input_text, answer, label, reason, model_name):
    """分類結果をCSVに保存する。"""
    with CSV_PATH.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "input_text",
                "emotion",
                "reason",
                "raw_response",
                "model",
            ],
        )

        writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now()
                .astimezone()
                .isoformat(timespec="seconds"),
            "input_text": input_text,
            "emotion": label,
            "reason": reason,
            "raw_response": answer,
            "model": model_name,
        })


def main():
    print("=== SNS感情分類テスト ===")
    print(f"入力文章:\n{INPUT_TEXT}\n")

    api_url, model_name = load_env()

    print(f"使用モデル: {model_name}")
    print("LM Studioに問い合わせています...")

    answer = classify_emotion(api_url, model_name)
    label, reason = parse_answer(answer)

    save_to_csv(
        INPUT_TEXT,
        answer,
        label,
        reason,
        model_name,
    )

    print("\n=== LLMの回答 ===")
    print(answer)

    print("\n=== CSV保存結果 ===")
    print(f"分類ラベル: {label}")
    print(f"理由: {reason}")
    print(f"保存先: {CSV_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(
            f"エラーが発生しました: "
            f"{type(error).__name__}: {error}"
        )
        raise
