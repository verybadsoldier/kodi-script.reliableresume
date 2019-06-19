import os
import time

import xbmcaddon
import xbmc


__addonID__ = "script.reliableresume"
DATADIR = xbmc.translatePath("special://profile/addon_data/" + __addonID__ + "/")

DATAFILE = os.path.join(DATADIR, "ResumeSaverA.xml")
DATAFILE2 = os.path.join(DATADIR, "ResumeSaverB.xml")

if os.access(DATADIR, os.F_OK) == 0:
    os.mkdir(DATADIR)


class ResumeSaver:
    lastExecutionTime = time.clock()
    lastConfigReadTime = 0

    timer_amounts = {}
    timer_amounts['0'] = 5
    timer_amounts['1'] = 30
    timer_amounts['2'] = 120
    timer_amounts['3'] = 300
    timer_amounts['4'] = 600

    def __init__(self):
        self._currentFile = 0
        self._videoEnable = False
        self._audioEnable = False
        self._executeInterval = 60
        self._autoResume = False

    def _log(self, msg):
        xbmc.log("%s: %s" % (__addonID__, msg), level=xbmc.LOGNOTICE)

    def _should_execute(self):
        now = time.clock()
        if (now - self.lastExecutionTime) >= self._executeInterval:
            self.lastExecutionTime = now
            return True
        return False

    def _should_read_config(self):
        now = time.clock()
        if (now - self.lastConfigReadTime) >= 5:
            self.lastConfigReadTime = now
            return True
        return False

    def _reload_config(self):
        Addon = xbmcaddon.Addon(__addonID__)
        self._videoEnable = (Addon.getSetting('observe_video') == 'true')
        self._audioEnable = (Addon.getSetting('observe_audio') == 'true')
        self._executeInterval = self.timer_amounts[Addon.getSetting('timer_amount')]
        self._autoResume = (Addon.getSetting('auto_resume') == 'true')

    def _reload_config_if_needed(self):
        if self._should_read_config():
            self._reload_config()

    def loader(self):
        self._reload_config()

        if self._autoResume:
            self._execute_resume()

        while not xbmc.abortRequested:
            time.sleep(2)

            self._reload_config_if_needed()

            if not self._should_execute():
                continue

            if xbmc.Player().isPlayingAudio() and self._audioEnable:
                plist = xbmc.PlayList(0)
                media = "audio"
            elif xbmc.Player().isPlayingVideo() and self._videoEnable:
                plist = xbmc.PlayList(1)
                media = "video"
            else:
                continue  # not playing, do not write new state file and keep current as is

            # we are playing, but where?
            if not self._check_observe_folder(plist):
                return

            play_pos = xbmc.Player().getTime()
            if play_pos >= 10.0:  # do not save at the beginning to avoid resaving when starting to play but not having seeked yet
                self._write_playstate(media, plist, play_pos)
            else:
                self._log("Playing time is only %s. Write state skipped.")

    def _execute_resume(self):
        try:
            xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.ExecuteAddon", "params": {"addonid": "%s"}, "id": 1}' % __addonID__)
        except Exception as ex:
            self._log("Exception on resume: " + str(ex))

    @staticmethod
    def _check_observe_folder(playlist):
        """Check if we are currently playing in observing folders."""
        addon = xbmcaddon.Addon(__addonID__)

        if not (addon.getSetting('observe_limit') == 'true'):
            return True

        obsFolders = []
        obsFolders.append(addon.getSetting('observe_folder1'))
        obsFolders.append(addon.getSetting('observe_folder2'))
        obsFolders.append(addon.getSetting('observe_folder3'))
        for i in range(0, playlist.size()):
            pl_filename = playlist[i].getfilename()
            for j in obsFolders:
                if (len(j) > 0) and (j in pl_filename):
                    return True
        return False

    def _write_playstate(self, media_type, playlist, play_pos):
        if self._currentFile == 0:
            self._write_data_ex(DATAFILE, media_type, playlist, play_pos)
            self._currentFile = 1
        else:
            self._write_data_ex(DATAFILE2, media_type, playlist, play_pos)
            self._currentFile = 0

    @staticmethod
    def _write_data_ex(filename, media_type, playlist, play_pos):
        with open(filename, "w") as f:
            f.write("<data>\n")
            f.write("\t<media>" + media_type + "</media>\n")
            f.write("\t<time>" + str(play_pos) + "</time>\n")
            f.write("\t<pl_pos>" + str(playlist.getposition()) + "</pl_pos>\n")
            for i in range(0, playlist.size()):
                f.write("\t<plistfile>" + str(playlist[i].getfilename()) + "</plistfile>\n")
            f.write("</data>\n")
            f.close()


m = ResumeSaver()
m.loader()
