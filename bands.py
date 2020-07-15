#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import sys, time, subprocess, json
    from logger import log
    from datetime import datetime
    from auth import miband3_auth, miband4_auth
    from bluepy.btle import BTLEDisconnectError
    from constants import ALERT_TYPES, MUSICSTATE
except Exception as e:
    print("Some Modules are missings {}".format_map(e))

class miband3():

    # Send simple call
    def call_immediate(self):
        log.info('Sending Call\n')
        time.sleep(1)
        band.send_alert(ALERT_TYPES.PHONE)

    # Send simple message
    def msg_immediate(self):
        log.info('Sending Message\n')
        time.sleep(1)
        band.send_alert(ALERT_TYPES.MESSAGE)

    # Get detailed information of the device
    def detail_info(self, band, buffer):
        buffer.append(('software', {"MIBAND3 - {}".format(band.mac_address): band.get_revision()}))
        buffer.append(('hardware', {"MIBAND3 - {}".format(band.mac_address): band.get_hrdw_revision()}))
        buffer.append(('serial', {"MIBAND3 - {}".format(band.mac_address): band.get_serial()}))
        buffer.append(('battery', {"MIBAND3 - {}".format(band.mac_address): band.get_battery_info()}))
        buffer.append(('time', {"MIBAND3 - {}".format(band.mac_address): band.get_current_time()}))
        buffer.append(('steps', {"MIBAND3 - {}".format(band.mac_address): band.get_steps()}))

    # Send custom message
    def custom_message(self):
        band.send_custom_alert(5)

    # Send custom call
    def custom_call(self):
        # custom_call
        band.send_custom_alert(3)
    # Send custom missed call
    def custom_missed_call(self):
        band.send_custom_alert(4)

    def l(self,x):
        log.info('Beats per second:', x)

    # Get single heart rate value
    def heart_beat(self):
        band.start_raw_data_realtime(heart_measure_callback=self.l)

    # Set the date
    def change_date(self):
        band.change_date()

    def miband3_menu(self,MAC_ADDR,buffer):
        log.info('Mi Band 3 - Attempting to connect to {}'.format(MAC_ADDR))

        def updateFirmware(self):
            fileName = input('Mi Band 3 - Enter the file Name with Extension\n')
            band.dfuUpdate(fileName)

        global band
        band = miband3_auth(MAC_ADDR, debug=True)
        band.setSecurityLevel(level = "medium")
    
        if band.initialize():
            log.info("Mi Band 3 - Initialized")
            self.detail_info(band,buffer)
        else:
            band.authenticate()
            band.setSecurityLevel(level = "medium")
            log.info("Mi Band 3 - Authenticated")
            self.detail_info(band,buffer)
        band.disconnect()


class miband4():

    @staticmethod
    # Get detailed information of the device
    def detail_info(band, buffer):
        buffer.append(('software', {"MIBAND4 - {}".format(band.mac_address): band.get_revision()}))
        buffer.append(('hardware', {"MIBAND4 - {}".format(band.mac_address): band.get_hrdw_revision()}))
        buffer.append(('serial', {"MIBAND4 - {}".format(band.mac_address): band.get_serial()}))
        buffer.append(('battery', {"MIBAND4 - {}".format(band.mac_address): band.get_battery_info()}))
        buffer.append(('time', {"MIBAND4 - {}".format(band.mac_address): band.get_current_time()}))
        buffer.append(('steps', {"MIBAND4 - {}".format(band.mac_address): band.get_steps()}))

    @staticmethod
    # Send simple call
    def call_immediate(band):
        log.info('Mi Band 4 - Sending Call\n')
        time.sleep(1)
        band.send_alert(ALERT_TYPES.PHONE)

    @staticmethod
    # Send simple message
    def msg_immediate(band):
        log.info('Mi Band 4 - Sending Message\n')
        time.sleep(1)
        band.send_alert(ALERT_TYPES.MESSAGE)

    @staticmethod
    # Send Call / Missed Call / Message
    def send_notif(band):
        msg = input("Mi Band 4 - Enter message or phone number to be displayed: ")
        ty = int(input("Mi Band 4 - 1 for Message / 2 for Missed Call / 3 for Call: "))
        if (ty > 3 or ty < 1):
            log.info('Mi Band 4 - Invalid choice')
            time.sleep(2)
            return
        a = [5, 4, 3]
        band.send_custom_alert(a[ty - 1], msg)

    # Send custom message
    def custom_message(self, band):
        band.send_custom_alert(5)

    # Send custom call
    def custom_call(self, band):
        band.send_custom_alert(3)

    # Send custom missed call
    def custom_missed_call(self, band):
        band.send_custom_alert(4)

    def l(self, x):
        log.info('Mi Band 4 - Beats per second:', x)

    def heart_beat(self, band):
        band.start_raw_data_realtime(heart_measure_callback=self.l)

    # Set custom date
    def change_date(self, band):
        band.change_date()

    # Get the steps count
    def get_step_count(self, band):
        binfo = band.get_steps()
        log.info('Number of steps: ', binfo['steps'])
        log.info('Fat Burned: ', binfo['fat_burned'])
        log.info('Calories: ', binfo['calories'])
        log.info('Distance travelled in meters: ', binfo['meters'])

    # Get single heart rate value
    def get_heart_rate(self, band):
        log.info('Latest heart rate is : %i' % band.get_heart_rate_one_time())
        input('Press a key to continue')

    def heart_logger(self, data):
        log.info('Mi Band 4 - Realtime heart BPM:', data)

    # Get heart rate values in real time
    def get_realtime(self, band):
        band.start_heart_rate_realtime(heart_measure_callback=self.heart_logger)
        input('Press Enter to continue')

    # Destroy / Restore / Update the Firmware
    def restore_firmware(self, band):
        log.warning("This feature has the potential to brick your Mi Band 4. You are doing this at your own risk.")
        path = input("Enter the path of the firmware file :")
        band.dfuUpdate(path)

    # Set custom time
    def set_time(self, band):
        now = datetime.now()
        log.info('Set time to:', now)
        band.set_current_time(now)

    def _default_music_play(self):
        log.info("Played")

    def _default_music_pause(self):
        log.info("Paused")

    def _default_music_forward(self):
        log.info("Forward")

    def _default_music_back(self):
        log.info("Backward")

    def _default_music_vup(self):
        log.info("volume up")

    def _default_music_vdown(self):
        log.info("volume down")

    def _default_music_focus_in(self):
        log.info("Music focus in")

    def _default_music_focus_out(self):
        log.info("Music focus out")

    # Set the music controls
    def set_music(self, band):
        band.setMusicCallback(self._default_music_play,
                              self._default_music_pause,
                              self._default_music_forward,
                              self._default_music_back,
                              self._default_music_vup,
                              self._default_music_vdown,
                              self._default_music_focus_in,
                              self._default_music_focus_out)
        fi = input("Set music track to : ")
        band.setTrack(fi, MUSICSTATE.PLAYED)
        while True:
            if band.waitForNotifications(0.5):
                continue
        input("enter any key")

    @staticmethod
    def activity_log_callback(timestamp, c, i, s, h, buffer):
        # Valid only when the heart rate is below 255
        if h != 255:
            buffer.append(('mi4-logs', {'Log - ': "{}: category: {}; intensity {}; steps {}; heart rate {};\n".format(
                timestamp.strftime('%d.%m - %H:%M'), c, i, s, h)}))

    # Get activity logs for a day from the band's internal memory
    def get_activity_logs(self, band):
        # The number of notifications was limited to prevent the thread from being blocked indefinitely
        temp = datetime.now()
        band.get_activity_betwn_intervals(datetime(temp.year, temp.month, temp.day), datetime.now(),
                                          self.activity_log_callback)
        with open('configs.json') as file:
            data = json.load(file)
        counter = 0
        # This part extracts up to 24h of internal logs, however most of the date is not relevant and takes a lot of time to extract
        while counter < data['log_limit']:
            band.waitForNotifications(0.2)
            counter += 1

    # Return a list with the desired format for the function that sends information
    # Example: [('routing-key', {key:value}), ('routing-key', {key:value})...]
    def get_buffer(self, MAC_ADDR, AUTH_KEY, buffer):
        success = False
        AUTH_KEY = bytes.fromhex(AUTH_KEY)
        reconnect_counter = 0
        while not success:
            try:
                if (AUTH_KEY):
                    band = miband4_auth(MAC_ADDR, AUTH_KEY, debug=True)
                    success = band.initialize()
                else:
                    band = miband4_auth(MAC_ADDR, debug=True)
                    success = True
                break
            except BTLEDisconnectError:
                log.error('Connection to the Mi Band 4 failed. Trying out again in 3 seconds')
                time.sleep(3)
                if reconnect_counter <= 3:
                    reconnect_counter += 1
                    continue
                else:
                    log.error('Failed to connect to Mi band 4!')
                    break
            except KeyboardInterrupt:
                log.warning("\nExit.")
                exit()

        return self.detail_info(band, buffer), self.get_step_count(band, buffer), self.get_activity_logs(band, buffer)
        band.disconnect()


