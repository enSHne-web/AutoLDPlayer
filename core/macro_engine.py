import threading
import time
from models.action import ActionType, AdbAction

class MacroEngine:
    def __init__(self, adb_manager, code_manager=None):
        self.adb_manager = adb_manager
        self.code_manager = code_manager
        # Dictionary luu tru cac luong dang chay theo device_id
        self.running_threads = {}
        # Dictionary luu cờ stop
        self.stop_flags = {}

    def is_running(self, device_id):
        return self.running_threads.get(device_id) is not None and self.running_threads[device_id].is_alive()

    def start_macro(self, device_id, actions, loop_count=1, callback_status=None):
        if self.is_running(device_id):
            return False

        self.stop_flags[device_id] = False
        thread = threading.Thread(target=self._run_macro_loop, args=(device_id, actions, loop_count, callback_status))
        thread.daemon = True
        self.running_threads[device_id] = thread
        thread.start()
        return True

    def stop_macro(self, device_id):
        if device_id in self.stop_flags:
            self.stop_flags[device_id] = True

    def stop_all(self):
        for device_id in self.stop_flags:
            self.stop_flags[device_id] = True

    def _run_macro_loop(self, device_id, actions, loop_count, callback_status):
        # Lay device
        devices = self.adb_manager.get_devices()
        target_device = None
        for d in devices:
            if d.serial == device_id:
                target_device = d
                break
                
        if not target_device:
            if callback_status:
                callback_status(device_id, 'Device not found')
            return

        if callback_status:
            callback_status(device_id, 'Running')

        try:
            # Reset queue code cho thiết bị này để không bị nhảy cóc
            if self.code_manager:
                self.code_manager.reset_queue(device_id)
                
            current_loop = 0
            while not self.stop_flags.get(device_id, False):
                if loop_count > 0 and current_loop >= loop_count:
                    break
                    
                for action in actions:
                    if self.stop_flags.get(device_id, False):
                        break
                    
                    if not self._execute_action(target_device, action, device_id, callback_status):
                        self.stop_flags[device_id] = True
                        break
                    
                    # Nghi nho giua cac step neu can
                    time.sleep(0.05)
                current_loop += 1
        except Exception as e:
            if callback_status:
                callback_status(device_id, f'Error: {str(e)}')
            return
            
        if callback_status:
            callback_status(device_id, 'Stopped')

    def _execute_action(self, device, action: AdbAction, device_id: str, callback_status) -> bool:
        """Thuc thi action. Tra ve False neu muon dung macro."""
        if action.action_type == ActionType.TAP:
            device.shell(f"input tap {action.x} {action.y}")
            time.sleep(0.1)
        elif action.action_type == ActionType.SWIPE:
            device.shell(f"input swipe {action.x} {action.y} {action.end_x} {action.end_y} {action.duration_ms}")
            time.sleep(0.1)
        elif action.action_type == ActionType.TEXT:
            device.shell(f"input text \"{action.text}\"")
            time.sleep(0.1)
        elif action.action_type == ActionType.KEYEVENT:
            device.shell(f"input keyevent {action.keycode}")
            time.sleep(0.1)
        elif action.action_type == ActionType.INPUT_CODE:
            if self.code_manager:
                code = self.code_manager.next_code(device_id)
                if code is None:
                    if callback_status:
                        callback_status(device_id, 'Hết Code! Tự động dừng.')
                    return False # Het code -> ngung macro
                
                # Giả lập gõ từng ký tự ĐỘC LẬP (chạy ngầm) sử dụng lệnh ldconsole của LDPlayer
                try:
                    import subprocess
                    import os
                    # Tim duong dan ldconsole
                    res = subprocess.run(["powershell", "-Command", "(Get-Process dnplayer | Select-Object -First 1).Path"], 
                                         capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    dnplayer_path = res.stdout.strip()
                    if dnplayer_path and os.path.exists(dnplayer_path):
                        ldconsole_path = os.path.join(os.path.dirname(dnplayer_path), "ldconsole.exe")
                        if ldconsole_path:
                            if device_id.startswith('127.0.0.1:'):
                                port = int(device_id.split(':')[1])
                                index = (port - 5555) // 2
                            elif device_id.startswith('emulator-'):
                                port = int(device_id.split('-')[1])
                                index = (port - 5554) // 2
                            else:
                                raise Exception("Not LDPlayer port")
                                
                            # Gõ nguyên cả đoạn code 1 lần để đạt tốc độ tối đa
                            subprocess.run([ldconsole_path, "action", "--index", str(index), "--key", "call.input", "--value", code], 
                                           creationflags=subprocess.CREATE_NO_WINDOW)
                    else:
                        raise Exception("LDPlayer path not found")
                except Exception as e:
                    # Fallback ADB neu co loi
                    device.shell(f"input text \"{code}\"")
                        
                time.sleep(0.1)
        elif action.action_type == ActionType.DELAY:
            time.sleep(action.delay_ms / 1000.0)

                
        return True
