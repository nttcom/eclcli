try:
    import oslo_i18n as i18n
except Exception:
    from oslo import i18n

_translators = i18n.TranslatorFactory(domain='sssclient')

_ = _translators.primary

_LI = _translators.log_info
_LW = _translators.log_warning
_LE = _translators.log_error
_LC = _translators.log_critical
