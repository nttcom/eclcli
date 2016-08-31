from .. import base


def getname(obj):
    try:
        return obj.name
    except AttributeError:
        return obj


class User(base.Resource):
    HUMAN_ID = True

    def __repr__(self):
        return '<User: %s>' % getattr(self, 'name', 'unknown-name')

    def delete(self):
        self.manager.delete(self)

    def update(self, name=None):
        self.manager.update(self, name=name)


class UserManager(base.BootingManagerWithFind):
    resource_class = User

    def get(self, user):
        return self._get("/users/%s" % getname(user), "user")

    def list(self):
        return self._list("/users", "users")

    def create(self, name="", password=None, **kwargs):
        body = {
            "user": {}
        }

        if name:
            body["user"]["name"] = name

        if password:
            body["user"]["password"] = password

        return self._create("/users", body, "user")

    def update(self, user, password=None):
        body = {
            "user": {
            }
        }
        if password:
            body['user']['password'] = password
        return self._update("/users/%s" % getname(user), body, "")

    def delete(self, user):
        return self._delete("/users/%s" % getname(user))
