/////Japanese Version<br/>
このPythonプログラムは、翻訳業務委託サイトをリアルタイムで監視するシステムです。
プログラムが動作するPCには、BIOS設定で自動起動を有効にし、Windowsのタスクスケジューラを使用して、プログラムの開始・終了時刻およびPCの自動シャットダウンを設定しています。
プログラムは起動時、終了時、および1時間ごとにメールを送信し、外出先からでも正常に動作していることを確認できます。
メールアドレス、ID、パスワードを入力後、サイト上に新しい翻訳案件が掲載されたタイミングで自動的に検出し、以下の条件に基づいてフィルタリングを行います。

1. 登録住所からの距離
2. 希望する業務開始時間

条件を満たす業務が見つかると、**自動的に受託（仕事を取得）**します。
⚠️ 本リポジトリには、対象Webサイトやログイン情報などの機密情報は含まれていません。これらは .env ファイルを使ってローカルで管理しています。

🔐 セキュリティに関する注意
メールアドレス、ID、パスワードなどの認証情報は .env ファイルに保存し、GitHubにはアップロードしておりません。本リポジトリでは、これらの情報を共有しません。

📬 お問い合わせ
本プロジェクトに関してご質問がありましたら、お気軽にご連絡ください。
栗原 義彰（Yoshi Kurihara）
<br/>
<br/>
<hr/>
<br/>
/////English Version<br/>
This Python program is a real-time monitoring system for freelance translation job postings on a specific website.
The PC running the program is configured to start automatically via BIOS settings, and Windows Task Scheduler is used to define the program’s start and end times, as well as to perform automatic system shutdown.
The program sends email notifications at startup, shutdown, and every hour, allowing the user to remotely confirm that it is operating correctly.
After entering the email address, user ID, and password, the program automatically detects newly posted translation jobs on the website and filters them based on the following criteria.

1. Distance from your registered home address
2. Desired job start time

If a job meets the criteria, it will be automatically accepted on your behalf.

⚠️ Due to confidentiality, the specific website and login credentials are not included in this repository. Storing private information locally using a .env file.

🔐 Security Note
All authentication details (email, ID, password, etc.) must not be disclosed in this repogitory. These details are never uploaded to the repository.
