#!/usr/bin/env python
import serial
import socket
import os
import logging
import logging.handlers
import sys
import time
import subprocess
import signal
import re
from datetime import datetime, timedelta

logger = logging.getLogger("dreampi")
logger.propagate = False

def check_internet_connection():
    """ Returns True if there's a connection """

    IP_ADDRESS_LIST = [
        "1.1.1.1",  # Cloudflare
        "8.8.8.8",  # Google DNS
    ]

    port = 53
    timeout = 3
    for host in IP_ADDRESS_LIST:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            pass
    else:
        logger.exception("No internet connection")
        return False


def detect_device_and_speed():
    ENABLE_SPEED_DETECTION = True
    MAX_SPEED = 57600

    if not ENABLE_SPEED_DETECTION:
        return ("/dev/ttyACM0", MAX_SPEED)

    command = ["wvdialconf", "/dev/null"]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode("utf-8", errors="replace")
        lines = output.split("\n")
        for line in lines:
            match = re.match(r"(.+)<Info>:\sSpeed\s(\d+);", line.strip())
            if match:
                device = "/dev/" + match.group(1)
                speed = min(int(match.group(2)), MAX_SPEED)
                logger.info("Detected device {} with speed {}".format(device, speed))
                return device, speed
        else:
            logger.info("No modem device detected")
    except:
        logger.exception("Unable to detect modem. Falling back to ttyACM0")
    return ("/dev/ttyACM0", MAX_SPEED)


def get_server_names():
    try:
        cmd = "printf '\x01\xC0\x15\xDC\x03' | nc -u -w6 dcnet.flyca.st 7655 | hexdump -C"
        output = subprocess.check_output(cmd, shell=True)

        output_str = output.decode('utf-8') if hasattr(output, 'decode') else output

        ascii_parts = re.findall(r'\|([^\|]+)\|', output_str)
        ascii_text = ''.join(ascii_parts)

        matches = re.findall(r'(US East|US West|Europe|South America)', ascii_text)
        return matches

    except subprocess.CalledProcessError as e:
        logger.info("Erro ao executar comando: %s", e)
        return []


def best_host(server_names, hosts, count=3, timeout=1):
    results = {}
    for host in hosts:
        pings = []
        for _ in range(count):
            try:
                proc = subprocess.Popen(
                    ["ping", "-c", "1", "-W", str(timeout), host],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                out, err = proc.communicate()
                if proc.returncode == 0:
                    for line in out.splitlines():
                        if "time=" in line:
                            try:
                                ms = float(line.split("time=")[1].split()[0])
                                pings.append(ms)
                            except Exception:
                                pass
            except Exception as e:
                logger.warning("Ping failed: %s (%s)", host, str(e))
        if pings:
            results[host] = sum(pings) / float(len(pings))
        else:
            results[host] = float("inf")

    if not results:
        logger.info("No response")
    
    logger.info("Available DCNET Regions: %s", ', '.join(server_names))
    logger.info("Available DCNET Access Points: %s", ', '.join(hosts))
    
    for host, ping in results.items():
        if ping == float("inf"):
            logger.info("Host %s: no response", host)
        else:
            logger.info("Host %s: %.1f ms", host, ping)        

    best = min(results, key=results.get)
    logger.info("Best DCNET Access Point: %s (%.1f ms)", best, results[best])
    return best


def is_running(process_name):
    try:
        output = subprocess.check_output(["pgrep", "-f", process_name])
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False



class Modem(object):
    def __init__(self, device, speed, send_dial_tone=True):
        self._device, self._speed = device, speed
        self._serial = None
        self._sending_tone = False

        if send_dial_tone:
            self._dial_tone_wav = self._read_dial_tone()
        else:
            self._dial_tone_wav = None

        self._time_since_last_dial_tone = None
        self._dial_tone_counter = 0

    @property
    def device_speed(self):
        return self._speed

    @property
    def device_name(self):
        return self._device

    def _read_dial_tone(self):
        this_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
        dial_tone_wav = os.path.join(this_dir, "dial-tone.wav")

        with open(dial_tone_wav, "rb") as f:
            dial_tone = f.read()  # Read the entire wav file
            dial_tone = dial_tone[44:]  # Strip the header (44 bytes)

        return dial_tone

    def connect(self):
        if self._serial:
            self.disconnect()

        logger.info("Opening serial interface to {}".format(self._device))
        self._serial = serial.Serial(
            self._device, self._speed, timeout=0
        )
        return self._serial

    def disconnect(self):
        if self._serial and self._serial.isOpen():
            self._serial.flush()
            self._serial.close()
            self._serial = None

    def reset(self):
        while True:
            try:
                self.send_command("ATZ0",timeout=3)  # Send reset command
                time.sleep(0.5)
                self.send_command("ATE0W2")  # Don't echo our responses
                return
            except IOError:
                self.shake_it_off()

    def start_dial_tone(self):
        if not self._dial_tone_wav:
            return
        i = 0
        while i < 3:
            try:
                self.reset()
                self.send_command(b"AT+FCLASS=8")  # Enter voice mode
                self.send_command(b"AT+VLS=1")  # Go off-hook
                self.send_command(b"AT+VSM=141,8000")  # 8 bit unsigned PCM
                self.send_command(b"AT+VTX")  # Voice transmission mode
                logger.info("<LISTENING>")
                break
            except IOError:
                time.sleep(0.5)
                self.shake_it_off()
                i+=1
                pass

        self._sending_tone = True
        self._time_since_last_dial_tone = datetime.now() - timedelta(seconds=100)
        self._dial_tone_counter = 0

    def stop_dial_tone(self):
        if not self._sending_tone:
            return
        if self._serial is None:
            raise Exception("Not connected")

        self._serial.write(b"\x00\x10\x03\r\n")
        self.send_escape()
        self.send_command(b"ATH0")  # Go on-hook
        self.reset()
        self._sending_tone = False

    def answer(self):
        if os.path.isfile("/home/pi/mute"):
            self.send_command(b"ATM0") #mute speaker modems

        port = dcnet_port
        
        if "5360010" in dial_string:
            port = "7656"
            logger.info("DCNET: Power Smash/VOOT digits detected. Connecting with port {} ".format(port))
        
        self.send_command(b"ATA", ignore_responses=[b"OK"])
        time.sleep(3)
        logger.info("Call answered!")
       
        process="dcnet.rpi"
        cmd = ["/home/pi/dreampi/dcnet.rpi", "-t", "{}".format(self._device), "-b", "{}".format(self._speed), "-p", "{}".format(port)]

        if os.path.isfile("/home/pi/socat"):           
            try:
                subprocess.check_output(["socat", "-V"], stderr=subprocess.STDOUT)
                logger.info("SOCAT: Connecting with " + best_ap)
                process="socat"
                cmd = ["socat", "{},raw,echo=0".format(self._device), "TCP4:{}:7654".format(best_ap)]
            except (OSError, subprocess.CalledProcessError):
                logger.info("socat not installed, falling back to dcnet.rpi")
        else:
            logger.info("DCNET: Connecting with " + best_ap)

        subprocess.Popen(cmd)
        time.sleep(3)
        self.disconnect()
        
        while is_running(process):
            time.sleep(3)

        logger.info("Connection terminated")
  
    def send_command(self, command, timeout=60, ignore_responses = None):
        if self._serial is None:
            raise Exception("Not connected")
        if ignore_responses is None:
            ignore_responses = []

        VALID_RESPONSES = [b"OK", b"ERROR", b"CONNECT", b"VCON"]
        for ignore in ignore_responses:
            VALID_RESPONSES.remove(ignore)

        if isinstance(command, bytes):
            final_command = command + b'\r\n'
        else:
            final_command = ("%s\r\n" % command).encode() 
        time.sleep(0.2)
        self._serial.write(final_command)
        logger.info('Command: %s' % command.decode())
        start = time.time()
        line = b""
        while True:
            new_data = self._serial.readline().strip()
            if not new_data:
                if time.time() - start < timeout:
                    continue
                raise IOError("There was a timeout while waiting for a response from the modem")
            line = line + new_data
            for resp in VALID_RESPONSES:
                if resp in line:
                    if resp != b"OK" and "VSM" not in command:
                        logger.info('Response: %s' % line.decode())
                        if resp == b"ERROR":
                            logger.info("Command refused")
                            self._serial.write("\x00\x10\x03\r\n")
                            time.sleep(1)
                            response = self._serial.read(64)  # ou usar .readline() se espera texto
                            logger.info(repr(response))
                    return

    def send_escape(self):
        if self._serial is None:
            raise Exception("Not connected")
        time.sleep(1.0)
        self._serial.write(b"+++")
        time.sleep(1.0)

    def shake_it_off(self):
        for i in range(3):
            self._serial.write(b'+')
            time.sleep(0.2)
        time.sleep(3)
        self.send_command('ATH0')
        logger.info("Shook it off")

    def update(self):
        now = datetime.now()
        if self._sending_tone:
            # Keep sending dial tone
            BUFFER_LENGTH = 1000
            TIME_BETWEEN_UPLOADS_MS = (1000.0 / 8000.0) * BUFFER_LENGTH

            if self._dial_tone_wav is None:
                raise Exception("Dial tone wav not loaded")
            if self._serial is None:
                raise Exception("Not connected")

            if (
                not self._time_since_last_dial_tone
                or ((now - (self._time_since_last_dial_tone)).microseconds * 1000)
                >= TIME_BETWEEN_UPLOADS_MS
            ):
                byte = self._dial_tone_wav[
                    self._dial_tone_counter : self._dial_tone_counter + BUFFER_LENGTH
                ]
                self._dial_tone_counter += BUFFER_LENGTH
                if self._dial_tone_counter >= len(self._dial_tone_wav):
                    self._dial_tone_counter = 0
                self._serial.write(byte)
                self._time_since_last_dial_tone = now


class GracefulKiller(object):
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        logging.warning("Received signal: %s", signum)
        self.kill_now = True

def process():
    killer = GracefulKiller()
    os.system("sudo apt-get install -qq -y socat 2> /dev/null &")
        
    server_names = get_server_names()

    region_to_host = {
    "US East": "dcnet-use.flyca.st",
    "US West": "dcnet-usw.flyca.st",
    "Europe": "dcnet-eu.flyca.st",
    "South America": "dcnet-br.flyca.st"
    }
    
    if server_names:
        hosts = [region_to_host[name] for name in server_names if name in region_to_host]
    else:
        server_names = list(region_to_host.keys())
        hosts = list(region_to_host.values())
    
    global dial_string
    global best_ap
    global dcnet_port
    dial_string = ""
    best_ap = best_host(server_names, hosts)
    dcnet_port = "7654"

    logger.info("Detecting modem...")
    global device_and_speed
    device_and_speed = detect_device_and_speed()

    logger.info("Internet connected and device found!")

    modem = Modem(device_and_speed[0], device_and_speed[1])
    modem.connect()
    modem.start_dial_tone()
    
    mode = "LISTENING"
    time_digit_heard = None

    while True:
        if killer.kill_now:
            modem.stop_dial_tone()
            break

        now = datetime.now()

        if mode == "LISTENING":
            modem.update()
            char = modem._serial.read(1)
            char = char.strip()
            if not char:
                continue

            if ord(char) == 16:
                try:
                    last_heard = time.time()
                    raw_string = ""
                    tel_digits = ['0','1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#']
                    char = modem._serial.read(1).decode()
                    if char in tel_digits:
                        raw_string += char
                        while True:
                            if time.time() - last_heard > 3:
                                break
                            try:
                                char = modem._serial.read(1).decode() #first character was <DLE>, what's next?
                                if ord(char) == 16:
                                    continue
                                if char in tel_digits:
                                    last_heard = time.time()
                                    raw_string += char
                            except (TypeError, ValueError):
                                pass

                    if len(raw_string) > 0:
                        logger.info("Heard: %s", raw_string)
                        dial_string = raw_string
                        mode = "ANSWERING"
                        modem.stop_dial_tone()
                        time_digit_heard = now
                    else:
                        pass
                except (TypeError, ValueError):
                    pass

        elif mode == "ANSWERING":
            if (now - time_digit_heard).total_seconds() > 5:
                time_digit_heard = None

                modem.answer()
                modem.connect()
                mode = "LISTENING"
                modem.start_dial_tone()
    return 0


def enable_prom_mode_on_wlan0():
    try:
        subprocess.check_call("sudo ifconfig wlan0 promisc".split())
        logging.info("Promiscuous mode set on wlan0")
    except subprocess.CalledProcessError:
        logging.info("Attempted to set promiscuous mode on wlan0 but was unsuccessful")
        logging.info("Probably no wifi connected, or using a different device name")


def main():
    global master
    master = False
    try:
        while not check_internet_connection():
            logger.info("Waiting for internet connection...")
            time.sleep(3)
        enable_prom_mode_on_wlan0()
        return process()
    except:
        logger.exception("Something went wrong...")        
        modem = Modem(device_and_speed[0], device_and_speed[1])
        modem.connect()
        modem.stop_dial_tone()
        modem.disconnect()
        return 1
    finally:
        logger.info("DCNET Dreampi quit successfully")


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
    syslog_handler.setFormatter(
        logging.Formatter("%(name)s[%(process)d]: %(levelname)s %(message)s")
    )
    logger.addHandler(syslog_handler)
    sys.exit(main())
