from rest_framework.pagination import PageNumberPagination


class PropertyTenantPaginator(PageNumberPagination):
    page_size = 3


class PropertyLandlordPaginator(PageNumberPagination):
    page_size = 3