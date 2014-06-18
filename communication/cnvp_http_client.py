# coding:utf-8
import urllib2
import json
import random
from slice.slice_exception import VirttoolError
from etc.config import virttool_disable
import traceback

RE_CONNECT_MAX_NUM = 5
CUR_RE_CONNECT_NUM = 0


def buildRequest(url, cmd):
    random_id = random.randint(0, 100)
    j = {"jsonrpc": "2.0",
         "method": "cnvp_jsonrpc_service",
         "params": {"command": cmd},
         "id": str(random_id)}
    h = {"Content-Type": "application/json"}
    return urllib2.Request(url, json.dumps(j), h)


def parseResponse(data):
    resp = json.loads(data)
    if "error" in resp:
        result = resp["error"]
        print result["code"]
        print result["message"]
        return [{"resultcode": 1, "resultmsg": "json foam error"}]
    if "result" in resp:
        result = resp["result"]
    else:
        return [{"resultcode": 2, "resultmsg": "json foam error"}]
    print result[0]["resultcode"]
    print result[0]["resultmsg"]
    return result


def cnvp_service(cmd, url):
    global RE_CONNECT_MAX_NUM
    global CUR_RE_CONNECT_NUM
    print cmd
    print url
    if virttool_disable:
        return [{"resultcode": 0, "resultmsg": "virttool_disable"}]
    try:
        req = buildRequest(url, cmd)
        ph = urllib2.urlopen(req)
        ret = parseResponse(ph.read())
        CUR_RE_CONNECT_NUM = 0
        return ret
    except RuntimeError, e:
        print "cnvp error2"
        traceback.print_exc()
        CUR_RE_CONNECT_NUM = 0
        raise
    except Exception, e:
        print "cnvp error1"
        print "CUR_RE_CONNECT_NUM", CUR_RE_CONNECT_NUM
        traceback.print_exc()
        if CUR_RE_CONNECT_NUM < RE_CONNECT_MAX_NUM and\
            (str(e) == '<urlopen error [Errno 104] Connection reset by peer>' or str(e) == "''"):
            CUR_RE_CONNECT_NUM = CUR_RE_CONNECT_NUM + 1
            return cnvp_service(cmd, url)
        else:
            CUR_RE_CONNECT_NUM = 0
            raise


class CnvpClient(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.url = 'http://{}:{}'.format(self.ip, self.port)

    def add_slice(self, slice_name, controller_ip, controller_port):
        try:
            cmd = "add slice -s " + str(slice_name) + " -t tcp -i " + \
                controller_ip + " -p " + str(controller_port)
            ret = cnvp_service(cmd, self.url)
            if ret[0]["resultcode"] != 0:
                raise VirttoolError("虚网创建失败!")
        except:
            raise VirttoolError("虚网创建失败!")

    def show_slice(self, slice_name):
        try:
            if slice_name:
                cmd = "show slice -s " + str(slice_name)
            else:
                cmd = "show slice"
            ret = cnvp_service(cmd, self.url)
            if ret[0]["resultcode"] != 0:
                raise VirttoolError("虚网信息获取失败!")
            else:
                slices = []
                if len(ret) > 1:
                    for slice_ret in ret[1:]:
                        slice_obj = {'slice_name': slice_ret["slice_name"]}
                        slice_obj['controller_ip'] = slice_ret["controller_ip"]
                        slice_obj['controller_port'] = slice_ret["controller_port"]
                        slice_obj['state'] = slice_ret["slice_state_value"]
                        slices.append(slice_obj)
                print slices
                return slices
        except:
            raise VirttoolError("虚网信息获取失败!")

    def change_slice_controller(self, slice_name, controller_ip, controller_port):
        try:
            cmd = "update slice -s " + str(slice_name) + " -t tcp -i " + \
                controller_ip + " -p " + str(controller_port)
            ret = cnvp_service(cmd, self.url)
            if ret[0]["resultcode"] != 0:
                raise VirttoolError("控制器更新失败!")
        except:
            raise VirttoolError("控制器更新失败!")

    def start_slice(self, slice_name):
        try:
            cmd = "start slice -s " + str(slice_name)
            ret = cnvp_service(cmd, self.url)
            if ret[0]["resultcode"] != 0:
                if ret[0]["resultcode"] == 3758125058 and ret[0]["resultmsg"] == "slice is running already!":
                    pass
                else:
                    raise VirttoolError("虚网启动失败!")
        except:
            raise VirttoolError("虚网启动失败!")

    def stop_slice(self, slice_name):
        try:
            cmd = "stop slice -s " + str(slice_name)
            ret = cnvp_service(cmd, self.url)
            if ret[0]["resultcode"] != 0:
                if ret[0]["resultcode"] == 3758125057 and ret[0]["resultmsg"] == "slice is NOT running!":
                    pass
                else:
                    raise VirttoolError("虚网停止失败!")
        except:
            raise VirttoolError("虚网停止失败!")

    def delete_slice(self, slice_name):
        try:
            cmd = "delete slice -s " + str(slice_name)
            ret = cnvp_service(cmd, self.url)
            if ret[0]["resultcode"] != 0:
                if ret[0]["resultcode"] == 3758125059 and ret[0]["resultmsg"] == "slice name is NOT exist!":
                    pass
                else:
                    raise VirttoolError("虚网删除失败!")
        except:
            raise VirttoolError("虚网删除失败!")

    def add_port(self, slice_name, dpid, port):
        try:
            cmd = "add port -s " + str(slice_name) + " -d " + dpid + " -p " + str(port)
            ret = cnvp_service(cmd, self.url)
            if ret[0]["resultcode"] != 0:
                raise VirttoolError("端口添加失败!")
        except:
            raise VirttoolError("端口添加失败!")

    def delete_port(self, slice_name, dpid, port):
        try:
            if dpid and port:
                cmd = "delete port -s " + str(slice_name) + " -d " + dpid + " -p " + str(port)
            else:
                cmd = "delete port -s " + str(slice_name)
            ret = cnvp_service(cmd, self.url)
            if ret[0]["resultcode"] != 0:
                if ret[0]["resultcode"] == 3758120963 and ret[0]["resultmsg"] == "no port in this slice!":
                    pass
                else:
                    raise VirttoolError("端口删除失败!")
        except:
            raise VirttoolError("端口删除失败!")

    def add_flowspace(self, slice_name, slice_action, dpid, priority, arg_match):
        try:
            cmd = "add flowspace -p " + str(priority) + " -d " + dpid + " -m " + \
                arg_match + " -a Slice:" + str(slice_name) + "=" + str(slice_action)
            ret = cnvp_service(cmd, self.url)
            if ret[0]["resultcode"] != 0:
                raise VirttoolError("流规则添加失败!")
        except:
            raise VirttoolError("流规则添加失败！")

    def delete_flowspace(self, slice_name, flowspace_id):
        try:
            if flowspace_id:
                cmd = "delete flowspace -s " + str(slice_name) + " -r " + str(flowspace_id)
            else:
                cmd = "delete flowspace -s " + str(slice_name)
            ret = cnvp_service(cmd, self.url)
            if ret[0]["resultcode"] != 0:
                raise VirttoolError("流规则删除失败!")
        except:
            raise VirttoolError("流规则删除失败！")

    def get_switches(self):
        try:
            cmd = "show switch"
            ret = cnvp_service(cmd, self.url)
            if ret[0]["resultcode"] != 0:
                raise VirttoolError("物理交换机信息获取失败!")
            else:
                switches = []
                if len(ret) > 1 and ret[1]["switches"]:
                    for datapath in ret[1]["switches"]:
                        switch = {'dpid': datapath["dpid"]}
                        switch['ports'] = self._parse_ports(datapath["ports"])
                        ip_addr_list = datapath["ip_addr"].split(":")
                        if len(ip_addr_list) > 1:
                            switch['target_switch'] = (ip_addr_list[0], ip_addr_list[1])
                        else:
                            switch['target_switch'] = ()
                        switches.append(switch)
#                 print switches
                return switches
        except:
            raise VirttoolError("物理交换机信息获取失败!")

    def get_links(self):
        try:
            cmd = "show links"
            ret = cnvp_service(cmd, self.url)
            if ret[0]["resultcode"] != 0:
                raise VirttoolError("物理链接信息获取失败!")
            else:
                links = []
                if len(ret) > 1:
                    for link in ret[1:]:
                        if link != {}:
                            link_dict = {}
                            link_dict['dst-port'] = link['dst_port']
                            link_dict['dst-switch'] = link['dst_dpid']
                            link_dict['src-port'] = link['src_port']
                            link_dict['src-switch'] = link['src_dpid']
                            links.append(link_dict)
                return links
        except:
            raise VirttoolError("物理链接信息获取失败!")

    def _parse_ports(self, ports_info):
        ports = []
        for port_info in ports_info:
            port_dict = {}
            port_dict['portNumber'] = port_info["port_no"]
            port_dict['name'] = port_info["port_name"]
            ports.append(port_dict)
        return ports
