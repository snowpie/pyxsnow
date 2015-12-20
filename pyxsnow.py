#!/usr/bin/env python
## by snowpie@github.com 2015
## Inspired by the venerable xsnow from 2001 and earlier. Some images
## may bare a striking resemblence to the original xsnow images.

import gtk
import cairo
import gobject
import pango
import math
import argparse
from random import randint,seed
#import sys
#	if sys.argv:


def progress_timeout(object):
    x, y, w, h = object.allocation
    object.window.invalidate_rect((0,0,w,h),False)
    return True


class MainWindow(gtk.Window):
    __gsignals__ = {
                  #  'realize': 'override',
                     'expose-event' : 'override',
                  #   'size-allocate': 'override',
                  #   'size-request': 'override',
                   }

    def __init__(self):
        super(MainWindow, self).__init__()
        parser = argparse.ArgumentParser(description='Clone of the venerable xsnow, in python.')
        parser.add_argument('--flakes',  metavar='N', type=int, default=150,help='Number of flakes to show.')

        parser.add_argument('--santa', help='Show Santa', action='store_true')
        parser.add_argument('--gusty', help='Random Gusts', action='store_true')
        parser.add_argument('--tinsel', help='Show Tinsel', action='store_true')
#        parser.add_argument('--things', metavar='FILEROOT', action='append', help='Root file name for other stuff. These must be .png files, named pixmaps/FILEROOTnn.png . May be specified multiple times.')
#        parser.add_argument('--numthings',  metavar='N', action='append', type=int, help='Number of things to show, matched positionally wiith the --things argument.')

        args = parser.parse_args()
        print args
        self.flakecount=args.flakes
        self.showsanta=args.santa
        self.showtinsel=args.tinsel
        self.gusty=args.gusty

        gtk.Window.set_keep_above(self,True)

        self.maxx,self.maxy=gtk.gdk.screen_width(),gtk.gdk.screen_height()

        width, height = self.get_size()
        bitmap = gtk.gdk.Pixmap(None, width, height, 1)
        cr = bitmap.cairo_create()

        ## Clear the bitmap
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0.0, 0.0, 0.0,0.0)
        cr.rectangle(0,0,width,height)

        cr.fill()
        self.input_shape_combine_mask(bitmap, 0, 0)

        if (self.showsanta):
            self.santa = [ cairo.ImageSurface.create_from_png("pixmaps/BigSantaRudolf1.png"),
                       cairo.ImageSurface.create_from_png("pixmaps/BigSantaRudolf2.png"),
                       cairo.ImageSurface.create_from_png("pixmaps/BigSantaRudolf3.png"),
                       cairo.ImageSurface.create_from_png("pixmaps/BigSantaRudolf4.png"),
                     ]
        self.flakeimgs = [
                           cairo.ImageSurface.create_from_png("pixmaps/snow00.png"),
                           cairo.ImageSurface.create_from_png("pixmaps/snow01.png"),
                           cairo.ImageSurface.create_from_png("pixmaps/snow02.png"),
                           cairo.ImageSurface.create_from_png("pixmaps/snow03.png"),
                           cairo.ImageSurface.create_from_png("pixmaps/snow04.png"),
                           cairo.ImageSurface.create_from_png("pixmaps/snow05.png"),
                           cairo.ImageSurface.create_from_png("pixmaps/snow06.png"),
                     ]
        self.stuffimgs = [
                           cairo.ImageSurface.create_from_png("pixmaps/tree.png"),
                           cairo.ImageSurface.create_from_png("pixmaps/tree.png"),
                           cairo.ImageSurface.create_from_png("pixmaps/chalet.png"),
                     ]
        if (self.showtinsel):
            self.tinselimgs = [
                           cairo.ImageSurface.create_from_png("pixmaps/htinsel100.png"),
                           cairo.ImageSurface.create_from_png("pixmaps/vtinsel100.png"),
                     ]
            self.tinselsize=[]
            for t in self.tinselimgs:
                self.tinselsize.append( [t.get_width(),t.get_height()])
        self.counter=1
        self.flakes=[]
        self.stuff=[]
        self.santaindex=0
        # self.flakecount=100
        self.santaframes=4
        #self.maxx=1300
        #self.maxy=700
        self.santax=150
        self.santay=20
        self.init_snow()
        self.init_stuff()
	self.gust=0;

        self.set_app_paintable(True)
        # no window border
        self.set_decorated(False)

        # see if we can do transparency
        screen = self.get_screen()
        
        alphamap = screen.get_rgba_colormap()
        rgbmap   = screen.get_rgb_colormap()

        if alphamap is not None:
            self.set_colormap(alphamap)
        else:
            self.set_colormap(rgbmap)
            print 'sorry, no alpha channel available :('
            
        self.set_size_request(self.maxx, self.maxy)
        self.timer = gobject.timeout_add (100, progress_timeout, self)

    def init_snow(self):
        for flake in range(0, self.flakecount):
            f=randint(0,6)
            x=randint(0,self.maxx)
            y=randint(0,self.maxy)
            dx=randint(0,2)-1
            dy=randint(2,5)
            self.flakes.append([f,x,y,dx,dy])

    def init_stuff(self):
        for thing in range(0,10):
            f=randint(0,2)
            x=randint(0,self.maxx)
            y=randint(0,self.maxy)
            self.stuff.append([f,x,y])

    def calculate_flakes(self):
        if (self.gusty):
            r=randint(0,10000)
            if (r <50 or self.gust <0):
                self.gust=-25
            elif ( r>9950 or self.gust >0):
                self.gust=25
            if ( r>4900 and r<5500):
                self.gust=0;
        else: self.gust=0;
        for i,member in enumerate(self.flakes):
            g=i % 10
            x= self.flakes[i][1]
            if ( x > self.maxx or x < 0) :
                x=randint(0,self.maxx)
            y= self.flakes[i][2]
            if ( y > self.maxy ) :
                y=0
            dx= self.flakes[i][3]+(g*self.gust)/10
            dy= self.flakes[i][4]+(g*abs(self.gust))/20
            self.flakes[i][1]=x+dx
            self.flakes[i][2]=y+dy

    def do_expose_event(self, event):
        # we're going to draw on a temporary surface
        # then copy to the window surface
        # you can also draw directly on the window

        width, height = self.get_size()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        # background is gray and transparent
        ctx.set_source_rgba(.7, .8, .7, 0.0)
        ctx.paint()

        ## Stuff first (trees, houses etc)
        for things in self.stuff:
            ctx.set_source_surface(self.stuffimgs[things[0]],things[1],things[2])
            ctx.paint()

        ## Then Santa
        if (self.showsanta):
            self.santax=self.santax+3
            if (self.santax > self.maxx):
                self.santax=-100
                self.santay=randint(20,self.maxy)
            self.santaindex=( (self.santaindex+1) % self.santaframes )
            ctx.set_source_surface(self.santa[self.santaindex], self.santax, self.santay)
            ctx.paint()

        ## Here comes the snow

        self.calculate_flakes()
        for flake in self.flakes:
            ctx.set_source_surface(self.flakeimgs[flake[0]],flake[1],flake[2])
            ctx.paint()

        ## and some tinsel on top
        if (self.showtinsel):
            steps=self.maxx/self.tinselsize[0][0]
            tinselwidth,tinselheight=self.tinselsize[0][0],self.tinselsize[0][1]
            for x in range(0,steps):
                ctx.set_source_surface(self.tinselimgs[0],x * tinselwidth,0)
                ctx.paint()
                ctx.set_source_surface(self.tinselimgs[0],x * tinselwidth,self.maxy-tinselheight)
                ctx.paint()
            steps=self.maxx/self.tinselsize[1][0]
            tinselwidth,tinselheight=self.tinselsize[1][0],self.tinselsize[1][1]
            for y in range(0,steps):
                ctx.set_source_surface(self.tinselimgs[1],0,y * tinselheight)
                ctx.paint()
                ctx.set_source_surface(self.tinselimgs[1],self.maxx-tinselwidth, y * tinselheight)
                ctx.paint()

        
        # now copy to our window surface
        dest_ctx = self.window.cairo_create()
        # only update what needs to be drawn
        dest_ctx.rectangle(event.area.x, event.area.y, 
                           event.area.width, event.area.height)
        dest_ctx.clip()
        # source operator means replace, don't draw on top of
        dest_ctx.set_operator(cairo.OPERATOR_SOURCE)
        dest_ctx.set_source_surface(surface, 0, 0)
        dest_ctx.paint()

    def _on_size_allocate(self,win,allocation):
          w,h = allocation.width, allocation.height
          bitmap = gtk.gdk.Pixmap(None, w, h, 1)
          cr = bitmap.cairo_create()

          # Clear the bitmap
          cr.set_source_rgb(0.0, 0.0, 0.0)
          cr.set_operator(cairo.OPERATOR_CLEAR)
          cr.paint()
          win.shape_combine_mask(bitmap, 0, 0)
        
if __name__ == "__main__":
    w = MainWindow()
    w.show()
    gtk.main()
