import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GstVideo, GdkX11
GObject.threads_init()
Gst.init(None)

from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.src = self.queue = self.scale = self.sink = self.bus = self.pipeline = None
        container = QWidget(self)
        self.setCentralWidget(container)
        self.winId = container.winId()
        self.resize(800, 450)
        self.pipeline = Gst.Pipeline()

        # Create GStreamer elements
        self.src = Gst.ElementFactory.make('ximagesrc', None)
        self.src.set_property('startx', 0)
        # Hardcoded for the moment. Monitors on nvidia seems to be merge together into a huge one :/
        self.src.set_property('endx', 1920)
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
        # Create bus to get events from GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.on_sync_message)

    def on_sync_message(self, bus, message):
        if message.get_structure().get_name() == 'prepare-window-handle':
            message.src.set_property('force-aspect-ratio', True)
            message.src.set_window_handle(self.winId)

    def start(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        self.showMaximized()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.start()
    sys.exit(app.exec_())