EXT_NS = '_extension_ns'
XML_NS_V20 = 'http://openstack.org/quantum/api/v2.0'
XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XSI_ATTR = "xsi:nil"
XSI_NIL_ATTR = "xmlns:xsi"
TYPE_XMLNS = "xmlns:quantum"
TYPE_ATTR = "quantum:type"
VIRTUAL_ROOT_KEY = "_v_root"
ATOM_NAMESPACE = "http://www.w3.org/2005/Atom"
ATOM_XMLNS = "xmlns:atom"
ATOM_LINK_NOTATION = "{%s}link" % ATOM_NAMESPACE

TYPE_BOOL = "bool"
TYPE_INT = "int"
TYPE_LONG = "long"
TYPE_FLOAT = "float"
TYPE_LIST = "list"
TYPE_DICT = "dict"

PLURALS = {'networks': 'network',
           'ports': 'port',
           'subnets': 'subnet',
           'subnetpools': 'subnetpool',
           'dns_nameservers': 'dns_nameserver',
           'host_routes': 'host_route',
           'allocation_pools': 'allocation_pool',
           'fixed_ips': 'fixed_ip',
           'extensions': 'extension'}
