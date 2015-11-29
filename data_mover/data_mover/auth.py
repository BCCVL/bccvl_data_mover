import binascii
import time

from pyramid.authentication import AuthTktAuthenticationPolicy as BasePolicy
from pyramid.authentication import AuthTktCookieHelper as BaseCookieHelper


class AuthTktAuthenticationPolicy(BasePolicy):

    def __init__(self,
                 secret,
                 callback=None,
                 cookie_name='auth_tkt',
                 secure=False,
                 include_ip=False,
                 timeout=None,
                 reissue_time=None,
                 max_age=None,
                 path="/",
                 http_only=False,
                 wild_domain=False,
                 debug=False,
                 hashalg='md5',
                 ):
        self.cookie = AuthTktCookieHelper(
            secret=secret,
            cookie_name=cookie_name,
            secure=secure,
            include_ip=include_ip,
            timeout=timeout,
            reissue_time=reissue_time,
            max_age=max_age,
            http_only=http_only,
            path=path,
            wild_domain=wild_domain,
            hashalg=hashalg)
        self.callback = callback
        self.debug = debug


class AuthTktCookieHelper(BaseCookieHelper):

    def identify(self, request):
        """ Return a dictionary with authentication information, or ``None``
        if no valid auth_tkt is attached to ``request``"""
        environ = request.environ
        cookie = request.cookies.get(self.cookie_name)

        if cookie is None:
            return None

        if self.include_ip:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'
        ticket = binascii.a2b_base64(cookie)

        try:
            timestamp, userid, tokens, user_data = self.parse_ticket(
                self.secret, ticket, remote_addr, self.hashalg)
        except self.BadTicket:
            return None

        now = self.now  # service tests

        if now is None:
            now = time.time()

        if self.timeout and ((timestamp + self.timeout) < now):
            # the auth_tkt data has expired
            return None

        userid_typename = 'userid_type:'
        user_data_info = user_data.split('|')
        for datum in filter(None, user_data_info):
            if datum.startswith(userid_typename):
                userid_type = datum[len(userid_typename):]
                decoder = self.userid_type_decoders.get(userid_type)
                if decoder:
                    userid = decoder(userid)

        reissue = self.reissue_time is not None

        if reissue and not hasattr(request, '_authtkt_reissued'):
            if ((now - timestamp) > self.reissue_time):
                # See https://github.com/Pylons/pyramid/issues#issue/108
                tokens = list(filter(None, tokens))
                headers = self.remember(request, userid, max_age=self.max_age,
                                        tokens=tokens)

                def reissue_authtkt(request, response):
                    if not hasattr(request, '_authtkt_reissue_revoked'):
                        for k, v in headers:
                            response.headerlist.append((k, v))

                request.add_response_callback(reissue_authtkt)
                request._authtkt_reissued = True

        environ['REMOTE_USER_TOKENS'] = tokens
        environ['REMOTE_USER_DATA'] = user_data
