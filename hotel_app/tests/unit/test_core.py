"""Core utility tests."""
from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from core.utils      import phan_hoi, doc_json, kiem_tra_role
from core.validators import kiem_tra_truong_bat_buoc, kiem_tra_ngay
from hotel_app.models    import User
import json


class PhanHoiTest(TestCase):

    def test_tra_ve_200_mac_dinh(self):
        res = phan_hoi(data={'id': 1})
        self.assertIsInstance(res, JsonResponse)
        self.assertEqual(res.status_code, 200)

    def test_co_data(self):
        res = phan_hoi(data={'key': 'value'})
        body = json.loads(res.content)
        self.assertIn('data', body)
        self.assertEqual(body['data']['key'], 'value')

    def test_co_message(self):
        res = phan_hoi(message='Thành công')
        body = json.loads(res.content)
        self.assertIn('message', body)
        self.assertEqual(body['message'], 'Thành công')

    def test_co_error(self):
        res = phan_hoi(error='Lỗi rồi', status=400)
        self.assertEqual(res.status_code, 400)
        body = json.loads(res.content)
        self.assertIn('error', body)

    def test_status_tuy_chinh(self):
        res = phan_hoi(message='Tạo mới', status=201)
        self.assertEqual(res.status_code, 201)


class DocJsonTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_doc_json_hop_le(self):
        req = self.factory.post('/',
            data=json.dumps({'name': 'test'}),
            content_type='application/json')
        data, err = doc_json(req)
        self.assertIsNotNone(data)
        self.assertIsNone(err)
        self.assertEqual(data['name'], 'test')

    def test_doc_json_khong_hop_le(self):
        req = self.factory.post('/',
            data='not json',
            content_type='application/json')
        data, err = doc_json(req)
        self.assertIsNone(data)
        self.assertIsNotNone(err)
        self.assertEqual(err.status_code, 400)


class KiemTraTruongBatBuocTest(TestCase):

    def test_du_truong(self):
        data = {'name': 'test', 'phone': '123'}
        ok, msg = kiem_tra_truong_bat_buoc(data, ['name', 'phone'])
        self.assertTrue(ok)
        self.assertEqual(msg, '')

    def test_thieu_truong(self):
        data = {'name': 'test'}
        ok, msg = kiem_tra_truong_bat_buoc(data, ['name', 'phone'])
        self.assertFalse(ok)
        self.assertIn('phone', msg)

    def test_truong_rong(self):
        data = {'name': '', 'phone': '123'}
        ok, msg = kiem_tra_truong_bat_buoc(data, ['name', 'phone'])
        self.assertFalse(ok)
        self.assertIn('name', msg)


class KiemTraNgayTest(TestCase):

    def test_ngay_hop_le(self):
        ok, msg = kiem_tra_ngay('2026-06-10', '2026-06-13')
        self.assertTrue(ok)
        self.assertEqual(msg, '')

    def test_check_out_truoc_check_in(self):
        ok, msg = kiem_tra_ngay('2026-06-13', '2026-06-10')
        self.assertFalse(ok)
        self.assertIn('sau check_in', msg)

    def test_check_in_bang_check_out(self):
        ok, msg = kiem_tra_ngay('2026-06-10', '2026-06-10')
        self.assertFalse(ok)

    def test_dinh_dang_sai(self):
        ok, msg = kiem_tra_ngay('10/06/2026', '13/06/2026')
        self.assertFalse(ok)
        self.assertIn('YYYY-MM-DD', msg)


class KiemTraRoleTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(
            username='ql_test', password='123',
            email='ql@t.com', role='quan_ly')

    def _make_request_with_session(self, user_id):
        from django.test import Client
        client = Client()
        session = client.session
        session['user_id'] = user_id
        session.save()
        req = self.factory.get('/')
        req.session = session
        return req

    def test_chua_dang_nhap(self):
        req = self.factory.get('/')
        req.session = {}
        user, err = kiem_tra_role(req, ['quan_ly'])
        self.assertIsNone(user)
        self.assertIsNotNone(err)
        self.assertEqual(err.status_code, 401)

    def test_dung_role(self):
        req = self._make_request_with_session(self.user.id)
        user, err = kiem_tra_role(req, ['quan_ly'])
        self.assertIsNotNone(user)
        self.assertIsNone(err)

    def test_sai_role(self):
        req = self._make_request_with_session(self.user.id)
        user, err = kiem_tra_role(req, ['le_tan'])  # Yêu cầu le_tan
        self.assertIsNone(user)
        self.assertIsNotNone(err)
        self.assertEqual(err.status_code, 403)
