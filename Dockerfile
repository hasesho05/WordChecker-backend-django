FROM python:3.8.6

ENV PYTHONUNBUFFERD 1
#ローカルのrequirements.txtをコンテナにコピー
COPY ./requirements.txt /requirements.txt
# requirements.txtに従ってパッケージを一括でインストール
RUN pip install -r /requirements.txt
# Djangoプロジェクトを置くディレクトリをコンテナ上に作成
RUN mkdir /app
# コンテナ上の作業ディレクトリを変更
WORKDIR /app
# カレントディレクトリにある資産をコンテナ上の指定のディレクトリにコピーする
ADD . /app
# コンテナポート8000番で受け付けるように起動
CMD python manage.py runserver 0.0.0.0:8000
