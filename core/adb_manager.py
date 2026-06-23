from ppadb.client import Client as AdbClient
import subprocess
import socket

class AdbManager:
    def __init__(self, host='127.0.0.1', port=5037):
        self.host = host
        self.port = port
        self.client = None
        self._init_adb()
        
    def _init_adb(self):
        """Khoi tao ADB client an toan — khong bao gio treo app."""
        # Kiem tra ADB server co dang chay khong bang socket nhanh
        if not self._is_adb_server_running():
            self._try_start_adb_server()
        
        # Neu da chay roi thi tao client
        if self._is_adb_server_running():
            try:
                self.client = AdbClient(host=self.host, port=self.port)
            except Exception:
                self.client = None

    def _is_adb_server_running(self):
        """Kiem tra nhanh ADB server co listening khong (timeout 2s)."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((self.host, self.port))
            s.close()
            return True
        except Exception:
            return False

    def _try_start_adb_server(self):
        """Thu khoi dong ADB server."""
        try:
            subprocess.run(['adb', 'start-server'], check=True,
                           timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            pass

    def get_devices(self):
        try:
            if self.client is None:
                return []
            return self.client.devices()
        except Exception:
            return []
            
    def connect_device(self, host='127.0.0.1', port=5555):
        try:
            if self.client is None:
                return False
            self.client.remote_connect(host, port)
            return True
        except Exception:
            return False

    def scan_local_emulators(self, start_port=5555, end_port=5585, step=2):
        '''Quet cac port de tim gia lap LDPlayer hoac Nox'''
        found_devices = []
        for port in range(start_port, end_port, step):
            if self.connect_device('127.0.0.1', port):
                found_devices.append(f'127.0.0.1:{port}')
        return found_devices
