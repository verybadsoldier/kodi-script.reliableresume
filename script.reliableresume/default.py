import time
import os

import xbmc
import xbmcaddon
import xbmcgui


__addonID__= "script.reliableresume"
DATADIR = xbmc.translatePath( "special://profile/addon_data/" + __addonID__ + "/" )

AUTOEXEC_DIR = xbmc.translatePath( "special://profile" )
DATAFILE = os.path.join( DATADIR, "ResumeSaverA.xml" )
DATAFILE2 = os.path.join( DATADIR, "ResumeSaverB.xml" )

Addon = xbmcaddon.Addon()


class ResumePlayer:
    rewind_before_play = {}
    rewind_before_play['0'] = 0.0
    rewind_before_play['1'] = 5.0
    rewind_before_play['2'] = 15.0
    rewind_before_play['3'] = 60.0
    rewind_before_play['4'] = 180.0
    rewind_before_play['5'] = 300.0

    rewind_s = rewind_before_play[Addon.getSetting('rewind_before_play')]

    def __init__(self):
        pass

    def log(self, msg):
        xbmc.log("%s: %s" % (__addonID__, msg), level=xbmc.LOGINFO)

    def main(self):
        if not os.path.exists(DATAFILE):
            self.log('No datafile found at: ' + DATAFILE)
            return  # no datafile

        media, items, plspos, play_pos = self._opendata()

        if len(items) == 0:
            return # nothing to play

        if media == "audio":
                self.log('Creating audio playlist')
                playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        elif media == "video":
                self.log('Creating video playlist')
                playlist = xbmc.PlayList(1)
        else:
                self.log('Creating audio playlist (fallback)')
                playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)

        playlist.clear()
        for i, path in enumerate(items):
            listitem = xbmcgui.ListItem()
            # it is IMPORTANT to create a ListItem and set this info otherwise the InfoLabels won't return information correctly in the observer!!
            listitem.setInfo(type="Music",infoLabels={})
            self.log(f'Adding to playlist: {path}')
            playlist.add(path, listitem)

        xbmc.Player().play(playlist)

        while True:
            self.log('Querying playing...')
            if xbmc.Player().isPlaying():
                cur_pos = xbmc.Player().getTime()
                self.log(f'Waiting for play time > 1.0... Current play Time: {cur_pos}')
                if cur_pos > 1.0:
                    break
            else:
                self.log('Not playing yet...')
            
            time.sleep(1.0)
                
        self._seek_time(play_pos)

    def _seek_time(self, seekTo):
            wait_time = 1
            self.log(f'Sleeping before seek: {wait_time} seconds')
            time.sleep(wait_time) #wait 'a bit'. if doing seek directly it does not work when we just started playing
            self.log(f'Seeking to: {seekTo}')
            xbmc.Player().seekTime(seekTo)

    def _opendata(self):
        firstFile = DATAFILE
        secondFile = DATAFILE2

        if ( os.access(firstFile, os.F_OK) and os.access(secondFile, os.F_OK) ):
            self.log('Both files existing. checking which is newer')
            if ( os.path.getctime( secondFile ) > os.path.getctime( firstFile ) ):
                firstFile = DATAFILE2
                secondFile = DATAFILE

        try:
            return self._read_datafile(firstFile)
        except:
            return self._read_datafile(secondFile)

    def _read_datafile(self, datafile):
        play_pos = None
        media = None
        pl_pos = None
        items = []
        
        self.log(f'Reading datafile from: {datafile}')

        with open(datafile, 'r', encoding='utf-8') as fh:
            for line in fh.readlines():
                line = line.strip()
                if "<pl_pos>" in line:
                    pl_pos = int(line[8:-9])
                elif "<time>" in line:
                    play_pos = float(line[6:-7])
                elif "<media>" in line:
                    media = line[7:-8]
                elif "<plistfile>" in line:
                    items.append(line[11:-12])
        self.log(f'Read datafile. PlPos:{pl_pos} Items:{len(items)} media:{media} PlayPos:{play_pos}')
        return media, items, pl_pos, play_pos
                

m = ResumePlayer()
m.main()
