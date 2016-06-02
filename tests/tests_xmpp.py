from unittest import TestCase

from sleek.component import Component
from db_access.sql_sever_interface import DB
from queueing_systems.sqs import SQS
from queueing_systems.kinesis import Kinesis

class TestQueues(TestCase):
	def test_sqs(self):
		pass

	def test_kinesis(self):
		pass 

class TestStanzas(TestCase):
	pass


class TestComponent(TestCase):
	def setUp(self):
		db = DB()
		queue = SQS()
		component = Component(db=db, queue=queue)
		component.connect()