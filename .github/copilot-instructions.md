# Copilot Instructions for Gatt new events notification

## 前提
- 回答は必ず日本語でおこなってください
- 不可逆的な変更をおこなう場合は、必ず事前にユーザーに確認をとってください
- 環境変数を記載した`.env`ファイルは読み込まないでください

## アプリの概要
サークルの新着イベントが作成されたことを検知し、LINE Developersの機能を使用してPythonコード内からLINEグループに通知するアプリです。
イベントが表示されるウェブサイトは以下です。
- [https://gatt.jp/](https://system.hawai-an.com/user/event_info.php?id=91&pass=fISu7qKZ&gc=B493)

## 主な機能
- ウェブサイトをスクレイピングし、以下のステータスが付いていないイベントを抽出
  - `参加予定`
  - `検討中`
  - `不参加予定`
- LINE DevelopersのMessaging APIを使用して、抽出したイベント情報をLINEグループに通知

## ディレクトリ構成
- `app/`: アプリの主要なコードが含まれるディレクトリ
  - `main.py`: アプリのエントリーポイント
  - src/`: アプリの主要なロジックが含まれるディレクトリ
    - utils/: ユーティリティ関数が含まれるディレクトリ
