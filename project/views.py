import json
import datetime
import logging
logger = logging.getLogger("plugins")

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db.models import Q
from django.conf import settings

from guardian.decorators import permission_required
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from project.models import Project, Membership, Category, Island, City
from project.forms import ProjectForm
from invite.forms import ApplicationForm, InvitationForm
from invite.models import Invitation, Application
from slice.models import Slice

from resources.models import Switch, Server, VirtualSwitch
from communication.flowvisor_client import FlowvisorClient
from plugins.openflow.models import Flowvisor
from common.models import  Counter
from notifications.models import Notification


def home(request):
    user = request.user
    if user.is_authenticated():
        if user.is_superuser:
            return redirect('manage_index')
        return redirect('project_manage')
    else:
        return redirect('account_login')


@login_required
def index(request):
    
    context = {}
    user = request.user
    context = {}
    if user.is_superuser:
        projects = Project.objects.all()
        context['extent_html'] = "admin_base.html"
    else:
        project_ids = Membership.objects.filter(user=user).values_list(
                "project__id", flat=True)
        projects = Project.objects.filter(id__in=project_ids)
        context['extent_html'] = "site_base.html"
    if 'query' in request.GET:
        query = request.GET.get('query')
        if query:
            projects = projects.filter(Q(name__icontains=query) |
                    Q(description__icontains=query))
            context['query'] = query
    context['projects'] = projects
    today = datetime.date.today()
    counCounter = Counter.objects.filter(date__year=today.strftime('%Y'),
                                         date__month=today.strftime('%m'),
                                         date__day=today.strftime('%d'),
                                         target=0,
                                         type=2)
    if counCounter:
        context['new_projects_num'] = counCounter[0].count
    else:
        context['new_projects_num'] = 0
    context['total_projects'] = Project.objects.all().count()
    context['target'] = "project"
    context['type'] = "day"
    if request.is_ajax():
        print '89'
        return render(request, 'project/list_page.html', context)
    return render(request, 'project/index.html', context)


@login_required
def perm_admin(request, id, user_id):
    project = get_object_or_404(Project, id=id)
    current_user = request.user
    if not (current_user == project.owner):
        return redirect('forbidden')
    context = {}
    context['project'] = project
    content_type = ContentType.objects.get_for_model(project)
    perms = Permission.objects.filter(content_type=content_type).exclude(codename="add_project")
    context['perms'] = perms
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        select_perms = request.POST.getlist('perm')
        user_perms = get_perms(user, project)
        for perm in perms:
            remove_perm("{}.{}".format(perm.content_type.app_label, perm.codename), user, project)
        for perm in select_perms:
            assign_perm(perm, user, project)
    context['member_user'] = user
    return render(request, 'project/perm.html', context)

@login_required
def detail(request, id):
    user = request.user
    project = get_object_or_404(Project, id=id)
    #if not user.has_perm('project.view_project', project):
    #    return redirect('forbidden')
    context = {}
    target_type = ContentType.objects.get_for_model(project)
    try:
        invitation = Invitation.objects.get(to_user=user, target_id=project.id, target_type=target_type)
    except Invitation.DoesNotExist, e:
        pass
    else:
        context['invitation'] = invitation
    if user.is_superuser:
        context['extent_html'] = "admin_base.html"
    else:
        context['extent_html'] = "site_base.html"
    context['project'] = project
    return render(request, 'project/detail.html', context)


@login_required
def manage(request):
    user = request.user
    project_ids = Membership.objects.filter(user=user).values_list(
            "project__id", flat=True)
    projects = Project.objects.filter(id__in=project_ids)
    context = {}
    context['extent_html'] = "site_base.html"
    context['projects'] = projects[:4]
    return render(request, 'project/manage.html', context)


@login_required
def invite(request, id):
    project = get_object_or_404(Project, id=id)
    #if not request.user.has_perm('project.invite_project_member', project):
    if not (request.user == project.owner):
        return redirect('forbidden')
    context = {}
    context['project'] = project
    target_type = ContentType.objects.get_for_model(project)

    if request.method == 'POST':
        user_ids = request.POST.getlist('user')
        message = request.POST.get('message')
        if message:
            for user_id in user_ids:
                user = get_object_or_404(User, id=user_id)
                try:
                    Invitation.objects.get(to_user=user, target_id=project.id, target_type=target_type)
                    messages.add_message(request, messages.INFO,
                            _("The user has been invited of this project"))
                    continue
                except Invitation.DoesNotExist:
                    pass

                try:
                    application = Application.objects.get(from_user=user, target_id=project.id, target_type=target_type, state__gt=0)
                    messages.add_message(request, messages.INFO,
                            _("The user has applied this project"))
                    continue
                except Application.DoesNotExist:
                    pass

                form = InvitationForm({'message': message, 'to_user': user_id})
                if form.is_valid():
                    invitation = form.save(commit=False)
                    invitation.from_user = request.user
                    invitation.target = project
                    invitation.save()
        else:
            messages.add_message(request, messages.ERROR,
                    _("Invitation message is required."))

    invited_user_ids = []#list(Invitation.objects.filter(target_id=project.id,
            #target_type=target_type).values_list("to_user__id", flat=True))
    #invited_user_ids.extend(project.member_ids())
    invited_user_ids.append(project.owner.id)
    invited_user_ids.append(settings.ANONYMOUS_USER_ID)
    invited_user_ids.extend(User.objects.filter(is_superuser=True).values_list("id", flat=True))
    users = User.objects.exclude(id__in=set(invited_user_ids)).filter(is_active=True)
    if 'query' in request.GET:
        query = request.GET.get('query')
        if query:
            if len(query) > 256:
                query = query[:256]
            users = users.filter(username__icontains=query)
            context['query'] = query
    context['users'] = users
    return render(request, 'project/invite.html', context)


@login_required
def apply(request):
    context = {}
    user = request.user
    projects = Project.objects.all().exclude(owner=user)
    if 'category' in request.GET:
        cat_id = request.GET.get('category')
        if cat_id and cat_id != u'-1':
            current_cat = get_object_or_404(Category, id=cat_id)
            projects = projects.filter(category=current_cat)
            context['current_cat'] = current_cat
    if 'query' in request.GET:
        query = request.GET.get('query')
        if query:
            if len(query) > 256:
                query = query[:256]
            projects = projects.filter(Q(name__icontains=query) |
                    Q(description__icontains=query))
            context['query'] = query
    categories = Category.objects.all()
    context['projects'] = projects
    context['categories'] = categories
    if request.method == 'POST':
        project_ids = request.POST.getlist('project_id')
        message = request.POST.get('message')
        if message:
            apply_count = 0
            for project_id in project_ids:
                project = get_object_or_404(Project, id=project_id)
                target_type = ContentType.objects.get_for_model(project)
                try:
                    Application.objects.get(from_user=user, target_id=project.id, target_type=target_type)
                    messages.add_message(request, messages.INFO,
                            _("You have applied for this project"))
                    continue
                except Application.DoesNotExist:
                    pass

                try:
                    Invitation.objects.get(to_user=user, target_id=project.id, target_type=target_type, state__gt=0)
                    messages.add_message(request, messages.INFO,
                            _("The user has been invited for this project"))
                    continue
                except Invitation.DoesNotExist:
                    pass
                form = ApplicationForm({"to_user": project.owner.id, "message": message})
                if form.is_valid():
                    application = form.save(commit=False)
                    application.target = project
                    application.from_user = user
                    try:
                        application.save()
                        apply_count += 1
                    except IntegrityError:
                        pass
            if apply_count > 0:
                messages.add_message(request, messages.INFO, _("Application is submitted, please wait to audit."))
        else:
            messages.add_message(request, messages.ERROR, _("Application message is required."))
    return render(request, 'project/apply.html', context)

@login_required
#@permission_required('project.add_project', login_url='/forbidden/')
def create_or_edit(request, id=None):
    user = request.user
    context = {}
    instance = None
    if id:
        instance = get_object_or_404(Project, id=id)
        island_ids = instance.slice_set.all().values_list('sliceisland__island__id', flat=True)
        if not user.has_perm('project.change_project', instance):
            return redirect('forbidden')
        context['slice_islands'] = set(list(island_ids))
    else:
        if not user.has_perm('project.add_project'):
            return redirect('forbidden')

    if request.method == 'GET':
        form = ProjectForm(instance=instance)
    else:
        form = ProjectForm(request.POST, instance=instance)
        if form.is_valid():
            project = form.save(commit=False)
            category_name = request.POST.get('category_name')
            try:
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                category = Category(name=category_name)
                category.save()
            project.category = category
            if not id:
                project.owner = user
            project.save()
            form.save_m2m()
            return redirect('project_detail', id=project.id)

    context['form'] = form
    cats = Category.objects.all()
    context['cats'] = cats
    return render(request, 'project/create.html', context)

@login_required
def delete_member(request, id):
    user = request.user
    membership = get_object_or_404(Membership, id=int(id))
    project = membership.project
    if project.owner == user and not membership.is_owner:
        membership.delete()
    else:
        return redirect("forbidden")
    return redirect("project_detail", id=project.id)

@login_required
def delete_project(request, id):
    project = get_object_or_404(Project, id=id)
    if request.user.has_perm('project.delete_project', project):
        try:
            project.delete()
        except Exception, e:
            messages.add_message(request, messages.ERROR, e)
    else:
        project.dismiss(request.user)
    if 'next' in request.GET:
        return redirect(request.GET.get('next'))
    return redirect("project_index")

@login_required
def applicant(request, id, user_id=None):
    project = get_object_or_404(Project, id=id)
    context = {}
    user = request.user
    if not (request.user == project.owner):
        return redirect('forbidden')
    target_type = ContentType.objects.get_for_model(project)
    applications = Application.objects.filter(target_id=project.id, target_type=target_type, state=0)
    if user_id:
        applications = applications.filter(from_user__id=user_id)
    if 'query' in request.GET:
        query = request.GET.get('query')
        if query:
            applications = applications.filter(from_user__username__icontains=query)
            context['query'] = query
    context['applications'] = applications
    context['project'] = project

    if request.method == 'POST':
        application_ids = request.POST.getlist('application')
        selected_applications = Application.objects.filter(id__in=application_ids)
        for application in selected_applications:
            if 'approve' in request.POST:
                application.accept()
            elif 'deny' in request.POST:
                application.reject()

    return render(request, 'project/applicant.html', context)

def get_island_flowvisors(island_id=None):
    flowvisors = Flowvisor.objects.all()
    if island_id:
        flowvisors = flowvisors.filter(island__id=island_id)
    flowvisor_list = []
    for flowvisor in flowvisors:
        flowvisor_list.append({"host": flowvisor.ip + ":" + str(flowvisor.http_port), "id": flowvisor.id})
    return flowvisor_list

def get_all_cities():
    return [], 2,2,2,2,2

def topology(request):
    from resources.models import Switch
    root_controller = None
    no_parent = request.GET.get('no_parent')
    hide_filter = request.GET.get('hide_filter')
    island_id = request.GET.get('island_id', 0)
    show_virtual_switch = request.GET.get('show_virtual_switch')
    direct = request.GET.get('direct')
    size = request.GET.get('size')
    try:
        island_id = int(island_id)
    except:
        island_id = 0
    flowvisors = get_island_flowvisors(island_id)

    all_gre_ovs = Switch.objects.filter(has_gre_tunnel=True)
    if island_id:
        all_gre_ovs = all_gre_ovs.filter(island__id=island_id)

    node_infos, total_server, total_switch, total_ctrl, total_nodes, total_island = get_all_cities()
    city_id = int(request.GET.get('city_id', 0))
    island_id = int(island_id)
    total_facility = 4

    #slices = get_slices()
    return render(request, 'topology/index.html', {
        'node_infos': node_infos,
        'city_id': city_id,
        'island_id': island_id,
        'total_server':total_server,
        'total_switch': total_switch,
        'total_ctrl': total_ctrl,
        'total_nodes': total_nodes,
        'total_island': total_island,
        'total_facility':total_facility,
        'all_gre_ovs': all_gre_ovs,
        'direct': direct,
        'no_parent': no_parent,
        'hide_filter': hide_filter,
        'size': size,
        'show_virtual_switch':show_virtual_switch,
        #'slices': slices,
        'root_controllers': json.dumps(flowvisors)})

def swicth_desc(request, host, port, dpid):
    return HttpResponse(json.dumps({dpid:[]}), content_type="application/json")

def swicth_aggregate(request, host, port, dpid):
    return HttpResponse(json.dumps({dpid:[]}), content_type="application/json")

def device_proxy(request, host, port):
    return HttpResponse(json.dumps([]), content_type="application/json")

def links_proxy(request, host, port):
    flowvisor = Flowvisor.objects.get(ip=host, http_port=port)
    links = flowvisor.link_set.all()
    link_data = []
    for link in links:
        if link.source.switch.island != flowvisor.island:
            continue
        if link.target.switch.island != flowvisor.island:
            continue
        link_data.append({
            "dst-port": link.target.port,
            "dst-port-name": link.target.name,
            "dst-switch": link.target.switch.dpid,
            "src-port": link.source.port,
            "src-port-name": link.source.name,
            "src-switch": link.source.switch.dpid
            })

    return HttpResponse(json.dumps(link_data), content_type="application/json")

def links_direct(request, host, port):
    flowvisor = Flowvisor.objects.get(ip=host, http_port=port)
    client = FlowvisorClient(host, port, flowvisor.password)
    data = client.get_links()
    return HttpResponse(json.dumps(data), content_type="application/json")

def switch_direct(request, host, port):
    flowvisor = Flowvisor.objects.get(ip=host, http_port=port)
    client = FlowvisorClient(host, port, flowvisor.password)
    json_data = client.get_switches()
    for i in range(len(json_data)):
        entry = json_data[i]
        dpid = entry['dpid']
        try:
            switch = Switch.objects.get(dpid=dpid)
        except Switch.DoesNotExist:
            pass
        else:
            json_data[i]['db_name'] = switch.name
            db_id = switch.id
            try:
                db_id = switch.virtualswitch.server.id
            except VirtualSwitch.DoesNotExist:
                pass
            json_data[i]['db_id'] = db_id
    data = json.dumps(json_data)
    return HttpResponse(data, content_type="application/json")

#@cache_page(60 * 60 * 24 * 10)
def switch_proxy(request, host, port):
    flowvisor = Flowvisor.objects.get(ip=host, http_port=port)
    switch_ids_tuple = flowvisor.link_set.all().values_list(
            'source__switch__id', 'target__switch__id')
    switch_ids = set()
    for switch_id_tuple in switch_ids_tuple:
        switch_ids.add(switch_id_tuple[0])
        switch_ids.add(switch_id_tuple[1])
    switches = Switch.objects.filter(id__in=switch_ids, island=flowvisor.island)
    switch_data = []
    for switch in switches:
        ports = switch.switchport_set.all()
        port_data = []
        for port in ports:
            if port.virtualmachine_set.all().count() > 0:
                continue
            port_data.append({"name": port.name, "portNumber": str(port.port), "db_id": port.id})
        switch_data.append({"dpid": switch.dpid, "db_name": switch.name, "ports": port_data, "db_id": switch.id})

    data = json.dumps(switch_data)
    return HttpResponse(data, content_type="application/json")


@login_required
def member(request, id):
    user = request.user
    project = get_object_or_404(Project, id=id)
    context = {}
    if user.is_superuser:
        context['extent_html'] = "admin_base.html"
    else:
        context['extent_html'] = "site_base.html"
    context['project'] = project
    context['members'] = project.membership_set.all()
    return render(request, 'project/member.html', context)


@login_required
def manage_index(request):
    user = request.user
    context = {}
    if user.is_superuser:
        context['slices'] = Slice.objects.all()
        context['total_islands'] = Island.objects.all().count()
        context['total_projects'] = Project.objects.all().count()
        context['total_users'] = User.objects.all().count()
        context['total_cities'] = City.objects.all().count()
        context['total_servers'] = Server.objects.all().count()
        context['total_switches'] = Switch.objects.all().count() - VirtualSwitch.objects.count()
        if Server.objects.all():
            context['host_id'] = Server.objects.all()[0].id
        else:
            context['host_id'] = -1
        if Switch.objects.all():
            context['switch_id'] = Switch.objects.all()[0].id
        else:
            context['switch_id'] = -1
        return render(request, 'manage_index.html', context)
    else:
        return redirect("forbidden")

@login_required
def delete_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(recipient=user)
    if request.method == 'POST':
        notice_ids = request.POST.getlist('notification_id')
        notifications = notifications.filter(id__in=notice_ids)
    notifications.delete()
    return redirect('notifications:all')
