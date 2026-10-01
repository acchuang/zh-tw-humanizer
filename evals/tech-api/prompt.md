---
max_turns: 8
tags: [localization, fidelity]
allowed_tools: [Skill]
---

此接口用於獲取用戶信息。請求方式為 `GET /v1/users/{id}`。當請求頻率過高時，服務器將返回 429 狀態碼，並在響應頭中附帶 `Retry-After` 欄位，提示客戶端稍後重試。

直接給我最終稿就好，不用附草稿和說明。
