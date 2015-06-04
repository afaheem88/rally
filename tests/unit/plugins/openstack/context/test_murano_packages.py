# Copyright 2015: Mirantis Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock

from rally.plugins.openstack.context import murano_packages
from tests.unit import test

CTX = "rally.plugins.openstack.context"


class MuranoGeneratorTestCase(test.TestCase):

    def setUp(self):
        super(MuranoGeneratorTestCase, self).setUp()

    @staticmethod
    def _get_context():
        return {
            "config": {
                "users": {
                    "tenants": 2,
                    "users_per_tenant": 1,
                    "concurrent": 1,
                },
                "murano_packages": {
                    "app_package": (
                        "rally-jobs/extra/murano/"
                        "applications/HelloReporter/"
                        "io.murano.apps.HelloReporter.zip")
                }
            },
            "admin": {
                "endpoint": mock.MagicMock()
            },
            "task": mock.MagicMock(),
            "users": [
                {
                    "id": "user_0",
                    "tenant_id": "tenant_0",
                    "endpoint": "endpoint"
                },
                {
                    "id": "user_1",
                    "tenant_id": "tenant_1",
                    "endpoint": "endpoint"
                }
            ],
            "tenants": {
                "tenant_0": {"name": "tenant_0_name"},
                "tenant_1": {"name": "tenant_1_name"}
            }
        }

    @mock.patch("rally.plugins.openstack.context.murano_packages.osclients")
    def test_setup(self, mock_osclients):
        mock_app = mock.MagicMock(id="fake_app_id")
        (mock_osclients.Clients().murano().
            packages.create.return_value) = mock_app

        murano_ctx = murano_packages.PackageGenerator(self._get_context())
        murano_ctx.setup()

        self.assertEqual(2, len(murano_ctx.context["tenants"]))
        tenant_id = murano_ctx.context["users"][0]["tenant_id"]
        self.assertEqual([mock_app],
                         murano_ctx.context["tenants"][tenant_id]["packages"])

    @mock.patch("rally.plugins.openstack.context.murano_packages.osclients")
    @mock.patch("%s.images.resource_manager.cleanup" % CTX)
    def test_cleanup(self, mock_cleanup, mock_osclients):
        mock_app = mock.Mock(id="fake_app_id")
        (mock_osclients.Clients().murano().
            packages.create.return_value) = mock_app

        murano_ctx = murano_packages.PackageGenerator(self._get_context())
        murano_ctx.setup()

        murano_ctx.cleanup()
        mock_cleanup.assert_called_once_with(names=["murano.packages"],
                                             users=murano_ctx.context["users"])
