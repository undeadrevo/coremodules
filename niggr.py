import requests
from util.hook import *
from util import output

apiurl = 'http://nig.gr/api/'


@hook(cmds=['short', 'nig', 'bitly'], ex='shorten url', rate=10, args=True)
def search(code, input):

    try:
        url = input.group(2)
        niggurl = requests.get(apiurl + url)

        return code.say('Shortened URL: %s' % niggurl.text())
    except Exception as e:
        output.error('Error in nigurl.py: %s' % str(e))
        return code.say('{b}Unable to shorten %s{b}' % input.group(2))
