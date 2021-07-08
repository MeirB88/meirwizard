################################################################################
#      Copyright (C) 2019 drinfernoo                                           #
#                                                                              #
#  This Program is free software; you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation; either version 2, or (at your option)         #
#  any later version.                                                          #
#                                                                              #
#  This Program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with XBMC; see the file COPYING.  If not, write to                    #
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.       #
#  http://www.gnu.org/copyleft/gpl.html                                        #
################################################################################

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

import glob
import os
import re

try:  # Python 3
    from urllib.parse import quote_plus
    from urllib.request import urlretrieve
except ImportError:  # Python 2
    from urllib import quote_plus
    from urllib import urlretrieve

from resources.libs.common import directory
from resources.libs.common.config import CONFIG


###########################
#      Menu Items         #
###########################

def check_for_fm():
    if not xbmc.getCondVisibility('System.HasAddon(script.kodi.android.update)'):
        from resources.libs.gui import addon_menu
        addon_menu.install_from_kodi('script.kodi.android.update')
    
    try:
        updater = xbmcaddon.Addon('script.kodi.android.update')
    except RuntimeError as e:
        return False
        
    fm = int(updater.getSetting('File_Manager'))
    apps = xbmcvfs.listdir('androidapp://sources/apps/')[1]
    
    if fm == 0 and 'com.android.documentsui' not in apps:
        dialog = xbmcgui.Dialog()
        choose = dialog.yesno(CONFIG.ADDONTITLE, 'למכשיר שלך אין מנהל קבצים כברירת מחדל. תרצה לבחור אחד עכשיו?')
        if not choose:
            dialog.ok(CONFIG.ADDONTITLE, 'אם האפליקציה יורדת אך לא ניתנת להתקנה, שנה את מנהל הקבצים שלך ב: {}\'s "Install Settings".'.format(CONFIG.ADDONTITLE))
        else:
            from resources.libs import install
            install.choose_file_manager()
            
    return True


def apk_menu(url=None):
    from resources.libs.common import logging
    from resources.libs.common import tools

    if check_for_fm():
        directory.add_dir('קבצי APK רשמיים של קודי', {'mode': 'kodiapk'}, icon=CONFIG.ICONAPK, themeit=CONFIG.THEME1)
        directory.add_separator()

    response = tools.open_url(CONFIG.APKFILE)
    url_response = tools.open_url(url)

    if response:
        TEMPAPKFILE = tools.clean_text(url_response.text if url else response.text)

        if TEMPAPKFILE:
            match = re.compile('name="(.+?)".+?ection="(.+?)".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?dult="(.+?)".+?escription="(.+?)"').findall(TEMPAPKFILE)
            if len(match) > 0:
                x = 0
                for aname, section, url, icon, fanart, adult, description in match:
                    if not CONFIG.SHOWADULT == 'true' and adult.lower() == 'yes':
                        continue
                    if section.lower() == 'yes':
                        x += 1
                        directory.add_dir("[B]{0}[/B]".format(aname), {'mode': 'apk', 'name': aname, 'url': url}, description=description, icon=icon, fanart=fanart, themeit=CONFIG.THEME3)
                    else:
                        x += 1
                        directory.add_file(aname, {'mode': 'apkinstall', 'name': aname, 'url': url}, description=description, icon=icon, fanart=fanart, themeit=CONFIG.THEME2)
                    if x == 0:
                        directory.add_file("לא נוספו עדיין הרחבות לתפריט זה!", themeit=CONFIG.THEME2)
            else:
                logging.log("[תפריט APK] שגיאה: פורמט שגוי.", level=xbmc.LOGERROR)
        else:
            logging.log("[תפריט APK] שגיאה: הקישור לא עובד.", level=xbmc.LOGERROR)
            directory.add_file('הקישור לקובץ הטקסט לא עובד.', themeit=CONFIG.THEME3)
            directory.add_file('{0}'.format(CONFIG.APKFILE), themeit=CONFIG.THEME3)
    else:
        logging.log("[תפריט APK] לא נוספו רשימות אפליקציות.")


def youtube_menu(url=None):
    from resources.libs.common import logging
    from resources.libs.common import tools

    response = tools.open_url(CONFIG.YOUTUBEFILE)
    url_response = tools.open_url(url)

    if response:
        TEMPYOUTUBEFILE = url_response.text if url else response.text

        if TEMPYOUTUBEFILE:
            link = TEMPYOUTUBEFILE.replace('\n', '').replace('\r', '').replace('\t', '')
            match = re.compile('name="(.+?)".+?ection="(.+?)".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?escription="(.+?)"').findall(link)
            if len(match) > 0:
                for name, section, url, icon, fanart, description in match:
                    if section.lower() == "yes":
                        directory.add_dir("[B]{0}[/B]".format(name), {'mode': 'youtube', 'name': name, 'url': url}, description=description, icon=icon, fanart=fanart, themeit=CONFIG.THEME3)
                    else:
                        directory.add_file(name, {'mode': 'viewVideo', 'url': url}, description=description, icon=icon, fanart=fanart, themeit=CONFIG.THEME2)
            else:
                logging.log("[תפריט יוטיוב] שגיאה: פורמט שגוי")
        else:
            logging.log("[תפריט יוטיוב] שגיאה: הקישור לא עובד")
            directory.add_file('הקישור לקובץ הטקסט לא עובד.', themeit=CONFIG.THEME3)
            directory.add_file('{0}'.format(CONFIG.YOUTUBEFILE), themeit=CONFIG.THEME3)
    else:
        logging.log("[תפריט יוטיוב] לא נוספו רשימות יוטיוב.")

#########################################NET TOOLS#############################################


def net_tools():
    directory.add_dir('בדיקת מהירות', {'mode': 'speedtest'}, icon=CONFIG.ICONSPEED, themeit=CONFIG.THEME1)
    if CONFIG.HIDESPACERS == 'No':
        directory.add_separator()
    directory.add_dir('הצג IP וMAC', {'mode': 'viewIP'}, icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME1)


def view_ip():
    from resources.libs import speedtest

    mac, inter_ip, ip, city, state, country, isp = speedtest.net_info()
    directory.add_file('[COLOR {0}]MAC:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, mac), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]פנימי IP: [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, inter_ip), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]חיצוני IP:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ip), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]עיר:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, city), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]מדינה:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, state), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]ארץ:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, country), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]ספק רשת:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, isp), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)


def speed_test():
    from datetime import date

    directory.add_file('הרץ בדיקת מהירות', {'mode': 'speedtest'}, icon=CONFIG.ICONSPEED, themeit=CONFIG.THEME3)
    if os.path.exists(CONFIG.SPEEDTEST):
        speedimg = glob.glob(os.path.join(CONFIG.SPEEDTEST, '*.png'))
        speedimg.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        if len(speedimg) > 0:
            directory.add_file('נקה תוצאות', {'mode': 'clearspeedtest'}, icon=CONFIG.ICONSPEED, themeit=CONFIG.THEME3)
            directory.add_separator('תוצאות קודמות', icon=CONFIG.ICONSPEED, themeit=CONFIG.THEME3)
            for item in speedimg:
                created = date.fromtimestamp(os.path.getmtime(item)).strftime('%m/%d/%Y %H:%M:%S')
                img = item.replace(os.path.join(CONFIG.SPEEDTEST, ''), '')
                directory.add_file('[B]{0}[/B]: [I]Ran {1}[/I]'.format(img, created), {'mode': 'viewspeedtest', 'name': img}, icon=CONFIG.ICONSPEED, themeit=CONFIG.THEME3)


def clear_speed_test():
    from resources.libs.common import tools

    speedimg = glob.glob(os.path.join(CONFIG.SPEEDTEST, '*.png'))
    for file in speedimg:
        tools.remove_file(file)


def view_speed_test(img=None):
    from resources.libs.gui import window

    img = os.path.join(CONFIG.SPEEDTEST, img)
    window.show_speed_test(img)


def run_speed_test():
    from resources.libs.common import logging
    from resources.libs import speedtest

    try:
        found = speedtest.speedtest()
        if not os.path.exists(CONFIG.SPEEDTEST):
            os.makedirs(CONFIG.SPEEDTEST)
        urlsplits = found[0].split('/')
        dest = os.path.join(CONFIG.SPEEDTEST, urlsplits[-1])
        urlretrieve(found[0], dest)
        view_speed_test(urlsplits[-1])
    except Exception as e:
        logging.log("[בדיקת מהירות] שגיאה בבדיקת המהירות: {0}".format(e), level=xbmc.LOGDEBUG)
        pass


def system_info():
    from resources.libs.common import logging
    from resources.libs.common import tools
    from resources.libs import speedtest

    infoLabel = ['System.FriendlyName', 'System.BuildVersion', 'System.CpuUsage', 'System.ScreenMode',
                 'Network.IPAddress', 'Network.MacAddress', 'System.Uptime', 'System.TotalUptime', 'System.FreeSpace',
                 'System.UsedSpace', 'System.TotalSpace', 'System.Memory(free)', 'System.Memory(used)',
                 'System.Memory(total)']
    data = []
    x = 0
    for info in infoLabel:
        temp = tools.get_info_label(info)
        y = 0
        while temp == "Busy" and y < 10:
            temp = tools.get_info_label(info)
            y += 1
            logging.log("{0} מצב שינה {1}".format(info, str(y)))
            xbmc.sleep(200)
        data.append(temp)
        x += 1
    storage_free = data[8] if 'Una' in data[8] else tools.convert_size(int(float(data[8][:-8])) * 1024 * 1024)
    storage_used = data[9] if 'Una' in data[9] else tools.convert_size(int(float(data[9][:-8])) * 1024 * 1024)
    storage_total = data[10] if 'Una' in data[10] else tools.convert_size(int(float(data[10][:-8])) * 1024 * 1024)
    ram_free = tools.convert_size(int(float(data[11][:-2])) * 1024 * 1024)
    ram_used = tools.convert_size(int(float(data[12][:-2])) * 1024 * 1024)
    ram_total = tools.convert_size(int(float(data[13][:-2])) * 1024 * 1024)

    picture = []
    music = []
    video = []
    programs = []
    repos = []
    scripts = []
    skins = []

    fold = glob.glob(os.path.join(CONFIG.ADDONS, '*/'))
    for folder in sorted(fold, key = lambda x: x):
        foldername = os.path.split(folder[:-1])[1]
        if foldername == 'packages': continue
        xml = os.path.join(folder, 'addon.xml')
        if os.path.exists(xml):
            prov = re.compile("<provides>(.+?)</provides>").findall(tools.read_from_file(xml))
            if len(prov) == 0:
                if foldername.startswith('skin'):
                    skins.append(foldername)
                elif foldername.startswith('repo'):
                    repos.append(foldername)
                else:
                    scripts.append(foldername)
            elif not (prov[0]).find('executable') == -1:
                programs.append(foldername)
            elif not (prov[0]).find('video') == -1:
                video.append(foldername)
            elif not (prov[0]).find('audio') == -1:
                music.append(foldername)
            elif not (prov[0]).find('image') == -1:
                picture.append(foldername)

    directory.add_file('[B]מידע[/B]', icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]שם:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[0]), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR {0}]גירסה:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[1]), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR {0}]פלטפורמה:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, tools.platform().title()), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR {0}]שימוש במעבד:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[2]), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME3)
    directory.add_file('[COLOR {0}]מצב מסך:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[3]), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME3)

    directory.add_file('[B]זמן ריצה:[/B]', icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]זמן ריצה נוכחי:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[6]), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]זמן ריצה כללי:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[7]), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)

    directory.add_file('[B]אחסון מקומי:[/B]', icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]אחסון בשימוש:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, storage_used), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]אחסון פנוי:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, storage_free), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]סה"כ:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, storage_total), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)

    directory.add_file('[B]שימוש בזיכרון:[/B]', icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]זיכרון תפוס:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ram_free), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]זיכרון פנוי:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ram_used), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]סה"כ:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ram_total), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)

    mac, inter_ip, ip, city, state, country, isp = speedtest.net_info()
    directory.add_file('[B]רשת:[/B]', icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Mac:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, mac), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]פנימי IP: [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, inter_ip), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]חיצוני IP:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ip), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]עיר:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, city), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]מדינה:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, state), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]ארץ:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, country), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]ספק:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, isp), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)

    totalcount = len(picture) + len(music) + len(video) + len(programs) + len(scripts) + len(skins) + len(repos)
    directory.add_file('[B]הרחבות([COLOR {0}]{1}[/COLOR]):[/B]'.format(CONFIG.COLOR1, totalcount), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]הרחבות וידאו:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(video))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]הרחבות תוכנה:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(programs))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]הרחבות מוזיקה:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(music))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]הרחבות תמונות:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(picture))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]מקורות:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(repos))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]מעטפות:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(skins))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]סקריפטים/מודולים:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(scripts))), icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME2)


def save_menu():
    on = '[COLOR springgreen]פעיל[/COLOR]'
    off = '[COLOR red]כבוי[/COLOR]'

    trakt = 'true' if CONFIG.KEEPTRAKT == 'true' else 'false'
    debrid = 'true' if CONFIG.KEEPDEBRID == 'true' else 'false'
    login = 'true' if CONFIG.KEEPLOGIN == 'true' else 'false'
    sources = 'true' if CONFIG.KEEPSOURCES == 'true' else 'false'
    advanced = 'true' if CONFIG.KEEPADVANCED == 'true' else 'false'
    profiles = 'true' if CONFIG.KEEPPROFILES == 'true' else 'false'
    playercore = 'true' if CONFIG.KEEPPLAYERCORE == 'true' else 'false'
    guisettings = 'true' if CONFIG.KEEPGUISETTINGS == 'true' else 'false'
    favourites = 'true' if CONFIG.KEEPFAVS == 'true' else 'false'
    repos = 'true' if CONFIG.KEEPREPOS == 'true' else 'false'
    super = 'true' if CONFIG.KEEPSUPER == 'true' else 'false'
    whitelist = 'true' if CONFIG.KEEPWHITELIST == 'true' else 'false'

    directory.add_dir('שמור מידע טראקט', {'mode': 'trakt'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME1)
    directory.add_dir('שמור דבריד', {'mode': 'realdebrid'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME1)
    directory.add_dir('שמור פרטי התחברות', {'mode': 'login'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME1)
    directory.add_file('ייבא מידע שמור', {'mode': 'managedata', 'name': 'import'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('ייצא מידע שמור', {'mode': 'managedata', 'name': 'export'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('- לחץ להפעלה/נטרול ההגדרות -', themeit=CONFIG.THEME3)
    directory.add_file('שמור טראקט: {0}'.format(trakt.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keeptrakt'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME1)
    directory.add_file('שמור דבריד: {0}'.format(debrid.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepdebrid'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME1)
    directory.add_file('שמור פרטי התחברות: {0}'.format(login.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keeplogin'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME1)
    directory.add_file('שמור \'Sources.xml\': {0}'.format(sources.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepsources'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('שמור \'Profiles.xml\': {0}'.format(profiles.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepprofiles'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('שמור \'playercorefactory.xml\': {0}'.format(playercore.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepplayercore'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('שמור \'guisettings.xml\': {0}'.format(guisettings.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepguiseettings'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('שמור \'Advancedsettings.xml\': {0}'.format(advanced.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepadvanced'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('שמור \'Favourites.xml\': {0}'.format(favourites.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepfavourites'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('שמור Super Favourites: {0}'.format(super.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepsuper'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('שמור Installed Repo\'s: {0}'.format(repos.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keeprepos'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    directory.add_file('שמור My \'WhiteList\': {0}'.format(whitelist.replace('true', on).replace('false', off)), {'mode': 'togglesetting', 'name': 'keepwhitelist'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
    if whitelist == 'true':
        directory.add_file('עריכת רשימה לבנה', {'mode': 'whitelist', 'name': 'edit'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
        directory.add_file('הצג רשימה לבנה', {'mode': 'whitelist', 'name': 'view'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
        directory.add_file('ניקוי רשימה לבנה', {'mode': 'whitelist', 'name': 'clear'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
        directory.add_file('ייבא רשימה לבנה', {'mode': 'whitelist', 'name': 'import'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)
        directory.add_file('ייצא רשימה לבנה', {'mode': 'whitelist', 'name': 'export'}, icon=CONFIG.ICONSAVE, themeit=CONFIG.THEME1)


def trakt_menu():
    from resources.libs import traktit

    keep_trakt = '[COLOR springgreen]פעיל[/COLOR]' if CONFIG.KEEPTRAKT == 'true' else '[COLOR red]מנוטרל[/COLOR]'
    last = str(CONFIG.TRAKTSAVE) if not CONFIG.TRAKTSAVE == '' else 'Trakt hasn\'t been saved yet.'
    directory.add_file('[I]הירשם בחינם ב https://www.trakt.tv/[/I]', icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    directory.add_file('שמור מידע טראקט: {0}'.format(keep_trakt), {'mode': 'togglesetting', 'name': 'keeptrakt'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    if CONFIG.KEEPTRAKT == 'true':
        directory.add_file('שמירה אחרונה: {0}'.format(str(last)), icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    directory.add_separator(icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)

    for trakt in traktit.ORDER:
        if xbmc.getCondVisibility('System.HasAddon({0})'.format(traktit.TRAKTID[trakt]['plugin'])):
            name = traktit.TRAKTID[trakt]['name']
            path = traktit.TRAKTID[trakt]['path']
            saved = traktit.TRAKTID[trakt]['saved']
            file = traktit.TRAKTID[trakt]['file']
            user = CONFIG.get_setting(saved)
            auser = traktit.trakt_user(trakt)
            icon = traktit.TRAKTID[trakt]['icon'] if os.path.exists(path) else CONFIG.ICONTRAKT
            fanart = traktit.TRAKTID[trakt]['fanart'] if os.path.exists(path) else CONFIG.ADDON_FANART
            menu = create_addon_data_menu('Trakt', trakt)
            menu2 = create_save_data_menu('Trakt', trakt)
            menu.append((CONFIG.THEME2.format('{0} Settings'.format(name)), 'RunPlugin(plugin://{0}/?mode=opensettings&name={1}&url=trakt)'.format(CONFIG.ADDON_ID, trakt)))

            directory.add_file('[+]-> {0}'.format(name), icon=icon, fanart=fanart, themeit=CONFIG.THEME3)
            if not os.path.exists(path):
                directory.add_file('[COLOR red]מידע הרחבה: לא מותקן[/COLOR]', icon=icon, fanart=fanart, menu=menu)
            elif not auser:
                directory.add_file('[COLOR red]מידע הרחבה: לא רשום[/COLOR]', {'mode': 'authtrakt', 'name': trakt}, icon=icon, fanart=fanart, menu=menu)
            else:
                directory.add_file('[COLOR springgreen]מידע הרחבה: {0}[/COLOR]'.format(auser), {'mode': 'authtrakt', 'name': trakt}, icon=icon, fanart=fanart, menu=menu)
            if user == "":
                if os.path.exists(file):
                    directory.add_file('[COLOR red]מידע שמור: קובץ נמצא(ייבא מידע)[/COLOR]', {'mode': 'importtrakt', 'name': trakt}, icon=icon, fanart=fanart, menu=menu2)
                else:
                    directory.add_file('[COLOR red]מידע שמור: לא נשמר[/COLOR]', {'mode': 'savetrakt', 'name': trakt}, icon=icon, fanart=fanart, menu=menu2)
            else:
                directory.add_file('[COLOR springgreen]מידע שמור: {0}[/COLOR]'.format(user), icon=icon, fanart=fanart, menu=menu2)

    directory.add_separator()
    directory.add_file('שמור כל מידע טראקט', {'mode': 'savetrakt', 'name': 'all'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    directory.add_file('שחזר את כל המידע השמור מטראקט', {'mode': 'restoretrakt', 'name': 'all'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    directory.add_file('ייבא מידע טראקט', {'mode': 'importtrakt', 'name': 'all'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    directory.add_file('ניקוי כל מידע של טראקט מההרחבות', {'mode': 'addontrakt', 'name': 'all'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)
    directory.add_file('ניקוי כל מידע שמור של טראקט', {'mode': 'cleartrakt', 'name': 'all'}, icon=CONFIG.ICONTRAKT, themeit=CONFIG.THEME3)


def debrid_menu():
    from resources.libs import debridit

    keep_debrid = '[COLOR springgreen]פעיל[/COLOR]' if CONFIG.KEEPDEBRID == 'true' else '[COLOR red]מנוטרל[/COLOR]'
    last = str(CONFIG.DEBRIDSAVE) if not CONFIG.DEBRIDSAVE == '' else 'Debrid authorizations haven\'t been saved yet.'
    directory.add_file('[I]https://www.real-debrid.com/ הינו שירות בתשלום.[/I]', icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_file('[I]https://www.premiumize.me/ הינו שירות בתשלום.[/I]', icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_file('שמור מידע דבריד: {0}'.format(keep_debrid), {'mode': 'togglesetting', 'name': 'keepdebrid'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    if CONFIG.KEEPDEBRID == 'true':
        directory.add_file('שמירה אחרונה: {0}'.format(str(last)), icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_separator(icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)

    for debrid in debridit.ORDER:
        if xbmc.getCondVisibility('System.HasAddon({0})'.format(debridit.DEBRIDID[debrid]['plugin'])):
            name = debridit.DEBRIDID[debrid]['name']
            path = debridit.DEBRIDID[debrid]['path']
            saved = debridit.DEBRIDID[debrid]['saved']
            file = debridit.DEBRIDID[debrid]['file']
            user = CONFIG.get_setting(saved)
            auser = debridit.debrid_user(debrid)
            icon = debridit.DEBRIDID[debrid]['icon'] if os.path.exists(path) else CONFIG.ICONDEBRID
            fanart = debridit.DEBRIDID[debrid]['fanart'] if os.path.exists(path) else CONFIG.ADDON_FANART
            menu = create_addon_data_menu('Debrid', debrid)
            menu2 = create_save_data_menu('Debrid', debrid)
            menu.append((CONFIG.THEME2.format('{0} Settings'.format(name)), 'RunPlugin(plugin://{0}/?mode=opensettings&name={1}&url=debrid)'.format(CONFIG.ADDON_ID, debrid)))

            directory.add_file('[+]-> {0}'.format(name), icon=icon, fanart=fanart, themeit=CONFIG.THEME3)
            if not os.path.exists(path):
                directory.add_file('[COLOR red]מידע הרחבה: לא מותקן[/COLOR]', icon=icon, fanart=fanart, menu=menu)
            elif not auser:
                directory.add_file('[COLOR red]מידע הרחבה: לא רשום[/COLOR]', {'mode': 'authdebrid', 'name': debrid}, icon=icon, fanart=fanart, menu=menu)
            else:
                directory.add_file('[COLOR springgreen]מידע הרחבה: {0}[/COLOR]'.format(auser), {'mode': 'authdebrid', 'name': debrid}, icon=icon, fanart=fanart, menu=menu)
            if user == "":
                if os.path.exists(file):
                    directory.add_file('[COLOR red]מידע שמור: קובץ נמצא(ייבא מידע)[/COLOR]', {'mode': 'importdebrid', 'name': debrid}, icon=icon, fanart=fanart, menu=menu2)
                else:
                    directory.add_file('[COLOR red]מידע שמור: לא נשמר[/COLOR]', {'mode': 'savedebrid', 'name': debrid}, icon=icon, fanart=fanart, menu=menu2)
            else:
                directory.add_file('[COLOR springgreen]מידע שמור: {0}[/COLOR]'.format(user), icon=icon, fanart=fanart, menu=menu2)

    directory.add_separator(themeit=CONFIG.THEME3)
    directory.add_file('שמור את כל מידע הדבריד', {'mode': 'savedebrid', 'name': 'all'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_file('שחזר מידע דבריד', {'mode': 'restoredebrid', 'name': 'all'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_file('ייבא מידע דבריד', {'mode': 'importdebrid', 'name': 'all'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_file('נקה מידע דבריד מההרחבות', {'mode': 'addondebrid', 'name': 'all'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)
    directory.add_file('נקה את כל מידע הדבריד השמור', {'mode': 'cleardebrid', 'name': 'all'}, icon=CONFIG.ICONDEBRID, themeit=CONFIG.THEME3)


def login_menu():
    from resources.libs import loginit

    keep_login = '[COLOR springgreen]פעיל[/COLOR]' if CONFIG.KEEPLOGIN == 'true' else '[COLOR red]מנוטרל[/COLOR]'
    last = str(CONFIG.LOGINSAVE) if not CONFIG.LOGINSAVE == '' else 'פרטי ההתחברות עדיין לא נשמרו'
    directory.add_file('[I]חלק מההרחבות בתשלום.[/I]', icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    directory.add_file('שמירת מפתח  API: {0}'.format(keep_login), {'mode': 'togglesetting', 'name': 'keeplogin'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    if CONFIG.KEEPLOGIN == 'true':
        directory.add_file('שמירה אחרונה: {0}'.format(str(last)), icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    directory.add_separator(icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)

    for login in loginit.ORDER:
        if xbmc.getCondVisibility('System.HasAddon({0})'.format(loginit.LOGINID[login]['plugin'])):
            name = loginit.LOGINID[login]['name']
            path = loginit.LOGINID[login]['path']
            saved = loginit.LOGINID[login]['saved']
            file = loginit.LOGINID[login]['file']
            user = CONFIG.get_setting(saved)
            auser = loginit.login_user(login)
            icon = loginit.LOGINID[login]['icon'] if os.path.exists(path) else CONFIG.ICONLOGIN
            fanart = loginit.LOGINID[login]['fanart'] if os.path.exists(path) else CONFIG.ADDON_FANART
            menu = create_addon_data_menu('Login', login)
            menu2 = create_save_data_menu('Login', login)
            menu.append((CONFIG.THEME2.format('{0} Settings'.format(name)), 'RunPlugin(plugin://{0}/?mode=opensettings&name={1}&url=login)'.format(CONFIG.ADDON_ID, login)))

            directory.add_file('[+]-> {0}'.format(name), icon=icon, fanart=fanart, themeit=CONFIG.THEME3)
            if not os.path.exists(path):
                directory.add_file('[COLOR red]מידע הרחבה: לא מותקן[/COLOR]', icon=icon, fanart=fanart, menu=menu)
            elif not auser:
                directory.add_file('[COLOR red]מידע הרחבה: לא רשום[/COLOR]', {'mode': 'authlogin', 'name': login}, icon=icon, fanart=fanart, menu=menu)
            else:
                directory.add_file('[COLOR springgreen]מידע הרחבה: {0}[/COLOR]'.format(auser), {'mode': 'authlogin', 'name': login}, icon=icon, fanart=fanart, menu=menu)
            if user == "":
                if os.path.exists(file):
                    directory.add_file('[COLOR red]מידע שמור: קובץ נמצא(ייבא מידע)[/COLOR]', {'mode': 'importlogin', 'name': login}, icon=icon, fanart=fanart, menu=menu2)
                else:
                    directory.add_file('[COLOR red]מידע שמור: לא נשמר[/COLOR]', {'mode': 'savelogin', 'name': login}, icon=icon, fanart=fanart, menu=menu2)
            else:
                directory.add_file('[COLOR springgreen]מידע שמור: {0}[/COLOR]'.format(user), icon=icon, fanart=fanart, menu=menu2)

    directory.add_separator(themeit=CONFIG.THEME3)
    directory.add_file('שמור את כל פרטי ההתחברות', {'mode': 'savelogin', 'name': 'all'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    directory.add_file('שחזר את כל פרטי ההתחברות השמורים', {'mode': 'restorelogin', 'name': 'all'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    directory.add_file('ייבא פרטי התחברות', {'mode': 'importlogin', 'name': 'all'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    directory.add_file('ניקוי פרטי ההתחברות של ההרחבות', {'mode': 'addonlogin', 'name': 'all'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)
    directory.add_file('ניקוי כל פרטי ההתחברות', {'mode': 'clearlogin', 'name': 'all'}, icon=CONFIG.ICONLOGIN, themeit=CONFIG.THEME3)


def enable_addons(all=False):
    from resources.libs.common import tools
    
    from xml.etree import ElementTree

    fold = glob.glob(os.path.join(CONFIG.ADDONS, '*/'))
    addonnames = []
    addonids = []
    for folder in sorted(fold, key=lambda x: x):
        foldername = os.path.split(folder[:-1])[1]
        if foldername in CONFIG.EXCLUDES:
            continue
        elif foldername in CONFIG.DEFAULTPLUGINS:
            continue
        elif foldername == 'packages':
            continue
        xml = os.path.join(folder, 'addon.xml')
        if os.path.exists(xml):
            root = ElementTree.parse(xml).getroot()
            addonid = root.get('id')
            addonname = root.get('name')
            addonids.append(addonid)
            addonnames.append(addonname)
    if not all:
        if len(addonids) == 0:
            directory.add_file("לא נמצאו הרחבות להפעיל או לנטרל", icon=CONFIG.ICONMAINT)
        else:
            directory.add_file("[I][B][COLOR red]שים לב! נטרול הרחבות מסוימות עלול ליצור בעיות[/COLOR][/B][/I]", icon=CONFIG.ICONMAINT)
            directory.add_dir('הפעל את כל ההרחבות', {'mode': 'enableall'}, icon=CONFIG.ICONMAINT, themeit=CONFIG.THEME3)
            for i in range(0, len(addonids)):
                folder = os.path.join(CONFIG.ADDONS, addonids[i])
                icon = os.path.join(folder, 'icon.png') if os.path.exists(os.path.join(folder, 'icon.png')) else CONFIG.ADDON_ICON
                fanart = os.path.join(folder, 'fanart.jpg') if os.path.exists(os.path.join(folder, 'fanart.jpg')) else CONFIG.ADDON_FANART
                if tools.get_addon_info(addonids[i], 'name'):
                    state = "[COLOR springgreen][מופעל][/COLOR]"
                    goto = "false"
                else:
                    state = "[COLOR red][מנוטרל][/COLOR]"
                    goto = "true"

                directory.add_file("{0} {1}".format(state, addonnames[i]), {'mode': 'toggleaddon', 'name': addonids[i], 'url': goto}, icon=icon, fanart=fanart)
    else:
        from resources.libs import db
        for addonid in addonids:
            db.toggle_addon(addonid, 'true')
        xbmc.executebuiltin('Container.Refresh()')


def remove_addon_data_menu():
    if os.path.exists(CONFIG.ADDON_DATA):
        directory.add_file('[COLOR red][B][הסר][/B][/COLOR] את כל מידע ההרחבות', {'mode': 'removedata', 'name': 'all'}, themeit=CONFIG.THEME2)
        directory.add_file('[COLOR red][B][הסר][/B][/COLOR] את כל מידע ההרחבות שהוסרו', {'mode': 'removedata', 'name': 'uninstalled'}, themeit=CONFIG.THEME2)
        directory.add_file('[COLOR red][B][הסר][/B][/COLOR] תיקיות ריקות בתיקיית מידע ההרחבות', {'mode': 'removedata', 'name': 'empty'}, themeit=CONFIG.THEME2)
        directory.add_file('[COLOR red][B][הסר][/B][/COLOR] {0} את כל מידע ההרחבות'.format(CONFIG.ADDONTITLE), {'mode': 'resetaddon'}, themeit=CONFIG.THEME2)
        directory.add_separator(themeit=CONFIG.THEME3)
        fold = glob.glob(os.path.join(CONFIG.ADDON_DATA, '*/'))
        for folder in sorted(fold, key = lambda x: x):
            foldername = folder.replace(CONFIG.ADDON_DATA, '').replace('\\', '').replace('/', '')
            icon = os.path.join(folder.replace(CONFIG.ADDON_DATA, CONFIG.ADDONS), 'icon.png')
            fanart = os.path.join(folder.replace(CONFIG.ADDON_DATA, CONFIG.ADDONS), 'fanart.png')
            folderdisplay = foldername
            replace = {'audio.': '[COLOR orange][AUDIO] [/COLOR]', 'metadata.': '[COLOR cyan][METADATA] [/COLOR]',
                       'module.': '[COLOR orange][MODULE] [/COLOR]', 'plugin.': '[COLOR blue][PLUGIN] [/COLOR]',
                       'program.': '[COLOR orange][PROGRAM] [/COLOR]', 'repository.': '[COLOR gold][REPO] [/COLOR]',
                       'script.': '[COLOR springgreen][SCRIPT] [/COLOR]',
                       'service.': '[COLOR springgreen][SERVICE] [/COLOR]', 'skin.': '[COLOR dodgerblue][SKIN] [/COLOR]',
                       'video.': '[COLOR orange][VIDEO] [/COLOR]', 'weather.': '[COLOR yellow][WEATHER] [/COLOR]'}
            for rep in replace:
                folderdisplay = folderdisplay.replace(rep, replace[rep])
            if foldername in CONFIG.EXCLUDES:
                folderdisplay = '[COLOR springgreen][B][מוגן][/B][/COLOR] {0}'.format(folderdisplay)
            else:
                folderdisplay = '[COLOR red][B][הסר][/B][/COLOR] {0}'.format(folderdisplay)
            directory.add_file(' {0}'.format(folderdisplay), {'mode': 'removedata', 'name': foldername}, icon=icon, fanart=fanart, themeit=CONFIG.THEME2)
    else:
        directory.add_file('לא נמצאה תיקיית מידע הרחבות.', themeit=CONFIG.THEME3)


def change_freq():
    from resources.libs.common import logging

    dialog = xbmcgui.Dialog()

    change = dialog.select("[COLOR {0}]באיזה תדירות תרצה ניקיון אוטומטי של קבצים עם הפעלת הקודי?[/COLOR]".format(CONFIG.COLOR2), CONFIG.CLEANFREQ)
    if not change == -1:
        CONFIG.set_setting('autocleanfreq', str(change))
        logging.log_notify('[COLOR {0}]ניקיון אוטומטי[/COLOR]'.format(CONFIG.COLOR1),
                           '[COLOR {0}]תדירות נוכחית {1}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.CLEANFREQ[change]))


def developer():
    directory.add_file('צור ברקוד', {'mode': 'createqr'}, themeit=CONFIG.THEME1)
    directory.add_file('בדיקת התראות', {'mode': 'testnotify'}, themeit=CONFIG.THEME1)
    directory.add_file('בדיקת עדכונים', {'mode': 'testupdate'}, themeit=CONFIG.THEME1)
    directory.add_file('בדיקת הנחיות בילד', {'mode': 'testbuildprompt'}, themeit=CONFIG.THEME1)
    directory.add_file('בדיקת הגדרות שמירת נתונים', {'mode': 'testsavedata'}, themeit=CONFIG.THEME1)
    directory.add_file('בדיקת איתור בינארי', {'mode': 'binarycheck'}, themeit=CONFIG.THEME1)


###########################
#      Misc Functions     #
###########################


def create_addon_data_menu(add='', name=''):
    menu_items = []

    add2 = quote_plus(add.lower().replace(' ', ''))
    add3 = add.replace('Debrid', 'Real Debrid')
    name2 = quote_plus(name.lower().replace(' ', ''))
    name = name.replace('url', 'URL Resolver')
    menu_items.append((CONFIG.THEME2.format(name.title()), ' '))
    menu_items.append((CONFIG.THEME3.format('שמור {0} מידע'.format(add3)), 'RunPlugin(plugin://{0}/?mode=save{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))
    menu_items.append((CONFIG.THEME3.format('שחזר {0} מידע'.format(add3)), 'RunPlugin(plugin://{0}/?mode=restore{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))
    menu_items.append((CONFIG.THEME3.format('נקה {0} מידע'.format(add3)), 'RunPlugin(plugin://{0}/?mode=clear{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))

    menu_items.append((CONFIG.THEME2.format('{0} Settings'.format(CONFIG.ADDONTITLE)), 'RunPlugin(plugin://{0}/?mode=settings)'.format(CONFIG.ADDON_ID)))

    return menu_items


def create_save_data_menu(add='', name=''):
    menu_items = []

    add2 = quote_plus(add.lower().replace(' ', ''))
    add3 = add.replace('Debrid', 'Real Debrid')
    name2 = quote_plus(name.lower().replace(' ', ''))
    name = name.replace('url', 'URL Resolver')
    menu_items.append((CONFIG.THEME2.format(name.title()), ' '))
    menu_items.append((CONFIG.THEME3.format('הירשם {0}'.format(add3)), 'RunPlugin(plugin://{0}/?mode=auth{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))
    menu_items.append((CONFIG.THEME3.format('שמור {0} מידע'.format(add3)), 'RunPlugin(plugin://{0}/?mode=save{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))
    menu_items.append((CONFIG.THEME3.format('שחזר {0} מידע'.format(add3)), 'RunPlugin(plugin://{0}/?mode=restore{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))
    menu_items.append((CONFIG.THEME3.format('ייבא {0} מידע'.format(add3)), 'RunPlugin(plugin://{0}/?mode=import{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))
    menu_items.append((CONFIG.THEME3.format('נקה מידע {0} הרחבה'.format(add3)), 'RunPlugin(plugin://{0}/?mode=addon{1}&name={2})'.format(CONFIG.ADDON_ID, add2, name2)))

    menu_items.append((CONFIG.THEME2.format('{0} Settings'.format(CONFIG.ADDONTITLE)), 'RunPlugin(plugin://{0}/?mode=settings)'.format(CONFIG.ADDON_ID)))

    return menu_items
