import time
import os

import xbmcgui
import xbmc
import xbmcaddon


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
        xbmc.log("%s: %s" % (__addonID__, msg), level=xbmc.LOGNOTICE)

    def main(self):
        if not os.path.exists(DATAFILE):
            self.log('No datafile found at: ' + DATAFILE)
            return  # no datafile

        media, items, plspos, play_pos = self._opendata()

        if items is None:
            return # nothing to play

        if media == "audio":
                self.log('Creating audio playlist')
                playlist = xbmc.PlayList(0)
        elif media == "video":
                self.log('Creating video playlist')
                playlist = xbmc.PlayList(1)
        else:
                self.log('Creating audio playlist (fallback)')
                playlist = xbmc.PlayList(0)

        for i in items:
            self.log('Adding to playlist: ' + i)
            playlist.add(i)

        xbmc.Player().play(playlist, startpos=plspos)

        while True:
            self.log('Querying playing...')
            cur_pos = xbmc.Player().getTime()
            self.log('Waiting for playing... Play Time: %s' % cur_pos)
            if cur_pos > 1.0:
                self.log('### breaking')
                break
            self.log('### sleeping')
            time.sleep(1.0)
                

        self._seek_time(play_pos)

    def _seek_time(self, seekTo):
            wait_time = 1
            self.log('Sleeping before seek: %s seconds' % wait_time)
            time.sleep(wait_time) #wait 'a bit'. if doing seek directly it does not work when we just started playing
            self.log('Seeking to: %s' % seekTo)
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
        
        self.log('Reading datafile from: ' + datafile)

        with open(datafile) as fh:
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
        self.log('Read datafile. PlPos:%s Items:%s media:%s PlayPos:%s' % (pl_pos, len(items), media, play_pos))
        return media, items, pl_pos, play_pos
                

m = ResumePlayer()
m.main()
