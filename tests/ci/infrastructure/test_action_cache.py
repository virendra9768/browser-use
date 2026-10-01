import json

from browser_use.agent.action_cache import (
	CACHE_PATH_ENV,
	cache_executed_actions,
)


class FakeAction:
	def __init__(self, payload):
		self.payload = payload

	def model_dump(self, **kwargs):
		return self.payload


class FakeElement:
	def __init__(self, payload):
		self.payload = payload

	def to_dict(self):
		return self.payload


class FakeResult:
	def __init__(self, payload):
		self.payload = payload

	def model_dump(self, **kwargs):
		return self.payload


def test_cache_disabled_without_environment_variable(tmp_path, monkeypatch):
	monkeypatch.delenv(CACHE_PATH_ENV, raising=False)

	cache_path = tmp_path / 'actions.jsonl'

	count = cache_executed_actions(
		agent_id='agent-1',
		step=1,
		url_before='https://example.com',
		actions=[FakeAction({'click': {'index': 1}})],
		interacted_elements=[FakeElement({'node_name': 'button'})],
		results=[FakeResult({'success': True})],
	)

	assert count == 0
	assert not cache_path.exists()


def test_cache_writes_execution_record(tmp_path, monkeypatch):
	cache_path = tmp_path / 'actions.jsonl'
	monkeypatch.setenv(CACHE_PATH_ENV, str(cache_path))

	count = cache_executed_actions(
		agent_id='agent-123',
		step=2,
		url_before='https://example.com/login',
		actions=[
			FakeAction(
				{
					'input': {
						'index': 7,
						'text': 'hello',
					}
				}
			)
		],
		interacted_elements=[
			FakeElement(
				{
					'node_name': 'input',
					'attributes': {
						'name': 'username',
					},
				}
			)
		],
		results=[
			FakeResult(
				{
					'success': True,
				}
			)
		],
	)

	assert count == 1

	records = [json.loads(line) for line in cache_path.read_text(encoding='utf-8').splitlines()]

	assert len(records) == 1

	record = records[0]

	assert record['agent_id'] == 'agent-123'
	assert record['step'] == 2
	assert record['url_before'] == 'https://example.com/login'
	assert record['action']['input']['text'] == 'hello'
	assert record['interacted_element']['attributes']['name'] == 'username'
	assert record['result']['success'] is True
	assert record['timestamp']


def test_cache_appends_records(tmp_path, monkeypatch):
	cache_path = tmp_path / 'actions.jsonl'
	monkeypatch.setenv(CACHE_PATH_ENV, str(cache_path))

	for step in (1, 2):
		cache_executed_actions(
			agent_id='agent-1',
			step=step,
			url_before='https://example.com',
			actions=[FakeAction({'click': {'index': step}})],
			interacted_elements=[FakeElement({'node_name': 'button'})],
			results=[FakeResult({'success': True})],
		)

	records = [json.loads(line) for line in cache_path.read_text(encoding='utf-8').splitlines()]

	assert len(records) == 2
	assert records[0]['step'] == 1
	assert records[1]['step'] == 2
