# Copyright 2012 OpenStack Foundation
# All Rights Reserved
# Copyright (c) 2015 Cisco Systems, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# This is a close copy of a log of nova.network.model (which has a
# partner in Neutron): we're simplying the Neutron model, but to do
# that we need some of the information in the backend of Gluon

# Constants for the 'vif_type' field in VIF class
VIF_TYPE_OVS = 'ovs'
VIF_TYPE_IVS = 'ivs'
VIF_TYPE_DVS = 'dvs'
VIF_TYPE_IOVISOR = 'iovisor'
VIF_TYPE_BRIDGE = 'bridge'
VIF_TYPE_802_QBG = '802.1qbg'
VIF_TYPE_802_QBH = '802.1qbh'
VIF_TYPE_HW_VEB = 'hw_veb'
VIF_TYPE_MLNX_DIRECT = 'mlnx_direct'
VIF_TYPE_IB_HOSTDEV = 'ib_hostdev'
VIF_TYPE_MIDONET = 'midonet'
VIF_TYPE_VHOSTUSER = 'vhostuser'
VIF_TYPE_VROUTER = 'vrouter'
VIF_TYPE_OTHER = 'other'
VIF_TYPE_TAP = 'tap'
VIF_TYPE_MACVTAP = 'macvtap'
VIF_TYPE_BINDING_FAILED = 'binding_failed'

# Constants for dictionary keys in the 'vif_details' field in the VIF
# class
VIF_DETAILS_PORT_FILTER = 'port_filter'
VIF_DETAILS_OVS_HYBRID_PLUG = 'ovs_hybrid_plug'
VIF_DETAILS_PHYSICAL_NETWORK = 'physical_network'

# The following constant defines an SR-IOV related parameter in the
# 'vif_details'. 'profileid' should be used for VIF_TYPE_802_QBH
VIF_DETAILS_PROFILEID = 'profileid'

# The following constant defines an SR-IOV and macvtap related parameter in
# the 'vif_details'. 'vlan' should be used for VIF_TYPE_HW_VEB or
# VIF_TYPE_MACVTAP
VIF_DETAILS_VLAN = 'vlan'

# The following three constants define the macvtap related fields in
# the 'vif_details'.
VIF_DETAILS_MACVTAP_SOURCE = 'macvtap_source'
VIF_DETAILS_MACVTAP_MODE = 'macvtap_mode'
VIF_DETAILS_PHYS_INTERFACE = 'physical_interface'

# Constants for vhost-user related fields in 'vif_details'.
# Sets mode on vhost-user socket, valid values are 'client'
# and 'server'
VIF_DETAILS_VHOSTUSER_MODE = 'vhostuser_mode'
# vhost-user socket path
VIF_DETAILS_VHOSTUSER_SOCKET = 'vhostuser_socket'
# Specifies whether vhost-user socket should be plugged
# into ovs bridge. Valid values are True and False
VIF_DETAILS_VHOSTUSER_OVS_PLUG = 'vhostuser_ovs_plug'

# Constants for dictionary keys in the 'vif_details' field that are
# valid for VIF_TYPE_TAP.
VIF_DETAILS_TAP_MAC_ADDRESS = 'mac_address'

# Define supported virtual NIC types. VNIC_TYPE_DIRECT and VNIC_TYPE_MACVTAP
# are used for SR-IOV ports
VNIC_TYPE_NORMAL = 'normal'
VNIC_TYPE_DIRECT = 'direct'
VNIC_TYPE_MACVTAP = 'macvtap'

# Constant for max length of network interface names
# eg 'bridge' in the Network class or 'devname' in
# the VIF class
NIC_NAME_LEN = 14
