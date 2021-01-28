from xmlrpc.client import ServerProxy


def stop_node_service(ip_port):
    try:
        s = ServerProxy("http://%s" % ip_port)
        res = s.stop_server()
        return res
    except TimeoutError:
        return 'Node connection timeout!'
    except AttributeError:
        return 'Node function not exists!'
    except ConnectionRefusedError:
        return 'Node connection refused!'
    except Exception as e:
        return f'Node Error: {e.__str__()[:256]}...'


def update_node_service(ip_port):
    try:
        s = ServerProxy("http://%s" % ip_port)
        res = s.update_node()
        return res
    except TimeoutError:
        return 'Node connection timeout!'
    except AttributeError:
        return 'Node function not exists!'
    except ConnectionRefusedError:
        return 'Node connection refused!'
    except Exception as e:
        print(e.__str__())
        return f'Node Error: {e.__str__()[:256]}...'




