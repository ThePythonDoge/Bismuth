from time import sleep


def execute(cursor, query):
    """
    Secure execute for slow nodes
    """
    
    while 1:
        try:
            cursor.execute(query)
            return cursor
        except Exception as exc:
            print("Retrying database execute due to %s"% exc)
            sleep(0.1)

def execute_param(cursor, query, param):
    """
    Secure execute w/ param for slow nodes
    """
    
    while 1:
        try:
            cursor.execute(query, param)
            return cursor
        except Exception as exc:
            print("Retrying database execute due to %s" % ex)
            sleep(0.1)
