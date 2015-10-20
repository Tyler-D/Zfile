#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Page(object):
    def __init__(self, total, page_no, page_size, template_link=None):
        if (page_no - 1) * page_size < 0 or (page_no - 1) * page_size >= total:
            page_no = 1

        self.total = total
        self.current = page_no
        self.previous = page_no - 1 if page_no > 1 else 0
        self.next = page_no + 1 if (page_no * page_size) < total else 0
