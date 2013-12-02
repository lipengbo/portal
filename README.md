pinax-project-account
=====================

a starter project the incorporates account features from django-user-accounts


Usage:

    django-admin.py startproject --template=https://github.com/pinax/pinax-project-account/zipball/master <project_name>

Getting Started:

    pip install virtualenv
    virtualenv mysiteenv
    source mysiteenv/bin/activate
    pip install Django==1.4.5
    django-admin.py startproject --template=https://github.com/pinax/pinax-project-account/zipball/master mysite
    cd mysite
    pip install -r requirements.txt
    python manage.py syncdb
    python manage.py runserver

=====================

plugins/ipam:
  [功能]
  1、网络管理：用于且分子网，它管理两种类型的网络
               type0:基础设施管理层面的IP地址管理，用于分配给Controller
               type1:用于分配给slice的IP地址，用于分配给slice内的虚拟机
  2、创建子网：可以分配64/32/16/8大小的子网，slice创建时会创建子网
  3、删除子网：slice删除时会删除子网;slice创建失败也是调用该接口
  4、子网过期管理：用于slice没有真正创建,但网络地址已经分配的情况，默认过期时间为120秒，如果120秒slice内有被创建，该子网将分配给下一个slice;所以建议在slice提交页面添加定时功能,在规定时间内不提交该slice则不能提交(类是于购物网站的定时支付功能,关于前台定时的功能请陈俊霞配合完成，谢谢)
  4、网络地址分配：给虚拟机/controller分配IP地址,虚拟机/controller被创建时调用
  5、IP地址释放：虚拟机/controller被删除时调用

  [接口]
  1、 网络管理接口：环境被创建时被导入,可配置
  2、 子网创建接口：
      函数调用：IPUsage.objects.create_subnet(owner, ipcount=64, timeout=120)
      参数说明：owner用于唯一标识一个slice的字符串,如slice.name
                ipcount子网IP地址的数目，用户可以使用的IP地址的数目为ipcount-2,因为要减去网络地址和网络广播地址,取值范围64/32/16/8;因为ipcount=4没有意义(4-2-2=0)
                timeout子网的过期时间，如果子网过期后slice被创建在该slice上创建虚拟机的虚拟机state为failed
      返回值：返回字符串,格式如下：'10.0.0.1/26'
  3、 子网创建结果接口：slice创建成功后被调用用于确认给subnet被分配给自己
      函数调用： def subnet_create_success(self, owner)
      参数说明：owner用于唯一标识一个slice的字符串,如slice.name
      返回值：True/Exception
  4、 子网删除接口：
      函数调用： def delete_subnet(self, owner)
      参数说明：owner用于唯一标识一个slice的字符串,如slice.name
      返回值：True/Exception
  5、 网络地址分配接口：
      函数调用： def allocate_ip(self, owner)给vt使用
      函数调用： def allocate_ip_for_controller(self)给create_vm_for_controller使用
  6、 网络地址释放接口：
      函数调用： def release_ip(self, ip)
      函数调用： def release_ip_for_controller(self, ip)

=====================

plugins/vt:
  [功能]
  1、Flavor管理：提供了init方法用于导入初始flavor配置，提供了admin界面，用于管理flavor。需要提醒的是当Flavor被删除时依赖与它的虚拟机也都会被删除
  2、Image管理：提供了init方法用于导入glance server中已经存在的image，目前没有提供完备的Image管理功能；所以在安装环境前先上传image到glance server，然后在ccf的etc/config.py中配置glance server；然后按照ccf安装，启动流程启动ccf即可
  3、虚拟机管理：目前管理着两种虚拟机
     a、vm for slice：提供了端到端的解决方案
     b、vm for controller：提供了create_vm_for_controller ; delete_vm_for_controller接口；controller宿主机的选择采用了调度的方式，Flavor采用默认方式（需要在etc/config.py中配置），Image的选择根据Image的名字（即controller type name == image name），这就要求image中必须要含有floodlight、nox、pox等名字的image（详情请查看Image 管理）
  4、新增调度功能

  [接口]
  1、create_vm_for_controller(island_obj, slice_obj, image_name):由俊霞调用
      参数说明：island_obj , slice_obj , image_name(即controller_sys)
      返回值：vm对象, ipaddr(字符串)
  2、delete_vm_for_controller:由俊霞调用
      参数说明：vm对象
      返回值：如果错误会有Exception

=====================

plugins/network:
  [功能]
   1、添加gateway功能
   2、添加的dhcp功能，本期不支持dhcp自定义
   3、新增ovs监控功能
  [接口]

=====================
plugins/common:
=====================
  [功能]
  1、提供基础的工具集，比如文件操作，进程，命令行，异常处理
  2、glance client：由于自有glanceclient安装问题比较多，所以重写了一个glance client（安装文档中可以吧所有有关glance client安装的步骤都去掉）
  3、vt_manager client：调用vt_manager实现虚拟机的管理
  4、undoManager：通用的事物管理工具，用于回滚（比如删除底层虚拟机时需要清除的资源比较多，为了保障整体的事务性需要提供一个类似RDB的事务管理工具）
=====================
noVNC:
   新增noVNC功能用于远程桌面获取
##启动
   cd noVNC
   ./run.sh
