# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__author__ = 'Erdinç Yılmaz'
__date__ = '23/Aug/2016'

from PySide6.QtCore import Qt, QRegExp
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont


########################################################################
class HtmlHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(HtmlHighlighter, self).__init__(parent)

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontWeight(QFont.Bold)

        keywordPatterns = ["\\b?xml\\b", "/>", ">", "<"]

        self.highlightingRules = [(QRegExp(pattern), keywordFormat)
                                  for pattern in keywordPatterns]

        htmlElementFormat = QTextCharFormat()
        htmlElementFormat.setFontWeight(QFont.Bold)
        htmlElementFormat.setForeground(Qt.darkMagenta)
        # self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=[\s/>])"), htmlElementFormat))
        # self.highlightingRules.append((QRegExp("\\b<([A-Z][A-Z0-9]*)\b[^>]*>(.*?)</\1>"), htmlElementFormat))
        self.highlightingRules.append((QRegExp(''), htmlElementFormat))

        htmlAttributeFormat = QTextCharFormat()
        htmlAttributeFormat.setFontItalic(True)
        htmlAttributeFormat.setForeground(Qt.blue)
        self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\=)"), htmlAttributeFormat))

    # VIRTUAL FUNCTION WE OVERRIDE THAT DOES ALL THE COLLORING
    def highlightBlock(self, text):

        # for every pattern
        for pattern, frmt in self.highlightingRules:

            # Create a regular expression from the retrieved pattern
            expression = QRegExp(pattern)

            # Check what index that expression occurs at with the ENTIRE text
            index = expression.indexIn(text)

            # While the index is greater than 0
            while index >= 0:
                # Get the length of how long the expression is true,
                # set the format from the start to the length with the text format
                length = expression.matchedLength()
                self.setFormat(index, length, frmt)

                # Set index to where the expression ends in the text
                index = expression.indexIn(text, index + length)

        # HANDLE QUOTATION MARKS NOW.. WE WANT TO START WITH " AND END WITH "..
        # A THIRD " SHOULD NOT CAUSE THE WORDS INBETWEEN SECOND AND THIRD TO BE COLORED
        self.setCurrentBlockState(0)
