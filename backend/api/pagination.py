from rest_framework.pagination import PageNumberPagination


class CustomPaginator(PageNumberPagination):
    """Стандартный пагинатор для вывода запрошенного количества страниц."""

    page_size_query_param = 'limit'
