#[plugin-vt]
glance_host = '192.168.5.107'
glance_port = 9292


def generate_glance_url():
    """Generate the URL to glance."""
    return "http://%s:%d" % (glance_host, glance_port)


#[plugin-advance]
#高级配置项，用于配置文件锁的位置
lock_path = '/var/run/'
