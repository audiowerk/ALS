# Copyright 2012 Michael Juen und Nikolaus Fleischhacker
# ALS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Luminosus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.graphics import Color, Ellipse, Line

from kivy.app import App
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.widget import Widget

from ArtNet import ArtNet               #ARTNET SUPPORT
#import time
#import pickle  

class Move_xy(Widget):
    def on_touch_move(self, touch):
        with self.canvas:
            Color(1,1,0)
            d=30.
            Ellipse(pos=(touch.x-d/2,touch.y-d/2),size=(d,d))

class actions():
    def quit(self):        
        alc_fc_App().stop()

    
class fc_gui(TabbedPanel):
   
    artnet = ArtNet()                   #ARTNET KLASSE GLOBAL DEFINIEREN
    universe_max = 50                   #MAXIMALE UNIVERSENANZAHL DEFININIEREN
    univ = [0] * universe_max           #UNIVERSE ARRAY MIT MAXIMALER ANZAHL DEFIBNIEREN
    for i in range(0,universe_max):     #ALLE UNIVERSEN MIT 512 DATENSAETZE FUELLEN
        univ[i] = [0] * 512                
    

    universe = 0                        #DEFAULT UNIVERSE
    channel = 0                         #DEFAULT CHANNEL
    artnet_thread = False

    action = actions()

    t_universe = ObjectProperty(None)
    t_channel = ObjectProperty(None)
    s_test_1 = ObjectProperty(None)
    s_test_2 = ObjectProperty(None)
    s_test_3 = ObjectProperty(None)
    s_test_4 = ObjectProperty(None)
    s_test_5 = ObjectProperty(None)
    
    def button_artnet_start(self):
        if self.artnet_thread == False:
            self.artnet.start()
            self.artnet_thread = True
            self.l_status.text = "ArtNet thread started"
        else:
            self.l_status.text = "ArtNet thread runs already - nothing to do"   
    
    def button_artnet_stop(self): 
        if self.artnet_thread == True:         
            self.artnet.close() 
            self.artnet_thread = False
            self.l_status.text = "ArtNet thread stopped"
        else:
            self.l_status.text = "ArtNet thread not running - nothing to do"
    
    def action_textinput_universe(self):
        self.universe = int(self.t_universe.text)
        if self.universe >= 0 and self.universe < self.universe_max:
            pass
        else:
            self.universe = self.universe_max-1
            self.t_universe.text = str(self.universe)
        self.l_status.text = "Universe changed to " + str(self.universe)

    def action_textinput_channel(self):
        self.channel = int(self.t_channel.text)-1
        if self.channel >= 0 and self.channel < 512:
            pass
        else:
            self.channel = 0
            self.t_channel.text = str(self.channel+1)
        self.l_status.text = "Startaddress changed to " + str(self.channel+1)
        self.l_test_channel_1 = "Address_" + str (self.channel+0+1)
        self.l_test_channel_2 = "Address_" + str (self.channel+1+1)
        self.l_test_channel_3 = "Address " + str (self.channel+2+1)
        self.l_test_channel_4 = "Address " + str (self.channel+3+1)
        self.l_test_channel_5 = "Address " + str (self.channel+4+1)
    
    def tab_panel_test(self):
        self.l_test_channel_1 = "Address " + str (self.channel+0+1)
        self.l_test_channel_2 = "Address " + str (self.channel+1+1)
        self.l_test_channel_3 = "Address " + str (self.channel+2+1)
        self.l_test_channel_4 = "Address " + str (self.channel+3+1)
        self.l_test_channel_5 = "Address " + str (self.channel+4+1)
        
    def action_slider_1(self):
        self.univ[self.universe][self.channel+0]=int(self.s_test_1.value)
        self.artnet.send_dmx_data_mike(self.univ[self.universe],self.universe)
        self.l_test_1.text = str(int(self.s_test_1.value))
        self.l_test_status.text = "Sending Universe " + str(self.universe) + ", Channel " + str(self.channel+0+1) + ", Value " + str(self.univ[self.universe][self.channel])
            
    def action_slider_2(self):
        self.univ[self.universe][self.channel+1]=int(self.s_test_2.value)
        self.artnet.send_dmx_data_mike(self.univ[self.universe],self.universe)
        self.l_test_2.text = str(int(self.s_test_2.value))
        self.l_test_status.text = "Sending Universe " + str(self.universe) + ", Channel " + str(self.channel+1+1) + ", Value " + str(self.univ[self.universe][self.channel+1])
        
    def action_slider_3(self):
        self.univ[self.universe][self.channel+2]=int(self.s_test_3.value)
        self.artnet.send_dmx_data_mike(self.univ[self.universe],self.universe)
        self.l_test_3.text = str(int(self.s_test_3.value))
        self.l_test_status.text = "Sending Universe " + str(self.universe) + ", Channel " + str(self.channel+2+1) + ", Value " + str(self.univ[self.universe][self.channel+2])
        
    def action_slider_4(self):
        self.univ[self.universe][self.channel+3]=int(self.s_test_4.value)
        self.artnet.send_dmx_data_mike(self.univ[self.universe],self.universe)
        self.l_test_4.text = str(int(self.s_test_4.value))
        self.l_test_status.text = "Sending Universe " + str(self.universe) + ", Channel " + str(self.channel+3+1) + ", Value " + str(self.univ[self.universe][self.channel+3])
        
    def action_slider_5(self):
        self.univ[self.universe][self.channel+4]=int(self.s_test_5.value)
        self.artnet.send_dmx_data_mike(self.univ[self.universe],self.universe)
        self.l_test_5.text = str(int(self.s_test_5.value))
        self.l_test_status.text = "Sending Universe " + str(self.universe) + ", Channel " + str(self.channel+4+1) + ", Value " + str(self.univ[self.universe][self.channel+4])
        
#=======Main Program
class alc_fc_App(App): 
    def build(self):     
        return fc_gui()

if __name__ in ('__main__', '__android__'):
    alc_fc_App().run()
    