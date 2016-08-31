from .. import base

def getversion(obj):
    try:
        return obj.version
    except AttributeError:
        return obj


class Version(base.Resource):
    def __repr__(self):
        return "<Version>"


class VersionManager(base.ManagerWithFind):
    resource_class = Version

    def list(self):
        return self._list("../../", "versions")

    def get(self, version):
        return self._get("../../%s" % getversion(version), "version")

