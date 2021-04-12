# -*- coding: utf-8 -*-
class Pagination(object):
    """Internal helper class returned by :meth:`BaseQuery.paginate`.  You
    can also construct it from any other SQLAlchemy query object if you are
    working with other libraries.  Additionally it is possible to pass `None`
    as query object in which case the :meth:`prev` and :meth:`next` will
    no longer work.
    """

    def __init__(self, paginator, page, per_page, total, total_count, items):
        #: the unlimited query object that was used to create this
        #: pagination object.
        # self.query = query
        #: the current page number (1 indexed)
        self.paginator = paginator
        self.page = page
        #: the number of items to be displayed on a page.
        self.per_page = per_page
        #: the total number of items matching the query
        self.total = total
        #: the total number of query
        self.total_count = total_count
        #: the items for the current page
        self.items = items

    def page_view(self):
        return {'page': self.page, 'limit': self.per_page, 'total': self.total_count}

    @property
    def pages(self):
        """The total number of pages"""
        pages = self.total
        return pages

    def prev(self, error_out=False):
        """Returns a :class:`Pagination` object for the previous page."""
        # assert self.query is not None, 'a query object is required ' \
        # 'for this method to work'
        return Pagination(self.paginator, self.page - 1, self.per_page, self.paginator.total_pages,
                          self.paginator.page(self.page - 1).object_list)

    @property
    def prev_num(self):
        """Number of the previous page."""
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        return Pagination(self.paginator, self.page + 1, self.per_page, self.paginator.total_pages,
                          self.paginator.page(self.page + 1).object_list)
        # assert self.query is not None, 'a query object is required ' \
        # 'for this method to work'
        # items = self.query(self.page+1, self.per_page)
        # return Pagination(self.query, self.page+1, self.per_page, self.total, items)
        # return self.query.paginate(self.page + 1, self.per_page, error_out)

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def next_num(self):
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or (
                    num > self.page - left_current - 1 and num < self.page + right_current) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
