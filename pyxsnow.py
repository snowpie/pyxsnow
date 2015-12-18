#!/usr/bin/env python

import gtk
import cairo
import gobject
import pango
import math
from random import randint

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
        self.counter=1
        self.flakes=[]
        self.santaindex=0
        self.santaframes=4
        self.maxx=1920
        self.maxy=1080
        self.santax=20
        self.santay=20
        self.init_snow()

        #b = gtk.Button("A Button")
        #self.add(b)
        #b.show()
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
        for flake in range(0, 150):
            f=randint(0,6)
            x=randint(0,self.maxx)
            y=randint(0,self.maxy)
            dx=randint(0,2)-1
            dy=randint(2,5)
            self.flakes.append([f,x,y,dx,dy])

    def calculate_flakes(self):
        for i,member in enumerate(self.flakes):
            x= self.flakes[i][1]
            if ( x > self.maxx or x < 0) :
                x=randint(0,self.maxx)
            y= self.flakes[i][2]
            if ( y > self.maxy ) :
                y=0
            dx= self.flakes[i][3]
            dy= self.flakes[i][4]
            self.flakes[i][1]=x+dx
            self.flakes[i][2]=y+dy

    def do_expose_event(self, event):
        # we're going to draw on a temporary surface
        # then copy to the window surface
        # you can also draw directly on the window
        self.santax=self.santax+3
        if (self.santax > self.maxx):
            self.santax=-100
            self.santay=randint(20,self.maxy)
        self.santaindex=( (self.santaindex+1) % self.santaframes )
       
        width, height = self.get_size()
        
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        # background is gray and transparent
        ctx.set_source_rgba(.7, .8, .7, 0.10)
        ctx.paint()

        ctx.set_source_surface(self.santa[self.santaindex], self.santax, self.santay)
        ctx.paint()

        self.calculate_flakes()
        for flake in self.flakes:
            ctx.set_source_surface(self.flakeimgs[flake[0]],flake[1],flake[2])
            ctx.paint()

        # red border
        ctx.set_line_width(1.0)
        ctx.rectangle(10, 10, width-20, height-20)
        ctx.set_source_rgba(1.0, 0.0, 0.0, .25)
        ctx.stroke()

        #ctx.set_line_width(5.0)
        #ctx.set_source_rgba(.1, .1, .1, 1)
        #ctx.move_to(width/2,height/2)
        #ctx.line_to(width/2 + (min(width,height)/2 -20) * 0.8 * math.cos(self.counter - math.pi/2),
        #    height/2 + (min(width,height)/2 -20) * 0.8 * math.sin(self.counter - math.pi/2))
        #ctx.stroke()


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

        
if __name__ == "__main__":
    w = MainWindow()
    w.show()
    gtk.main()
