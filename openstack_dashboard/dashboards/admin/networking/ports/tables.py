# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 NEC Corporation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django.core.urlresolvers import reverse  # noqa
from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import tables

from openstack_dashboard import api
from contrail_openstack_dashboard.openstack_dashboard.dashboards.project.networking.ports import \
    tables as project_tables


LOG = logging.getLogger(__name__)


class DeletePort(tables.DeleteAction):
    data_type_singular = _("Port")
    data_type_plural = _("Ports")

    def delete(self, request, obj_id):
        try:
            api.neutron.port_delete(request, obj_id)
        except Exception:
            msg = _('Failed to delete subnet %s') % obj_id
            LOG.info(msg)
            network_id = self.table.kwargs['network_id']
            redirect = reverse('horizon:admin:networking:detail',
                               args=[network_id])
            exceptions.handle(request, msg, redirect=redirect)


class CreatePort(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Port")
    url = "horizon:admin:networking:addport"
    classes = ("ajax-modal", "btn-create")

    def get_link_url(self, datum=None):
        network_id = self.table.kwargs['network_id']
        return reverse(self.url, args=(network_id,))


class UpdatePort(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Port")
    url = "horizon:admin:networking:editport"
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, port):
        network_id = self.table.kwargs['network_id']
        return reverse(self.url, args=(network_id, port.id))


class PortsTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:admin:networking:ports:detail")
    fixed_ips = tables.Column(
        project_tables.get_fixed_ips, verbose_name=_("Fixed IPs"))
    device_id = tables.Column(
        project_tables.get_attached, verbose_name=_("Device Attached"))
    status = tables.Column("status", verbose_name=_("Status"))
    admin_state = tables.Column("admin_state",
                                verbose_name=_("Admin State"))

    class Meta:
        name = "ports"
        verbose_name = _("Ports")
        table_actions = (project_tables.PortFilterAction, CreatePort, DeletePort)
        row_actions = (UpdatePort, DeletePort,)
