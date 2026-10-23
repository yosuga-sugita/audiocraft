# 証明書更新（2026-10-23）

emSign / eMudhra の中間CA鍵漏えいに対応します。既存のアプリ用Python環境で実行してください。

```powershell
python -m pip install --upgrade -r requirements-security.txt
python tls_ca_maintenance.py --apply --backup-dir .tls-ca-backup-20261023
python tls_ca_maintenance.py
python -m pip check
```

通常の依存パッケージをインストール・更新した後にも、この順で実行してください。
certifi 2026.10.19以上、pip 26.2.2以上を使用します。gRPC / botocore が独自に持つCAファイルは、同梱スクリプトで対象ルート2枚のSHA-256を照合し、該当する証明書だけ除去します。GPU・音声・動画処理パッケージの版は変更しません。

最初の実行はバックアップ先を指定します。同じ場所のバックアップが既にあり、除去が再度必要なときは、新しいバックアップ先を指定してください。アプリを終了後、通常の起動方法で再起動するとメモリー内の証明書設定にも反映されます。

HTTPSの証明書検証は有効のまま使用します。社内CAが必要なら、HTTPXが対応するSSL_CERT_FILEで信頼済みCAファイルを指定してください。証明書検証を無効化して回避しないでください。

Node.jsを使う場合、24系は24.22.1以上を使用してください。Docker / Modalなどクラウド側は、各イメージのCAストアも別途更新・確認し、再ビルドと検証後の再デプロイが必要です。ローカル更新だけでは稼働中のコンテナは更新されません。

参考: https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576
技術資料: https://seclists.org/oss-sec/2026/q4/233

この更新手順のpip 26.2.2はPython 3.10以上が必要です。Python 3.9以下の実行環境・CI・コンテナでは、先に対応Pythonへの移行とアプリ互換性を確認してください。
