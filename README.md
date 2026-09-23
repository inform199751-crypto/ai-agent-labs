# 拿五把業界的尺，量一套自己寫的餐飲 AI 系統

一套 AI Agent 開發課程給了五個診斷工具：工具 schema 體檢、context 預算試算、
SKILL.md linter、委派成本試算、行為契約判別。

多數人拿它們跑課程給的範例。我拿它們去量自己寫的系統——
[微醺之夜 Bistro](https://github.com/inform199751-crypto/bistro-ai-analytics)，
約 7,400 行 Python 的餐飲營運 AI，Dify workflow 加標準函式庫 HTTP API。

**結論：五次量測裡三次是工具誤報，不是系統有問題。** 每一次都有證據。
剩下兩次抓到真正該補的東西，另外撞到一個線上會回 500 的 bug，已修復並補上該專案的第一組測試。

---

## 五關的結果

| Lab | 量什麼 | 結果 |
|---|---|---|
| 1 | 工具 schema | 4 支有 3 支被判「沒寫何時用」→ **誤報**。Dify 把觸發條件放在 classifier 節點，不在工具描述裡 |
| 2 | Context 預算 | 常駐只佔視窗 2.4%，**沒問題**；但四種關鍵識別碼全被漏掉 → **真問題，已補** |
| 3 | SKILL.md | 19 支業界真實 skill **全數不及格** → **尺壞了**，60 字元上限是用中文校準的 |
| 4 | 委派成本 | 工具點名的兩個「坑」，系統早就用正確機制繞開了 → **確認架構正確** |
| 5 | 測試品質 | 22 題的測試集只撐得起「25 個百分點以上」的改善宣稱 → **真問題** |

完整論證在 [`homework/`](homework/)，每一關一份。

---

## 三個最值得看的發現

### Lab 3：19 支真實 skill 全滅，所以我去拆規則

零支通過。當一個 linter 在公認品質不錯的語料上 100% 噴錯，要先懷疑的是規則。

- `description` 超過 60 字元：**19/19**。但工具自己的好例子是**中文** 37 字，
  19 支英文的最短 79、中位 154、最長 335。規則沒翻譯。
- 「用了 shell 指令名」7/19，逐一回原文看**全部是英文單字**——
  `find` 是動詞、`head-to-head` 是慣用語。
- 反過來，整批語料唯一一行真的 shell pipeline
  （`git log | grep ... | head -1 | awk ...`）**沒被抓到**，
  因為規則會先刪掉程式碼區塊——而該規則的立論正是「你寫什麼動詞 agent 就做什麼動作」。

唯一站得住的規則是「description 沒寫何時用」，只噴 **1/19**。
**語料在真正要緊的地方是強的，不及格幾乎全來自標題取名和字數。**

### Lab 2：課程推薦的策略，我的系統不能用

課程實測 Lean 小尾巴召回率 68.3%、完勝 Legacy 的 45.8%。照抄就是選 Lean。

但那 68.3% 是**搭配回溯搜尋**測的——小尾巴丟掉的靠事後搜尋找回來。
而 Dify workflow **沒有 session 回溯搜尋**，節點間傳的是變數不是可檢索的歷史。

所以真正的結論不是「選哪個」，是**兩個選項都在輸的那一邊，該先補回溯搜尋**。

### Lab 4：工具開的兩張罰單，系統兩個月前就解了

- 「每日食材監控必須活過重啟，你需要的是排程不是委派」→
  它**已經是排程**，掛在 Windows Task Scheduler，理由寫在啟動檔註解裡：
  政府 API 一次只回最近四天，漏掉一天永久補不回來。
- 「貼文排程啟動背景行程卻不等它」→
  用的是佇列＋發布前重審，原始碼註解給的理由更深一層：
  「佇列只記草稿，不記已核准這個狀態。規則是活的，核准不是。」

---

## 稽核帶出來的實際修正

量測工具輸出大小時撞到 `/ops schedule` 對所有呼叫端回 500——
排班模組回傳三元組，API 當成單一 DataFrame 接。

- 先寫會紅的測試（2 failed / 5 passed，確認紅得對），再修，7 passed
- 補上該專案的**第一組 Python 測試**（22 條）
- 修好後才量得到它是系統最大的工具輸出（3,806 tokens，第二名的五倍），
  改成預設回摘要後降到 563（**-85%**），並讓原本沒有 API 出口的人力缺口露出來

詳見 [`homework/`](homework/) 與該專案的 commit 紀錄。

---

## 目錄

```
homework/          五關的完整論證，一關一份
bistro_tools*.json Lab 1 輸入（忠實版／修正版／加新參數後）
bistro_plan.json   Lab 4 輸入，每個 task 有 _basis 欄位記錄數字怎麼估的
bistro_conversation.txt  Lab 2 的對話樣本
bistro_patterns.py Lab 2 第 4 題作答：用 import 擴充課程腳本，不改原檔
bistro_asserts_*.txt     Lab 5 Part A 兩版（直覺寫法／改寫成契約）
bistro_my_asserts.txt    後來實際補進系統的測試斷言，回頭用同一把尺量
```

## 重跑

課程腳本（`lab1_` ~ `lab5_`）**不在這個 repo 裡**——那是課程提供的教材，
授權未確認，不隨此專案散布。放進 `course-scripts/` 就能重跑：

```bash
mkdir course-scripts && cp /path/to/lab*.py course-scripts/
PYTHONIOENCODING=utf-8 python course-scripts/lab1_schema_lint.py bistro_tools.json --tools 5 --turns 30 --tasks 60
PYTHONIOENCODING=utf-8 python bistro_patterns.py bistro_conversation.txt
```

環境：Python 3.8+，只用標準函式庫。中文輸出要設 `PYTHONIOENCODING=utf-8`。
課程腳本的用法寫 `python3`，Windows 上要改成 `python`。

每一關的完整指令在 [`homework/`](homework/) 各自的檔案裡。

---

## 限制

- **token 數是本地估算不是 provider 實測**，不同 tokenizer 可差 ±20%
- **視窗大小 128K 是假設**，需向 provider 文件核對
- **Lab 1 是翻譯不是抽取**：受測系統是 Dify workflow，沒有現成的 function-calling schema。
  參數描述逐字保留，工具層描述用 Dify 節點的原始 instruction
- **Lab 4 是設計提案不是現況稽核**：系統目前零子代理
- **Lab 3 的語料不是受測系統**：它沒有 SKILL.md，所以這一關檢驗的是工具，不是系統
