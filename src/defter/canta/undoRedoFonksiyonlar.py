# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '05/Nov/2018'
__author__ = 'Erdinç Yılmaz'

from .undoRedoSiniflar import (UndoableSayfaAdiDegistir, UndoableAddItem, UndoableRemoveItem, UndoableGroup,
                               UndoableUnGroup, UndoableParent, UndoableUnParent, UndoableResizeBaseItem, UndoableScaleBaseItemByResizing,
                               UndoableScalePathItemByScalingPath, UndoableSetFont, UndoableSetFontSizeF, UndoableRotate,
                               UndoableRotateWithOffset, UndoableSetZValue, UndoableSetLineStyle, UndoableSetLineJoinStyle,
                               UndoableSetLineCapStyle, UndoableSetLineColor, UndoableSetTextColor,
                               UndoableSetLineColorAlpha, UndoableSetTextColorAlpha, UndoableSetItemBackgroundColor,
                               UndoableSetItemBackgroundColorAlpha, UndoableStilAdiDegistir, UndoableStiliNesneyeUygula, UndoableStiliUygula,
                               UndoableSetImageOpacity, UndoableSetSceneBackgroundBrush, UndoableSetSceneBackgroundImage,
                               UndoableEmbedSceneBackgroundImage, UndoableSetPinStatus, UndoableItemSetText, UndoableItemCustomCommand,
                               UndoableEmbedImage, UndoableEmbedVideo, UndoableMove, UndoableEmbedFile, UndoableResizeLineItem,
                               UndoableMovePathPoint, UndoableSetTextAlignment, UndoableSetCharacterFormat, UndoableSetLineWidthF,
                               UndoableConvertToPlainText, UndoRedoBaglantisiYaziNesnesiDocuna, UndoableScaleLineItemByScalingLine,
                               UndoableScaleTextItemByResizing, UndoableScaleGroupItemByResizing, UndoableDeletePathPoint, UndoableResizeGroupItem,
                               UndoableResizePathItem)


# ---------------------------------------------------------------------
def undoRedoBaglantisiYaziNesnesiDocuna(undoStack, description, doc):
    command = UndoRedoBaglantisiYaziNesnesiDocuna(description, doc)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSayfaAdiDegistir(undoStack, description, sayfa, sayfa_eski_adi):
    command = UndoableSayfaAdiDegistir(description, sayfa, sayfa_eski_adi)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableAddItem(undoStack, description, scene, item):
    command = UndoableAddItem(description, scene, item)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableRemoveItem(undoStack, description, scene, item, addToUnGroupedRootItems):
    command = UndoableRemoveItem(description, scene, item, addToUnGroupedRootItems)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableGroup(undoStack, description, items, scene):
    command = UndoableGroup(description, items, scene)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableUnGroup(undoStack, description, group):
    command = UndoableUnGroup(description, group)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableParent(undoStack, description, item, parentItem, yeniPos):
    command = UndoableParent(description, item, parentItem, yeniPos)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableUnParent(undoStack, description, item, yeniParentItem, yeniPos):
    command = UndoableUnParent(description, item, yeniParentItem, yeniPos)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableResizeBaseItem(undoStack, description, item, yeniRect, eskiRect, eskiPos):
    command = UndoableResizeBaseItem(description, item, yeniRect, eskiRect, eskiPos)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableResizeLineItem(undoStack, description, item, yeniLine, eskiLine, eskiPos, degisenNokta=None):
    command = UndoableResizeLineItem(description, item, yeniLine, eskiLine, eskiPos, degisenNokta)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableResizeGroupItem(undoStack, description, item, eskiRect, yeniRect, eskiPos, yeniPos, scaleFactorX, scaleFactorY):
    command = UndoableResizeGroupItem(description, item, eskiRect, yeniRect, eskiPos, yeniPos, scaleFactorX, scaleFactorY)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableResizePathItem(undoStack, description, item, scaledPath, yeniPos):
    command = UndoableResizePathItem(description, item, scaledPath, yeniPos)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableScaleGroupItemByResizing(undoStack, description, item, yeniRect, scaleFactor, yeniPos):
    command = UndoableScaleGroupItemByResizing(description, item, yeniRect, scaleFactor, yeniPos)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableScaleBaseItemByResizing(undoStack, description, item, yeniRect, scaleFactor, yeniPos):
    command = UndoableScaleBaseItemByResizing(description, item, yeniRect, scaleFactor, yeniPos)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableScaleTextItemByResizing(undoStack, description, item, scaleFactor, fontPointSizeF):
    command = UndoableScaleTextItemByResizing(description, item, scaleFactor, fontPointSizeF)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableScalePathItemByScalingPath(undoStack, description, item, path, scaleFactor):
    command = UndoableScalePathItemByScalingPath(description, item, path, scaleFactor)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableScaleLineItemByScalingLine(undoStack, description, item, line, scaleFactor):
    command = UndoableScaleLineItemByScalingLine(description, item, line, scaleFactor)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetFont(undoStack, description, item, font):
    command = UndoableSetFont(description, item, font)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetFontSizeF(undoStack, description, item, fontPointSizeF):
    command = UndoableSetFontSizeF(description, item, fontPointSizeF)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetCharacterFormat(undoStack, description, item, sozluk):
    command = UndoableSetCharacterFormat(description, item, sozluk)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetTextAlignment(undoStack, description, item, hiza):
    command = UndoableSetTextAlignment(description, item, hiza)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableRotate(undoStack, description, item, rotation):
    command = UndoableRotate(description, item, rotation)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableRotateWithOffset(undoStack, description, item, rotation):
    command = UndoableRotateWithOffset(description, item, rotation)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetZValue(undoStack, description, item, zValue):
    command = UndoableSetZValue(description, item, zValue)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetLineStyle(undoStack, description, item, lineStyle):
    command = UndoableSetLineStyle(description, item, lineStyle)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetLineJoinStyle(undoStack, description, item, joinStyle):
    command = UndoableSetLineJoinStyle(description, item, joinStyle)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetLineCapStyle(undoStack, description, item, capStyle):
    command = UndoableSetLineCapStyle(description, item, capStyle)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetLineWidthF(undoStack, description, item, widthF):
    command = UndoableSetLineWidthF(description, item, widthF)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetLineColor(undoStack, description, item, color, renkSecicidenMi):
    command = UndoableSetLineColor(description, item, color, renkSecicidenMi)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetTextColor(undoStack, description, item, color, renkSecicidenMi):
    command = UndoableSetTextColor(description, item, color, renkSecicidenMi)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetItemBackgroundColor(undoStack, description, item, color, renkSecicidenMi):
    command = UndoableSetItemBackgroundColor(description, item, color, renkSecicidenMi)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetItemBackgroundColorAlpha(undoStack, description, item, color):
    command = UndoableSetItemBackgroundColorAlpha(description, item, color)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetLineColorAlpha(undoStack, description, item, color):
    command = UndoableSetLineColorAlpha(description, item, color)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetTextColorAlpha(undoStack, description, item, color):
    command = UndoableSetTextColorAlpha(description, item, color)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableStilAdiDegistir(undoStack, description, nesne, yeni_isim):
    command = UndoableStilAdiDegistir(description, nesne, yeni_isim)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableStiliNesneyeUygula(undoStack, description, item, pen, brush, font, yaziRengi, cizgiRengi):
    command = UndoableStiliNesneyeUygula(description, item, pen, brush, font, yaziRengi, cizgiRengi)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableStiliUygula(undoStack, description, eskiPen, yeniPen, yaziRengi, eskiYaziRengi, cizgiRengi,
                        eskiCizgiRengi,
                        eskiArkaPlanRengi, yeniArkaPlanRengi, eskiFont, yeniFont, scene):
    command = UndoableStiliUygula(description, eskiPen, yeniPen, yaziRengi, eskiYaziRengi, cizgiRengi,
                                  eskiCizgiRengi,
                                  eskiArkaPlanRengi, yeniArkaPlanRengi, eskiFont, yeniFont,
                                  scene)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetImageOpacity(undoStack, description, item, imageOpacity):
    command = UndoableSetImageOpacity(description, item, imageOpacity)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetSceneBackgroundBrush(undoStack, description, view, color):
    command = UndoableSetSceneBackgroundBrush(description, view, color)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetSceneBackgroundImage(undoStack, description, view, imagePath):
    command = UndoableSetSceneBackgroundImage(description, view, imagePath)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableEmbedSceneBackgroundImage(undoStack, description, view, ):
    command = UndoableEmbedSceneBackgroundImage(description, view)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableSetPinStatus(undoStack, description, item, value):
    command = UndoableSetPinStatus(description, item, value)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableItemSetText(undoStack, description, item, eskiText, text):
    command = UndoableItemSetText(description, item, eskiText, text)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableConvertToPlainText(undoStack, description, item):
    command = UndoableConvertToPlainText(description, item)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableItemCustomCommand(undoStack, description, item, command):
    command = UndoableItemCustomCommand(description, item, command)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableEmbedImage(undoStack, description, item):
    command = UndoableEmbedImage(description, item)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableEmbedVideo(undoStack, description, item):
    command = UndoableEmbedVideo(description, item)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableEmbedFile(undoStack, description, item):
    command = UndoableEmbedFile(description, item)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableMove(undoStack, description, movedItem, eskiPosition):
    command = UndoableMove(description, movedItem, eskiPosition)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableMovePathPoint(undoStack, description, item, movedPointIndex, eskiPosTuple, yeniPosTuple):
    command = UndoableMovePathPoint(description, item, movedPointIndex, eskiPosTuple, yeniPosTuple)
    undoStack.push(command)


# ---------------------------------------------------------------------
def undoableDeletePathPoint(undoStack, description, item, eskiPath, yeniPath):
    command = UndoableDeletePathPoint(description, item, eskiPath, yeniPath)
    undoStack.push(command)
