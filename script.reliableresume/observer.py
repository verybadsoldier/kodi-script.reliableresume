import sys, email, xbmcgui, xbmc
import string, time, mimetypes, re, os
import xbmcaddon

__addonID__= "script.reliableresume"
DATADIR = xbmc.translatePath( "special://profile/addon_data/" + __addonID__ + "/" )

DATAFILE = os.path.join( DATADIR, "ResumeSaverA.xml" )
DATAFILE2 = os.path.join( DATADIR, "ResumeSaverB.xml" )

if os.access(DATADIR, os.F_OK)==0:
    os.mkdir(DATADIR)
    


class ResumeSaver:
        currentFile = 0
        
        lastExecutionTime = time.clock()
        lastConfigReadTime = 0
        
        timer_amounts = {}
        timer_amounts['0'] = 5
        timer_amounts['1'] = 30
        timer_amounts['2'] = 120
        timer_amounts['3'] = 300
        timer_amounts['4'] = 600

        videoEnable = False
        audioEnable = False
        executeInterval = 60
        autoResume = False

        def log(self,msg):
            xbmc.log("%s: %s" % (__addonID__, msg))

        def shouldExecute(self):
            now = time.clock()
            if ( ( now - self.lastExecutionTime ) >= self.executeInterval ):
                self.lastExecutionTime = now
                return True
            return False

        def shouldReadConfig(self):
            now = time.clock()
            if ( ( now - self.lastConfigReadTime ) >= 5 ):
                self.lastConfigReadTime = now
                return True
            return False
        
        def reloadConfig(self):
            Addon = xbmcaddon.Addon(__addonID__)
            self.videoEnable = ( Addon.getSetting('observe_video') == 'true' )
            self.audioEnable = ( Addon.getSetting('observe_audio') == 'true' )
            self.executeInterval = self.timer_amounts[Addon.getSetting('timer_amount')]
            self.autoResume = ( Addon.getSetting('auto_resume') == 'true' )
            
        def reloadConfigIfNeeded(self):
            if ( self.shouldReadConfig() ):
                self.reloadConfig()
        
        def loader(self):
            self.reloadConfig()
            
            if ( self.autoResume ):
                self.executeResume()
                
            while ( not xbmc.abortRequested ):
                time.sleep( 2 )

                self.reloadConfigIfNeeded()
                                        
                if ( not self.shouldExecute() ):
                    continue
                
                self.playlist = []
                if ( xbmc.Player().isPlayingAudio() ) and ( self.audioEnable ):
                        self.media = "audio"
                        self.time = xbmc.Player().getTime()
                        self.plist = xbmc.PlayList(0)
                        self.playing = xbmc.Player().getPlayingFile()
                        for i in range (0 , len(self.plist)):
                                self.playlist.append(self.plist[i].getfilename())
                        self.place = self.plist.getposition()
                        self.writedata()
                elif ( xbmc.Player().isPlayingVideo() ) and ( self.videoEnable ):
                        self.media = "video"
                        self.time = xbmc.Player().getTime()
                        self.plist = xbmc.PlayList(1)
                        self.playing = xbmc.Player().getPlayingFile()
                        for i in range (0 , len(self.plist)):
                                self.playlist.append(self.plist[i].getfilename())
                        self.place = self.plist.getposition()
                        self.writedata()

        def executeResume(self):
            results = []
            result = eval(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.ExecuteAddon", "params": {"addonid": "%s"}, "id": 1}' % __addonID__))

        def checkObserveFolder(self):
            Addon = xbmcaddon.Addon(__addonID__)

            if ( not ( Addon.getSetting('observe_limit') == 'true' )):
                return True
                        
            obsFolders = []
            obsFolders.append(Addon.getSetting('observe_folder1'))
            obsFolders.append(Addon.getSetting('observe_folder2'))
            obsFolders.append(Addon.getSetting('observe_folder3'))
            for pl in self.playlist:
                for j in obsFolders:
                    if ((len(j) >0) and (j in pl)):
                        return True
            return False
        
        def writedata(self):
            if (not self.checkObserveFolder()):
                return
                
            if ( self.currentFile == 0 ):
                self.writedataex(DATAFILE)
                self.currentFile = 1
            else:
                self.writedataex(DATAFILE2)
                self.currentFile = 0

        def writedataex(self, datafile):
            f = open(datafile, "wb")
            f.write("<data>\n")
            f.write("\t<media>"+self.media+"</media>\n")
            f.write("\t<time>"+str(self.time)+"</time>\n")
            f.write("\t<plspos>"+str(self.place)+"</plspos>\n")
            f.write("\t<plsize>"+str(len(self.playlist))+"</plsize>\n")
            for i in range (0 , len(self.playlist)): 
                f.write("\t<plistfile"+str(i)+">"+str(self.playlist[i])+"</plistfile"+str(i)+">\n")
            f.write("\t<playing>"+str(self.playing)+"</playing>\n")
            f.write("</data>\n")
            f.close()
                
m = ResumeSaver()
m.loader()
del m