#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lab 2 第 4 題的作答：把微醺之夜 Bistro 的識別碼補進 PATTERNS 再跑一次。

不改 lab2_context_budget.py，用 import 的方式擴充，原檔維持乾淨。
用法：python bistro_patterns.py bistro_conversation.txt
"""
import os
import sys

# 課程腳本放在 course-scripts/(未納入版控,見 README)。
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "course-scripts"))
import lab2_context_budget as lab2

# 這四種被改寫掉，整段對話就作廢——客人回不來、店裡也查不到。
BISTRO_PATTERNS = [
    ("訂位代碼",  r"\bR[0-9A-F]{6}\b"),              # reservation._new_code()：R + token_hex(3).upper()
    ("客訴單號",  r"\bC\d{8}-\d{6}-\d{4}\b"),        # api._next_ticket()：C%Y%m%d-%H%M%S-0001
    ("電話",      r"\b09\d{2}-?\d{3}-?\d{3}\b"),     # 訂位唯一的聯絡方式
    ("桌號",      r"\bT\d{2}\b"),                    # tables.yaml
]

lab2.PATTERNS = BISTRO_PATTERNS + lab2.PATTERNS

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "bistro_conversation.txt"
    sys.exit(lab2.identifiers_report(path))
