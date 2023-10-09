import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib

# データの読み込み
df = pd.read_excel('/Users/ootakazutaka/Desktop/課題アプリ/PLANTAR_FASCIITIS_APP 0924/predict_data.xlsx')
# 説明変数と目的変数の切り分け
t = df['post_vas'].values
x = df.drop(['post_vas','No','ID'], axis=1).values

# 学習データとテストデータの切り分け
x_train, x_test, t_train, t_test = train_test_split(x, t, test_size=0.3, random_state=1)

# モデルの宣言
model = LinearRegression()

# モデルの学習と推論
model.fit(x_train, t_train)
pred = model.predict(x_test)

# モデルの検証
print('train score : ', model.score(x_train, t_train))
print('test score : ', model.score(x_test, t_test))

# 学習済みモデルの保存
joblib.dump(model, 'predict.pkl', compress=True)

