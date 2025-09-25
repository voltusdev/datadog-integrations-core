# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import logging

import mock
import pytest

from datadog_checks.consul import ConsulCheck
from datadog_checks.consul.common import MAX_SERVICES

from . import common, consul_mocks

pytestmark = pytest.mark.unit

log = logging.getLogger(__file__)


def test_get_nodes_with_service(aggregator):
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG])
    consul_mocks.mock_check(consul_check, consul_mocks._get_consul_mocks())
    consul_check.check(None)

    expected_tags = [
        'consul_datacenter:dc1',
        'consul_service_id:service-1',
        'consul_service-1_service_tag:active',
        'consul_service-1_service_tag:standby',
        'consul_service_tag:active',
        'consul_service_tag:standby',
    ]

    aggregator.assert_metric('consul.catalog.nodes_up', value=4, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.nodes_passing', value=4, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.nodes_warning', value=0, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.nodes_critical', value=0, tags=expected_tags)

    expected_tags = ['consul_datacenter:dc1', 'consul_node_id:node-1']

    aggregator.assert_metric('consul.catalog.services_up', value=24, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.services_passing', value=24, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.services_warning', value=0, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.services_critical', value=0, tags=expected_tags)

    expected_tags = [
        'consul_datacenter:dc1',
        'consul_service-1_service_tag:standby',
        'consul_service_id:service-1',
        'consul_node_id:node-1',
        'consul_status:passing',
    ]
    aggregator.assert_metric('consul.catalog.services_count', value=3, tags=expected_tags)
    expected_tags.append('consul_service-1_service_tag:active')
    aggregator.assert_metric('consul.catalog.services_count', value=1, tags=expected_tags)


def test_get_peers_in_cluster(aggregator):
    my_mocks = consul_mocks._get_consul_mocks()
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG])
    consul_mocks.mock_check(consul_check, my_mocks)
    consul_check.check(None)

    # When node is leader
    aggregator.assert_metric('consul.peers', value=3, tags=['consul_datacenter:dc1', 'mode:leader'])

    my_mocks['_get_cluster_leader'] = consul_mocks.mock_get_cluster_leader_B
    consul_mocks.mock_check(consul_check, my_mocks)
    consul_check.check(None)

    aggregator.assert_metric('consul.peers', value=3, tags=['consul_datacenter:dc1', 'mode:follower'])


def test_count_all_nodes(aggregator):
    my_mocks = consul_mocks._get_consul_mocks()
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG])
    consul_mocks.mock_check(consul_check, my_mocks)
    consul_check.check(None)

    aggregator.assert_metric('consul.catalog.total_nodes', value=2, tags=['consul_datacenter:dc1'])


def test_get_nodes_with_service_warning(aggregator):
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG])
    my_mocks = consul_mocks._get_consul_mocks()
    my_mocks['get_nodes_with_service'] = consul_mocks.mock_get_nodes_with_service_warning
    consul_mocks.mock_check(consul_check, my_mocks)
    consul_check.check(None)

    expected_tags = [
        'consul_datacenter:dc1',
        'consul_service_id:service-1',
        'consul_service-1_service_tag:active',
        'consul_service-1_service_tag:standby',
        'consul_service_tag:active',
        'consul_service_tag:standby',
    ]
    aggregator.assert_metric('consul.catalog.nodes_up', value=4, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.nodes_passing', value=0, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.nodes_warning', value=4, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.nodes_critical', value=0, tags=expected_tags)

    expected_tags = ['consul_datacenter:dc1', 'consul_node_id:node-1']
    aggregator.assert_metric('consul.catalog.services_up', value=24, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.services_passing', value=0, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.services_warning', value=24, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.services_critical', value=0, tags=expected_tags)

    expected_tags = [
        'consul_datacenter:dc1',
        'consul_service-1_service_tag:standby',
        'consul_service_id:service-1',
        'consul_node_id:node-1',
        'consul_status:warning',
    ]
    aggregator.assert_metric('consul.catalog.services_count', value=3, tags=expected_tags)
    expected_tags.append('consul_service-1_service_tag:active')
    aggregator.assert_metric('consul.catalog.services_count', value=1, tags=expected_tags)


def test_get_nodes_with_service_critical(aggregator):
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG])
    my_mocks = consul_mocks._get_consul_mocks()
    my_mocks['get_nodes_with_service'] = consul_mocks.mock_get_nodes_with_service_critical
    consul_mocks.mock_check(consul_check, my_mocks)
    consul_check.check(None)

    expected_tags = [
        'consul_datacenter:dc1',
        'consul_service_id:service-1',
        'consul_service-1_service_tag:active',
        'consul_service-1_service_tag:standby',
        'consul_service_tag:active',
        'consul_service_tag:standby',
    ]
    aggregator.assert_metric('consul.catalog.nodes_up', value=4, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.nodes_passing', value=0, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.nodes_warning', value=0, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.nodes_critical', value=4, tags=expected_tags)

    expected_tags = ['consul_datacenter:dc1', 'consul_node_id:node-1']
    aggregator.assert_metric('consul.catalog.services_up', value=24, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.services_passing', value=0, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.services_warning', value=0, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.services_critical', value=24, tags=expected_tags)

    expected_tags = [
        'consul_datacenter:dc1',
        'consul_service-1_service_tag:standby',
        'consul_service_id:service-1',
        'consul_node_id:node-1',
        'consul_status:critical',
    ]
    aggregator.assert_metric('consul.catalog.services_count', value=3, tags=expected_tags)
    expected_tags.append('consul_service-1_service_tag:active')
    aggregator.assert_metric('consul.catalog.services_count', value=1, tags=expected_tags)


def test_consul_request(aggregator, instance, mocker):
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG])
    mocker.patch("datadog_checks.base.utils.serialization.json.loads")
    with mock.patch("datadog_checks.consul.consul.requests.Session.get") as mock_requests_get:
        consul_check.consul_request("foo")
        url = "{}/{}".format(instance["url"], "foo")
        aggregator.assert_service_check("consul.can_connect", ConsulCheck.OK, tags=["url:{}".format(url)], count=1)

        aggregator.reset()
        mock_requests_get.side_effect = Exception("message")
        with pytest.raises(Exception):
            consul_check.consul_request("foo")
        aggregator.assert_service_check(
            "consul.can_connect",
            ConsulCheck.CRITICAL,
            tags=["url:{}".format(url)],
            count=1,
            message="Consul request to {} failed: message".format(url),
        )


def test_service_checks(aggregator):
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG_DISABLE_SERVICE_TAG])
    my_mocks = consul_mocks._get_consul_mocks()
    my_mocks['consul_request'] = consul_mocks.mock_get_health_check
    consul_mocks.mock_check(consul_check, my_mocks)
    consul_check.check(None)

    expected_tags = [
        "consul_datacenter:dc1",
        "check:server-loadbalancer",
        "consul_service_id:server-loadbalancer",
        "consul_service:server-loadbalancer",
        "consul_node:node-2",
    ]
    aggregator.assert_service_check('consul.check', status=ConsulCheck.CRITICAL, tags=expected_tags, count=1)

    expected_tags = [
        "consul_datacenter:dc1",
        "check:server-api",
        "consul_service_id:server-loadbalancer",
        "consul_service:server-loadbalancer",
        "consul_node:node-1",
    ]
    aggregator.assert_service_check('consul.check', status=ConsulCheck.OK, tags=expected_tags, count=1)

    expected_tags = [
        "consul_datacenter:dc1",
        "check:server-api",
        "consul_service:server-loadbalancer",
        "consul_node:node-1",
    ]
    aggregator.assert_service_check('consul.check', status=ConsulCheck.OK, tags=expected_tags, count=1)

    expected_tags = [
        "consul_datacenter:dc1",
        "check:server-api",
        "consul_service_id:server-loadbalancer",
        "consul_node:node-1",
    ]
    aggregator.assert_service_check('consul.check', status=ConsulCheck.OK, tags=expected_tags, count=1)

    expected_tags = [
        "consul_datacenter:dc1",
        "check:server-status-empty",
        "consul_service_id:server-empty",
        "consul_service:server-empty",
        "consul_node:node-1",
    ]
    aggregator.assert_service_check('consul.check', status=ConsulCheck.UNKNOWN, tags=expected_tags, count=1)

    aggregator.assert_service_check('consul.check', count=5)


@pytest.mark.parametrize(
    'collect_health_checks, expected_metric_count, expected_metric_total',
    [
        pytest.param(True, 1, 6, id="collect_health_checks enabled"),
        pytest.param(False, 0, 0, id="collect_health_checks disabled"),
    ],
)
def test_health_checks(aggregator, collect_health_checks, expected_metric_count, expected_metric_total):
    config = consul_mocks.MOCK_CONFIG_DISABLE_SERVICE_TAG
    config['collect_health_checks'] = collect_health_checks
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [config])
    my_mocks = consul_mocks._get_consul_mocks()
    my_mocks['consul_request'] = consul_mocks.mock_get_health_check
    consul_mocks.mock_check(consul_check, my_mocks)
    consul_check.check(None)

    expected_tags = [
        'consul_datacenter:dc1',
        'check:server-loadbalancer',
        'consul_service_id:server-loadbalancer',
        'consul_service:server-loadbalancer',
        'consul_node:node-2',
        'consul_status:passing',
    ]
    aggregator.assert_metric('consul.check.up', 1, tags=expected_tags, count=expected_metric_count)

    expected_tags = [
        'check:server-api',
        'consul_datacenter:dc1',
        'consul_node:node-1',
        'consul_service:server-loadbalancer',
        'consul_status:passing',
    ]
    aggregator.assert_metric('consul.check.up', 1, tags=expected_tags, count=expected_metric_count)

    expected_tags = [
        'check:server-api',
        'consul_datacenter:dc1',
        'consul_node:node-1',
        'consul_service_id:server-loadbalancer',
        'consul_status:passing',
    ]
    aggregator.assert_metric('consul.check.up', 1, tags=expected_tags, count=expected_metric_count)

    expected_tags = [
        'check:server-api',
        'consul_datacenter:dc1',
        'consul_node:node-1',
        'consul_service:server-loadbalancer',
        'consul_service_id:server-loadbalancer',
        'consul_status:passing',
    ]
    aggregator.assert_metric('consul.check.up', 1, tags=expected_tags, count=expected_metric_count)

    expected_tags = [
        'check:server-status-empty',
        'consul_datacenter:dc1',
        'consul_node:node-1',
        'consul_service:server-empty',
        'consul_service_id:server-empty',
        'consul_status:',
    ]
    aggregator.assert_metric('consul.check.up', 0, tags=expected_tags, count=expected_metric_count)

    expected_tags = [
        'check:server-loadbalancer',
        'consul_datacenter:dc1',
        'consul_node:node-1',
        'consul_service:server-loadbalancer',
        'consul_service_id:server-loadbalancer',
        'consul_status:critical',
    ]
    aggregator.assert_metric('consul.check.up', 3, tags=expected_tags, count=expected_metric_count)

    aggregator.assert_metric('consul.check.up', count=expected_metric_total)

    event = {
        "event_type": "consul.check_failed",
        "source_type_name": "consul",
        "msg_title": "Service 'server-loadbalancer' check Failed",
        "msg_text": "Check server-loadbalancer for service server-loadbalancer, id: server-loadbalancerfailed "
        "on node node-1: CheckHttp CRITICAL: Request error: Connection refused - connect(2) "
        "for \"localhost\" port 80\n",
        "aggregation_key": "consul.status_check",
        "tags": [
            'check:server-loadbalancer',
            'consul_service:server-loadbalancer',
            'consul_service_id:server-loadbalancer',
            'consul_node:node-1',
            'consul_status:critical',
        ],
    }

    aggregator.assert_event(exact_match=False, count=expected_metric_count, **event)

    # make sure event is only emitted once even though the check runs multiple times
    consul_check.check(None)
    consul_check.check(None)
    consul_check.check(None)
    aggregator.assert_event(exact_match=False, count=expected_metric_count, **event)


def test_service_checks_disable_service_tag(aggregator):
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG_DISABLE_SERVICE_TAG])
    my_mocks = consul_mocks._get_consul_mocks()
    my_mocks['consul_request'] = consul_mocks.mock_get_health_check
    consul_mocks.mock_check(consul_check, my_mocks)
    consul_check.check(None)

    expected_tags = [
        'consul_datacenter:dc1',
        'check:server-loadbalancer',
        'consul_service_id:server-loadbalancer',
        'consul_service:server-loadbalancer',
        'consul_node:node-2',
    ]
    aggregator.assert_service_check('consul.check', status=ConsulCheck.CRITICAL, tags=expected_tags, count=1)

    expected_tags = [
        'consul_datacenter:dc1',
        'check:server-api',
        'consul_service_id:server-loadbalancer',
        'consul_service:server-loadbalancer',
        'consul_node:node-1',
    ]
    aggregator.assert_service_check('consul.check', status=ConsulCheck.OK, tags=expected_tags, count=1)

    expected_tags = [
        'consul_datacenter:dc1',
        'check:server-api',
        'consul_service:server-loadbalancer',
        'consul_node:node-1',
    ]
    aggregator.assert_service_check('consul.check', status=ConsulCheck.OK, tags=expected_tags, count=1)

    expected_tags = [
        'consul_datacenter:dc1',
        'check:server-api',
        'consul_service_id:server-loadbalancer',
        'consul_node:node-1',
    ]
    aggregator.assert_service_check('consul.check', status=ConsulCheck.OK, tags=expected_tags, count=1)

    expected_tags = [
        'consul_datacenter:dc1',
        'check:server-status-empty',
        'consul_service_id:server-empty',
        'consul_service:server-empty',
        'consul_node:node-1',
    ]
    aggregator.assert_service_check('consul.check', status=ConsulCheck.UNKNOWN, tags=expected_tags, count=1)

    aggregator.assert_service_check('consul.check', count=5)


def test_cull_services_list():
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG_LEADER_CHECK])
    my_mocks = consul_mocks._get_consul_mocks()
    consul_mocks.mock_check(consul_check, my_mocks)

    # Pad num_services to kick in truncation logic
    num_services = MAX_SERVICES + 20

    # Max services parameter (from consul.yaml) set to be bigger than MAX_SERVICES and smaller than total of services
    max_services = num_services - 10

    # Big include list
    services = consul_mocks.mock_get_n_services_in_cluster(num_services)
    consul_check.services_include = ['service_{}'.format(k) for k in range(num_services)]
    assert len(consul_check._cull_services_list(services)) == MAX_SERVICES

    # Big include list with max_services
    consul_check.max_services = max_services
    assert len(consul_check._cull_services_list(services)) == max_services

    # include list < MAX_SERVICES should spit out the include list
    consul_check.services_include = ['service_{}'.format(k) for k in range(MAX_SERVICES - 1)]
    assert set(consul_check._cull_services_list(services)) == set(consul_check.services_include)

    # include list < max_services param should spit out the include list
    consul_check.services_include = ['service_{}'.format(k) for k in range(max_services - 1)]
    assert set(consul_check._cull_services_list(services)) == set(consul_check.services_include)

    # No include list, still triggers truncation
    consul_check.services_include = []
    consul_check.max_services = MAX_SERVICES
    assert len(consul_check._cull_services_list(services)) == MAX_SERVICES

    # No include list with max_services set, also triggers truncation
    consul_check.services_include = []
    consul_check.max_services = max_services
    assert len(consul_check._cull_services_list(services)) == max_services

    # Num. services < MAX_SERVICES should be no-op in absence of include list
    num_services = MAX_SERVICES - 1
    services = consul_mocks.mock_get_n_services_in_cluster(num_services)
    assert len(consul_check._cull_services_list(services)) == num_services

    # Num. services < MAX_SERVICES should spit out only the include list when one is defined
    consul_check.services_include = ['service_1', 'service_2', 'service_3']
    assert set(consul_check._cull_services_list(services)) == set(consul_check.services_include)

    # Num. services < max_services (from consul.yaml) should be no-op in absence of include list
    num_services = max_services - 1
    consul_check.services_include = []
    services = consul_mocks.mock_get_n_services_in_cluster(num_services)
    assert len(consul_check._cull_services_list(services)) == num_services

    # Num. services < max_services should spit out only the include list when one is defined
    consul_check.services_include = ['service_1', 'service_2', 'service_3']
    assert set(consul_check._cull_services_list(services)) == set(consul_check.services_include)

    # Excluded services will not be in final service list
    consul_check.services_exclude = ['service_1', 'service_2', 'service_3']
    assert set(consul_check.services_exclude) not in set(consul_check._cull_services_list(services))

    # Excluded services will be prioritized over include list services
    consul_check.services_exclude = ['service_1', 'service_2', 'service_3']
    consul_check.services_include = ['service_4', 'service_5', 'service_6']
    test_include_length = len(consul_check.services_include)
    test_service_list_length = len(set(consul_check._cull_services_list(services)))
    assert (
        set(consul_check.services_exclude) not in set(consul_check._cull_services_list(services))
        and test_service_list_length > test_include_length
    )

    # Use of services exclude will still trigger truncation logic
    services = consul_mocks.mock_get_n_services_in_cluster(num_services)
    consul_check.services_exclude = ['service_1', 'service_2', 'service_3']
    consul_check.max_services = MAX_SERVICES
    assert len(consul_check._cull_services_list(services)) == consul_check.max_services

    # Num. services < MAX_SERVICES (from consul.yaml) should be no-op in absence of services exclude
    num_services = MAX_SERVICES + 1
    consul_check.services_exclude = []
    services = consul_mocks.mock_get_n_services_in_cluster(num_services)
    assert len(consul_check._cull_services_list(services)) == MAX_SERVICES


def test_new_leader_event(aggregator):
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG_LEADER_CHECK])
    my_mocks = consul_mocks._get_consul_mocks()
    my_mocks['_get_cluster_leader'] = consul_mocks.mock_get_cluster_leader_B
    consul_mocks.mock_check(consul_check, my_mocks)

    consul_check._last_known_leader = 'My Old Leader'

    consul_check.check(None)
    assert len(aggregator.events) == 1

    event = aggregator.events[0]
    assert event['event_type'] == 'consul.new_leader'
    assert 'prev_consul_leader:My Old Leader' in event['tags']
    assert 'curr_consul_leader:My New Leader' in event['tags']


def test_self_leader_event(aggregator):
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG_SELF_LEADER_CHECK])
    my_mocks = consul_mocks._get_consul_mocks()

    consul_check._last_known_leader = 'My Old Leader'

    our_url = consul_mocks.mock_get_cluster_leader_A()
    other_url = consul_mocks.mock_get_cluster_leader_B()

    # We become the leader
    my_mocks['_get_cluster_leader'] = consul_mocks.mock_get_cluster_leader_A
    consul_mocks.mock_check(consul_check, my_mocks)
    consul_check.check(None)
    assert len(aggregator.events) == 1
    assert our_url == consul_check._last_known_leader
    event = aggregator.events[0]
    assert event['event_type'] == 'consul.new_leader'
    assert 'prev_consul_leader:My Old Leader' in event['tags']
    assert 'curr_consul_leader:{}'.format(our_url) in event['tags']

    # We are already the leader, no new events
    aggregator.reset()
    consul_check.check(None)
    assert len(aggregator.events) == 0

    # We lose the leader, no new events
    my_mocks['_get_cluster_leader'] = consul_mocks.mock_get_cluster_leader_B
    consul_mocks.mock_check(consul_check, my_mocks)
    aggregator.reset()
    consul_check.check(None)
    assert len(aggregator.events) == 0
    assert other_url == consul_check._last_known_leader

    # We regain the leadership
    my_mocks['_get_cluster_leader'] = consul_mocks.mock_get_cluster_leader_A
    consul_mocks.mock_check(consul_check, my_mocks)
    aggregator.reset()
    consul_check.check(None)
    assert len(aggregator.events) == 1
    assert our_url == consul_check._last_known_leader
    event = aggregator.events[0]
    assert event['event_type'] == 'consul.new_leader'
    assert 'prev_consul_leader:{}'.format(other_url) in event['tags']
    assert 'curr_consul_leader:{}'.format(our_url) in event['tags']


def test_network_latency_checks(aggregator):
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG_NETWORK_LATENCY_CHECKS])
    my_mocks = consul_mocks._get_consul_mocks()
    consul_mocks.mock_check(consul_check, my_mocks)

    # We start out as the leader, and stay that way
    consul_check._last_known_leader = consul_mocks.mock_get_cluster_leader_A()

    consul_check.check(None)

    latency = []
    for m_name, metrics in aggregator._metrics.items():
        if m_name.startswith('consul.net.'):
            latency.extend(metrics)
    latency.sort()
    # Make sure we have the expected number of metrics
    assert 19 == len(latency)

    # Only 3 dc-latency metrics since we only do source = self
    dc = [m for m in latency if '.dc.latency.' in m[0]]
    assert 3 == len(dc)
    assert 1.6746410750238774 == dc[0][2]

    # 16 latency metrics, 2 nodes * 8 metrics each
    node = [m for m in latency if '.node.latency.' in m[0]]
    assert 16 == len(node)
    assert 0.26577747932995816 == node[0][2]


@pytest.mark.parametrize(
    'use_node_name_as_hostname, expected_hostname, expected_tags, expected_agent_hostname',
    [
        ('false', [''], ['host-1', 'host-2'], []),
        ('true', ['host-1'], ['host-1'], ['agent_hostname:stubbed.hostname']),
    ],
)
def test_network_latency_node_name(
    aggregator, use_node_name_as_hostname, expected_hostname, expected_tags, expected_agent_hostname
):
    consul_mocks.MOCK_CONFIG_NETWORK_LATENCY_CHECKS['use_node_name_as_hostname'] = use_node_name_as_hostname
    consul_check = ConsulCheck(common.CHECK_NAME, {}, [consul_mocks.MOCK_CONFIG_NETWORK_LATENCY_CHECKS])

    consul_mocks.mock_check(consul_check, consul_mocks._get_consul_mocks())

    # We start out as the leader, and stay that way
    consul_check._last_known_leader = consul_mocks.mock_get_cluster_leader_A()

    consul_check.check(None)

    metrics = [
        'consul.net.node.latency.max',
        'consul.net.node.latency.median',
        'consul.net.node.latency.min',
        'consul.net.node.latency.p25',
        'consul.net.node.latency.p75',
        'consul.net.node.latency.p90',
        'consul.net.node.latency.p95',
        'consul.net.node.latency.p99',
    ]

    for m in metrics:
        for host in expected_hostname:
            for tag in expected_tags:
                tags = ['consul_datacenter:dc1', 'consul_node_name:{}'.format(tag)] + expected_agent_hostname
                aggregator.assert_metric(m, hostname=host, tags=tags)


@pytest.mark.parametrize(
    'test_case, extra_config, expected_http_kwargs',
    [
        (
            "new config",
            {
                'url': '',
                'tls_cert': 'certfile',
                'tls_private_key': 'keyfile',
                'tls_ca_cert': 'file/path',
                'acl_token': 'token',
                'headers': {'X-foo': 'bar'},
            },
            {
                'cert': ('certfile', 'keyfile'),
                'verify': 'file/path',
                'headers': {'X-Consul-Token': 'token', 'X-foo': 'bar'},
            },
        ),
        (
            "default config",
            {'url': ''},
            {
                'cert': None,
                'verify': True,
                'headers': {'User-Agent': 'Datadog Agent/0.0.0', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate'},
            },
        ),
        (
            "legacy config",
            {
                'url': '',
                'client_cert_file': 'certfile',
                'private_key_file': 'keyfile',
                'ca_bundle_file': 'file/path',
                'acl_token': 'token',
            },
            {
                'cert': ('certfile', 'keyfile'),
                'verify': 'file/path',
                'headers': {
                    'X-Consul-Token': 'token',
                    'User-Agent': 'Datadog Agent/0.0.0',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate',
                },
            },
        ),
    ],
)
def test_config(test_case, extra_config, expected_http_kwargs, mocker):
    instance = extra_config
    check = ConsulCheck(common.CHECK_NAME, {}, instances=[instance])
    mocker.patch("datadog_checks.base.utils.serialization.json.loads")

    with mock.patch('datadog_checks.base.utils.http.requests.Session') as session:
        mock_session = mock.MagicMock()
        session.return_value = mock_session
        mock_session.get.return_value = mock.MagicMock(status_code=200)

        check.check(None)

        http_wargs = {
            'auth': mock.ANY,
            'cert': mock.ANY,
            'headers': mock.ANY,
            'proxies': mock.ANY,
            'timeout': mock.ANY,
            'verify': mock.ANY,
            'allow_redirects': mock.ANY,
        }
        http_wargs.update(expected_http_kwargs)
        mock_session.get.assert_called_with('/v1/status/leader', **http_wargs)


@pytest.mark.parametrize(
    'include_service_name_in_tag_key, should_have_service_specific_tags',
    [
        pytest.param(True, True, id="include_service_name_in_tag_key enabled (default behavior)"),
        pytest.param(False, False, id="include_service_name_in_tag_key disabled"),
    ],
)
def test_include_service_name_in_tag_key(aggregator, include_service_name_in_tag_key, should_have_service_specific_tags):
    """Test that include_service_name_in_tag_key configuration controls service-specific tag generation."""
    config = consul_mocks.MOCK_CONFIG.copy()
    config['include_service_name_in_tag_key'] = include_service_name_in_tag_key

    consul_check = ConsulCheck(common.CHECK_NAME, {}, [config])
    consul_mocks.mock_check(consul_check, consul_mocks._get_consul_mocks())
    consul_check.check(None)

    # Build expected tags based on configuration
    base_tags = [
        'consul_datacenter:dc1',
        'consul_service_id:service-1',
    ]

    # Generic tags should always be present
    expected_generic_tags = [
        'consul_service_tag:active',
        'consul_service_tag:standby',
    ]

    # Service-specific tags should only be present when include_service_name_in_tag_key=True
    expected_service_specific_tags = []
    if should_have_service_specific_tags:
        expected_service_specific_tags = [
            'consul_service-1_service_tag:active',
            'consul_service-1_service_tag:standby',
        ]

    expected_tags = base_tags + expected_service_specific_tags + expected_generic_tags

    # Verify the metrics contain the expected tags
    aggregator.assert_metric('consul.catalog.nodes_up', value=4, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.nodes_passing', value=4, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.nodes_warning', value=0, tags=expected_tags)
    aggregator.assert_metric('consul.catalog.nodes_critical', value=0, tags=expected_tags)


def test_include_service_name_in_tag_key_default_behavior(aggregator):
    """Test that the default behavior (include_service_name_in_tag_key=True) is preserved when config is not specified."""
    config = consul_mocks.MOCK_CONFIG.copy()
    # Intentionally not setting include_service_name_in_tag_key to test default

    consul_check = ConsulCheck(common.CHECK_NAME, {}, [config])
    consul_mocks.mock_check(consul_check, consul_mocks._get_consul_mocks())
    consul_check.check(None)

    # Verify that the default behavior includes service-specific tags
    expected_tags = [
        'consul_datacenter:dc1',
        'consul_service_id:service-1',
        'consul_service-1_service_tag:active',
        'consul_service-1_service_tag:standby',
        'consul_service_tag:active',
        'consul_service_tag:standby',
    ]

    aggregator.assert_metric('consul.catalog.nodes_up', value=4, tags=expected_tags)


def test_get_service_tags_method():
    """Test the _get_service_tags static method directly to ensure it respects the include_service_name_in_tag_key parameter."""
    from datadog_checks.consul.consul import ConsulCheck

    service_name = "test-service"
    service_tags = ["tag1", "tag2"]

    # Test with include_service_name_in_tag_key=True (default)
    result_with_service_name = ConsulCheck._get_service_tags(service_name, service_tags, include_service_name_in_tag_key=True)
    expected_with_service_name = [
        'consul_service_id:test-service',
        'consul_test-service_service_tag:tag1',
        'consul_service_tag:tag1',
        'consul_test-service_service_tag:tag2',
        'consul_service_tag:tag2',
    ]
    assert result_with_service_name == expected_with_service_name

    # Test with include_service_name_in_tag_key=False
    result_without_service_name = ConsulCheck._get_service_tags(service_name, service_tags, include_service_name_in_tag_key=False)
    expected_without_service_name = [
        'consul_service_id:test-service',
        'consul_service_tag:tag1',
        'consul_service_tag:tag2',
    ]
    assert result_without_service_name == expected_without_service_name

    # Test default parameter (should be True)
    result_default = ConsulCheck._get_service_tags(service_name, service_tags)
    assert result_default == expected_with_service_name


def test_allowed_service_tags_method():
    """Test the _get_service_tags static method with allowed_service_tags filtering."""
    from datadog_checks.consul.consul import ConsulCheck

    service_name = "test-service"
    service_tags = ["env=prod", "version=1.2.3", "team", "monitoring"]

    # Test with no filtering (None - default behavior)
    result_no_filter = ConsulCheck._get_service_tags(service_name, service_tags, allowed_service_tags=None)
    expected_no_filter = [
        'consul_service_id:test-service',
        'consul_test-service_service_tag:env=prod',
        'consul_service_tag:env=prod',
        'consul_test-service_service_tag:version=1.2.3',
        'consul_service_tag:version=1.2.3',
        'consul_test-service_service_tag:team',
        'consul_service_tag:team',
        'consul_test-service_service_tag:monitoring',
        'consul_service_tag:monitoring',
    ]
    assert result_no_filter == expected_no_filter

    # Test with simple tag filtering
    result_simple_filter = ConsulCheck._get_service_tags(service_name, service_tags, allowed_service_tags=["team", "monitoring"])
    expected_simple_filter = [
        'consul_service_id:test-service',
        'consul_test-service_service_tag:team',
        'consul_service_tag:team',
        'consul_test-service_service_tag:monitoring',
        'consul_service_tag:monitoring',
    ]
    assert result_simple_filter == expected_simple_filter

    # Test with key-based filtering (for key=value tags)
    result_key_filter = ConsulCheck._get_service_tags(service_name, service_tags, allowed_service_tags=["env", "version"])
    expected_key_filter = [
        'consul_service_id:test-service',
        'consul_test-service_service_tag:env=prod',
        'consul_service_tag:env=prod',
        'consul_test-service_service_tag:version=1.2.3',
        'consul_service_tag:version=1.2.3',
    ]
    assert result_key_filter == expected_key_filter

    # Test with mixed filtering (exact matches and key matches)
    result_mixed_filter = ConsulCheck._get_service_tags(service_name, service_tags, allowed_service_tags=["env", "team"])
    expected_mixed_filter = [
        'consul_service_id:test-service',
        'consul_test-service_service_tag:env=prod',
        'consul_service_tag:env=prod',
        'consul_test-service_service_tag:team',
        'consul_service_tag:team',
    ]
    assert result_mixed_filter == expected_mixed_filter

    # Test case insensitive matching
    result_case_insensitive = ConsulCheck._get_service_tags(service_name, ["ENV=PROD", "Team"], allowed_service_tags=["env", "team"])
    expected_case_insensitive = [
        'consul_service_id:test-service',
        'consul_test-service_service_tag:ENV=PROD',
        'consul_service_tag:ENV=PROD',
        'consul_test-service_service_tag:Team',
        'consul_service_tag:Team',
    ]
    assert result_case_insensitive == expected_case_insensitive

    # Test with no matches - should only have consul_service_id
    result_no_matches = ConsulCheck._get_service_tags(service_name, service_tags, allowed_service_tags=["nonexistent"])
    expected_no_matches = ['consul_service_id:test-service']
    assert result_no_matches == expected_no_matches

    # Test combined with include_service_name_in_tag_key=False
    result_combined = ConsulCheck._get_service_tags(service_name, service_tags, include_service_name_in_tag_key=False, allowed_service_tags=["env", "team"])
    expected_combined = [
        'consul_service_id:test-service',
        'consul_service_tag:env=prod',
        'consul_service_tag:team',
    ]
    assert result_combined == expected_combined


@pytest.mark.parametrize(
    'allowed_service_tags, expected_service_tags',
    [
        pytest.param(None, ['active', 'standby', 'env=prod', 'version=1.2.3'], id="no filtering (None)"),
        pytest.param(["active", "standby", "env=prod", "version=1.2.3"], ['active', 'standby', 'env=prod', 'version=1.2.3'], id="allow all existing tags"),
        pytest.param(["active"], ['active'], id="allow only active tag"),
        pytest.param(["env=prod"], ['env=prod'], id="allow only env=prod tag"),
        pytest.param(["env", "version"], ['env=prod', 'version=1.2.3'], id="allow key-based matching for key=value tags"),
        pytest.param(["active", "env"], ['active', 'env=prod'], id="mixed simple and key=value tags"),
        pytest.param(["nonexistent"], [], id="allow no existing tags"),
        pytest.param(["ACTIVE"], ['active'], id="case insensitive matching"),
        pytest.param(["ENV"], ['env=prod'], id="case insensitive key matching for key=value tags"),
    ],
)
def test_allowed_service_tags_integration(aggregator, allowed_service_tags, expected_service_tags):
    """Test that allowed_service_tags configuration filters tags in the full integration."""
    config = consul_mocks.MOCK_CONFIG.copy()
    config['allowed_service_tags'] = allowed_service_tags

    consul_check = ConsulCheck(common.CHECK_NAME, {}, [config])

    # Use enhanced mocks with key=value tags
    enhanced_mocks = consul_mocks._get_consul_mocks().copy()
    enhanced_mocks['get_services_in_cluster'] = consul_mocks.mock_get_services_in_cluster_with_key_value_tags
    enhanced_mocks['get_nodes_with_service'] = consul_mocks.mock_get_nodes_with_service_with_key_value_tags

    consul_mocks.mock_check(consul_check, enhanced_mocks)
    consul_check.check(None)

    # Build expected tags for all metrics that should have filtered service tags
    base_tags = [
        'consul_datacenter:dc1',
        'consul_service_id:service-1',
    ]

    # Add expected service-specific tags (with service name in key)
    service_specific_tags = [f'consul_service-1_service_tag:{tag}' for tag in expected_service_tags]

    # Add expected generic service tags
    generic_service_tags = [f'consul_service_tag:{tag}' for tag in expected_service_tags]

    expected_tags = base_tags + service_specific_tags + generic_service_tags
    expected_tags_set = set(expected_tags)

    # List of metric names that should have filtered service tags
    service_tag_metrics = [
        'consul.catalog.nodes_up',
        'consul.catalog.nodes_passing',
        'consul.catalog.nodes_warning',
        'consul.catalog.nodes_critical'
    ]

    # Verify tag filtering is applied to all relevant metrics
    for metric_name in service_tag_metrics:
        metrics = aggregator._metrics.get(metric_name, [])
        assert len(metrics) > 0, f"Expected at least one {metric_name} metric"

        # Check that all instances of this metric have the expected filtered tags
        for metric in metrics:
            # Only check metrics for service-1 (our test service with key=value tags)
            if 'consul_service_id:service-1' in metric.tags:
                actual_tags = set(metric.tags)
                assert actual_tags == expected_tags_set, (
                    f"Metric {metric_name} has incorrect tags. "
                    f"Expected: {expected_tags_set}, "
                    f"Got: {actual_tags}. "
                    f"Missing: {expected_tags_set - actual_tags}, "
                    f"Extra: {actual_tags - expected_tags_set}"
                )

    # Also check consul.catalog.services_count which now respects include_service_name_in_tag_key
    services_count_metrics = aggregator._metrics.get('consul.catalog.services_count', [])
    if services_count_metrics:
        # Collect all service-specific tags from all service-1 metrics
        all_actual_service_specific_tags = set()
        service_1_metrics_found = 0

        for metric in services_count_metrics:
            if 'consul_service_id:service-1' in metric.tags:
                service_1_metrics_found += 1
                actual_tags = set(metric.tags)
                # services_count metrics only have service-specific tags (consul_service-1_service_tag:xxx)
                # when include_service_name_in_tag_key is True (default), otherwise no service tags
                service_specific_tags_found = {tag for tag in actual_tags if tag.startswith('consul_service-1_service_tag:')}
                all_actual_service_specific_tags.update(service_specific_tags_found)

        # Check that we found some service-1 metrics
        assert service_1_metrics_found > 0, "Expected at least one consul.catalog.services_count metric for service-1"

        expected_service_specific_tags = {f'consul_service-1_service_tag:{tag}' for tag in expected_service_tags}

        # Check that the union of all service-specific tags matches what we expect
        assert all_actual_service_specific_tags == expected_service_specific_tags, (
            f"Metric consul.catalog.services_count has incorrect service-specific tags. "
            f"Expected: {expected_service_specific_tags}, "
            f"Got: {all_actual_service_specific_tags}. "
            f"Missing: {expected_service_specific_tags - all_actual_service_specific_tags}, "
            f"Extra: {all_actual_service_specific_tags - expected_service_specific_tags}"
        )


def test_allowed_service_tags_default_behavior(aggregator):
    """Test allowed_service_tags default behavior (None) preserves all tags."""
    config = consul_mocks.MOCK_CONFIG.copy()
    # Intentionally not setting allowed_service_tags to test default (None)

    consul_check = ConsulCheck(common.CHECK_NAME, {}, [config])
    consul_mocks.mock_check(consul_check, consul_mocks._get_consul_mocks())
    consul_check.check(None)

    # Verify that the default behavior includes all service tags
    expected_tags = [
        'consul_datacenter:dc1',
        'consul_service_id:service-1',
        'consul_service-1_service_tag:active',
        'consul_service-1_service_tag:standby',
        'consul_service_tag:active',
        'consul_service_tag:standby',
    ]

    aggregator.assert_metric('consul.catalog.nodes_up', value=4, tags=expected_tags)


def test_combined_configuration_options(aggregator):
    """Test that include_service_name_in_tag_key and allowed_service_tags work together correctly."""
    config = consul_mocks.MOCK_CONFIG.copy()
    config['include_service_name_in_tag_key'] = False
    config['allowed_service_tags'] = ['active']

    consul_check = ConsulCheck(common.CHECK_NAME, {}, [config])
    consul_mocks.mock_check(consul_check, consul_mocks._get_consul_mocks())
    consul_check.check(None)

    # When both options are configured:
    # - include_service_name_in_tag_key=False: no service-specific tags
    # - allowed_service_tags=['active']: only 'active' tag should be included
    expected_tags = [
        'consul_datacenter:dc1',
        'consul_service_id:service-1',
        'consul_service_tag:active',
        # Should NOT have:
        # - 'consul_service-1_service_tag:active' (due to include_service_name_in_tag_key=False)
        # - 'consul_service_tag:standby' (due to allowed_service_tags=['active'])
        # - 'consul_service-1_service_tag:standby' (both reasons)
    ]

    aggregator.assert_metric('consul.catalog.nodes_up', value=4, tags=expected_tags)
