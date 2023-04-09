import re

def get_email_body(envelope):
    body_plain = envelope['message']['payload']['body']['data']
    decoded_body_plain = base64.urlsafe_b64decode(body_plain).decode('utf-8')
    pattern = r'On .* wrote:|From: .* <.*@.*>\r\nSent:.*\r\nTo:.*\r\nSubject:.*\r\n|To:.*\r\nSubject:.*\r\n|On .* wrote:.*\r\n|.* <.*@.*> wrote:.*\r\n'
    regex = re.compile(pattern)
    cleaned_body_plain = regex.sub('', decoded_body_plain).replace('\r\n', ' ')
    return cleaned_body_plain.strip()
