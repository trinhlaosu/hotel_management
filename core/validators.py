"""Cac ham kiem tra du lieu dau vao."""
from core import messages as msg


def kiem_tra_truong_bat_buoc(data, ds_truong):
    """Kiem tra cac truong bat buoc."""
    for truong in ds_truong:
        if not data.get(truong):
            return False, msg.REQUIRED_FIELD.format(field=truong)
    return True, ''


def kiem_tra_ngay(check_in, check_out):
    """Kiem tra ngay tra phong sau ngay nhan phong."""
    from datetime import date
    try:
        ci = date.fromisoformat(str(check_in))
        co = date.fromisoformat(str(check_out))
        if co <= ci:
            return False, msg.CHECKOUT_AFTER_CHECKIN
        return True, ''
    except ValueError:
        return False, msg.DATE_FORMAT_INVALID

