import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.mapview import MapView, MapMarker
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog

kivy.require("1.11.1")

class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        self.map_view = MapView(zoom=14)
        layout.add_widget(self.map_view)
        btn = Button(text="Back", font_size=30,  size_hint=(1, 0.1))
        btn.bind(on_press=self.go_back)
        layout.add_widget(btn)
        self.add_widget(layout)

    def show_location(self, latitude, longitude):
        marker = MapMarker(lat=latitude, lon=longitude, source='marker.png')
        self.map_view.add_marker(marker)
        self.map_view.center_on(latitude, longitude)

    def go_back(self, instance):
        self.manager.current = "main"
        self.manager.transition.direction = "right"

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        btn = Button(text="Show my location", font_size=30)
        btn.bind(on_press=self.show_location)
        layout.add_widget(btn)
        self.add_widget(layout)

    def show_location(self, instance):
        # Code to retrieve the user's GPS location goes here
        latitude = 37.7749
        longitude = -122.4194
        self.manager.get_screen("map").show_location(latitude, longitude)
        self.manager.current = "map"
        self.manager.transition.direction = "left"

        bool = False
        if(platform == 'android'):
            from android.permissions import Permission, request_permissions
            def callback(permission, results):
                if all([res for res in results]):
                    print("Got all permissions")
                    from plyer import gps
                    gps.configure(on_location=self.update_blinker_position,
                                  on_status=self.on_auth_status)
                    gps.start(minTime=1000, minDistance=0)
                else:
                    print("Did not get all permissions")

            request_permissions([Permission.ACCESS_COARSE_LOCATION,
                                 Permission.ACCESS_FINE_LOCATION], callback)

        # Configure GPS
        if platform == 'ios':
            from plyer import gps
            gps.configure(on_location=self.update_blinker_position,
                          on_status=self.on_auth_status)
            gps.start(minTime=1000, minDistance=0)

    def update_blinker_position(self, *args, **kwargs):
        my_lat = kwargs['lat']
        my_lon = kwargs['lon']
        print("GPS POSITION", my_lat, my_lon)
        # Update GpsBlinker position
        if(not bool):
            self.manager.get_screen("map").show_location(my_lat, my_lon)
            bool = True

    def on_auth_status(self, general_status, status_message):
        if general_status == 'provider-enabled':
            pass
        else:
            self.open_gps_access_popup()

    def open_gps_access_popup(self):
        dialog = MDDialog(title="GPS Error", text="You need to enable GPS access for the app to function properly")
        dialog.size_hint = [.8, .8]
        dialog.pos_hint = {'center_x': .5, 'center_y': .5}
        dialog.open()


class LocationApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(MapScreen(name="map"))
        return sm

if __name__ == "__main__":
    LocationApp().run()
