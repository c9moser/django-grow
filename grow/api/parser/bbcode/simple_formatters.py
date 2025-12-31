
SIMPLE_FORMATTERS = [
    (('h1', "<h1>%(value)s</h1>"), {}),
    (('h2', "<h2>%(value)s</h2>"), {}),
    (('h3', "<h3>%(value)s</h3>"), {}),
    (('h4', "<h4>%(value)s</h4>"), {}),
    (('h5', "<h5>%(value)s</h5>"), {}),
    (('h6', "<h6>%(value)s</h6>"), {}),
    (('mark', "<mark>%(value)s</mark>"), {}),
    (("strong", "<strong>%(value)s</strong>"), {}),
    (("em", "<em>%(value)s</em>"), {}),
    (("br", "<br>"), {"standalone": True}),
    (('copy', "&copy;"), {'standalone': True}),
    (('reg', "&reg;"), {'standalone': True}),
    (('trade', "&trade;"), {'standalone': True}),
]

SIMPLE_DESCRIPTION_FORMATTERS = [
    (('h1', "<h3>%(value)s</h3>"), {}),
    (('h', "<h3>%(value)s</h3>"), {}),
    (('h2', "<h4>%(value)s</h4>"), {}),
    (('h3', "<h5>%(value)s</h5>"), {}),
    (('h4', "<h6>%(value)s</h6>"), {}),
    (('mark', "<mark>%(value)s</mark>"), {}),
    (("strong", "<strong>%(value)s</strong>"), {}),
    (("em", "<em>%(value)s</em>"), {}),
    (("br", "<br>"), {"standalone": True}),
    (('copy', "&copy;"), {'standalone': True}),
    (('reg', "&reg;"), {'standalone': True}),
    (('trade', "&trade;"), {'standalone': True}),
]
