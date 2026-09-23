# AI Agent 開發實戰｜Lab 1–5

用「微醺之夜 Bistro」(`../bistro_concierge`) 的真實素材跑課程的五個診斷工具。

五次量測裡三次的結論是**工具誤報**，不是系統有問題；兩次抓到真正該補的東西。
完整論證見作品集頁面，這裡只放可重跑的輸入檔與指令。

環境：Python 3.13，只用標準函式庫。中文輸出要設 `PYTHONIOENCODING=utf-8`。
課程腳本寫 `python3`，Windows 上要改成 `python`。

---

## Lab 1｜工具 schema 體檢

Bistro 是 Dify workflow，沒有現成的 function-calling schema。
這裡是把四個 parameter-extractor 節點翻譯過去的結果，
**參數描述逐字搬、一個字沒改**，只補上描述裡本來就列了值的 `enum`。

| 檔案 | 內容 |
|---|---|
| `bistro_tools.json` | 忠實版。工具層描述用 Dify 節點的原始 instruction，未潤飾 |
| `bistro_tools_v2.json` | 把 classifier 的分類文字折回工具描述 |
| `bistro_tools_v3.json` | v2 加上後來新增的 `detail` 參數 |

```bash
PYTHONIOENCODING=utf-8 python lab1_schema_lint.py bistro_tools.json --tools 5 --turns 30 --tasks 60
```

- v1：3/4 被判「沒寫何時用」。**誤報** —— Dify 的觸發條件在 classifier 的 class 名稱裡，不在工具描述裡。
- `report_complaint` 那支「通過」是假的：它的 L3 定義有「**要求**賠償」，命中關鍵字表而已。
- v2 全過，但每支從 295 漲到 396 tokens（+34%）。
- v3 的新參數乾淨過關，該支 250 → 363 tokens。

## Lab 2｜Context 預算與識別碼

```bash
# 預算表（數字為實測：系統提示 3,126、工具 schema 1,584）
PYTHONIOENCODING=utf-8 python lab2_context_budget.py \
  --window 128000 --tools 0 --system 3126 --skills 0 --memory 0 --per-turn 430

# 識別碼抽取：內建規則
PYTHONIOENCODING=utf-8 python lab2_context_budget.py --identifiers bistro_conversation.txt

# 第 4 題作答：補上 Bistro 的四種識別碼再跑一次
PYTHONIOENCODING=utf-8 python bistro_patterns.py bistro_conversation.txt
```

常駐只佔視窗 2.4%，**沒有 context 預算問題**。
但內建規則從一段真實對話裡只抓到 7 個識別碼，漏掉的四種正好是讓對話可以被執行的：

| 識別碼 | regex | 出處 |
|---|---|---|
| 訂位代碼 | `\bR[0-9A-F]{6}\b` | `reservation._new_code()` |
| 客訴單號 | `\bC\d{8}-\d{6}-\d{4}\b` | `api._next_ticket()` |
| 電話 | `\b09\d{2}-?\d{3}-?\d{3}\b` | 訂位唯一聯絡方式 |
| 桌號 | `\bT\d{2}\b` | `tables.yaml` |

補上後 7 → 11。`bistro_patterns.py` 用 import 擴充，**沒改課程原檔**。

## Lab 3｜SKILL.md Linter

Bistro 沒有 SKILL.md，改用兩批公開語料：
`superpowers-main/skills`（14 支）與 `dify-main/.agents/skills`（5 支）。

```bash
PYTHONIOENCODING=utf-8 python lab3_skill_lint.py <某個 skill 目錄>/SKILL.md
```

**19 支全部不及格，零支通過。** 拆完規則命中率後的結論是尺壞了：

- `description` 超過 60 字元：19/19。但工具自己的好例子是**中文** 37 字；
  19 支英文的最短 79、中位 154、最長 335。規則沒翻譯。
- 「用了 shell 指令名」7/19，逐一回原文看**全部是英文單字**
  （`find` 是動詞、`head-to-head`、`the head the previous review saw`）。
- 反過來漏掉唯一一行真的 shell pipeline
  （`git log | grep ... | head -1 | awk ...`），因為規則會先把程式碼區塊刪掉 ——
  而該規則的立論正是「你寫什麼動詞 agent 就做什麼動作」。
- 唯一站得住的是「description 沒寫何時用」，只噴 **1/19**。

## Lab 4｜委派成本

Bistro 目前零子代理，所以這是**設計提案不是現況稽核**：
把六個真實工作負載當成「如果改用多代理重建」的計畫草案。
固定成本用實測的 4,710（3,126 系統提示 + 1,584 工具 schema），非預設的 15,000。

```bash
PYTHONIOENCODING=utf-8 python lab4_delegate_cost.py bistro_plan.json
PYTHONIOENCODING=utf-8 python lab4_delegate_cost.py --scan-first 1000 12
```

四項該拆、一項邊緣、一項明確不該拆（L3 客訴通報，過程／結論比 1:1）。
工具點名的兩個「坑」，系統早就用排程與佇列繞開了，理由寫在原始碼註解裡。

`bistro_plan.json` 每個 task 都有 `_basis` 欄位記錄數字怎麼估的。

## Lab 5｜行為契約與 A/B 樣本數

```bash
PYTHONIOENCODING=utf-8 python lab5_contracts.py --classify bistro_asserts_v1.txt   # 3/3 是變更偵測器
PYTHONIOENCODING=utf-8 python lab5_contracts.py --classify bistro_asserts_v2.txt   # 0/3
PYTHONIOENCODING=utf-8 python lab5_contracts.py --classify bistro_my_asserts.txt   # 實際寫出來的測試
PYTHONIOENCODING=utf-8 python lab5_contracts.py --ab 22 0.70 0.85
```

Bistro 的 `tests/golden_set.yaml` 是 22 題，每題都綁一個已知失效模式。
**22 題只撐得起「25 個百分點以上」的改善宣稱**（+15 要 121 題、+20 要 62 題、+10 要 294 題）。

但這不是缺陷是用途問題：它是**回歸閘門**不是 A/B 量尺，這兩件事不該共用同一套題庫。

`bistro_my_asserts.txt` 是後來實際補進 Bistro 的測試斷言，回頭用同一把尺量：
**0 個變更偵測器**，但有 15 條被判「看不出來」——
`is True` / `isinstance` 這類形狀斷言不在工具的 pattern 表裡。
跟 Lab 3 是同一種毛病：規則沒涵蓋真實程式碼的語彙。

---

## 後續：稽核帶出來的實際修正

量測 Lab 2 的工具輸出時撞到 `/ops schedule` 對所有呼叫端回 500
（`build_schedule()` 回三元組，`api.py` 當成單一 DataFrame 接）。

已修，並補上該專案的第一組 Python 測試（22 條）。
順帶發現它是系統最大的工具輸出（3,806 tokens），改成預設回摘要後降到 563（-85%），
同時讓原本沒有 API 出口的人力缺口露出來。詳見 `bistro_concierge` 的 commit 紀錄。

---

## 注意

`lab1_` ~ `lab5_` 這五支是**課程提供的腳本，不是我寫的**，
放在這裡是為了讓每個數字都能重現。
若要把這個 repo 推成公開的，先確認課程材料的授權條款。
