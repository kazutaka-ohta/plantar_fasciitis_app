import joblib
from flask import Flask, request,render_template, redirect, url_for, flash
from wtforms import Form, FloatField, SubmitField, validators, StringField, PasswordField, BooleanField, RadioField, SelectField, ValidationError
import numpy as np
import pandas as pd
import openpyxl
from openpyxl import Workbook

def predict(x):
    # 学習済みモデル（predict.pkl）を読み込み
    model = joblib.load('./src/predict.pkl')
    x = x.reshape(1,-1)
    pred_data = model.predict(x)
    return pred_data

# Flaskのインスタンスを作成
app  = Flask(__name__)
app.secret_key = "your_secret_key_here"

    # 入力フォームの設定を行うクラス
class PlantarForm(Form):
    ID = FloatField('ID (0 ~ 999999)',
                    [validators.InputRequired(),
                    validators.NumberRange(min=0, max=999999, message='対象者のIDを入力してください')])

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

def add_to_excel(ID,gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas):
    file_path = '/Users/ootakazutaka/Desktop/PLANTAR_FASCIITIS_APP/plantar_fasciitis_data2.xlsx'  # エクセルファイルの場所を指定

    # 既存のエクセルファイルを読み込む。存在しない場合は新しいDataFrameを作成
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
    except FileNotFoundError:
        df = pd.DataFrame(columns=[ID, gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas])

    # 新しいデータをDataFrameに追加
    new_data = {'ID': ID, 'Gender': gender, 'Weight': weight, 'height': height, 'bmi': bmi, 'period': period, 'sports_history': sports_history, 'steroid': steroid, 'calcaneal_spur': calcaneal_spur, 'thickness': thickness, 'blood_flow': blood_flow, 'd_flex': d_flex, 'p_flex': p_flex, 'mp_ex': mp_ex, 'pre_vas': pre_vas}
    df = df.append(new_data, ignore_index=True)

    # 変更をエクセルファイルに保存
    df.to_excel(file_path, index=False, engine='openpyxl')


# URL にアクセスがあった場合の挙動の設定
@app.route('/', methods = ['GET', 'POST'])
def predicts():
    # フォームの設定 IrsiForm クラスをインスタンス化
    plantarform = PlantarForm(request.form)
    # POST メソッドの定義
    if request.method == 'POST':

        # 条件に当てはまる場合
        if plantarform.validate() == False:
            return render_template('index.html', forms=plantarform)
        # 条件に当てはまらない場合、推論を実行
        else:
            ID = float(request.form['ID'])
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

            save_to_excel(ID,gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas)

            flash('Data has been saved to Excel file')

            # 入力された値を ndarray に変換して推論
            x = np.array([gender, weight, height, bmi, period, sports_history, steroid,  calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas])
            pred = predict(x)
            plantar_score_ = pred

            return render_template('result.html', plantar_score=plantar_score_)

    # GET メソッドの定義
    elif request.method == 'GET':
        return render_template('index.html', forms=plantarform)
    
def save_to_excel(ID,gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas):
    file_path = 'data.xlsx'

    # Check if the file already exists
    try:
        wb = openpyxl.load_workbook(file_path)
    except FileNotFoundError:
        wb = Workbook()
        ws = wb.active
        ws.append([ID,gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas])  # headers

    ws = wb.active

    # Append new data
    ws.append([ID,gender, weight, height, bmi, period, sports_history, steroid, calcaneal_spur, thickness, blood_flow, d_flex, p_flex, mp_ex, pre_vas])

    # Save the changes
    wb.save(file_path)

    # アプリケーションの実行
if __name__ == '__main__':
    app.run()