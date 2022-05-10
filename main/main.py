def test():
    from client import Client

    c = Client("1b94f71484d0488681ef7c9a625a2169", "pyxy.s-2.link", 9190)
    import uasyncio as uas

    uas.run(
        c.remote_handshake(
            {
                "ip": '',
                "domain": 'www.google.com',
                "port": '443',
            }
        )
    )
    
    # uas.run(c.remote_writer.close())
    
    print('END TEST')
    
