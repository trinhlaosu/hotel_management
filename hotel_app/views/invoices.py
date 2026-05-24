"""Invoice APIs."""
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from hotel_app.services.invoice_service import InvoiceService
from core.utils import phan_hoi, doc_json, yeu_cau_dang_nhap


@method_decorator(csrf_exempt, name='dispatch')
class InvoiceView(View):
    def get(self, request, pk=None):
        # GET /api/invoices/ va /api/invoices/<id>/ - xem danh sach/chi tiet hoa don.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        svc = InvoiceService()
        if pk:
            data, err_msg = svc.lay_chi_tiet(pk)
            if not data:
                return phan_hoi(error=err_msg, status=404)
            return phan_hoi(data=data)
        return phan_hoi(data=svc.lay_danh_sach())

    def post(self, request):
        """POST /api/invoices/."""
        # POST /api/invoices/ - tao hoa don thu cong cho booking.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        invoice_data, err_msg = InvoiceService().tao_hoa_don_thu_cong(
            data.get('booking_id'))
        if not invoice_data:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(
            data=invoice_data,
            message='Tạo hóa đơn thành công',
            status=201,
        )


@method_decorator(csrf_exempt, name='dispatch')
class InvoiceByBookingView(View):
    """GET /api/bookings/<pk>/invoice/."""

    def get(self, request, pk):
        # GET /api/bookings/<id>/invoice/ - xem hoa don gan voi booking.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err

        data, err_msg = InvoiceService().lay_theo_booking(pk)
        if not data:
            return phan_hoi(error=err_msg, status=404)
        return phan_hoi(data=data)


@method_decorator(csrf_exempt, name='dispatch')
class InvoicePayView(View):
    """PUT /api/invoices/<pk>/pay/."""

    def put(self, request, pk):
        # PUT /api/invoices/<id>/pay/ - thanh toan hoa don.
        user, err = yeu_cau_dang_nhap(request)
        if err:
            return err
        data, err = doc_json(request)
        if err:
            return err

        invoice, err_msg = InvoiceService().thanh_toan(
            pk, data.get('payment_method', 'tien_mat'))
        if not invoice:
            return phan_hoi(error=err_msg, status=400)

        return phan_hoi(
            data={
                'invoice_id': invoice.id,
                'total': float(invoice.total),
                'payment_method': invoice.payment_method,
                'paid_at': str(invoice.paid_at),
            },
            message='Thanh toán thành công',
        )

