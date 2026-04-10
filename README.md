# Plantar Fasciitis Prediction App

## 足底腱膜炎の治療効果予測アプリ

キカガク AI人材育成長期コース（2023年春受講）の卒業制作として開発したWebアプリケーションです。

---

## 背景と動機

理学療法士として13年間の臨床経験の中で、足底腱膜炎は頻繁に遭遇する疾患の一つです。しかし、治療効果には個人差が大きく、患者さんにとって「この治療を受けたらどのくらい改善するのか」が見えにくいという課題がありました。

**患者さんが治療を受ける前に、ある程度の効果を把握できるようにしたい。**
**患者さん自身が主体的に治療方法を選択する手段を作りたい。**

この想いから、患者さんの身体データを入力すると治療後の痛み（VAS）を予測するアプリを開発しました。

---

## 主な機能

### 治療効果の予測（メイン機能）
患者さんの年齢、性別、体重、身長、BMI、罹患期間、各種検査所見などを入力すると、治療後のVAS（Visual Analog Scale：痛みの指標）を予測します。

### データ管理
入力されたデータは Excel ファイルと SQLite データベースの両方に保存され、`/data` ページで一覧表示できます。

### ダッシュボード
Dash + Plotly によるインタラクティブな可視化ダッシュボードを `/dashboard/` で提供しています。散布図、箱ひげ図、円グラフ、サンバースト図、3D散布図でデータの傾向を確認できます。

---

## 技術スタック

| カテゴリ | 技術 |
|---------|------|
| Web フレームワーク | Flask |
| フォームバリデーション | WTForms |
| 機械学習 | scikit-learn（線形回帰） |
| データ処理 | pandas, NumPy |
| データ可視化 | Dash, Plotly |
| データベース | SQLite |
| Excel 操作 | openpyxl |
| モデル永続化 | joblib |

---

## セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/kazutaka-ohta/plantar_fasciitis_app.git
cd plantar_fasciitis_app

# 仮想環境を作成・有効化
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 依存パッケージをインストール
pip install -r requirements.txt

# アプリを起動
python src/app.py
```

ブラウザで `http://127.0.0.1:5000` を開くと、入力フォームが表示されます。

---

## 使い方

1. トップページ（`/`）で患者データを入力
2. 「予測値を算出する」ボタンを押すと、予測 VAS が表示される
3. 入力データは自動的に Excel と SQLite に保存される
4. `/data` ページで保存されたデータを一覧表示
5. `/dashboard/` ページでデータの可視化

---

## フォルダ構成

```
plantar_fasciitis_app/
├── README.md
├── .gitignore
├── requirements.txt
├── predict.pkl              # 学習済みモデル
├── src/
│   ├── app.py               # メインアプリケーション
│   ├── predict.py           # モデル訓練スクリプト
│   ├── dash_app.py          # Dash 単体版（学習中の試行錯誤）
│   ├── dash_callback.py     # Dash コールバック練習（学習中の試行錯誤）
│   └── templates/
│       ├── index.html       # 入力フォーム
│       ├── data.html        # データ一覧
│       └── result.html      # 予測結果
└── data/
    └── predict_data.xlsx    # 訓練用ダミーデータ
```

---

## データについて

本リポジトリに含まれる `predict_data.xlsx` は **ChatGPT で生成したダミーデータ**です。実際の患者データは含まれていません。

ダミーデータで訓練しているため、モデルの予測精度は低い値になっています（train: 0.165, test: -0.176）。これは**データの質に起因するもの**であり、アプリの構造やアルゴリズムの問題ではありません。

---

## 当時の実装と、今の視点

このアプリは2023年春の学習成果をそのまま残しています。現在の視点から見た改善点を記録します。

### dash_app.py / dash_callback.py について
これらのファイルはメインの `app.py` からは使用されていません。Dash の学習過程で作成した試行錯誤のファイルです。`app.py` の中にDashの設定を直接記述する形で統合しました。

### FigureWidget の使用
Plotly の `go.FigureWidget()` は本来 Jupyter Notebook 向けのクラスです。Webアプリでは不要ですが、当時の講座テキストに沿って使用しています。動作には `anywidget` パッケージが必要です。

### secret_key のハードコード
`app.secret_key` にプレースホルダー値をハードコードしています。学習用アプリのため、環境変数化は行っていません。本番環境では環境変数で管理するべきです。

---

## 学んだこと

- **Webアプリの全体像**: Flask によるルーティング、テンプレートエンジン、フォーム処理の基礎
- **機械学習のワークフロー**: データ読み込み → 前処理 → 学習 → 推論 → 保存の一連の流れ
- **データの永続化**: Excel と SQLite、2つの保存方法の実装と使い分け
- **データの可視化**: Dash + Plotly でインタラクティブなグラフを構築する方法
- **臨床課題のプロダクト化**: 臨床現場の課題を「動くアプリ」として形にする経験

---

## その後の展開

この卒業制作での学びをベースに、臨床現場で実際に稼働する AI プロダクトの開発に取り組んでいます。

- **ESWT 治療効果予測モデル**（FastAPI + SQLite + scikit-learn）
- **院内マニュアル AI**（Claude API + Notion RAG）
- **クリニック経営ダッシュボード**（CSV/Excel 可視化）

詳細は [Zenn](https://zenn.dev/kinecode) で発信していきます。

---

## 作者

**大田 一貴（Kazutaka Ohta）**
理学療法士 / 13年の臨床経験 / Healthcare AI Product Developer

- GitHub: [@kazutaka-ohta](https://github.com/kazutaka-ohta)
- Zenn: [zenn.dev/kinecode](https://zenn.dev/kinecode)
- X: [@Bz1531](https://twitter.com/Bz1531)

---

## ライセンス

MIT License
