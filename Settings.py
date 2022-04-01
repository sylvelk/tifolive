import os

DEBUG           = True
DIRNAME         = os.path.dirname(__file__)
STATIC_PATH     = os.path.join(DIRNAME, 'static')
TEMPLATE_PATH   = os.path.join(DIRNAME, 'templates')
COOKIE_SECRET   = "6d605c8b99fd4dbe830865eb4018bf2a"
XSRF_COOKIES    =  True
PORT            = 8000