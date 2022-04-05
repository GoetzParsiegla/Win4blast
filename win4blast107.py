#!/usr/bin/python
# -*- coding: utf-8 -*-
# A simple GUI for Windows to run blast on local Databases
# It has been written in Python 3.6 but works also with Python 2.7
# Besides a local installation of blast, you also need to install  
# wxPython (v.4.0.4) from: https://pypi.org/project/wxPython/
#
# ----------------------------------------------------------------------
# This blast GUI is Copyright (C) 2018 by Goetz Parsiegla
#
#                        All Rights Reserved
#
# Permission to use, copy, modify, distribute, and distribute modified
# versions of this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright
# notice appear in all copies and that both the copyright notice and
# this permission notice appear in supporting documentation, and that
# the name of Daniel Seeliger not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# GOETZ PRSIEGLA DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS.  IN NO EVENT SHALL GOETZ PARSIEGLA BE LIABLE FOR ANY
# SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ----------------------------------------------------------------------

# This is Version 1.07

import wx
import os
import subprocess
from glob import glob

class Win4blastFrame(wx.Frame):
    def __init__(self, parent, ID, title):
        only_closeable = wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, parent, -1, title, pos=(-1, -1), size=(800, 550), style= only_closeable)
        self.statusbar = self.CreateStatusBar() # A StatusBar at the bottom of the window

        # set variables 
        self.blasttype = "blastp"
        self.options = ""
        self.BlastPath = ""
        self.database = ""
        self.newdatabase = ""
        self.dblist = []
        labelList = ['blastp', 'psiblast', 'deltablast', 'blastn', 'blastx']

        if "BLASTDB" in os.environ: # Is BLASTDB set in the system ?
            self.DatabasePath = os.environ['BLASTDB']
        else:
            self.DatabasePath = ""

        # Input Panel 
        panel = wx.Panel(self, -1)

        # Textboxes
        texte1 = wx.StaticText(panel, -1, "Enter sequence here :", wx.Point(10, 5), wx.Size(-1, -1))
        self.SequenceWindow = wx.TextCtrl(panel, value="", style=wx.TE_MULTILINE, pos=(30, 25), size=(500,250))

        self.BlastLocWindow = wx.TextCtrl(panel, value=self.BlastPath, style=wx.TE_READONLY, pos=(30, 320), size=(500,30))
        self.DatabaseLocWindow = wx.TextCtrl(panel, value=self.DatabasePath, style=wx.TE_READONLY, pos=(30, 395), size=(500,30))

        texte2 = wx.StaticText(panel, -1, "Enter options here :", wx.Point(545, 200), wx.Size(-1, -1))
        self.OptionsWindow = wx.TextCtrl(panel, value="", style=wx.TE_MULTILINE, pos=(550, 220), size=(200,60))
		  
        self.blastchoicebox = wx.RadioBox(panel, label='Blast type', pos=(540, 10), choices=labelList, majorDimension=1, style=wx.RA_SPECIFY_COLS) 
        self.blastchoicebox.Bind(wx.EVT_RADIOBOX,self.onRadioBox) 

        texte3 = wx.StaticText(panel, -1, "Select database from list :", wx.Point(560, 325), wx.Size(-1, -1), )
        self.dbselector = wx.ListBox(panel, pos=(560, 346) ,size=(180,70), choices=self.dblist, style=wx.LB_NEEDED_SB)
        self.Bind(wx.EVT_LISTBOX, self.onListBox, self.dbselector)

        # Checkboxes
        self.showoutput = wx.CheckBox(panel, label='show output', pos=(645,160), size=(-1, -1), style =wx.ALIGN_RIGHT)
        self.showoutput.SetValue(True)
        self.saveatcwd = wx.CheckBox(panel, label='write to current directory', pos=(545,295), size=(-1, -1), style =wx.ALIGN_RIGHT)
        self.saveatcwd.SetValue(False)              

        # Buttons
        ConfigButton1 = wx.Button(panel, -1, "Set Blast Path",  wx.Point(30, 280), wx.Size(-1, -1))
        ConfigButton2 = wx.Button(panel, -1, "Set Database Path",  wx.Point(30, 355), wx.Size(-1, -1))
        ConfigButton3 = wx.Button(panel, -1, "Save Config",  wx.Point(30, 435), wx.Size(-1, -1))
        DatabaseButton = wx.Button(panel, -1, "Make a new Database",  wx.Point(565, 425), wx.Size(-1, -1))
        BlastButton = wx.Button(panel, -1, "Blast",  wx.Point(645, 40), wx.Size(100, 100))
        OptionshelpButton = wx.Button(panel, -1, "?", pos=(675, 200), size=(20, 20))

        self.Bind(wx.EVT_BUTTON, self.setBlastPath, ConfigButton1)
        self.Bind(wx.EVT_BUTTON, self.setDatabasePath, ConfigButton2)    
        self.Bind(wx.EVT_BUTTON, self.saveConfig, ConfigButton3)
        self.Bind(wx.EVT_BUTTON, self.makedatabase, DatabaseButton)
        self.Bind(wx.EVT_BUTTON, self.doBlast, BlastButton)
        self.Bind(wx.EVT_BUTTON, self.onOptionshelpButton, OptionshelpButton)

        # run on startup
        self.onstartup()
       
    def onstartup(self):
        self.setRoamingDir()
        self.readconfig()   # read config file if present        
        self.setSavePath()
        if self.DatabasePath == "": 
            self.statusbar.SetStatusText("You have to set the database path first ")
        else:
            self.importdblist()

    def setRoamingDir(self):
        self.RoamingDir = os.path.join(os.environ['USERPROFILE'],"AppData\\Roaming\\Win4blast\\")
        if not os.path.exists(self.RoamingDir):
            os.mkdir(self.RoamingDir)        

    def setSavePath(self):
        if self.saveatcwd.GetValue():
            self.SavePath = os.getcwd()
        else:
            self.SavePath = self.RoamingDir

    def readconfig(self):
        if os.path.isfile(os.path.join(self.RoamingDir,"win4blast.cfg")):
            config_file=""
            config_file = open(os.path.join(self.RoamingDir,"win4blast.cfg"),'r').readline()
            self.BlastPath=(config_file.split(",")[0])
            self.DatabasePath=(config_file.split(",")[-1])
            self.BlastLocWindow.write(self.BlastPath)
            self.DatabaseLocWindow.write(self.DatabasePath)        
            self.statusbar.SetStatusText("Configuration file found and loaded")
            
    def onOptionshelpButton(self, event):
        helpframe = OptionsFrame(None, -1, self.blasttype+" Options", self.BlastPath, self.blasttype)
        helpframe.Show(True)
        return True

    def onError(self):
        ErrorMsg = ErrorFrame(None, -1, self.prog+" Error", self.command)
        ErrorMsg.Show(True)
        return True

    def importdblist(self): # creates a list of databases located in dbpath
        self.dblist =[] # just in case if a new database has been created
        lst_raw = glob(os.path.join(self.DatabasePath,"*.phr"))
        for item in lst_raw:
            dbname = item.split("\\")[-1].split(".")[0]
            self.dblist.append(dbname)
        self.dbselector.Set(self.dblist)

    def onListBox(self, event): 
        self.statusbar.SetStatusText( "Selected Database : "+event.GetEventObject().GetStringSelection())
        self.database = os.path.join(self.DatabasePath, event.GetEventObject().GetStringSelection())

    def onRadioBox(self,e): 
        self.blasttype = self.blastchoicebox.GetStringSelection()

    def makedatabase(self, event):
        self.newdatabase = wx.FileSelector(message="Choose a database in fasta format")
        if self.newdatabase == '': # in case of annulation
            pass
        else:
            self.prog = '"'+self.BlastPath+"makeblastdb.exe"+'"'
            if self.blasttype == 'blastp':
                dbtype = "prot"
            elif  self.blasttype == 'blastn':
                dbtype = "nucl"
            else:
                dbtype = "prot"
            infile = '"'+self.newdatabase+'"'
            dbname = self.newdatabase.split("\\")[-1].split(".")[0]
            self.command = '%s -in %s -out %s -parse_seqids -dbtype %s' % (self.prog, infile, dbname, dbtype)
            retcode = subprocess.call(self.command)
            if not retcode == 0:
                self.onError()
                self.statusbar.SetStatusText("Database could not be created") 
            elif os.path.exists(self.newdatabase.split(".")[0]+".phr"):
                self.statusbar.SetStatusText("Database "+dbname+" created")
            else:
                self.statusbar.SetStatusText("Database could not be created")
        self.importdblist()            

    def doBlast(self, event):
        self.setSavePath()
        if self.database == "":
            self.statusbar.SetStatusText("Select Database first !!!")
        else:
            self.SequenceWindow.SaveFile(filename=os.path.join(self.SavePath,"query.fasta"))
            if not self.OptionsWindow.IsEmpty():
                self.OptionsWindow.SetSelection(-1, -1)
                self.options = self.OptionsWindow.GetStringSelection()
            else:
               self.options = "" 
            self.prog = '"'+os.path.join(self.BlastPath+self.blasttype)+'.exe'+'"'
            infile = os.path.join(self.SavePath,"query.fasta")
            if "-html" in self.options:
                outfile = os.path.join(self.SavePath,"blastout.html")
            else:
                outfile = os.path.join(self.SavePath,"blastout.txt")
            self.command = '%s -query %s -db %s -out %s %s' % (self.prog, infile, self.database, outfile , self.options)
            retcode = subprocess.call(self.command)
            if not retcode == 0:
                self.onError()
                self.statusbar.SetStatusText(outfile+" could not be created")
            elif os.path.exists(outfile) and self.showoutput.GetValue():
                self.statusbar.SetStatusText(outfile+" created")
                subprocess.Popen(outfile, shell=True)
            elif os.path.exists(outfile):
                self.statusbar.SetStatusText(outfile+" created")
            else:
                self.statusbar.SetStatusText(outfile+" could not be created")
        
    def setBlastPath(self, event):       
        self.BlastPath = wx.DirSelector(message="Choose blast bin location")+'\\'
        if self.BlastPath == '\\': # in case of annulation
           self.BlastPath = ""   
        self.BlastLocWindow.Clear()
        self.BlastLocWindow.write(self.BlastPath)

    def setDatabasePath(self, event):
        self.DatabasePath = wx.DirSelector(message="Choose database location")
        self.DatabaseLocWindow.Clear()
        self.DatabaseLocWindow.write(self.DatabasePath)
        self.statusbar.SetStatusText(" You have set the Databasepath ")
        self.importdblist()
        self.dbselector.Set(self.dblist)

    def saveConfig(self, event):
        with open(os.path.join(self.RoamingDir,'win4blast.cfg'),'w') as config_file:
            config_file.write(self.BlastPath+",")
            config_file.write(self.DatabasePath)
        self.statusbar.SetStatusText("Saved Configuration")

class OptionsFrame(wx.Frame):
    def __init__(self, parent, ID, title, BlastPath, blasttype):
        not_resizeable = wx.SYSTEM_MENU | wx.MINIMIZE_BOX | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, parent, -1, title, pos=(-1, -1), size=(600, 550), style=not_resizeable)

        # Input Panel 
        panel = wx.Panel(self, -1)
        self.TextWindow = wx.TextCtrl(panel, value="", style=(wx.TE_MULTILINE), pos=(-1, -1), size=(590, 500))
        self.showOptions(BlastPath,blasttype)

    def showOptions(self, BlastPath, blasttype):
        prog = '"'+os.path.join(BlastPath+blasttype)+'.exe'+'"'
        subprocess.call(prog+" -help", shell=True)
        self.TextWindow.write(subprocess.check_output(prog+" -help", shell=True))
                
class ErrorFrame(wx.Frame):
    def __init__(self, parent, ID, title, command):
        on_top = wx.SYSTEM_MENU | wx.MINIMIZE_BOX | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.STAY_ON_TOP
        wx.Frame.__init__(self, parent, -1, title, pos=(-1, -1), size=(600, 550), style=on_top)

        # Input Panel 
        panel = wx.Panel(self, -1)
        self.TextWindow = wx.TextCtrl(panel, value="", style=wx.TE_MULTILINE, pos=(-1, -1), size=(590, 500))
        self.showError(command)

    def showError(self, command):
        try:
            self.TextWindow.write(subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode())
        except subprocess.CalledProcessError as e:
            self.TextWindow.write(e.output.decode())
            
class Win4blastApp(wx.App):
    def OnInit(self):
        frame = Win4blastFrame(None, -1, "Win4blast")
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

if __name__ == '__main__':
    app = Win4blastApp(0) # créer une nouvelle instance de l'application
    app.MainLoop()   # lancer l'application
