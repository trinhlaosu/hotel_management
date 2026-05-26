"""Service tests."""
from django.test import TestCase
from hotel_app.models import (
    Customer, RoomType, Room, Booking, Service,
    BookingService as BookingServiceModel,
)
from hotel_app.services.room_service    import RoomService
from hotel_app.services.booking_service import BookingService as BookingWorkflowService
from hotel_app.services.invoice_service import InvoiceService
from hotel_app.services.report_service  import ReportService
from datetime import date


class BaseTestData(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.room_type = RoomType.objects.create(
            name='Standard', price_per_night=500000, capacity=2)

        cls.room = Room.objects.create(
            room_type=cls.room_type,
            room_number='101', floor=1, status='trong')

        cls.customer = Customer.objects.create(
            full_name='Nguyễn Văn Test',
            phone='0901111111',
            id_card='111111111111')

        cls.service = Service.objects.create(
            name='Ăn sáng', price=150000, is_active=True)


class RoomServiceTest(BaseTestData):

    def setUp(self):
        self.svc = RoomService()

    def test_kiem_tra_phong_trong_khi_khong_co_booking(self):
        ket_qua = self.svc.kiem_tra_trong(
            self.room.id,
            date(2026, 6, 10),
            date(2026, 6, 13)
        )
        self.assertTrue(ket_qua)

    def test_kiem_tra_phong_da_co_booking(self):
        Booking.objects.create(
            customer=self.customer,
            room=self.room,
            check_in=date(2026, 6, 10),
            check_out=date(2026, 6, 13),
            status='da_xac_nhan'
        )
        ket_qua = self.svc.kiem_tra_trong(
            self.room.id,
            date(2026, 6, 11),
            date(2026, 6, 14)
        )
        self.assertFalse(ket_qua)

    def test_kiem_tra_phong_truoc_booking(self):
        Booking.objects.create(
            customer=self.customer,
            room=self.room,
            check_in=date(2026, 6, 15),
            check_out=date(2026, 6, 18),
            status='da_xac_nhan'
        )
        ket_qua = self.svc.kiem_tra_trong(
            self.room.id,
            date(2026, 6, 10),
            date(2026, 6, 14)
        )
        self.assertTrue(ket_qua)

    def test_cap_nhat_trang_thai_thanh_cong(self):
        ok, room = self.svc.cap_nhat_trang_thai(self.room.id, 'bao_tri')
        self.assertTrue(ok)
        self.assertEqual(room.status, 'bao_tri')
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, 'bao_tri')

    def test_cap_nhat_trang_thai_phong_khong_ton_tai(self):
        ok, room = self.svc.cap_nhat_trang_thai(9999, 'trong')
        self.assertFalse(ok)
        self.assertIsNone(room)

    def test_lay_thong_ke_phong(self):
        Room.objects.create(
            room_type=self.room_type,
            room_number='102', floor=1, status='co_khach')
        thong_ke = self.svc.lay_thong_ke_phong()
        self.assertIn('tong', thong_ke)
        self.assertIn('trong', thong_ke)
        self.assertIn('co_khach', thong_ke)
        self.assertGreaterEqual(thong_ke['tong'], 2)

    def test_ten_service(self):
        self.assertEqual(self.svc.ten_service, 'RoomService')


class BookingServiceTest(BaseTestData):

    def setUp(self):
        self.svc = BookingWorkflowService()

    def test_tinh_so_dem(self):
        so_dem = self.svc.tinh_so_dem(
            date(2026, 6, 10), date(2026, 6, 13))
        self.assertEqual(so_dem, 3)

    def test_tinh_so_dem_tu_string(self):
        so_dem = self.svc.tinh_so_dem('2026-06-10', '2026-06-15')
        self.assertEqual(so_dem, 5)

    def test_tinh_tien_phong(self):
        booking = Booking.objects.create(
            customer=self.customer, room=self.room,
            check_in=date(2026, 6, 10), check_out=date(2026, 6, 13),
            status='cho_xac_nhan')
        booking = Booking.objects.select_related(
            'room__room_type').get(id=booking.id)
        tien = self.svc.tinh_tien_phong(booking)
        self.assertEqual(tien, 1500000.0)   # 3 × 500.000

    def test_tao_booking_thanh_cong(self):
        data = {
            'customer_id': self.customer.id,
            'room_id':     self.room.id,
            'check_in':    '2026-06-20',
            'check_out':   '2026-06-23',
        }
        booking, err = self.svc.tao_booking(data)
        self.assertIsNotNone(booking)
        self.assertIsNone(err)
        self.assertEqual(booking.status, 'cho_xac_nhan')

    def test_tao_booking_phong_trung_lich(self):
        Booking.objects.create(
            customer=self.customer, room=self.room,
            check_in=date(2026, 6, 20), check_out=date(2026, 6, 23),
            status='da_xac_nhan')

        data = {
            'customer_id': self.customer.id,
            'room_id':     self.room.id,
            'check_in':    '2026-06-21',
            'check_out':   '2026-06-24',
        }
        booking, err = self.svc.tao_booking(data)
        self.assertIsNone(booking)
        self.assertIsNotNone(err)
        self.assertIn('đã có người đặt', err)

    def test_xac_nhan_booking(self):
        b = Booking.objects.create(
            customer=self.customer, room=self.room,
            check_in=date(2026, 7, 1), check_out=date(2026, 7, 3),
            status='cho_xac_nhan')
        result, err = self.svc.xac_nhan_booking(b.id)
        self.assertIsNotNone(result)
        self.assertIsNone(err)
        self.assertEqual(result.status, 'da_xac_nhan')

    def test_xac_nhan_booking_sai_trang_thai(self):
        b = Booking.objects.create(
            customer=self.customer, room=self.room,
            check_in=date(2026, 7, 5), check_out=date(2026, 7, 7),
            status='dang_o')
        result, err = self.svc.xac_nhan_booking(b.id)
        self.assertIsNone(result)
        self.assertIsNotNone(err)

    def test_huy_booking(self):
        b = Booking.objects.create(
            customer=self.customer, room=self.room,
            check_in=date(2026, 8, 1), check_out=date(2026, 8, 3),
            status='cho_xac_nhan')
        result, err = self.svc.huy_booking(b.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, 'da_huy')

    def test_check_in(self):
        b = Booking.objects.create(
            customer=self.customer, room=self.room,
            check_in=date(2026, 9, 1), check_out=date(2026, 9, 3),
            status='da_xac_nhan')
        result, err = self.svc.check_in(b.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, 'dang_o')
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, 'co_khach')

    def test_check_in_chua_xac_nhan(self):
        b = Booking.objects.create(
            customer=self.customer, room=self.room,
            check_in=date(2026, 9, 5), check_out=date(2026, 9, 7),
            status='cho_xac_nhan')    # Chưa xác nhận
        result, err = self.svc.check_in(b.id)
        self.assertIsNone(result)
        self.assertIsNotNone(err)

    def test_check_out(self):
        b = Booking.objects.create(
            customer=self.customer, room=self.room,
            check_in=date(2026, 10, 1), check_out=date(2026, 10, 4),
            status='dang_o')
        self.room.status = 'co_khach'
        self.room.save()

        b_full = Booking.objects.select_related(
            'room__room_type').get(id=b.id)
        result, err = self.svc.check_out(b_full.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, 'da_tra_phong')
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, 'trong')

    def test_ten_service(self):
        self.assertEqual(self.svc.ten_service, 'BookingService')


class InvoiceServiceTest(BaseTestData):

    def setUp(self):
        self.svc = InvoiceService()
        self.booking = Booking.objects.create(
            customer=self.customer, room=self.room,
            check_in=date(2026, 6, 10), check_out=date(2026, 6, 13),
            status='dang_o')
        self.booking = Booking.objects.select_related(
            'room__room_type').get(id=self.booking.id)

    def test_tao_hoa_don(self):
        invoice = self.svc.tao_hoa_don(self.booking)
        self.assertIsNotNone(invoice)
        self.assertEqual(float(invoice.room_charge), 1500000.0)
        self.assertEqual(invoice.payment_status, 'chua_thanh_toan')

    def test_tao_hoa_don_co_dich_vu(self):
        BookingServiceModel.objects.create(
            booking=self.booking, service=self.service,
            quantity=2, subtotal=300000)   # 2 × 150.000
        invoice = self.svc.tao_hoa_don(self.booking)
        self.svc.cap_nhat_hoa_don(self.booking)
        invoice.refresh_from_db()
        self.assertEqual(float(invoice.service_charge), 300000.0)
        self.assertEqual(float(invoice.total),
                         float(invoice.room_charge) + 300000.0)

    def test_thanh_toan_thanh_cong(self):
        invoice = self.svc.tao_hoa_don(self.booking)
        result, err = self.svc.thanh_toan(invoice.id, 'tien_mat')
        self.assertIsNotNone(result)
        self.assertIsNone(err)
        self.assertEqual(result.payment_status, 'da_thanh_toan')
        self.assertEqual(result.payment_method, 'tien_mat')
        self.assertIsNotNone(result.paid_at)

    def test_thanh_toan_lan_2_bi_loi(self):
        invoice = self.svc.tao_hoa_don(self.booking)
        self.svc.thanh_toan(invoice.id, 'tien_mat')      # Lần 1
        result, err = self.svc.thanh_toan(invoice.id, 'the')  # Lần 2
        self.assertIsNone(result)
        self.assertIn('đã được thanh toán', err)

    def test_ten_service(self):
        self.assertEqual(self.svc.ten_service, 'InvoiceService')


class ReportServiceTest(BaseTestData):

    def setUp(self):
        self.svc = ReportService()

    def test_thong_ke_trang_thai_phong(self):
        ket_qua = self.svc.thong_ke_trang_thai_phong()
        self.assertIn('tong', ket_qua)
        self.assertIn('trong', ket_qua)
        self.assertIn('co_khach', ket_qua)
        self.assertIn('bao_tri', ket_qua)
        self.assertEqual(ket_qua['tong'],
                         ket_qua['trong'] + ket_qua['co_khach']
                         + ket_qua['bao_tri'])

    def test_thong_ke_doanh_thu_trong(self):
        ket_qua = self.svc.thong_ke_doanh_thu()
        self.assertEqual(ket_qua['tong_doanh_thu'], 0)
        self.assertEqual(ket_qua['so_hoa_don_da_tt'], 0)

    def test_thong_ke_dat_phong(self):
        ket_qua = self.svc.thong_ke_dat_phong()
        self.assertIn('tong', ket_qua)
        self.assertIn('cho_xac_nhan', ket_qua)
        self.assertIn('dang_o', ket_qua)
        self.assertIn('da_tra_phong', ket_qua)
        self.assertIn('da_huy', ket_qua)

    def test_top_dich_vu(self):
        b = Booking.objects.create(
            customer=self.customer, room=self.room,
            check_in=date(2026, 6, 1), check_out=date(2026, 6, 3),
            status='da_tra_phong')
        BookingServiceModel.objects.create(
            booking=b, service=self.service,
            quantity=3, subtotal=450000)

        ds = self.svc.top_dich_vu(top_n=5)
        self.assertIsInstance(ds, list)
        if ds:
            item = ds[0]
            self.assertIn('ten_dich_vu', item)
            self.assertIn('tong_so_luong', item)
            self.assertIn('tong_tien', item)

    def test_ten_service(self):
        self.assertEqual(self.svc.ten_service, 'ReportService')
