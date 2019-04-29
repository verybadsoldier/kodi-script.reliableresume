import sys, email, xbmcgui, xbmc
import string, time, mimetypes, re, os
import shutil
import xbmcaddon

__addonID__= "script.reliableresume"
DATADIR = xbmc.translatePath( "special://profile/addon_data/" + __addonID__ + "/" )

AUTOEXEC_DIR = xbmc.translatePath( "special://profile" )
DATAFILE = os.path.join( DATADIR, "ResumeSaverA.xml" )
DATAFILE2 = os.path.join( DATADIR, "ResumeSaverB.xml" )

Addon = xbmcaddon.Addon()

class resumePlayer:
        rewind_before_play = {}
        rewind_before_play['0'] = 0.0
        rewind_before_play['1'] = 5.0
        rewind_before_play['2'] = 15.0
        rewind_before_play['3'] = 60.0
        rewind_before_play['4'] = 180.0
        rewind_before_play['5'] = 300.0
        
        rewind_s = rewind_before_play[Addon.getSetting('rewind_before_play')]
  
        def log(self,msg):
            xbmc.log("%s: %s" % (__addonID__, msg))
    
        def main(self):
                if os.path.exists(DATAFILE):
                        self.opendata()
                else:
                        return "no datafile"

                if self.plsize == False: #there is no playlist
                        xbmc.Player().play(self.playing)
                        self.seekTime(self.time)
                        
                if self.media == "audio":
                        self.plist = xbmc.PlayList(0)
                elif self.media == "video":
                        self.plist = xbmc.PlayList(1)
                else:
                       self.plist = xbmc.PlayList(0)
                       
                self.plist.clear()
                
                count = 0
                for count in range (0, self.plsize):
                    self.plist.add(self.playlist[count])
                    count = count + 1
                    
                xbmc.Player().play(self.plist)
                xbmc.Player().playselected(self.place)
                self.seekTime(self.time)
        
        def seekTime(self, seekTo):
                time.sleep(1) #wait 'a bit'. if doing seek directly it does not work when we just started playing
                xbmc.Player().seekTime(seekTo)

        def opendata(self):
                firstFile = DATAFILE
                secondFile = DATAFILE2
                
                if ( os.access(firstFile, os.F_OK) and os.access(secondFile, os.F_OK) ):
                    self.log('Both files exisitng. checking which is newer')
                    if ( os.path.getctime( secondFile ) > os.path.getctime( firstFile ) ):
                        firstFile = DATAFILE2
                        secondFile = DATAFILE
                        self.log('swapping files')
                        
                try:
                        self.opendataex(firstFile)
                except:
                        self.opendataex(secondFile)
        def opendataex(self,datafile):
                self.playlist = []
                tag = ["<window>", "<volume>", "<time>", "<plspos>", "<plsize>","<playing>","<media>"]
                fh = open(datafile)
                count = 0
                for line in fh.readlines():
                        theLine = line.strip()
                        if theLine.count(tag[0]) > 0:
                              self.window = theLine[8:-9]
                        if theLine.count(tag[1]) > 0:
                              self.volume = theLine[8:-9]
                        if theLine.count(tag[2]) > 0:
                              self.time = theLine[6:-7]
                              if self.time == "-":
                                      self.time = False
                              else:
                                      self.time = float(self.time)
                              self.time = max( 0.0, self.time - self.rewind_s )
                        if theLine.count(tag[3]) > 0:
                              self.place = theLine[8:-9]
                              if self.place == "-":
                                      self.place = False
                              else:
                                      self.place = int(self.place)
                        if theLine.count(tag[4]) > 0:
                              self.plsize = theLine[8:-9]
                              if self.plsize == "-":
                                      self.plsize = False
                              else:  
                                      self.plsize = int(self.plsize)
                        if theLine.count(tag[5]) > 0:
                              self.playing = theLine[9:-10]
                              if self.playing == "-":
                                      self.playing = False
                        if theLine.count(tag[6]) > 0:
                              self.media = theLine[7:-8]
                              if self.media == "-":
                                      self.media = False
                fh.close()
                fh = open(DATAFILE)
                if self.plsize != 0:
                        for line in fh.readlines():
                                theLine = line.strip()
                                for count in range(0, self.plsize):
                                        temp = "<plistfile"+str(count)+">"
                                        if theLine.startswith(temp):
                                                temp = theLine[len(temp):-1*len(temp)-1]
                                                self.playlist.append(temp)
                                                count = count + 1
                else:pass
                fh.close()
                return
        def checkme(self):
                self.plist = xbmc.PlayList(0)
                self.plsize = self.plist.size()
                if self.plsize !=0:
                        self.media = "audio"
                        for i in range (0 , self.plsize):
                                temp = self.plist[i]
                                self.playlist.append(xbmc.PlayListItem.getfilename(temp))
                        return
                else:pass
                self.plist = xbmc.PlayList(1)
                self.plsize = self.plist.size()                
                if self.plsize !=0:
                        self.media = "video"
                        for i in range (0 , self.plsize):
                                temp = self.plist[i]
                                self.playlist.append(xbmc.PlayListItem.getfilename(temp))
                        return
                else:
                        self.media = "-"
                        self.plsize = "-"
                        self.playlist = "-"
                        return
m = resumePlayer()
m.main()
del m
