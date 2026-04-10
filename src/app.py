import joblib
from flask import Flask, request,render_template, redirect, url_for, flash
from wtforms import Form, FloatField, SubmitField, validators, StringField, PasswordField, BooleanField, RadioField, SelectField, ValidationError
import numpy as np
import pandas as pd
import openpyxl
from openpyxl import Workbook
import sqlite3
import dash
from dash import dcc, html
from flask import Flask
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 学習済みモデル（predict.pkl）を読み込み
def predict(x):
    model = joblib.load('predict.pkl')
    x = x.reshape(1,-1)
    pred_data = model.predict(x)
    return pred_data

# Flaskのインスタンスを作成
app  = Flask(__name__)
app.secret_key = "your_secret_key_here"

# dashページ
app_dash = dash.Dash(__name__, server = app, url_base_pathname='/dashboard/', external_stylesheets=[dbc.themes.UNITED, dbc.icons.BOOTSTRAP])

# Read the files
df = pd.read_excel('./data/predict_data.xlsx')

# Build the Components
# Header Components
Header_component = html.H1("Plantar Fasciitis Analysis Dashboard", style = {'color': 'darkcyan', 'text-align': 'center', 'font-size': '72px'})

# Visual Components
# Component1
scatterfig = px.scatter(df, x='age', y='pre_vas', color='weight', size='height')
scatterfig.update_layout(title = '年齢、体重と治療前の痛みの関係性')
scatterfig = go.FigureWidget(scatterfig)

# Component2
boxfig = px.box(df,x='gender',y='pre_vas',color='steroid',notched=False,points='all',title='ステロイド使用の有無における性別ごとの違い')
boxfig.update_layout(title = '箱ひげ図')
boxfig = go.FigureWidget(boxfig)

# Component3
piefig = px.pie(df,names=('gender'))
piefig.update_layout(title = '性別ごとの割合')
piefig = go.FigureWidget(piefig)

# Component4
sunburstfig = px.sunburst(df,path=['gender','sports_history'],)
sunburstfig.update_layout(title = '性別ごとのスポーツ歴')
sunburstfig = go.FigureWidget(sunburstfig)

# Component5
scatter3dfig = px.scatter_3d(df,x='d_flex',y='p_flex',z='pre_vas',size='weight',color='steroid',hover_data=['post_vas'])
scatter3dfig.update_layout(title = '3D散布図')
scatter3dfig = go.FigureWidget(scatter3dfig)

# Design the app layout
app_dash.layout = html.Div([
        dbc.Row(Header_component),
        dbc.Row([
            dbc.Col([dcc.Graph(figure = scatterfig)]),
            dbc.Col([dcc.Graph(figure = boxfig)]
        )]),
        dbc.Row([
            dbc.Col([dcc.Graph(figure = piefig)]),
            dbc.Col([dcc.Graph(figure = sunburstfig)]),
            dbc.Col(dcc.Graph(figure = scatter3dfig))
        ]),
])


# 入力フォームの設定を行うクラス
class PlantarForm(Form):
    ID = FloatField('ID (0 ~ 999999)',
                    [validators.InputRequired(),
                    validators.NumberRange(min=0, max=999999, message='対象者のIDを入力してください')])
    
    age = FloatField('年齢 (0歳 ~ 200歳)',
                    [validators.InputRequired(),
                    validators.NumberRange(min=0, max=200, message='0〜200で入力してください')])

    gender = RadioField(label='性別', choices=[
                        ('0', '男性'), ('1', '女性')])

    weight = FloatField('体重 (0kg ~ 200kg)',
                    [validators.InputRequired(),
                    validators.NumberRange(min=0, max=200, message='0〜200で入力してください')])
    
    height = FloatField('身長 (0cm ~ 200cm)',
                    [validators.InputRequired(),
                    validators.NumberRange(min=0, max=200, message='0〜200で入力してください')])
    
    bmi = FloatField('BMI (体重/身長m^2)',
                    [validators.InputRequired(),
                    validators.NumberRange(min=0, max=50, message='0〜50で入力してください')])

    period  = FloatField('罹患期間 (0ヶ月 ~ 60ヶ月)',
                    [validators.InputRequired(),
                    validators.NumberRange(min=0, max=60, message='0〜60の数値を入力してください')])
    
    sports_history = RadioField(label='スポーツ歴の有無', choices=[
                        ('0', 'なし'), ('1', 'あり')])
    
    steroid = RadioField(label='ステロイド治療歴の有無', choices=[
                        ('0', 'なし'), ('1', 'あり')])
    
    calcaneal_spur = RadioField(label='踵骨棘の有無', choices=[
                        ('0', 'なし'), ('1', 'あり')])
    
    thickness = FloatField('足底腱膜の厚さ',
                    [validators.InputRequired(),
                    validators.NumberRange(min=0, max=100, message='0〜100の数値を入力してください')])
    
    blood_flow = RadioField(label='足底腱膜への血流の有無', choices=[
                        ('0', 'なし'), ('1', 'あり')])
    
    d_flex = FloatField('背屈可動域',
                    [validators.InputRequired(),
                    validators.NumberRange(min=0, max=100, message='0〜100の数値を入力してください')])
    
    p_flex = FloatField('底屈可動域',
                    [validators.InputRequired(),
                    validators.NumberRange(min=0, max=100, message='0〜100の数値を入力してください')])
    
    mp_ex = FloatField('MP関節伸展可動域',
                    [validators.InputRequired(),
                    validators.NumberRange(min=0, max=100, message='0〜100の数値を入力してください')])
    
    pre_vas = FloatField('治療前のVAS',
                    [validators.InputRequired(),
                    validators.NumberRange(min=0, max=10, message='0〜10の数値を入力してください')])

    # html 側で表示する submit ボタンの設定
    submit = SubmitField('予測値を算出する')

def add_to_excel(ID, age, gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas):
    file_path = './data/plantar_fasciitis_data2.xlsx'  # エクセルファイルの場所を指定

    # 既存のエクセルファイルを読み込む。存在しない場合は新しいDataFrameを作成
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
    except FileNotFoundError:
        df = pd.DataFrame(columns=[ID, age, gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas])

    # 新しいデータをDataFrameに追加
    new_data = {'ID': ID, 'age': age, 'Gender': gender, 'Weight': weight, 'height': height, 'bmi': bmi, 'period': period, 'sports_history': sports_history, 'steroid': steroid, 'calcaneal_spur': calcaneal_spur, 'thickness': thickness, 'blood_flow': blood_flow, 'd_flex': d_flex, 'p_flex': p_flex, 'mp_ex': mp_ex, 'pre_vas': pre_vas}
    df = df.append(new_data, ignore_index=True)

    # 変更をエクセルファイルに保存
    df.to_excel(file_path, index=False, engine='openpyxl')


# URL にアクセスがあった場合の挙動の設定
@app.route('/', methods = ['GET', 'POST'])
def predicts():
    # フォームの設定 Form クラスをインスタンス化
    plantarform = PlantarForm(request.form)
    # POST メソッドの定義
    if request.method == 'POST':

        # 条件に当てはまる場合
        if plantarform.validate() == False:
            return render_template('index.html', forms=plantarform)
        # 条件に当てはまらない場合、推論を実行
        else:
            ID = float(request.form['ID'])
            age = float(request.form['age'])
            gender = float(request.form['gender'])
            weight = float(request.form['weight'])
            height = float(request.form['height'])
            bmi = float(request.form['bmi'])
            period = float(request.form['period'])
            sports_history = float(request.form['sports_history'])
            steroid = float(request.form['steroid'])
            calcaneal_spur = float(request.form['calcaneal_spur'])
            thickness = float(request.form['thickness'])
            blood_flow = float(request.form['blood_flow'])
            d_flex = float(request.form['d_flex'])
            p_flex = float(request.form['p_flex'])
            mp_ex = float(request.form['mp_ex'])
            pre_vas = float(request.form['pre_vas'])

            save_to_excel(ID, age, gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas)

            # SQLiteにも保存
            con = sqlite3.connect(DATABASE)
            con.execute('INSERT INTO plantars VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        [ID, age, gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas])
            con.commit()
            con.close()
            flash('Data has been saved to Excel and SQLite')

            # 入力された値を ndarray に変換して推論
            x = np.array([age, gender, weight, height, bmi, period, sports_history, steroid,  calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas])
            pred = predict(x)
            plantar_score_ = pred

            return render_template('result.html', plantar_score=plantar_score_)

    # GET メソッドの定義
    elif request.method == 'GET':
        return render_template('index.html', forms=plantarform)

def save_to_excel(ID,age, gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas):
    file_path = 'data.xlsx'

    # 既存のエクセルファイルがあるか確認
    try:
        wb = openpyxl.load_workbook(file_path)
    except FileNotFoundError:
        wb = Workbook()
        ws = wb.active
        ws.append([ID, age, gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas])  # headers

    ws = wb.active

    # Append new data
    ws.append([ID, age, gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas])

    # Save the changes
    wb.save(file_path)


# データベースの構築
DATABASE = 'database.db'
def create_plantars_table():
    con = sqlite3.connect(DATABASE)
    con.execute("CREATE TABLE IF NOT EXISTS plantars (ID, age, gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas)")
    con.close()
create_plantars_table()

# データベースの表示ページへ遷移
@app.route('/data')
def data():
    con = sqlite3.connect(DATABASE)
    db_plantars = con.execute('SELECT * FROM plantars').fetchall()
    con.close()

    plantars = []
    for row in db_plantars:
        plantars.append({'ID': row[0], 'age': row[1], 'gender': row[2], 'weight': row[3], 'height': row[4], 'bmi': row[5], 'period': row[6], 'sports_history': row[7], 'steroid': row[8], 'calcaneal_spur': row[9], 'thickness': row[10], 'blood_flow': row[11], 'd_flex': row[12], 'p_flex': row[13], 'mp_ex': row[14], 'pre_vas': row[15]})
    return render_template(
        'data.html',
        plantars=plantars
        )

# データベースへの登録
@app.route('/register', methods=['post'])
def register():
    ID = request.form['ID']
    age = request.form['age']
    gender = request.form['gender']
    weight = request.form['weight']
    height = request.form['height']
    bmi = request.form['bmi']
    period = request.form['period']
    sports_history = request.form['sports_history']
    steroid = request.form['steroid']
    calcaneal_spur = request.form['calcaneal_spur']
    thickness = request.form['thickness']
    blood_flow = request.form['blood_flow']
    d_flex = request.form['d_flex']
    p_flex = request.form['p_flex']
    mp_ex = request.form['mp_ex']
    pre_vas = request.form['pre_vas']

    con = sqlite3.connect(DATABASE)
    con.execute('INSERT INTO plantars VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                [ID, age, gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas])
    con.commit()
    con.close()
    return redirect( url_for('data'))

# 可視化ページ
@app.route('/dashboard/')
def dashboard():
    return app.index()

    # アプリケーションの実行
if __name__ == '__main__':
    app.run()