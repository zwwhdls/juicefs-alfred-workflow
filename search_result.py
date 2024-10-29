class SearchResult(object):
    def __init__(self):
        self._title = None
        self._link = None
        self._subtitle = None
        self._content = None
        self._action = None

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, value):
        self._link = value

    @property
    def subtitle(self):
        return self._subtitle

    @subtitle.setter
    def subtitle(self, value):
        self._subtitle = value

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action = value
