from .paginate import Pagination
from .paginator import Paginator


def pager(query, page=1, per_page=20):
    paginator = Paginator(query, per_page)
    try:
        pagination = Pagination(paginator, page, per_page, paginator.total_pages, paginator.count,
                                paginator.page(page).object_list)
    except:
        page = paginator.total_pages
        paginator = Paginator(query, per_page)
        pagination = Pagination(paginator, page, per_page, paginator.total_pages, paginator.count,
                                paginator.page(page).object_list)
    return pagination
