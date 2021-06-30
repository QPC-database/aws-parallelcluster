# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "LICENSE.txt" file accompanying this file.
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied.
# See the License for the specific language governing permissions and limitations under the License.


import pytest
import base64
from assertpy import assert_that

from tests.common.utils import generate_random_string
from utils import generate_stack_name

# Client Interface
from pcluster_client.model.create_cluster_request_content import CreateClusterRequestContent
from pcluster_client.api import cluster_operations_api

@pytest.mark.usefixtures("region", "os", "instance")
def test_cluster_operations(request, scheduler, region, pcluster_config_reader, clusters_factory, api_client):
    cluster_config_path = pcluster_config_reader(scaledown_idletime=3)

    with open(cluster_config_path) as config_file:
        cluster_config = config_file.read()

    client = cluster_operations_api.ClusterOperationsApi(api_client)

    new_cluster = clusters_factory(cluster_config_path)
    _test_list_clusters(client, new_cluster, region)
    _test_describe_cluster(client, new_cluster, region)

    stack_name = generate_stack_name("integ-tests", request.config.getoption("stackname_suffix"))

    print(_test_create(client, cluster_config, region, stack_name))


def _test_list_clusters(client, cluster, region):
    response = client.list_clusters(region=region)
    cluster_names = [c['cluster_name'] for c in response['items']]
    assert_that(cluster_names).contains(cluster.name)


def _test_describe_cluster(client, cluster, region):
    response = client.describe_cluster(cluster.name, region=region)
    assert_that(response['cluster_name']).is_equal_to(cluster.name)


def _test_create(api_client, cluster_config, region, stack_name):
    cluster_config_data = base64.b64encode(cluster_config.encode('utf-8')).decode('utf-8')
    body = CreateClusterRequestContent(stack_name,
                                       cluster_config_data,
                                       region=region)
    return api_client.create_cluster(body)
