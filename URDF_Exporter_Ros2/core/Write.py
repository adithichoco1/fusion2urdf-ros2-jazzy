# -*- coding: utf-8 -*-
"""
Created on Sun May 12 20:46:26 2019

@author: syuntoku
"""

import adsk, os
from xml.etree.ElementTree import Element, SubElement
from . import Link, Joint, launch_templates
from ..utils import utils

def write_link_urdf(joints_dict, repo, links_xyz_dict, file_name, inertial_dict):
    """
    Write links information into urdf "repo/file_name"


    Parameters
    ----------
    joints_dict: dict
        information of the each joint
    repo: str
        the name of the repository to save the xml file
    links_xyz_dict: vacant dict
        xyz information of the each link
    file_name: str
        urdf full path
    inertial_dict:
        information of the each inertial

    Note
    ----------
    In this function, links_xyz_dict is set for write_joint_tran_urdf.
    The origin of the coordinate of center_of_mass is the coordinate of the link
    """
    with open(file_name, mode='a') as f:
        # for base_link
        center_of_mass = inertial_dict['base_link']['center_of_mass']
        link = Link.Link(name='base_link', xyz=[0,0,0],
            center_of_mass=center_of_mass, repo=repo,
            mass=inertial_dict['base_link']['mass'],
            inertia_tensor=inertial_dict['base_link']['inertia'])
        links_xyz_dict[link.name] = link.xyz
        link.make_link_xml()
        f.write(link.link_xml)
        f.write('\n')

        # others
        for joint in joints_dict:
            name = joints_dict[joint]['child']
            center_of_mass = \
                [ i-j for i, j in zip(inertial_dict[name]['center_of_mass'], joints_dict[joint]['xyz'])]
            link = Link.Link(name=name, xyz=joints_dict[joint]['xyz'],\
                center_of_mass=center_of_mass,\
                repo=repo, mass=inertial_dict[name]['mass'],\
                inertia_tensor=inertial_dict[name]['inertia'])
            links_xyz_dict[link.name] = link.xyz
            link.make_link_xml()
            f.write(link.link_xml)
            f.write('\n')


def write_joint_urdf(joints_dict, repo, links_xyz_dict, file_name):
    """
    Write joints and transmission information into urdf "repo/file_name"


    Parameters
    ----------
    joints_dict: dict
        information of the each joint
    repo: str
        the name of the repository to save the xml file
    links_xyz_dict: dict
        xyz information of the each link
    file_name: str
        urdf full path
    """

    with open(file_name, mode='a') as f:
        for j in joints_dict:
            parent = joints_dict[j]['parent']
            child = joints_dict[j]['child']
            joint_type = joints_dict[j]['type']
            upper_limit = joints_dict[j]['upper_limit']
            lower_limit = joints_dict[j]['lower_limit']
            try:
                xyz = [round(p-c, 6) for p, c in \
                    zip(links_xyz_dict[parent], links_xyz_dict[child])]  # xyz = parent - child
            except KeyError as ke:
                app = adsk.core.Application.get()
                ui = app.userInterface
                ui.messageBox("There seems to be an error with the connection between\n\n%s\nand\n%s\n\nCheck \
whether the connections\nparent=component2=%s\nchild=component1=%s\nare correct or if you need \
to swap component1<=>component2"
                % (parent, child, parent, child), "Error!")
                quit()

            joint = Joint.Joint(name=j, joint_type = joint_type, xyz=xyz, \
            axis=joints_dict[j]['axis'], parent=parent, child=child, \
            upper_limit=upper_limit, lower_limit=lower_limit)
            joint.make_joint_xml()
            joint.make_transmission_xml()
            f.write(joint.joint_xml)
            f.write('\n')

def write_gazebo_endtag(file_name):
    """
    Write about gazebo_plugin and the </robot> tag at the end of the urdf


    Parameters
    ----------
    file_name: str
        urdf full path
    """
    with open(file_name, mode='a') as f:
        f.write('</robot>\n')


def write_urdf(joints_dict, links_xyz_dict, inertial_dict, package_name, robot_name, save_dir):
    try: os.mkdir(save_dir + '/urdf')
    except: pass

    file_name = save_dir + '/urdf/' + robot_name + '.xacro'  # the name of urdf file
    repo = package_name + '/meshes/'  # the repository of binary stl files
    with open(file_name, mode='w') as f:
        f.write('<?xml version="1.0" ?>\n')
        f.write('<robot name="{}" xmlns:xacro="http://www.ros.org/wiki/xacro">\n'.format(robot_name))
        f.write('\n')
        f.write('<xacro:include filename="$(find {})/urdf/materials.xacro" />'.format(package_name))
        f.write('\n')
        f.write('<xacro:include filename="$(find {})/urdf/{}.trans" />'.format(package_name, robot_name))
        f.write('\n')
        f.write('<xacro:include filename="$(find {})/urdf/{}.ros2_control.xacro" />'.format(package_name, robot_name))
        f.write('\n')
        f.write('<xacro:include filename="$(find {})/urdf/{}.gazebo" />'.format(package_name, robot_name))
        f.write('\n')

    write_link_urdf(joints_dict, repo, links_xyz_dict, file_name, inertial_dict)
    write_joint_urdf(joints_dict, repo, links_xyz_dict, file_name)
    write_gazebo_endtag(file_name)

def write_materials_xacro(joints_dict, links_xyz_dict, inertial_dict, package_name, robot_name, save_dir):
    try: os.mkdir(save_dir + '/urdf')
    except: pass

    file_name = save_dir + '/urdf/materials.xacro'  # the name of urdf file
    with open(file_name, mode='w') as f:
        f.write('<?xml version="1.0" ?>\n')
        f.write('<robot name="{}" xmlns:xacro="http://www.ros.org/wiki/xacro" >\n'.format(robot_name))
        f.write('\n')
        f.write('<material name="silver">\n')
        f.write('  <color rgba="0.700 0.700 0.700 1.000"/>\n')
        f.write('</material>\n')
        f.write('\n')
        f.write('</robot>\n')

def write_transmissions_xacro(joints_dict, links_xyz_dict, inertial_dict, package_name, robot_name, save_dir):
    """
    Write joints and transmission information into urdf "repo/file_name"


    Parameters
    ----------
    joints_dict: dict
        information of the each joint
    repo: str
        the name of the repository to save the xml file
    links_xyz_dict: dict
        xyz information of the each link
    file_name: str
        urdf full path
    """

    file_name = save_dir + '/urdf/{}.trans'.format(robot_name)  # the name of urdf file
    with open(file_name, mode='w') as f:
        f.write('<?xml version="1.0" ?>\n')
        f.write('<robot name="{}" xmlns:xacro="http://www.ros.org/wiki/xacro" >\n'.format(robot_name))
        f.write('\n')

        for j in joints_dict:
            parent = joints_dict[j]['parent']
            child = joints_dict[j]['child']
            joint_type = joints_dict[j]['type']
            upper_limit = joints_dict[j]['upper_limit']
            lower_limit = joints_dict[j]['lower_limit']
            try:
                xyz = [round(p-c, 6) for p, c in \
                    zip(links_xyz_dict[parent], links_xyz_dict[child])]  # xyz = parent - child
            except KeyError as ke:
                app = adsk.core.Application.get()
                ui = app.userInterface
                ui.messageBox("There seems to be an error with the connection between\n\n%s\nand\n%s\n\nCheck \
whether the connections\nparent=component2=%s\nchild=component1=%s\nare correct or if you need \
to swap component1<=>component2"
                % (parent, child, parent, child), "Error!")
                quit()

            joint = Joint.Joint(name=j, joint_type = joint_type, xyz=xyz, \
            axis=joints_dict[j]['axis'], parent=parent, child=child, \
            upper_limit=upper_limit, lower_limit=lower_limit)
            if joint_type != 'fixed':
                joint.make_transmission_xml()
                f.write(joint.tran_xml)
                f.write('\n')

        f.write('</robot>\n')

def write_gazebo_xacro(joints_dict, links_xyz_dict, inertial_dict, package_name, robot_name, save_dir):
    """
    FIXES applied here (see chat explanation for details):
      1. The gz_ros2_control plugin block previously had no <parameters> element, so
         controller_manager never knew where controllers.yaml was and loaded zero
         controllers - nothing in controllers.yaml ever took effect.
      2. "Gazebo/Silver" is a classic-Gazebo (Ogre1) material-script name. gz-sim's
         Ogre2 renderer doesn't resolve these; links rendered flat default grey.
         Replaced with an explicit ambient/diffuse/specular <material> block.
      3. Bare <mu1>/<mu2> as direct children of <gazebo reference="..."> was a
         classic-Gazebo-only URDF-extension shorthand that the modern URDF->SDF
         conversion path doesn't reliably honor. Replaced with the SDF-native
         <collision><surface><friction><ode><mu>/<mu2></ode></friction></surface>
         </collision> form, which is unambiguous under gz-sim.
    """
    try: os.mkdir(save_dir + '/urdf')
    except: pass

    file_name = save_dir + '/urdf/' + robot_name + '.gazebo'  # the name of urdf file
    repo = robot_name + '/meshes/'  # the repository of binary stl files
    #repo = package_name + '/' + robot_name + '/bin_stl/'  # the repository of binary stl files
    with open(file_name, mode='w') as f:
        f.write('<?xml version="1.0" ?>\n')
        f.write('<robot name="{}" xmlns:xacro="http://www.ros.org/wiki/xacro" >\n'.format(robot_name))
        f.write('\n')

        gazebo = Element('gazebo')
        plugin = SubElement(gazebo, 'plugin')
        plugin.attrib = {
            'name': 'gz_ros2_control::GazeboSimROS2ControlPlugin',
            'filename': 'libgz_ros2_control-system.so'
        }
        # FIX 1: point the plugin at controllers.yaml so controller_manager actually
        # loads the controllers write_controllers_yaml() generates.
        parameters = SubElement(plugin, 'parameters')
        parameters.text = '$(find {})/config/controllers.yaml'.format(package_name)
        gazebo_xml = "\n".join(utils.prettify(gazebo).split("\n")[1:])
        f.write(gazebo_xml)

        # for base_link
        f.write('<gazebo reference="base_link">\n')
        f.write('  <visual>\n')
        f.write('    <material>\n')
        f.write('      <ambient>0.7 0.7 0.7 1</ambient>\n')
        f.write('      <diffuse>0.7 0.7 0.7 1</diffuse>\n')
        f.write('      <specular>0.3 0.3 0.3 1</specular>\n')
        f.write('    </material>\n')
        f.write('  </visual>\n')
        f.write('  <collision>\n')
        f.write('    <surface>\n')
        f.write('      <friction>\n')
        f.write('        <ode>\n')
        f.write('          <mu>0.2</mu>\n')
        f.write('          <mu2>0.2</mu2>\n')
        f.write('        </ode>\n')
        f.write('      </friction>\n')
        f.write('    </surface>\n')
        f.write('  </collision>\n')
        f.write('  <self_collide>true</self_collide>\n')
        f.write('  <gravity>true</gravity>\n')
        f.write('</gazebo>\n')
        f.write('\n')

        # others
        for joint in joints_dict:
            name = joints_dict[joint]['child']
            f.write('<gazebo reference="{}">\n'.format(name))
            f.write('  <visual>\n')
            f.write('    <material>\n')
            f.write('      <ambient>0.7 0.7 0.7 1</ambient>\n')
            f.write('      <diffuse>0.7 0.7 0.7 1</diffuse>\n')
            f.write('      <specular>0.3 0.3 0.3 1</specular>\n')
            f.write('    </material>\n')
            f.write('  </visual>\n')
            f.write('  <collision>\n')
            f.write('    <surface>\n')
            f.write('      <friction>\n')
            f.write('        <ode>\n')
            f.write('          <mu>0.2</mu>\n')
            f.write('          <mu2>0.2</mu2>\n')
            f.write('        </ode>\n')
            f.write('      </friction>\n')
            f.write('    </surface>\n')
            f.write('  </collision>\n')
            f.write('  <self_collide>true</self_collide>\n')
            f.write('</gazebo>\n')
            f.write('\n')

        f.write('</robot>\n')

def write_display_launch(package_name, robot_name, save_dir):
    """
    write display launch file "save_dir/launch/display.launch"


    Parameter
    ---------
    robot_name: str
    name of the robot
    save_dir: str
    path of the repository to save
    """
    try: os.mkdir(save_dir + '/launch')
    except: pass

    file_text = launch_templates.get_display_launch_text(package_name, robot_name)

    file_name = os.path.join(save_dir, 'launch', 'display.launch.py')
    with open(file_name, mode='w') as f:
        f.write(file_text)

def write_gazebo_launch(package_name, robot_name, save_dir):
    """
    write gazebo launch file "save_dir/launch/gazebo.launch"


    Parameter
    ---------
    robot_name: str
        name of the robot
    save_dir: str
        path of the repository to save
    """

    try: os.mkdir(save_dir + '/launch')
    except: pass

    file_text = launch_templates.get_gazebo_launch_text(package_name, robot_name)

    file_name = os.path.join(save_dir, 'launch', 'gazebo.launch.py')
    with open(file_name, mode='w') as f:
        f.write(file_text)

def write_ros2_control_xacro(joints_dict, links_xyz_dict, inertial_dict, package_name, robot_name, save_dir):

    try:
        os.mkdir(save_dir + '/urdf')
    except:
        pass

    file_name = save_dir + '/urdf/{}.ros2_control.xacro'.format(robot_name)

    with open(file_name, mode='w') as f:
        f.write('<?xml version="1.0" ?>\n')
        f.write('<robot name="{}" xmlns:xacro="http://www.ros.org/wiki/xacro">\n'.format(robot_name))
        f.write('\n')

        f.write('  <ros2_control name="GazeboSimSystem" type="system">\n')
        f.write('\n')

        f.write('    <hardware>\n')
        f.write('      <plugin>gz_ros2_control/GazeboSimSystem</plugin>\n')
        f.write('    </hardware>\n')
        f.write('\n')

        for joint in joints_dict:
            joint_type = joints_dict[joint]['type']

            if joint_type == 'fixed':
                continue

            f.write('    <joint name="{}">\n'.format(joint))
            f.write('      <command_interface name="position"/>\n')
            f.write('      <state_interface name="position"/>\n')
            f.write('      <state_interface name="velocity"/>\n')
            f.write('    </joint>\n')
            f.write('\n')

        f.write('  </ros2_control>\n')
        f.write('\n')
        f.write('</robot>\n')

def write_controllers_yaml(joints_dict, package_name, robot_name, save_dir):
    """
    Generate the ros2_control controller configuration.

    Generates:
      - joint_state_broadcaster
      - arm_controller using JointTrajectoryController

    Only non-fixed joints are added to arm_controller.
    """

    # Create config directory if it does not exist
    config_dir = os.path.join(save_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)

    file_name = os.path.join(config_dir, 'controllers.yaml')

    # Collect movable joints
    movable_joints = []

    for joint_name, joint_data in joints_dict.items():
        if joint_data['type'] == 'fixed':
            continue

        movable_joints.append(joint_name)

    # Write controller configuration
    with open(file_name, mode='w') as f:

        f.write('controller_manager:\n')
        f.write('  ros__parameters:\n')
        f.write('    update_rate: 100\n')
        f.write('\n')

        # Joint state broadcaster
        f.write('    joint_state_broadcaster:\n')
        f.write('      type: joint_state_broadcaster/JointStateBroadcaster\n')
        f.write('\n')

        # Main trajectory controller
        f.write('    arm_controller:\n')
        f.write('      type: joint_trajectory_controller/JointTrajectoryController\n')
        f.write('\n')

        # Controller parameters
        f.write('arm_controller:\n')
        f.write('  ros__parameters:\n')

        # Joints
        f.write('    joints:\n')

        for joint_name in movable_joints:
            f.write('      - "{}"\n'.format(joint_name))

        f.write('\n')

        # Command interfaces
        f.write('    command_interfaces:\n')
        f.write('      - position\n')
        f.write('\n')

        # State interfaces
        f.write('    state_interfaces:\n')
        f.write('      - position\n')
        f.write('      - velocity\n')