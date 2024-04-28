my_str = 'https://oauth.vk.com/blank.html#access_token=vk1.a.hUyi5SWPPqeCXcgfS6aGw2uwFj7OUiq7MoiL5XJYXpsxHVOlqsS4iWmAGCMlTWeW50FGmmufiL29JcvITzrhkj5dmAU5hXmb3HFJvsknerxfxnsLRwU01OC5J2SAN0OUefunGhX7Bkp2U4n2fQKWYLmMPKKEqyc03XyBXoNxr961YxCxrRcnNjNrFsivIOpK&expires_in=86400&user_id=187352442&state=123456'
token = my_str.split('=')[1].replace('&expires_in', '')
user_id = my_str.split('=')[3].replace('&state', '')
print(token)
print(user_id)
print(str(), type(str()))
