from werkzeug.utils import cached_property
from flask import current_app
from sevencow import Cow, Bucket


def get_extension_item(name, app=None):
    app = current_app if app is None else app
    items = getattr(app, "extensions", {})
    if name not in items:
        raise RuntimeError("%r has not been initialized" % app)
    return items[name]


class LazyCow(Cow):
    """The Cow which use lazy-loading access key and secret key."""

    def __init__(self):
        super(LazyCow, self).__init__(None, None)
        del self.access_key
        del self.secret_key

    @cached_property
    def access_key(self):
        return self._load_from_config("QINIU_ACCESS_KEY")

    @cached_property
    def secret_key(self):
        return self._load_from_config("QINIU_SECRET_KEY")

    def _load_from_config(self, key):
        value = current_app.config[key]
        if not value:
            raise MissingKeyError("missing %s" % key)
        return value


class Qiniu(object):
    """The extension of Qiniu storage service."""

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault("QINIU_ACCESS_KEY", None)
        app.config.setdefault("QINIU_SECRET_KEY", None)

        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["qiniu.cow"] = LazyCow()
        app.extensions["qiniu.buckets"] = {}

    @property
    def cow(self):
        return get_extension_item("qiniu.cow")

    @property
    def buckets(self):
        buckets = get_extension_item("qiniu.buckets")
        if not buckets:
            buckets.update({name: Bucket(self.cow, name)
                            for name in self.cow.list_buckets() or []})
        return buckets

    def add_bucket(self, bucket_name):
        buckets = get_extension_item("qiniu.buckets")
        if bucket_name in buckets:
            raise KeyError("%r exists" % bucket_name)
        buckets[bucket_name] = Bucket(self.cow, bucket_name)
        return buckets[bucket_name]

    def __getattr__(self, bucket_name):
        if bucket_name in self.buckets:
            return self.buckets[bucket_name]
        raise AttributeError("no such bucket: %r" % bucket_name)


class QiniuException(Exception):
    pass


class MissingKeyError(QiniuException, KeyError):
    pass
