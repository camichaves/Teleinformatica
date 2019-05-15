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

    info('* Ingrese cantidad de sucursales (menor a 32) \n')
    try:
       sucursales= int(raw_input('Sucursales: '))
    except ValueError:
       sys.exit("No es un numero")
    if sucursales >32:
       sys.exit("No es menor a 32")

    print("Creando re para %s sucursales" %sucursales)
    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

	

    info( '* Adding controller\n' )
    info( '* Add switches\n')
    G=globals()
    for n in range(sucursales):
	n2=n+1
	G["s%i_lan"%n2] = net.addSwitch('s%s_lan'%n2, cls=OVSKernelSwitch, failMode='standalone')
	G["s%i_wan"%n2] = net.addSwitch('s%s_wan'%n2, cls=OVSKernelSwitch, failMode='standalone')
    	
    	

    r_central = net.addHost('r_central', cls=Node, ip='')

    for n in range(sucursales):
	n2=n+1
	G["r%i"%n2] = net.addHost('r%s'%n2, cls=Node, ip='')
	



    r_central.cmd('sysctl -w net.ipv4.ip_forward=1')

    for n in range(sucursales):
	n2=n+1
	G["r%i"%n2].cmd('sysctl -w net.ipv4.ip_forward=1')
    	


    info( '* Add hosts\n')

    for n in range(sucursales):
	n2=n+1
	G["h%i"%n2]= net.addHost('h%s'%n2, cls=Host, ip='10.0.%s.254/24'%n2, defaultRoute=None)
    

    info( '* Add links\n')

    ip_last=6;
    for n in range(sucursales):
	n2=n+1
	net.addLink(r_central,G["s%i_wan"%n2], intfName1='r_central-eth%s'%n, params1={ 'ip' : '192.168.100.%s/29'%ip_last })
	ip_last=ip_last+8
    

    ip_last=1;
    for n in range(sucursales):
    	n2=n+1
	net.addLink(G["r%i"%n2],G["s%i_wan"%n2], intfName1='r1-eth%s'%ip_last, params1={ 'ip' : '192.168.100.%s/29'%ip_last })
   	ip_last=ip_last+8
	net.addLink(G["r%i"%n2],G["s%i_lan"%n2], intfName1='r%s-eth'%n2, params1={ 'ip' : '10.0.%s.1/24'%n2 })
	net.addLink(G["h%i"%n2],G["s%i_lan"%n2])

    


    info( '* Starting network\n')
    net.build()
    info( '* Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '* Starting switches\n')

    for n in range(sucursales):
    	n2=n+1
	net.get('s%s_wan'%n2).start([])
       	net.get('s%s_lan'%n2).start([])



    ip_last_central=1 #8 EN 8
    ip_last_r=6 #8 EN 8
    info( '* Post configure switches and hosts\n')

    for n in range(sucursales):
    	n2=n+1
    	net['r_central'].cmd('ip route add 10.0.%s.0/24 via 192.168.100.%s'%(n2,ip_last_central))
	ip_last_central=ip_last_central+8
	net['h%s'%n2].cmd('ip route add 0/0 via 10.0.%s.1'%n2)

	net['r%s'%n2].cmd('ip route add 10.0.0.0/19 via 192.168.100.%s'%ip_last_r)
	ip_last_r=ip_last_r+8

    

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
