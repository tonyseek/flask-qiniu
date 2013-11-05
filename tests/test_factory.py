from flask import Flask
from flask.ext.qiniu import Qiniu, QiniuException, MissingKeyError
from pytest import fixture, raises
from mock import patch


qiniu = Qiniu()


def create_app():
    app = Flask(__name__)
    qiniu.init_app(app)
    return app


@fixture
def current_app(request):
    app = create_app()
    ctx = app.app_context()
    ctx.__enter__()
    request.addfinalizer(lambda: ctx.__exit__(None, None, None))
    return app


@fixture
def raw_app(request):
    app = Flask(__name__)
    ctx = app.app_context()
    ctx.__enter__()
    request.addfinalizer(lambda: ctx.__exit__(None, None, None))
    return app


def test_get_cow_without_init(raw_app):
    with raises(RuntimeError) as e:
        qiniu.cow
    assert repr(raw_app) in repr(e.value)


def test_get_cow(current_app):
    qiniu.cow


def test_missing_key(current_app):
    with raises(KeyError):
        qiniu.buckets
    with raises(QiniuException):
        qiniu.buckets
    with raises(MissingKeyError) as e:
        qiniu.buckets
    assert "QINIU_ACCESS_KEY" in str(e)

    current_app.config["QINIU_ACCESS_KEY"] = "exists"
    with raises(KeyError):
        qiniu.buckets
    with raises(QiniuException):
        qiniu.buckets
    with raises(MissingKeyError) as e:
        qiniu.buckets
    assert "QINIU_SECRET_KEY" in repr(e.value)


def test_get_buckets(current_app):
    current_app.config.update(dict(
        QINIU_ACCESS_KEY="QAK",
        QINIU_SECRET_KEY="QSK",
    ))

    with patch("sevencow.Cow.api_call") as api_call:
        qiniu.buckets
        api_call.assert_called_once_with("http://rs.qbox.me/buckets")
