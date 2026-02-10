#!/bin/bash
# Mermaid Validation Hook
# reports/ 配下の .md ファイルが書き込まれた際に、Mermaid図の構文を検証する。
# エラーがあれば Claude に通知し、修正を促す。

# stdin から hook input JSON を読み取り
INPUT=$(cat)

# 書き込まれたファイルパスを取得
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# ファイルパスが取得できない場合は終了
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# reports/ 配下の .md ファイルのみを対象
if ! echo "$FILE_PATH" | grep -q 'reports/.*\.md$'; then
  exit 0
fi

# ファイルが存在しない場合は終了
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# Mermaid ブロックが含まれていない場合はスキップ
if ! grep -q '```mermaid' "$FILE_PATH"; then
  exit 0
fi

# mmdc が利用可能か確認
if ! command -v mmdc &> /dev/null; then
  exit 0
fi

# Mermaid ブロックを抽出して個別に検証
ERRORS=""
BLOCK_NUM=0
TEMP_DIR=$(mktemp -d)

# Mermaid ブロックを抽出
awk '/^```mermaid$/,/^```$/' "$FILE_PATH" | \
awk '/^```mermaid$/{n++; next} /^```$/{next} {print > "'"$TEMP_DIR"'/block_"n".mmd"}'

for BLOCK_FILE in "$TEMP_DIR"/block_*.mmd; do
  [ -f "$BLOCK_FILE" ] || continue
  BLOCK_NUM=$((BLOCK_NUM + 1))

  # mmdc で検証（出力は /dev/null、タイムアウト10秒）
  RESULT=$(timeout 10 mmdc -i "$BLOCK_FILE" -o /dev/null 2>&1) || true

  if echo "$RESULT" | grep -qi "error\|parse\|syntax"; then
    BLOCK_PREVIEW=$(head -1 "$BLOCK_FILE")
    ERRORS="${ERRORS}\n- Block #${BLOCK_NUM} (${BLOCK_PREVIEW}...): ${RESULT}"
  fi
done

# 一時ファイルを削除
rm -rf "$TEMP_DIR"

# エラーがあれば報告（ブロックはせず警告のみ）
if [ -n "$ERRORS" ]; then
  cat << EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Mermaid validation warnings in ${FILE_PATH}:${ERRORS}\n\nConsider running /fix-mermaid to fix these issues."
  }
}
EOF
fi

exit 0
