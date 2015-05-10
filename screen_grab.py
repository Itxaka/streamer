import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from gi.repository import GObject, Gst, Gtk
from gi.repository import GdkX11, GstVideo
import os

# Based of http://bazaar.launchpad.net/~jderose/+junk/gst-examples/view/head:/webcam-1.0

GObject.threads_init()
Gst.init(None)


class ScreenGrabber:
    """Grabs the main screen and show it in a resizable gtk screen. Video scaling on screen resize"""
    def __init__(self):
        self.xid = None
        self.window = Gtk.Window()
        self.window.connect('destroy', self.quit)
        self.window.set_default_size(800, 450)

        self.drawingarea = Gtk.DrawingArea()
        self.window.add(self.drawingarea)

        # Create GStreamer pipeline
        self.pipeline = Gst.Pipeline()

        # Create bus to get events from GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::error', self.on_error)

        # This is needed to make the video output in our DrawingArea:
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.on_sync_message)

        # Create GStreamer elements
        self.src = Gst.ElementFactory.make('ximagesrc', None)
        self.src.set_property('startx', os.getenv('startx', 0))
        # Hardcoded for the moment. Monitors on nvidia seems to be merge together into a huge one :/
        self.src.set_property('endx', os.getenv('startx', 1920))
        self.src.set_property('use-damage', 0)
        self.queue = Gst.ElementFactory.make('queue', None)
        self.scale = Gst.ElementFactory.make('videoscale', None)
        self.sink = Gst.ElementFactory.make('ximagesink', None)

        # Add elements to the pipeline
        self.pipeline.add(self.src)
        self.pipeline.add(self.queue)
        self.pipeline.add(self.scale)
        self.pipeline.add(self.sink)

        # Link elements
        self.src.link(self.queue)
        self.queue.link(self.scale)
        self.scale.link(self.sink)

    def run(self):
        self.window.show_all()
        self.xid = self.drawingarea.get_property('window').get_xid()
        self.pipeline.set_state(Gst.State.PLAYING)
        self.window.maximize()  # workaround so the videoscale starts working from the start
        Gtk.main()

    def quit(self, window):
        self.pipeline.set_state(Gst.State.NULL)
        Gtk.main_quit()

    def on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            msg.src.set_property('force-aspect-ratio', True)
            msg.src.set_window_handle(self.xid)

    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())


screen = ScreenGrabber()
screen.run()

