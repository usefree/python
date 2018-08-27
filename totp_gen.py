def totpgen ():
	import time
	import hmac
	import hashlib
	import base64
	secret = base64.b32decode("ZVR5FGJUYC2DE6RY")
	counter = long(time.time() / 30)
	bytes=bytearray()
	for i in reversed(range(0, 8)):
		bytes.insert(0, counter & 0xff)
		counter >>= 8
	hs = bytearray(hmac.new(secret, bytes, hashlib.sha1).digest())
	n = hs[-1] & 0xF
	result = (hs[n] << 24 | hs[n+1] << 16 | hs[n+2] << 8 | hs[n+3]) & 0x7fffffff
	return str(result)[-6:]

print totpgen ()