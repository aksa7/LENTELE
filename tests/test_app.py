import unittest
from app import app, collection
from datetime import datetime

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        collection.delete_many({})
        self.test_events = [
            {'name': 'Event 1', 'date': datetime(2023, 1, 10)},
            {'name': 'Event 2', 'date': datetime(2023, 2, 15)},
            {'name': 'Event 3', 'date': datetime(2023, 3, 20)},
            {'name': 'Event 4', 'date': datetime(2023, 12, 25)},
        ]
        collection.insert_many(self.test_events)

    def tearDown(self):
        collection.delete_many({})

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Renginiai pagal mėnesius', response.data.decode('utf-8'))

    def test_add_event(self):
        response = self.client.post('/add', data={'name': 'Test Event', 'date': '12/31'})
        self.assertEqual(response.status_code, 302)
        event = collection.find_one({'name': 'Test Event'})
        self.assertIsNotNone(event)

    def test_add_event_invalid_date(self):
        response = self.client.post('/add', data={'name': 'Invalid Date Event', 'date': 'invalid_date'})
        self.assertEqual(response.status_code, 302)
        event = collection.find_one({'name': 'Invalid Date Event'})
        self.assertIsNone(event)

    def test_delete_all_events(self):
        response = self.client.post('/delete_all')
        self.assertEqual(response.status_code, 302)
        events_count = collection.count_documents({})
        self.assertEqual(events_count, 0)

    def test_empty_database_behavior(self):
        collection.delete_many({})
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Event 1', response.data.decode('utf-8'))

    def test_event_order(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = response.data.decode('utf-8')
        self.assertTrue(data.index('Event 1') < data.index('Event 4'))

if __name__ == '__main__':
    unittest.main()
