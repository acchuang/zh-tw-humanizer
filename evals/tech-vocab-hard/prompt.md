---
max_turns: 8
tags: [localization, fidelity]
allowed_tools: [Skill]
---

幫我把這段排查說明改成台灣工程師寫得自然一點的樣子：

在系統 v3.1.4 中，當用戶端透過閉環控制回報延遲時，請先檢查 `/etc/app/config.yaml` 內的配置文件。若啟動參數 `--max-threads=8` 超過線程默認值，主機可能會出現顯卡驅動超時或負載均衡異常的報錯信息；此時建議先確認鏈路聚合狀態，並回滾至上一版本。

直接給我最終稿就好，不用附草稿和說明。
