# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '04/Mar/2017'

from collections import deque


########################################################################
class SelectionQueue(deque):
    # def __init__(self, scene, iterable=None, maxLen=None):
    #     super(SelectionQueue, self).__init__(iterable, maxLen)
    def __init__(self, scene):
        super(SelectionQueue, self).__init__()
        self.scene = scene

    # ---------------------------------------------------------------------
    def append(self, item):
        if self:
            self[-1].isActiveItem = False
            self[-1].update()
        item.isActiveItem = True
        self.scene.activeItem = item
        item.update()
        super(SelectionQueue, self).append(item)

    # ---------------------------------------------------------------------
    def remove(self, item):
        item.isActiveItem = False
        item.update()
        self.scene.activeItem = None
        super(SelectionQueue, self).remove(item)
        if self:
            self[-1].isActiveItem = True
            self[-1].update()
            self.scene.activeItem = self[-1]
