from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch.event_handlers import OnProcessExit
from launch_ros.substitutions import FindPackageShare
import os
import xacro
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    share_dir = get_package_share_directory('Assem1_backup_9_description')

    xacro_file = os.path.join(share_dir, 'urdf', 'Assem1_backup_9.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_urdf = robot_description_config.toxml()

    # FIX: use_sim_time=True so TF stamps line up with gz-sim's /clock instead of
    # the wall clock - without this, RViz/tf2 report extrapolation errors.
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[
            {'robot_description': robot_urdf, 'use_sim_time': True}
        ]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={
            'gz_args': '-r empty.sdf'
        }.items()
    )

    # FIX: this bridge used to live in display.launch.py, where no Gazebo ever runs
    # (so it just idled waiting on a /clock that was never published). It belongs
    # here, where gz-sim actually publishes /clock.
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'Assem1_backup_9'
        ],
        output='screen'
    )

    # FIX: the gz_ros2_control plugin brings controller_manager up with the
    # controllers loaded (per controllers.yaml), but none of them are *active*
    # until something calls controller_manager's spawn service. These spawner
    # nodes do that. They're deferred until spawn_robot's one-shot process exits
    # (i.e. the entity actually exists in gz-sim and controller_manager's
    # services are up) - calling them any earlier races the spawn and fails.
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )

    arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_controller'],
        output='screen'
    )

    delayed_controller_spawners = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_robot,
            on_exit=[joint_state_broadcaster_spawner, arm_controller_spawner]
        )
    )

    return LaunchDescription([
        robot_state_publisher_node,
        gazebo,
        clock_bridge,
        spawn_robot,
        delayed_controller_spawners,
    ])
