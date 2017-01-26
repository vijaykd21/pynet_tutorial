#!/usr/bin/env python

import socket, sys
import time
import telnetlib
import getpass

TELNET_PORT = 23
TELNET_TIMEOUT = 6

class telnet_conn:
    ''' Attributes
    ip_addr: IP address
    username: username
    password: password
    conn: Telent connecction object
    conn_status: connection status
    '''
    
    def __init__(self, ip_address, username, password):
        self.ip_addr = ip_address
        self.username = username
        self.password = password
        self.conn =  telnetlib.Telnet()
        self.conn_status = False
        self.login_status = False
        try:
            self.conn.open(self.ip_addr, TELNET_PORT, TELNET_TIMEOUT)
            self.conn_status = True
        except socket.timeout:
            print "Conncetion timed-out"
            self.conn_status = False

    def update(self, ip, un, pw):
        self.ip_addr = ip
        self.username = un
        self.password = pw
        if not self.conn_status:
            try:
                self.conn.open(self.ip_addr, TELNET_PORT, TELNET_TIMEOUT)
                self.conn_status = True
            except socket.timeout:
                print "Conncetion timed-out"
                self.conn_status = False
        self.login_status = False

    def get_ip(self):
        return self.ip_addr

    def get_username(self):
        return self.username

    def connection_status(self):
        return self.conn_status

    def login_status(self):
        return self.login_status

    def __del__(self):
        if self.conn_status:
            self.conn.close()
    
    def close(self):
        self.conn.close()

    def login(self):
        if self.conn_status: 
            remoteConn = self.conn
            if not self.login_status:
                output = remoteConn.read_until('sername:', TELNET_TIMEOUT)
                remoteConn.write(self.username + '\n')
                output += remoteConn.read_until('assword:', TELNET_TIMEOUT)
                remoteConn.write(self.password +'\n')
                time.sleep(1)
                output = remoteConn.read_until('#', TELNET_TIMEOUT)
                if 'failed' not in output:
                    self.login_status = True
                else:
                    print "Login Failed to machine", self.ip_addr

            return self.login_status 
        else:
            print "Connection Error: Please check the connection for", self.ip_addr
            return self.login_status

    def send_command(self, cmd):
        output = ""
        remoteConn = self.conn
        if self.conn_status:
            remoteConn.write('terminal length 0' + '\n')
            cmd = cmd.rstrip()
            remoteConn.write(cmd + '\n')
            time.sleep(1)
            output = remoteConn.read_very_eager()
            return (True, output)
        else:
            print "Connection failed"
            return (False, output)


def main():
    ip_addr = raw_input("Enter IP Address: ")
    username = raw_input("Enter username: ")
    password = getpass.getpass()
    dev = telnet_conn(ip_addr, username, password)
    conn_status = dev.connection_status()
    while not conn_status:
        print "Error in connection. Check connection and reenter the following"
        ip_addr = raw_input("Enter IP Address: ")
        username = raw_input("Enter username: ")
        password = getpass.getpass()
        dev.update(ip_addr, username, password)
        conn_status = dev.connection_status()

    login_status = False
    while not login_status:
        login_status = dev.login()
        if not login_status:
            print "Error with login. Re-enter login info"
            ip_addr = dev.get_ip()
            username = raw_input("Enter username: ")
            password = getpass.getpass()
            dev.update(ip_addr, username, password)
 
    dev.send_command('terminal length 0')
    (status, output) = dev.send_command('show ip int brief')
    if status:
        print output
    else:
        print "Couldnt run the command"

if __name__ == "__main__":
    main()    
     
