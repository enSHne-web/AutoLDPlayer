import win32gui

def get_mapped_coordinate(screen_x, screen_y, adb_manager, selected_device_serial=None):
    '''
    Chuyen doi toa do man hinh Windows sang toa do noi bo cua gia lap thong qua ADB.
    '''
    # 1. Tim cua so render
    hwnd = win32gui.WindowFromPoint((screen_x, screen_y))
    if not hwnd:
        return screen_x, screen_y
        
    # Di nguoc len tim cua so cha cao nhat
    parent = hwnd
    while win32gui.GetParent(parent) != 0:
        parent = win32gui.GetParent(parent)
        
    # Tim cua so hien thi game (RenderWindow doi voi LDPlayer)
    render_hwnd = win32gui.FindWindowEx(parent, 0, 'RenderWindow', None)
    if not render_hwnd:
        # Thu voi theWindow cua cac gia lap khac
        render_hwnd = win32gui.FindWindowEx(parent, 0, 'subWin', None) # DVNox
    
    if not render_hwnd:
        render_hwnd = hwnd # Fallback

    left, top, right, bottom = win32gui.GetWindowRect(render_hwnd)
    
    local_x = screen_x - left
    local_y = screen_y - top
    width = right - left
    height = bottom - top
    
    if width <= 0 or height <= 0:
        return screen_x, screen_y

    # 2. Lay Device ADB de hoi do phan giai
    devices = adb_manager.get_devices()
    if not devices:
        return local_x, local_y
        
    target_device = devices[0]
    if selected_device_serial:
        for d in devices:
            if d.serial == selected_device_serial:
                target_device = d
                break

    # 3. Tinh toan ty le map
    try:
        size_str = target_device.shell('wm size')
        if 'Physical size:' in size_str:
            size_part = size_str.split(':')[1].strip()
            adb_w_str, adb_h_str = size_part.split('x')
            adb_w = int(adb_w_str)
            adb_h = int(adb_h_str)

            # Nhan chia ty le
            adb_x = int(local_x * adb_w / width)
            adb_y = int(local_y * adb_h / height)
            
            # Gioi han lai trong khoang man hinh neu lo vuot ra ngoai
            adb_x = max(0, min(adb_x, adb_w))
            adb_y = max(0, min(adb_y, adb_h))
            
            return adb_x, adb_y
    except Exception:
        pass

    return local_x, local_y
