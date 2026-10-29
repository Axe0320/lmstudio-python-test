# LM Studio Python Test

LM Studio のローカル LLM を Python から呼び出し、SNS文章の感情分類を行うテストプロジェクトです。

## 使用技術

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-Local%20LLM-000000?style=flat-square)](https://lmstudio.ai)
[![Docker](https://img.shields.io/badge/Docker-Dev%20Container-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)
[![VS Code](https://img.shields.io/badge/VS%20Code-Development-007ACC?style=flat-square&logo=visualstudiocode&logoColor=white)](https://code.visualstudio.com)

## 機能

- LM Studio の OpenAI 互換 API を利用した LLM 呼び出し
- SNS文章の感情分類（P / N / Nt）
- 分類結果・理由の CSV 出力

## ディレクトリ構成

```text
lmstudio-python-test/
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── main.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## セットアップ

1. LM Studio でモデルをロードし、Local Server を起動する。
2. `.env.example` を `.env` にコピーし、API URL とモデル名を設定する。
3. VS Code で Dev Container を起動する。

## 実行方法

```bash
python main.py
```

実行結果は `LocalLLM_Test.csv` に出力されます。

## 出力

実行結果は、プロジェクト直下の `LocalLLM_Test.csv` に保存されます。

| カラム         | 内容             |
| -------------- | ---------------- |
| `timestamp`    | 実行日時         |
| `input_text`   | 分類対象の文章   |
| `emotion`      | 分類ラベル       |
| `reason`       | 分類理由         |
| `raw_response` | LLM の回答       |
| `model`        | 使用したモデル名 |

CSV ファイルは実行時に生成・更新されます。

## 感情分類

SNS文章を、次の3種類のラベルに分類します。

- `P`：ポジティブ
- `N`：ネガティブ
- `Nt`：ニュートラル

分類結果に加えて、その理由も取得します。
