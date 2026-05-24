"""Cac ham kiem tra du lieu dau vao."""


def kiem_tra_truong_bat_buoc(data, ds_truong):
    """Kiem tra cac truong bat buoc."""
    for truong in ds_truong:
        if not data.get(truong):
            return False, f'Thiếu trường bắt buộc: {truong}'
    return True, ''


def kiem_tra_ngay(check_in, check_out):
    """Kiem tra ngay tra phong sau ngay nhan phong."""
    from datetime import date
    try:
        ci = date.fromisoformat(str(check_in))
        co = date.fromisoformat(str(check_out))
        if co <= ci:
            return False, 'Ngày check_out phải sau check_in'
        return True, ''
    except ValueError:
        return False, 'Định dạng ngày không hợp lệ (YYYY-MM-DD)'

