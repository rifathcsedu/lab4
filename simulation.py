'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import network
import link
import threading
from time import sleep
import sys

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 1 #give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads
    
    #create network hosts
    client = network.Host(1)
    object_L.append(client)
    server = network.Host(2)
    object_L.append(server)
    table=[]
    #create routers and routing tables for connected clients (subnets)
    router_a_rt_tbl_D = {1: {0: 1}} # packet to host 1 through interface 0 for cost 1
    router_a = network.Router(name='A', 
                              intf_cost_L=[1,1], 
                              rt_tbl_D = router_a_rt_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_a)
    router_b_rt_tbl_D = {2: {1: 3}} # packet to host 2 through interface 1 for cost 3
    router_b = network.Router(name='B', 
                              intf_cost_L=[1,3], 
                              rt_tbl_D = router_b_rt_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_b)
    table.append(router_a_rt_tbl_D)
    table.append(router_b_rt_tbl_D)
    #print table
    #create a Link Layer to keep track of links between network nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)
    
    #add all the links
    link_layer.add_link(link.Link(client, 0, router_a, 0))
    link_layer.add_link(link.Link(router_a, 1, router_b, 0))
    link_layer.add_link(link.Link(router_b, 1, server, 0))
    
    
    #start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run)) 
    
    for t in thread_L:
        t.start()
    
    #send out routing information from router A to router B interface 0
    router_a.send_routes(1)
    
    #create some send events    
    for i in range(1):
        server.udt_send(1, 'Sample client data %d' % i)
        
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)
    
    #router_a.print_routes()
    #router_b.print_routes()
    #print the final routing tables
    flag=0
    print("\n\n\n")
    for obj in object_L:
        if str(type(obj)) == "<class 'network.Router'>" and flag==0:
            print("  Cost to")
            print("  A B")
            obj.print_routes(1)
            flag=1
        elif str(type(obj)) == "<class 'network.Router'>":
            obj.print_routes(1)
    print("\n\n\n")
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")



# writes to host periodically