# ブックレビュー
書籍レビューサイト
[ブックレビュー](https://book-review.ml/){:target="_blank"} 

# 概要
書籍専用のレビュー共有サイトです。
読んだ書籍の感想を残したり、他のユーザのレビューを元に新しい１冊を見つけましょう！

# 機能・使用技術一覧
- 技術一覧
  - 言語/フレームワーク
    - Python3.7.3
    - Django2.2.4
  - インフラ(AWS)
    - EC2(サービス稼働基盤)
    - Route53・EIP(独自ドメイン)
    - S3(ファイル保存)
    - CloudFront(静的ファイル配信)
    - SES(メール配信)
  - データベース
    - PostgreSQL10.10
- 機能一覧
  - ソーシャルログイン(django-allauth)
  - 画像アップロード(django-storages)
  - 書籍検索(楽天API)
  - ページネーション
  - フォロー機能
  - お気に入り機能
  - 単体テスト(factory_boy)
- 開発環境
  - Docker
  - Docker-Compose
    - Webアプリケーション(Django)・Webサーバ(Nginx)・Database(PostgreSQL)
- CI/CD
  - CircleCI

