---
name: commit
description: "ステージされたコードの差分を分析してコミットメッセージを生成し、git commit を実行するスキル。Use when: committing staged changes, generating commit message, git commit, コミットメッセージを作成, ステージされた変更をコミット, コミットしたい"
argument-hint: "追加のコンテキストや指示（省略可）"
---

# Commit Skill

ステージ済みの変更差分を解析し、適切なコミットメッセージを生成して `git commit` を実行します。

## When to Use

- `git add` でステージした変更をコミットしたいとき
- コミットメッセージを自動生成したいとき
- Conventional Commits 形式でメッセージを統一したいとき

## Procedure

### 1. ステージ済み差分の取得

ターミナルで以下を実行して差分を取得する:

```bash
git diff --staged
```

差分が空の場合はステージされた変更がないため、ユーザーに `git add` を促して終了する。

### 2. コミットメッセージの生成

取得した差分を分析し、以下の **Conventional Commits** 形式でメッセージを生成する:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**type の選択基準:**

| type | 使用場面 |
|------|---------|
| `feat` | 新機能の追加 |
| `fix` | バグ修正 |
| `docs` | ドキュメントのみの変更 |
| `style` | コードの動作に影響しない変更（空白、フォーマット等） |
| `refactor` | バグ修正でも機能追加でもないコード変更 |
| `test` | テストの追加・修正 |
| `chore` | ビルドプロセス・補助ツールの変更 |
| `perf` | パフォーマンス改善 |
| `ci` | CI/CD 設定の変更 |

**メッセージ生成ルール:**
- `subject` は命令形・現在形で50文字以内（日本語）
- `scope` は変更対象のモジュール・ファイル名（省略可）
- 複数の変更種別が含まれる場合は最も重要な `type` を選ぶ
- body には変更の動機や背景を記載する（必要な場合のみ）

### 3. ユーザーへの確認

生成したコミットメッセージをユーザーに提示し、確認を求める:

```
以下のコミットメッセージでコミットします:

---
<生成したコミットメッセージ>
---

このメッセージでよいですか？修正が必要であれば指示してください。
```

### 4. git commit の実行

ユーザーの承認後、以下を実行する:

```bash
git commit -m "<subject行>" -m "<body（存在する場合）>"
```

body が不要な場合は `-m` を1つだけ使用する。

### 5. 結果の確認

コミット成功後、以下を実行してコミット内容を確認する:

```bash
git log --oneline -1
```

## Notes

- ステージされていないファイルは対象外。必要に応じてユーザーに `git add` を案内する。
- `git diff --staged` の出力が大きい場合は、変更ファイル一覧 (`git diff --staged --name-status`) も参照して要約する。
- breaking change がある場合は footer に `BREAKING CHANGE: <説明>` を追記する。
