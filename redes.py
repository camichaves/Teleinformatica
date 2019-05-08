#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '* Adding controller\n' )
    info( '* Add switches\n')
    s1_lan = net.addSwitch('s1_lan', cls=OVSKernelSwitch, failMode='standalone')
    s1_wan = net.addSwitch('s1_wan', cls=OVSKernelSwitch, failMode='standalone')
    s2_lan = net.addSwitch('s2_lan', cls=OVSKernelSwitch, failMode='standalone')
    s2_wan = net.addSwitch('s2_wan', cls=OVSKernelSwitch, failMode='standalone')
    s3_lan = net.addSwitch('s3_lan', cls=OVSKernelSwitch, failMode='standalone')
    s3_wan = net.addSwitch('s3_wan', cls=OVSKernelSwitch, failMode='standalone')

    r_central = net.addHost('r_central', cls=Node, ip='')
    r1 = net.addHost('r1', cls=Node, ip='')
    r2 = net.addHost('r2', cls=Node, ip='')
    r3 = net.addHost('r3', cls=Node, ip='')

    r_central.cmd('sysctl -w net.ipv4.ip_forward=1')
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')

    info( '* Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.1.254/24', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.2.254/24', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.3.254/24', defaultRoute=None)

    info( '* Add links\n')
    net.addLink(r_central, s1_wan, intfName1='r_central-eth0', params1={ 'ip' : '192.168.100.6/29' })
    net.addLink(r_central, s2_wan, intfName1='r_central-eth1', params1={ 'ip' : '192.168.100.14/29' })
    net.addLink(r_central, s3_wan, intfName1='r_central-eth2', params1={ 'ip' : '192.168.100.22/29' })
    net.addLink(r1, s1_wan, intfName1='r1-eth0', params1={ 'ip' : '192.168.100.1/29' })
    net.addLink(r2, s2_wan, intfName1='r2-eth0', params1={ 'ip' : '192.168.100.9/29' })
    net.addLink(r3, s3_wan, intfName1='r2-eth0', params1={ 'ip' : '192.168.100.17/29' })
    net.addLink(r1, s1_lan, intfName1='r1-eth1', params1={ 'ip' : '10.0.1.1/24' })
    net.addLink(r2, s2_lan, intfName1='r2-eth1', params1={ 'ip' : '10.0.2.1/24' })
    net.addLink(r3, s3_lan, intfName1='r3-eth1', params1={ 'ip' : '10.0.3.1/24' })

    net.addLink(h1, s1_lan)
    net.addLink(h2, s2_lan)
    net.addLink(h3, s3_lan)

    info( '* Starting network\n')
    net.build()
    info( '* Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '* Starting switches\n')
    net.get('s2_wan').start([])
    net.get('s2_lan').start([])
    net.get('s1_lan').start([])
    net.get('s1_wan').start([])
    net.get('s3_lan').start([])
    net.get('s3_wan').start([])

    info( '* Post configure switches and hosts\n')
    net['r_central'].cmd('ip route add 10.0.1.0/24 via 192.168.100.1')
    net['r_central'].cmd('ip route add 10.0.2.0/24 via 192.168.100.9')
    net['r_central'].cmd('ip route add 10.0.3.0/24 via 192.168.100.17')
    net['h1'].cmd('ip route add 0/0 via 10.0.1.1')
    net['h2'].cmd('ip route add 0/0 via 10.0.2.1')
    net['r1'].cmd('ip route add 10.0.0.0/19 via 192.168.100.6')
    net['r2'].cmd('ip route add 10.0.0.0/19 via 192.168.100.14')
    net['h3'].cmd('ip route add 0/0 via 10.0.3.1')
    net['r3'].cmd('ip route add 10.0.0.0/19 via 192.168.100.22')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
