from regcore import app
from regcore.handlers.layer import *
from flasktest import FlaskTest
import json
from mock import patch

class HandlersLayerTest(FlaskTest):

    def setUp(self):
        FlaskTest.setUp(self)
        app.register_blueprint(blueprint)

    def test_add_not_json(self):
        url = '/layer/layname/lablab/verver'

        response = self.client.put(url, data = json.dumps({'lablab': []}))
        self.assertEqual(400, response.status_code)

        response = self.client.put(url, content_type='application/json',
            data = '{Invalid}')
        self.assertEqual(400, response.status_code)

    def test_add_label_mismatch(self):
        url = '/layer/layname/lablab/verver'

        response = self.client.put(url, content_type='application/json',
            data = json.dumps({'nonlab': []}))
        self.assertEqual(400, response.status_code)

    def test_add_post(self):
        url = '/layer/layname/lablab/verver'

        response = self.client.post(url, content_type='application/json',
            data = json.dumps({'lablab': []}))
        self.assertEqual(405, response.status_code)

    @patch('regcore.handlers.layer.db')
    def test_add_success(self, db):
        url = '/layer/layname/lablab/verver'

        message = {
            'lablab': [1, 2],
            'lablab-b': [2, 3],
            'lablab-b-4': [3,4],
        }
        db.Regulations.return_value.get.return_value = {
            'label': ['lablab'],
            'children': [{
                'label': ['lablab', 'b'],
                'children': [{
                    'label': ['lablab', 'b', '4'],
                    'children': []
                }]
            }]
        }
        response = self.client.put(url, content_type='application/json',
            data = json.dumps(message))
        self.assertTrue(db.Layers.return_value.bulk_put.called)
        args = db.Layers.return_value.bulk_put.call_args[0][0]
        args = list(reversed(args))   # switch to outside in

        self.assertEqual(3, len(args))
        self.assertEqual(message, args[0]['layer'])
        self.assertEqual('verver/layname/lablab', args[0]['id'])
        self.assertEqual('lablab', args[0]['label'])
        #   Sub layers have fewer elements
        del message['lablab']
        self.assertEqual(message, args[1]['layer'])
        self.assertEqual('verver/layname/lablab-b', args[1]['id'])
        self.assertEqual('lablab-b', args[1]['label'])
        del message['lablab-b']
        self.assertEqual(message, args[2]['layer'])
        self.assertEqual('verver/layname/lablab-b-4', args[2]['id'])
        self.assertEqual('lablab-b-4', args[2]['label'])

    @patch('regcore.handlers.layer.db')
    def test_add_skip_level(self, db):
        url = '/layer/layname/lablab/verver'

        message = {
            'lablab': [1, 2],
            'lablab-b-4': [3,4],
        }
        db.Regulations.return_value.get.return_value = {
            'label': ['lablab'],
            'children': [{
                'label': ['lablab', 'b'],
                'children': [{
                    'label': ['lablab', 'b', '4'],
                    'children': []
                }]
            }]
        }
        response = self.client.put(url, content_type='application/json',
            data = json.dumps(message))
        self.assertTrue(db.Layers.return_value.bulk_put.called)
        args = db.Layers.return_value.bulk_put.call_args[0][0]
        args = list(reversed(args))   # switch to outside in

        self.assertEqual(3, len(args))
        self.assertEqual(message, args[0]['layer'])
        self.assertEqual('verver/layname/lablab', args[0]['id'])
        self.assertEqual('lablab', args[0]['label'])
        #   Sub layers have fewer elements
        del message['lablab']
        self.assertEqual(message, args[1]['layer'])
        self.assertEqual('verver/layname/lablab-b', args[1]['id'])
        self.assertEqual('lablab-b', args[1]['label'])
        self.assertEqual(message, args[2]['layer'])
        self.assertEqual('verver/layname/lablab-b-4', args[2]['id'])
        self.assertEqual('lablab-b-4', args[2]['label'])

    @patch('regcore.handlers.layer.db')
    def test_add_interp_children(self, db):
        url = '/layer/layname/99/verver'

        message = {'99-5-Interp': [1,2], '99-5-a-Interp': [3,4]}
        db.Regulations.return_value.get.return_value = {
            'label': ['99'],
            'children': [{
                'label': ['99', 'Interp'],
                'children': [{
                    'label': ['99', '5', 'Interp'],
                    'children': [{
                        'label': ['99', '5', 'a', 'Interp'],
                        'children': [],
                    }]
                }]
            }]
        }
        self.client.put(url, content_type='application/json',
            data = json.dumps(message))
        args = db.Layers.return_value.bulk_put.call_args[0][0]
        self.assertEqual(4, len(args))
        args = list(reversed(args))   # switch to outside in
        self.assertTrue('99-5-Interp' in args[0]['layer'])
        self.assertTrue('99-5-a-Interp' in args[0]['layer'])
        self.assertTrue('99-5-Interp' in args[1]['layer'])
        self.assertTrue('99-5-a-Interp' in args[1]['layer'])
        self.assertTrue('99-5-Interp' in args[2]['layer'])
        self.assertTrue('99-5-a-Interp' in args[2]['layer'])
        self.assertFalse('99-5-Interp' in args[3]['layer'])
        self.assertTrue('99-5-a-Interp' in args[3]['layer'])

    @patch('regcore.handlers.layer.db')
    def test_add_subpart_children(self, db):
        url = '/layer/layname/99/verver'

        message = {'99-1': [1,2], '99-1-a': [3,4]}
        db.Regulations.return_value.get.return_value = {
            'label': ['99'],
            'children': [{
                'label': ['99', 'Subpart', 'A'],
                'children': [{
                    'label': ['99', '1'],
                    'children': [{
                        'label': ['99', '1', 'a'],
                        'children': []
                    }]
                }]
            }]
        }
        self.client.put(url, content_type='application/json',
            data = json.dumps(message))
        args = db.Layers.return_value.bulk_put.call_args[0][0]
        self.assertEqual(4, len(args))
        args = list(reversed(args))   # switch to outside in
        self.assertTrue('99-1' in args[0]['layer'])
        self.assertTrue('99-1' in args[1]['layer'])
        self.assertTrue('99-1' in args[2]['layer'])
        self.assertTrue('99-1-a' in args[0]['layer'])
        self.assertTrue('99-1-a' in args[1]['layer'])
        self.assertTrue('99-1-a' in args[2]['layer'])
        self.assertTrue('99-1-a' in args[3]['layer'])

    @patch('regcore.handlers.layer.db')
    def test_add_referenced(self, db):
        url = '/layer/layname/99/verver'

        message = {'99-1': [1,2], '99-1-a': [3,4], 'referenced': [5,6]}
        db.Regulations.return_value.get.return_value = {
            'label': ['99'],
            'children': [{
                'label': ['99', 'Subpart', 'A'],
                'children': [{
                    'label': ['99', '1'],
                    'children': [{
                        'label': ['99', '1', 'a'],
                        'children': []
                    }]
                }]
            }]
        }
        self.client.put(url, content_type='application/json',
            data = json.dumps(message))
        args = db.Layers.return_value.bulk_put.call_args[0][0]
        self.assertEqual(4, len(args))
        self.assertTrue('referenced' in args[0]['layer'])
        self.assertTrue('referenced' in args[1]['layer'])
        self.assertTrue('referenced' in args[2]['layer'])
        self.assertTrue('referenced' in args[3]['layer'])

    @patch('regcore.handlers.layer.db')
    def test_child_layers_no_results(self, db):
        db.Regulations.return_value.get.return_value = None
        self.assertEqual([], child_layers('layname', 'lll', 'vvv', {}))
        self.assertTrue(db.Regulations.return_value.get.called)
        self.assertEqual('lll',
                db.Regulations.return_value.get.call_args[0][0])
        self.assertEqual('vvv',
                db.Regulations.return_value.get.call_args[0][1])

    @patch('regcore.handlers.layer.db')
    def test_get_none(self, db):
        url = '/layer/layname/lablab/verver'

        db.Layers.return_value.get.return_value = None
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    @patch('regcore.handlers.layer.db')
    def test_get_results(self, db):
        db.Layers.return_value.get.return_value = {'example': 'response'}
        response = self.client.get('/layer/nnn/lll/vvv')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'example': 'response'}, json.loads(response.data))

    @patch('regcore.handlers.layer.db')
    def test_get_results_empty_layer(self, db):
        db.Layers.return_value.get.return_value = {}
        response = self.client.get('/layer/nnn/lll/vvv')
        self.assertEqual(200, response.status_code)
        self.assertEqual({}, json.loads(response.data))


    def test_child_label_of(self):
        self.assertTrue(child_label_of('1005-5-a-1-Interp-1', 
            '1005-5-Interp'))
