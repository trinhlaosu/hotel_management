"""User business logic."""


class UserService:
    def disable(self, user):
        user.is_active = False
        user.save(update_fields=['is_active', 'updated_at'])
        return user

    def enable(self, user):
        user.is_active = True
        user.save(update_fields=['is_active', 'updated_at'])
        return user
