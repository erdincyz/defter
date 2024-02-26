![GIF](https://raw.githubusercontent.com/erdincyz/gorseller/master/_defter/defter.gif)

### [TÜRKÇE](https://github.com/erdincyz/defter)

### Welcome
**Defter** (means Notebook) is an open source software that is (hopefully) still being developed as time permits and as needed.

It can bu used for;
* To quickly take notes by double-clicking anywhere on the page
* To draw shapes, diagrams
* To collect data by dragging and dropping from the Internet
* To curate some data you collected about something.
* It is visual. It supports adding-embedding images, videos, (any) files to the document, and copy-paste, drag-and-drop text (supports HTML) from the browser (or from other software).
* You can make HTML-containing text objects clickable again by using the "Show as Web Page" feature in the menu that opens when you right-click on the object.
* If you double-click on an image that you have added to the scene, a text box will appear at the point you clicked on the image. You can take as many notes as you want on the image.

* You can export the scene as a PDF or HTML file.

_This software is not an alternative to pen and paper. It is perhaps most useful for quickly gathering data from digital environments._

It is licensed under **GPLv3**.

Contains many **Bugs** and **incomplete features**. It is recommended that you do not use it for important work, (without trying it thoroughly.)

You can follow the known bugs and features that are intended to be added (although not up-to-date at the moment) from the [Issues](https://github.com/erdincyz/defter/issues) section on this page.

### INSTALLING
It works on Python3.

You can download and install Python 3 from [https://www.python.org/downloads/](https://www.python.org/downloads/)

If you already have Python 3, you can install it with:
```
python3 -m pip install defter-argekod

```
After installation is finished, you can run defter with

```
defter
```

To update to the latest version;

```
python3 -m pip install -U defter-argekod

```

Also, if you wish, you can uninstall it with
```
python3 -m pip uninstall defter-argekod

```

### File Structure:
These are zip files with the extension changed to "def" and a compression ratio of 1. Zip files are used like containers. You can open them like a zip file and access other files archived in it. Additionally, each time a file is saved, an html file for each page in the document is also saved in def. You can also access your document by extracting the def file in a folder and opening the html files in it in the web browser.

### Tips:

#### To save files faster:

If 7z or zip is installed on your system and can be accessed directly from the command line, Defter can save files faster. Because the archive update feature supported by 7z or zip is not supported by the zipfile module that comes with Python. (Archive update feature: It writes only the added or changed files back to the disk. It saves all files from being written to the disk again.)

#### To take screenshots more easily:

You can take screenshots with Defter, but if there is another software for this purpose on your system, it is recommended that you use it. For example, in Linux, you can assign the following command to a system-wide shortcut and use it for taking screenshots to clipboard.

The following command takes screenshot and copies it to the clipboard.

#### For Linux:

(If Scrot and xclip software are not installed on your system, you must first install them with your package manager.)
```
scrot -s -q 100 '/tmp/foo.jpg' -e 'xclip -selection clipboard -t image/jpg -i $f'
```
#### For Windows:
You can use this shortcut.
```
Win + Shift + S
```
#### For OS X:
You can use this shortcut.
```
Command + Shift + 4
```

Defter supports pasting images from the clipboard. You can copy the screenshot to the clipboard and paste it into the Defter using the methods above or any other method you prefer.

### Thanks.
