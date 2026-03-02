import six
import sys
from kodi_six import xbmc, xbmcaddon, xbmcvfs, xbmcgui, xbmcplugin

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
_addon = xbmcaddon.Addon()
_addonname = _addon.getAddonInfo('name')
_addonname = _addonname if six.PY3 else _addonname.encode('utf8')
_version = _addon.getAddonInfo('version')
_addonID = _addon.getAddonInfo('id')
_icon = _addon.getAddonInfo('icon')
_fanart = _addon.getAddonInfo('fanart')
_path = _addon.getAddonInfo('path')
_ppath = _addon.getAddonInfo('profile')
_ipath = _path + '/resources/images/'
_listitem = xbmcgui.ListItem
kodiver = float(xbmc.getInfoLabel('System.BuildVersion')[0:3])
PY2 = six.PY2
LOGINFO = xbmc.LOGNOTICE if PY2 else xbmc.LOGINFO
TRANSLATEPATH = xbmc.translatePath if PY2 else xbmcvfs.translatePath
keyboard = xbmc.Keyboard
pDialog = xbmcgui.DialogProgress()
Dialog = xbmcgui.Dialog
xbmcua = xbmc.getUserAgent()
addDir = xbmcplugin.addDirectoryItems
setResolvedUrl = xbmcplugin.setResolvedUrl
setContent = xbmcplugin.setContent
eod = xbmcplugin.endOfDirectory
sleep = xbmc.sleep


mozhdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0'}
ioshdr = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0_1 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A402 Safari/604.1'}
droidhdr = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G610F Build/LMY48Z)'}
jiohdr = {'User-Agent': 'ExoPlayerDemo/5.2.0 (Linux;Android 6.0.1) ExoPlayerLib/2.3.0'}
chromehdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
safhdr = 'Mozilla/5.0 ({}) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A356 Safari/604.1'


def log(text, level='debug', caption=None):
    if not caption:
        caption = '@@@@DeccanDelight log'
    if level == 'debug':
        loglevel = xbmc.LOGDEBUG
    elif level == 'info':
        loglevel = LOGINFO
    elif level == 'error':
        loglevel = xbmc.LOGERROR
    xbmc.log('{} = {}'.format(caption, text), loglevel)


def bool2string(myinput):
    ''' Neatens up usage of prepack_images flag. '''
    return 'true' if myinput else 'false'


def string_compare(s1, s2):
    """ Method that takes two strings and returns True or False, based
        on if they are equal, regardless of case.
    """
    try:
        return s1.lower() == s2.lower()
    except AttributeError:
        log("Please only pass strings into this method.", 'error')
        log("You passed a %s and %s" % (s1.__class__, s2.__class__), 'error')


def clean_string(string):
    """
        Method that takes a string and returns it cleaned of any special characters
        in order to do proper string comparisons
    """
    try:
        return ''.join(e for e in string if e.isalnum())
    except:
        return string


def notify(msg, title=_addonname, duration=3000):
    '''
    Display msg as a notification

    Args:
        msg (str): message to notify
    '''
    xbmcgui.Dialog().notification(title, msg, _icon, duration, False)


def select(msg, items):
    '''
    Display a list of items to choose from as a Dialog box

    Args:
        msg (str): Dialog box title
        items (list): list of items
    '''
    xbmcgui.Dialog().select(msg, items)


def ok(msg, title=_addonname):
    '''
    Display msg as a Dialog box

    Args:
        title (str): Dialog box title
        msg (str): message to notify
    '''
    xbmcgui.Dialog().ok(title, msg)


def makecast(cast2):
    '''
    Make cast vtag

    Args:
        cast2 (list): list of cast dictionary with name, role, thumbnail
    '''
    return [xbmc.Actor(p['name'], p['role'], cast2.index(p), p['thumbnail']) for p in cast2]


def makeFilename(name):
    '''
    Make OS Legal filename

    Args:
        name (str): filename
    '''
    return xbmc.makeLegalFilename(name) if six.PY2 else xbmcvfs.makeLegalFilename(name)


def renameFile(original_name, new_name):
    '''
    Rename file

    Args:
        original_name (str): filename
        new_name (str): filename
    '''
    xbmcvfs.rename(original_name, new_name)


def pathExists(filename):
    '''
    Check if file exists

    Args:
        name (str): filename
    '''
    return xbmcvfs.exists(filename)


def deleteFile(filename):
    '''
    Delete file

    Args:
        name (str): filename
    '''
    xbmcvfs.delete(filename)


def openFile(filename):
    '''
    Open file

    Args:
        name (str): filename
    '''
    xbmcvfs.File(filename, 'w')


def get_setting(setting_id):
    '''
    Get setting value

    Args:
        setting_id (str): setting id
    '''
    return _addon.getSetting(setting_id)
