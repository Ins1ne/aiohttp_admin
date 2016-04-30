import os
import time

import psycopg2
import pymysql
import pytest

from docker import Client as DockerClient


def pytest_addoption(parser):
    parser.addoption("--dp", action="store_true", default=False,
                     help=("Force docker pull"))


@pytest.fixture(scope='session')
def docker_pull(request):
    return request.config.getoption("--dp")


@pytest.fixture(scope='session')
def session_id():
    """Unique session identifier, random string."""
    return 'aiohttp-admin'


@pytest.fixture(scope='session')
def docker():
    return DockerClient.from_env(assert_hostname=False)


@pytest.fixture(scope='session')
def pg_params(pg_server):
    return dict(**pg_server['pg_params'])


@pytest.yield_fixture(scope='session')
def pg_server(unused_port, docker, session_id, docker_pull):
    pg_tag = "9.5"
    print("Pulling postgress image")
    if docker_pull:
        docker.pull('postgres:{}'.format(pg_tag))
    port = unused_port()
    container = docker.create_container(
        image='postgres:{}'.format(pg_tag),
        name='aiopg-test-server-{}-{}'.format(pg_tag, session_id),
        ports=[5432],
        detach=True,
        host_config=docker.create_host_config(port_bindings={5432: port})
    )
    docker.start(container=container['Id'])
    host = os.environ.get('DOCKER_MACHINE_IP', '127.0.0.1')
    pg_params = dict(database='postgres',
                     user='postgres',
                     password='mysecretpassword',
                     host=host,
                     port=port)
    delay = 0.001
    for i in range(100):
        try:
            conn = psycopg2.connect(**pg_params)
            cur = conn.cursor()
            cur.close()
            conn.close()
            break
        except psycopg2.Error as e:
            print("Retry n = {} after e: {}".format(i, e))
            time.sleep(delay)
            delay *= 2
    else:
        pytest.fail("Cannot start postgres server")
    container['port'] = port
    container['pg_params'] = pg_params
    yield container

    docker.kill(container=container['Id'])
    docker.remove_container(container['Id'])


@pytest.fixture
def mysql_params(mysql_server):
    return dict(**mysql_server['mysql_params'])


@pytest.yield_fixture(scope='session')
def mysql_server(unused_port, docker, session_id, docker_pull):
    mysql_tag = '5.7'
    if docker_pull:
        docker.pull('mysql:{}'.format(mysql_tag))
    port = unused_port()
    container = docker.create_container(
        image='mysql:{}'.format(mysql_tag),
        name='mysql-test-server-{}-{}'.format(mysql_tag, session_id),
        ports=[3306],
        detach=True,
        environment={'MYSQL_USER': 'aiohttp_admin',
                     'MYSQL_PASSWORD': 'mysecretpassword',
                     'MYSQL_DATABASE': 'aiohttp_admin',
                     'MYSQL_ROOT_PASSWORD': 'mysecretpassword'},
        host_config=docker.create_host_config(port_bindings={3306: port})
    )
    docker.start(container=container['Id'])
    host = os.environ.get('DOCKER_MACHINE_IP', '127.0.0.1')
    mysql_params = dict(database='aiohttp_admin',
                        user='aiohttp_admin',
                        password='mysecretpassword',
                        host=host,
                        port=port)
    delay = 0.001
    for i in range(100):
        try:
            conn = pymysql.connect(**mysql_params)
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            cur.close()
            conn.close()
            break
        except pymysql.Error as e:
            print(e)
            time.sleep(delay)
            delay *= 2
    else:
        pytest.fail("Cannot start postgres server: {}".format(e))
    container['port'] = port
    container['mysql_params'] = mysql_params
    yield container

    docker.kill(container=container['Id'])
    docker.remove_container(container['Id'])