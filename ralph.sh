#!/bin/bash
# Ralph Loop — InfoHelper 自动构建脚本
# 每轮迭代让 Claude Code 完成一个任务，直到所有任务完成或卡住

set -e

MAX_ITERATIONS=${1:-10}  # 默认最多 10 轮，可通过参数覆盖
ITERATION=0

echo "=== Ralph Loop 启动 ==="
echo "最大迭代次数: $MAX_ITERATIONS"
echo ""

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    echo "--- 迭代 $ITERATION / $MAX_ITERATIONS ---"

    # 检查是否已完成
    if grep -q "STATUS: COMPLETE" IMPLEMENTATION_PLAN.md 2>/dev/null; then
        echo "所有任务已完成!"
        exit 0
    fi

    # 检查是否卡住
    if grep -q "STATUS: STUCK" IMPLEMENTATION_PLAN.md 2>/dev/null; then
        echo "Agent 报告卡住，请检查 IMPLEMENTATION_PLAN.md"
        exit 1
    fi

    # 执行一轮构建
    cat BUILD_PROMPT.md | claude --print

    echo ""
    echo "--- 迭代 $ITERATION 完成 ---"
    echo ""
done

echo "=== 达到最大迭代次数 ($MAX_ITERATIONS)，退出 ==="
echo "请检查 IMPLEMENTATION_PLAN.md 查看进度"
