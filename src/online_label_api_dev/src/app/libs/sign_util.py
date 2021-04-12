# -*- coding: utf8 -*-

if __name__ == '__main__':
    import hashlib
    import hmac
    import base64

    needToSign = bytes("123456").encode('utf-8')
    accesskeySecret = bytes("c3b3da6daa9c14d5082178a44be23fab").encode('utf-8')
    signature = base64.b64encode(hmac.new(accesskeySecret, needToSign, digestmod=hashlib.sha256).digest())
    print signature
