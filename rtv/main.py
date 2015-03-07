import argparse
from getpass import getpass
import praw
from requests.exceptions import ConnectionError, HTTPError
from praw.errors import InvalidUserPass

from rtv.errors import SubmissionURLError, SubredditNameError
from rtv.utils import curses_session, load_config, HELP
from rtv.subreddit import SubredditPage
from rtv.submission import SubmissionPage

description = """
Reddit Terminal Viewer is a lightweight browser for www.reddit.com built into a
terminal window.
"""

# TODO: Figure out a way to sync this with the README
epilog = """
Controls
-----
RTV currently supports browsing both subreddits and individual submissions.
In each mode the controls are slightly different. In subreddit mode you can 
browse through the top submissions on either the front page or a specific 
subreddit. In submission mode you can view the self text for a submission and 
browse comments.
"""

epilog += HELP

def main():

    parser = argparse.ArgumentParser(
        prog='rtv', description=description, epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-s', dest='subreddit', help='subreddit name')
    parser.add_argument('-l', dest='link', help='full link to a submission')

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

    if args.subreddit is None:
        args.subreddit = 'front'

    try:
        # TODO: Move version number to a centralized location
        reddit = praw.Reddit(user_agent='reddit terminal viewer v1.05a')
        reddit.config.decode_html_entities = True

        if args.username:
            if args.password:
                reddit.login(args.username, args.password)
            else:
                password = getpass()
                reddit.login(args.username, password)

        with curses_session() as stdscr:

                if args.link:
                    page = SubmissionPage(stdscr, reddit, url=args.link)
                    page.loop()

                page = SubredditPage(stdscr, reddit, args.subreddit)
                page.loop()

    except InvalidUserPass:
        print('Invalid password for username: {}'.format(args.username)) 

    except KeyboardInterrupt:
        return

    except ConnectionError:
        print('Timeout: Could not connect to website')

    except HTTPError:
        print('HTTP Error: 404 Not Found')

    except SubmissionURLError as e:
        print('Could not reach submission URL: {}'.format(e.url))

    except SubredditNameError as e:
        print('Could not reach subreddit: {}'.format(e.name))


if __name__ == '__main__':
    main()
