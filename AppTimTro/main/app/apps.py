from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        import app.signals  # Đảm bảo tín hiệu được kết nối khi ứng dụng khởi động
