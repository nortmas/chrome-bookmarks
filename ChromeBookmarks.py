import json
import logging
import os

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction

logging.basicConfig()
logger = logging.getLogger(__name__)

support_browsers = ['google-chrome', 'chromium', 'Brave-Browser']
browser_imgs = {
    'google-chrome': 'images/chrome.png',
    'chromium': 'images/chromium.png',
    'Brave-Browser': 'images/brave.png',
}


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = extension.get_items(event.get_argument())
        return RenderResultListAction(items)


class ChromeBookmarks(Extension):
    matches_len = 0
    max_matches_len = 10

    def __init__(self):
        self.bookmarks_paths = self.find_bookmarks_paths()
        super(ChromeBookmarks, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    @staticmethod
    def find_bookmarks_paths():
        res_lst = []
        for browser in support_browsers:
            f = os.popen('locate %s | grep Bookmarks' % browser)
            res = f.read().split('\n')
            if len(res) == 0:
                logger.info('Path to the %s Bookmarks was not found' % browser)
                continue
            for one_path in res:
                if one_path.endswith('Bookmarks'):
                    res_lst.append((one_path, browser))

        if len(res_lst) == 0:
            logger.exception('Path to the Chrome Bookmarks was not found')
        return res_lst

    def find_rec(self, data, query, matches):

        if self.matches_len >= self.max_matches_len:
            return

        if data['type'] == 'folder':
            for child in data['children']:
                self.find_rec(child, query, matches)
        else:
            res = data['name'].lower().find(query.lower())
            if res != -1:
                matches.append(data)
                self.matches_len += 1

    def get_items(self, query):

        items = []
        self.matches_len = 0

        if query is None:
            query = ''

        for bookmarks_path, browser in self.bookmarks_paths:
            
            matches = []
            
            with open(bookmarks_path) as data_file:
                data = json.load(data_file)
                self.find_rec(data['roots']['bookmark_bar'], query, matches)
                self.find_rec(data['roots']['other'], query, matches)

            for bookmark in matches:
                bookmark_name = bookmark['name'].encode('utf-8')
                bookmark_url = bookmark['url'].encode('utf-8')
                item = ExtensionResultItem(
                    icon=browser_imgs.get(browser),
                    name='%s' % bookmark_name.decode('utf-8'),
                    description='%s' % bookmark_url.decode('utf-8'),
                    on_enter=OpenUrlAction(bookmark_url.decode('utf-8'))
                )
                items.append(item)

        return items
