/////Japanese Version<br/>
このPythonプログラムは、翻訳業務委託のWebサイトをリアルタイムで監視するシステムです。
Email、ID、パスワードを入力後、サイト上に新しい翻訳業務が掲載されたタイミングで自動的に検出し、以下のパラメータに基づいてフィルタリングを行います：

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
This Python program serves as a real-time monitoring system for a translation subcontracting job website.
After entering email, user ID, and password, the script continuously monitors the website for newly posted translation jobs. When a new job appears, the program automatically filters listings based on customizable parameters such as:

1. Distance from your registered home address
2. Desired job start time

If a job meets the criteria, it will be automatically accepted on your behalf.

⚠️ Due to confidentiality, the specific website and login credentials are not included in this repository. Storing private information locally using a .env file.

🔐 Security Note
All authentication details (email, ID, password, etc.) must not be disclosed in this repogitory. These details are never uploaded to the repository.
