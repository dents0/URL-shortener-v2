import re


def validate_url(url=None):
    """
    Checks if the passed string is a URL
    """

    url_filter = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    # URL matches the required pattern
    if re.search(url_filter, url) and '.' in url and url[-1] != '.':
        if 'forward-url-dot-tsokarev-gcp-test.appspot.com' in url:
            return "Seems that this url has been shortened already"
        return True
    # URL doesn't match the required pattern
    return "Wrong URL format"


