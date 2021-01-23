import time
from multiprocessing.dummy import Pool as ThreadPool

import orjson
import pytest
import shortuuid

from django_unicorn.components import UnicornView
from django_unicorn.utils import generate_checksum


class FakeSlowComponent(UnicornView):
    template_name = "templates/test_component.html"

    counter = 0

    def slow_action(self):
        time.sleep(0.3)
        self.counter += 1


@pytest.mark.slow
def test_message_call_method_single(client):
    data = {}
    component_id = shortuuid.uuid()[:8]
    message = {
        "actionQueue": [{"payload": {"name": "slow_action"}, "type": "callMethod",}],
        "data": data,
        "checksum": generate_checksum(orjson.dumps(data)),
        "id": component_id,
        "epoch": time.time(),  # assert there is an epoch (or set it in Python?)
    }

    response = client.post(
        "/message/tests.views.message.test_call_method_multiple.FakeSlowComponent",
        message,
        content_type="application/json",
    )

    body = orjson.loads(response.content)
    assert body["data"].get("counter") == 1


def _message_runner(args):
    client = args[0]
    sleep_time = args[1]
    message = args[2]
    time.sleep(sleep_time)

    # TODO: assert there is an epoch (or set it in Python?) in component request init
    message["epoch"] = time.time()

    response = client.post(
        "/message/tests.views.message.test_call_method_multiple.FakeSlowComponent",
        message,
        content_type="application/json",
    )
    return response


@pytest.mark.slow
def test_message_call_method_two(client):
    data = {}
    component_id = shortuuid.uuid()[:8]
    message = {
        "actionQueue": [{"payload": {"name": "slow_action"}, "type": "callMethod",}],
        "data": data,
        "checksum": generate_checksum(orjson.dumps(data)),
        "id": component_id,
    }
    messages = [(client, 0, message), (client, 0.1, message)]

    with ThreadPool(len(messages)) as pool:
        results = pool.map(_message_runner, messages)
        assert len(results) == len(messages)

        first_result = results[0]
        first_body = orjson.loads(first_result.content)
        assert first_body["data"].get("counter") == 21

        second_result = results[1]
        second_body = orjson.loads(second_result.content)
        assert second_body["queued"] == True


@pytest.mark.slow
def test_message_call_method_multiple(client):
    data = {}
    component_id = shortuuid.uuid()[:8]
    message = {
        "actionQueue": [{"payload": {"name": "slow_action"}, "type": "callMethod",}],
        "data": data,
        "checksum": generate_checksum(orjson.dumps(data)),
        "id": component_id,
    }
    messages = [(client, 0, message), (client, 0.1, message), (client, 0.2, message)]

    with ThreadPool(len(messages)) as pool:
        results = pool.map(_message_runner, messages)
        assert len(results) == len(messages)

        first_result = results[0]
        first_body = orjson.loads(first_result.content)
        assert first_body["data"].get("counter") == len(results)

        for result in results[1:]:
            result = results[1]
            body = orjson.loads(result.content)
            assert body.get("queued") == True
