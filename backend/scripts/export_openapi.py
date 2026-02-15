"""OpenAPI スキーマエクスポートスクリプト

FastAPI アプリケーションから OpenAPI JSON スキーマを出力する。
CI/CD パイプラインやドキュメント生成で使用。

Usage:
    python scripts/export_openapi.py > docs/openapi.json
"""

import json
import sys
from pathlib import Path

# backend ディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402

if __name__ == "__main__":
    schema = app.openapi()
    print(json.dumps(schema, indent=2, ensure_ascii=False))
