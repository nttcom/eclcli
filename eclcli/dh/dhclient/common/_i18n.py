import oslo_i18n


# NOTE(dhellmann): This reference to o-s-l-o will be replaced by the
# application name when this module is synced into the separate
# repository. It is OK to have more than one translation function
# using the same domain, since there will still only be one message
# catalog.
_translators = oslo_i18n.TranslatorFactory(domain='dhclient')

# The primary translation function using the well-known name "_"
_ = _translators.primary

# Translators for log levels.
#
# The abbreviated names are meant to reflect the usual use of a short
# name like '_'. The "L" is for "log" and the other letter comes from
# the level.
_LI = _translators.log_info
_LW = _translators.log_warning
_LE = _translators.log_error
_LC = _translators.log_critical
