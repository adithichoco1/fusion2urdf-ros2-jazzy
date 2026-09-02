import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/adithi/Desktop/Astra_tasks/fusion2urdf-ros2-jazzy/Assem1_backup_5_description/install/Assem1_backup_5_description'
