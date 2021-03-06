import argparse
import locale

import praw
from requests.exceptions import ConnectionError, HTTPError
from praw.errors import InvalidUserPass

from .errors import SubmissionURLError, SubredditNameError
from .utils import Symbol, curses_session, load_config, HELP
from .subreddit import SubredditPage
from .submission import SubmissionPage

# Debugging
# import logging
# logging.basicConfig(level=logging.DEBUG, filename='rtv.log')

locale.setlocale(locale.LC_ALL, '')

AGENT = """
desktop:https://github.com/michael-lazar/rtv:(by /u/civilization_phaze_3)
"""

DESCRIPTION = """
Reddit Terminal Viewer is a lightweight browser for www.reddit.com built into a
terminal window.
"""

EPILOG = """
Controls
--------
RTV currently supports browsing both subreddits and individual submissions.
In each mode the controls are slightly different. In subreddit mode you can
browse through the top submissions on either the front page or a specific
subreddit. In submission mode you can view the self text for a submission and
browse comments.
"""

EPILOG += HELP

def main():

    parser = argparse.ArgumentParser(
        prog='rtv', description=DESCRIPTION, epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-s', dest='subreddit', help='subreddit name')
    parser.add_argument('-l', dest='link', help='full link to a submission')
    parser.add_argument('--unicode', help='enable unicode (experimental)',
            action='store_true')

    group = parser.add_argument_group(
        'authentication (optional)',
        'Authenticating allows you to view your customized front page. '
        'If only the username is given, the password will be prompted '
        'securely.')
    group.add_argument('-u', dest='username', help='reddit username')
    group.add_argument('-p', dest='password', help='reddit password')

    args = parser.parse_args()

    # Try to fill in empty arguments with values from the config.
    # Command line flags should always take priority!
    for key, val in load_config().items():
        if getattr(args, key) is None:
            setattr(args, key, val)

    Symbol.UNICODE = args.unicode

    if args.subreddit is None:
        args.subreddit = 'front'

    try:
        print('Connecting...')
        reddit = praw.Reddit(user_agent=AGENT)
        reddit.config.decode_html_entities = True

        if args.username:
            # PRAW will prompt for password if it is None
            reddit.login(args.username, args.password)

        with curses_session() as stdscr:

                if args.link:
                    page = SubmissionPage(stdscr, reddit, url=args.link)
                    page.loop()

                page = SubredditPage(stdscr, reddit, args.subreddit)
                page.loop()

    except InvalidUserPass:
        print('Invalid password for username: {}'.format(args.username))

    except ConnectionError:
        print('Connection timeout: Could not connect to http://www.reddit.com')

    except HTTPError:
        print('HTTP Error: 404 Not Found')

    except SubmissionURLError as e:
        print('Could not reach submission URL: {}'.format(e.url))

    except SubredditNameError as e:
        print('Could not reach subreddit: {}'.format(e.name))

    except KeyboardInterrupt:
        return

