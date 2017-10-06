from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction

import json
import logging
import os

matches_len = 0
bookmarks_path = ''
logger = logging.getLogger(__name__)


def find_bookmarks_path():
    f = os.popen('locate google-chrome | grep Bookmarks')
    res = f.read()
    res = res.split('\n')
    # logger.warning('IIIIIIIIIIIIIIIInfo "%s"' % res)
    # print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
    if len(res) == 0:
        print 'error'
        # logger.exception('Path to the Chrome Bookmarks was not found')
    if len(res) > 1:
        for i in range(0, len(res)):
            if res[i][-9:] == 'Bookmarks':
                return res[i]
    return ''


if len(bookmarks_path) == 0:
    bookmarks_path = find_bookmarks_path()
    if len(bookmarks_path) == 0:
        print 'error'
        # logger.exception('Path to the Chrome Bookmarks was not found')


def find_rec(data, query, matches):
    global matches_len

    if matches_len >= 10:
        return

    if data['type'] == 'folder':
        for i in range(0, len(data['children'])):
            find_rec(data['children'][i], query, matches)
    else:
        res = data['name'].lower().find(query, 0, len(data['name']))
        if res != -1:
            matches.append(data)
            matches_len += 1

    return matches


class DemoExtension(Extension):
    def __init__(self):
        super(DemoExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        global matches_len

        items = []
        matches = []
        matches_len = 0
        query = event.get_argument()

        if query is None:
            query = ''

        with open(bookmarks_path) as data_file:

            data = json.load(data_file)
            matches = find_rec(data['roots']['bookmark_bar'], query, matches)
            max_len = matches_len

            if matches_len < 10:
                max_len = matches_len
            for i in range(0, max_len):
                bookmark_name = matches[i]['name'].encode('utf-8')
                bookmark_url = matches[i]['url'].encode('utf-8')
                items.append(ExtensionResultItem(icon='images/chrome.png',
                                                 name='%s' % bookmark_name,
                                                 description='%s' % bookmark_url,
                                                 on_enter=OpenUrlAction(bookmark_url)))

        return RenderResultListAction(items)


if __name__ == '__main__':
    DemoExtension().run()
